import cv2
import asyncio
import base64
import io
import subprocess
import multiprocessing
import numpy as np
from shared_models.messaging import MessageShown as MessageShownSharedModel
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher
from thefuzz import process
from datetime import datetime, timedelta
from logging import Logger
from .config import Config
from .storage.base import BaseStorage
from .storage.models import Image, ShownMessage
from PIL.Image import Image as PILImage
from paddleocr import PaddleOCR
from paddlex.inference.pipelines.ocr.result import OCRResult
from uuid import uuid4


class CaptureLoopError(Exception):
    """Custom exception for errors in the capture loop."""

    pass


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
            if not queue.empty():
                queue.get()
            queue.put(raw_frame)
    finally:
        ffmpeg_proc.terminate()
        ffmpeg_proc.wait()
        queue.close()
        queue.join_thread()


class CaptureLoop:
    def __init__(
        self, storage: BaseStorage, logger: Logger, bot_publisher: AsyncAPIPublisher
    ) -> None:
        self.storage = storage
        self.logger = logger
        self.publisher = bot_publisher
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
        self.logger.info("Starting capture loop...")
        try:
            while True:
                try:
                    if self.queue.empty():
                        continue
                    raw_frame = self.queue.get(timeout=1)
                    frame = np.frombuffer(raw_frame, np.uint8).reshape(
                        (Config.VIDEO_HEIGHT, Config.VIDEO_WIDTH, Config.VIDEO_CHANNELS)
                    )
                    await self.process_frame(frame)
                    await self.match_frames()
                    await asyncio.sleep(0.1)
                except CaptureLoopError as e:
                    self.logger.error(f"Capture loop error: {e}")
                    raise
                except KeyboardInterrupt:
                    self.logger.info("Capture loop interrupted by user.")
                    return
                except Exception as e:
                    self.logger.error(f"Error in capture loop: {e}")
                    await asyncio.sleep(1)
                    continue
        except KeyboardInterrupt:
            self.logger.info("Capture loop stopped by user.")
        finally:
            self.proc.terminate()
            self.proc.join()
            self.logger.info("Capture loop terminated.")

    async def process_frame(self, frame: cv2.typing.MatLike) -> None:
        ocr_result: OCRResult = self.ocr.predict(input=frame)[0]
        print("".join(res.strip().lower() for res in ocr_result["rec_texts"]))
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

    async def match_frames(self) -> None:
        current_time = datetime.now()
        shown_messages = await self.storage.find_shown_messages_by_show_at_time(
            start=datetime(1970, 1, 1),
            end=current_time - timedelta(seconds=Config.ANALYTICS_DELAY_SECONDS),
        )
        images = await self.storage.find_images_by_created_time(
            start=current_time
            - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS),
            end=current_time,
        )
        for shown_message in shown_messages:
            for image in images:
                print(image)
            matched_image: Image = process.extractOne(
                "".join(
                    [
                        shown_message.message.name.strip().lower(),
                        shown_message.message.city.strip().lower(),
                        shown_message.message.text.strip().lower(),
                    ]
                ),
                choices=images,
            )[0]
            print(f"Matched image: {matched_image}")
            await self.send_shown_message(shown_message, matched_image)
            await self.storage.delete_shown_message(shown_message)
            await self.storage.delete_image(matched_image)

        await self.storage.delete_old_images(
            current_time - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS)
        )
        deleted_messages = await self.storage.delete_old_shown_messages(
            current_time - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS)
        )
        for message in deleted_messages:
            self.logger.error(
                "Cannot find image for shown message: %s", message.message.message_id
            )
            await self.send_shown_message(message, None)

    async def send_shown_message(
        self, shown_message: ShownMessage, image: Image | None
    ) -> None:
        self.logger.info(f"Sending shown message {shown_message.message.message_id}")
        await self.publisher.publish(
            MessageShownSharedModel(
                message=shown_message.message,
                photo_base64=image.image_base64 if image else None,
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
