import subprocess
import asyncio
import random
from .config import Config
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np
from .storage.base import BaseStorage
from typing import NamedTuple
from string import ascii_letters, digits

NewText = NamedTuple("NewText", [("text", str), ("name", str), ("city", str)])


class MockVideoStream:
    def __init__(self, storage: BaseStorage):
        self.ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}",
            "-r",
            str(Config.VIDEO_FPS),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "veryfast",
            "-tune",
            "zerolatency",
            "-crf",
            "18",
            "-g",
            "15",
            "-f",
            "flv",
            Config.RTMP_URL,
        ]
        self.storage = storage

    async def start(self):
        self.process = subprocess.Popen(self.ffmpeg_cmd, stdin=subprocess.PIPE)
        font = ImageFont.load_default(size=20)
        text_data = await self.get_new_text()
        counter = 1
        while True:
            background_color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
            img = Image.new(
                "RGB", (Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), color=background_color
            )
            draw = ImageDraw.Draw(img)

            # центрируем основной текст
            bbox_text = draw.textbbox((0, 0), text_data.text, font=font)
            text_w = bbox_text[2] - bbox_text[0]
            text_h = bbox_text[3] - bbox_text[1]
            center_x = (Config.VIDEO_WIDTH - text_w) // 2
            center_y = (Config.VIDEO_HEIGHT - text_h) // 2

            # основной текст в центре
            draw.text(
                (center_x, center_y),
                text_data.text,
                font=font,
                fill=tuple(255 - c for c in background_color),
            )

            # имя чуть выше и левее
            bbox_name = draw.textbbox((0, 0), text_data.name, font=font)
            name_w = bbox_name[2] - bbox_name[0]
            name_h = bbox_name[3] - bbox_name[1]
            draw.text(
                (center_x - name_w - 10, center_y - name_h - 10),
                text_data.name,
                font=font,
                fill=tuple(255 - c for c in background_color),
            )

            # город чуть выше и правее
            bbox_city = draw.textbbox((0, 0), text_data.city, font=font)
            city_w = bbox_city[2] - bbox_city[0]
            city_h = bbox_city[3] - bbox_city[1]
            draw.text(
                (center_x + city_w + 10, center_y - city_h - 10),
                text_data.city,
                font=font,
                fill=tuple(255 - c for c in background_color),
            )

            counter += 1
            img = self.random_transform(img)
            self.process.stdin.write(img.tobytes())  # type: ignore
            self.process.stdin.flush()  # type: ignore
            await asyncio.sleep(0.1)
            if counter % 50 == 0:
                text_data = await self.get_new_text()

    async def get_new_text(self) -> NewText:
        alphabet = ascii_letters + digits
        return NewText(
            name="".join(random.choice(alphabet) for _ in range(10)),
            city="".join(random.choice(alphabet) for _ in range(10)),
            text="".join(random.choice(alphabet) for _ in range(20)),
        )

    def random_transform(self, img: Image.Image) -> Image.Image:
        arr = np.array(img)

        # Шум
        if random.random() < 0.5:
            noise = np.random.randint(0, 64, arr.shape, dtype=np.uint8)
            arr = np.clip(arr + noise, 0, 255)

        # Инверсия цветов
        if random.random() < 0.1:
            arr = 255 - arr

        # Горизонтальные полосы (glitch)
        if random.random() < 0.3:
            num_stripes = random.randint(3, 10)
            h = arr.shape[0]
            for _ in range(num_stripes):
                y = random.randint(0, h - 5)
                height = random.randint(2, 10)
                shift = random.randint(-20, 20)
                arr[y : y + height] = np.roll(arr[y : y + height], shift, axis=1)

        img = Image.fromarray(arr)

        # Блюр
        if random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 2.0)))

        # Пикселизация
        if random.random() < 0.2:
            scale = random.randint(4, 10)
            small = img.resize(
                (img.width // scale, img.height // scale),
                resample=Image.Resampling.NEAREST,
            )
            img = small.resize(img.size, Image.Resampling.NEAREST)

        # Случайный поворот на небольшой угол
        if random.random() < 0.2:
            angle = random.uniform(-10, 10)
            img = img.rotate(angle, expand=False)

        # Контраст
        if random.random() < 0.5:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(random.uniform(0.5, 1.5))

        # Яркость
        if random.random() < 0.5:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(random.uniform(0.5, 1.5))

        return img
