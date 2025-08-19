import cv2
import asyncio
import base64
import io
from thefuzz import process
from datetime import datetime, timedelta
from logging import Logger
from .config import Config
from .storage.base import BaseStorage
from .storage.models import Image, ShownMessage
from PIL.Image import Image as PILImage
from paddleocr import PaddleOCR
from paddlex.inference.pipelines.ocr.result import OCRResult


class CaptureLoopError(Exception):
    """Custom exception for errors in the capture loop."""

    pass


class CaptureLoop:
    def __init__(self, storage: BaseStorage, logger: Logger):
        cap = cv2.VideoCapture(Config.RTMP_URL)
        if not cap.isOpened():
            raise RuntimeError("Could not open video stream.")
        self.cap = cap
        self.storage = storage
        self.logger = logger
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
            text_detection_model_name="PP-OCRv5_mobile_det",
        )

    async def start(self):
        self.logger.info("Starting capture loop...")
        while True:
            await asyncio.sleep(0.1)  # Allow other tasks to run
            try:
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Failed to read frame from video stream.")
                    raise CaptureLoopError("Failed to read frame from video stream.")
                await self.process_frame(frame)
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

    async def process_frame(self, frame: cv2.typing.MatLike) -> None:
        ocr_result: OCRResult = self.ocr.predict(input=frame)[0]
        await self.storage.save_image(
            Image(
                image_base64=self.image_to_base64(ocr_result.img["ocr_res_img"])
                if Config.DEBUG_MODE
                else self.frame_to_base64(frame),
                text="".join(res.strip().lower() for res in ocr_result["rec_texts"]),
            )
        )

    async def match_frames(self) -> None:
        current_time = datetime.now(Config.TIME_ZONE)
        shown_messages = await self.storage.find_shown_messages_by_show_at_time(
            start=current_time - timedelta(seconds=Config.ANALYTICS_DELAY_SECONDS),
            end=current_time,
        )
        images = await self.storage.find_images_by_created_time(
            start=current_time
            - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS),
            end=current_time,
        )
        for shown_message in shown_messages:
            matched_image: Image = process.extractOne(
                "".join(
                    [
                        shown_message.message.name.strip().lower(),
                        shown_message.message.city.strip().lower(),
                        shown_message.message.text.strip().lower(),
                    ]
                ),
                choices=images,
                processor=lambda x: x.text,
            )[0]
            await self.send_shown_message(shown_message, matched_image)

    async def send_shown_message(
        self, shown_message: ShownMessage, image: Image
    ) -> None:
        pass

    def image_to_base64(self, image: PILImage) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def frame_to_base64(self, frame: cv2.typing.MatLike) -> str:
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            raise ValueError("Cannot encode frame to JPEG format.")
        return base64.b64encode(buffer).decode("utf-8")  # type: ignore
