import cv2
import asyncio
import base64
import io
import subprocess
import multiprocessing
import numpy as np
from queue import Empty, Full
from datetime import datetime
from logging import Logger
from ..config import Config
from ..storage.base import BaseStorage
from ..storage.models import Image
from PIL.Image import Image as PILImage
from paddleocr import PaddleOCR
from paddlex.inference.pipelines.ocr.result import OCRResult
from uuid import uuid4


ffmpeg_queue = multiprocessing.Queue(maxsize=1)


def ffmpeg_reader(
    queue: multiprocessing.Queue,
    video_width: int,
    video_height: int,
    video_channels: int,
    video_fps: int,
) -> None:
    frame_size = video_width * video_height * video_channels
    ffmpeg_proc = subprocess.Popen(
        [
            "ffmpeg",
            "-fflags",
            "nobuffer",
            "-flags",
            "low_delay",
            "-analyzeduration",
            "0",
            "-probesize",
            "32",
            "-max_delay",
            "0",
            "-i",
            "rtmp://localhost/live",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-r",
            str(video_fps),
            "-s",
            f"{video_width}x{video_height}",
            "-tune",
            "zerolatency",
            "-preset",
            "ultrafast",
            "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=frame_size,
    )
    try:
        while True:
            raw_frame = ffmpeg_proc.stdout.read(frame_size)  # type: ignore
            if not raw_frame:
                break
            try:
                queue.get_nowait()
            except Empty:
                pass
            try:
                queue.put_nowait(raw_frame)
            except Full:
                continue
    finally:
        ffmpeg_proc.terminate()
        ffmpeg_proc.wait()
        queue.close()
        queue.join_thread()


class FrameProcessor:
    def __init__(self, storage: BaseStorage, logger: Logger) -> None:
        self.storage = storage
        self.logger = logger
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
            text_detection_model_name="PP-OCRv5_mobile_det",
        )
        self.frame_size = (
            Config.VIDEO_WIDTH * Config.VIDEO_HEIGHT * Config.VIDEO_CHANNELS
        )
        self.queue = ffmpeg_queue
        self.proc = multiprocessing.Process(
            target=ffmpeg_reader,
            args=(
                ffmpeg_queue,
                Config.VIDEO_WIDTH,
                Config.VIDEO_HEIGHT,
                Config.VIDEO_CHANNELS,
                Config.VIDEO_FPS,
            ),
        )
        self.proc.start()

    async def start(self):
        self.logger.info("Starting frame processor loop...")
        proceeded_frames = 0
        try:
            while True:
                try:
                    try:
                        raw_frame = self.queue.get_nowait()
                    except Empty:
                        self.logger.warning("No frames received from ffmpeg.")
                        await asyncio.sleep(1)
                        continue

                    frame = np.frombuffer(raw_frame, np.uint8).reshape(
                        (
                            Config.VIDEO_HEIGHT,
                            Config.VIDEO_WIDTH,
                            Config.VIDEO_CHANNELS,
                        )
                    )
                    await self.process_frame(frame)
                    if proceeded_frames == 0:
                        self.logger.info("First frame processed successfully.")
                    proceeded_frames += 1
                    if proceeded_frames % 100 == 0:
                        self.logger.info(f"Processed {proceeded_frames} frames so far.")

                except KeyboardInterrupt:
                    self.logger.info("Frame processor interrupted by user.")
                    return
                except Exception as e:
                    self.logger.error(f"Error in frame processor: {e}")
                    await asyncio.sleep(1)
                    continue
        except KeyboardInterrupt:
            self.logger.info("Frame processor stopped by user.")
        finally:
            self.proc.terminate()
            self.proc.join()
            self.logger.info("Frame processor terminated.")

    async def process_frame(self, frame: cv2.typing.MatLike) -> None:
        ocr_result: OCRResult = self.ocr.predict(input=frame)[0]
        await self.storage.save_image(
            Image(
                id=uuid4(),
                created_at=datetime.now(),
                image_base64=self.image_to_base64(ocr_result.img["ocr_res_img"])
                if Config.DEBUG_MODE
                else self.frame_to_base64(frame),
                text="".join(res.strip().lower() for res in ocr_result["rec_texts"]),
            )
        )

    def image_to_base64(self, image: PILImage) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def frame_to_base64(self, frame: cv2.typing.MatLike) -> str:
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            raise ValueError("Cannot encode frame to JPEG format.")
        return base64.b64encode(buffer).decode("utf-8")  # type: ignore
