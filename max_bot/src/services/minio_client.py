"""Клиент для работы с MinIO хранилищем."""

import io
import json
from datetime import timedelta
from minio import Minio
from minio.error import S3Error

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class MinIOClient:
    """Клиент для работы с MinIO."""

    def __init__(self):
        """Инициализация клиента MinIO."""
        # Подключаемся по внутреннему адресу (minio:9000 в Docker)
        self.client = Minio(
            Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=Config.MINIO_SECURE,
        )
        self.bucket = Config.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Создает bucket если он не существует и настраивает публичный доступ."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Создан bucket {self.bucket}")

                # Устанавливаем политику публичного чтения для bucket
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket}/*"]
                        }
                    ]
                }
                self.client.set_bucket_policy(self.bucket, json.dumps(policy))
                logger.info(f"Установлена публичная политика для bucket {self.bucket}")
        except S3Error as e:
            logger.error(f"Ошибка при создании bucket: {e}")
            raise

    def upload_photo(self, photo_bytes: bytes, object_name: str) -> str:
        """
        Загружает фото в MinIO и возвращает presigned URL.

        Args:
            photo_bytes: Байты изображения
            object_name: Имя объекта в хранилище (например, "user_{user_id}_{timestamp}.jpg")

        Returns:
            Presigned URL для доступа к изображению

        Raises:
            S3Error: При ошибке загрузки
        """
        try:
            # Загружаем файл через внутренний клиент
            photo_stream = io.BytesIO(photo_bytes)
            self.client.put_object(
                self.bucket,
                object_name,
                photo_stream,
                length=len(photo_bytes),
                content_type="image/jpeg",
            )

            # Формируем публичный URL с внешним хостом (localhost:9000 в dev, server-ip в prod)
            protocol = "https" if Config.MINIO_SECURE else "http"
            url = f"{protocol}://{Config.MINIO_PUBLIC_URL}/{self.bucket}/{object_name}"

            logger.info(f"Фото загружено в MinIO: {object_name}, URL: {url}")
            return url

        except S3Error as e:
            logger.error(f"Ошибка при загрузке фото в MinIO: {e}")
            raise

    def download_photo(self, object_name: str) -> bytes:
        """
        Скачивает фото из MinIO.

        Args:
            object_name: Имя объекта в хранилище

        Returns:
            Байты изображения

        Raises:
            S3Error: При ошибке скачивания
        """
        try:
            response = self.client.get_object(self.bucket, object_name)
            photo_bytes = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Фото скачано из MinIO: {object_name}")
            return photo_bytes
        except S3Error as e:
            logger.error(f"Ошибка при скачивании фото из MinIO: {e}")
            raise

    def delete_photo(self, object_name: str) -> None:
        """
        Удаляет фото из MinIO.

        Args:
            object_name: Имя объекта в хранилище
        """
        try:
            self.client.remove_object(self.bucket, object_name)
            logger.info(f"Фото удалено из MinIO: {object_name}")
        except S3Error as e:
            logger.error(f"Ошибка при удалении фото из MinIO: {e}")
            raise


# Singleton instance
_minio_client: MinIOClient | None = None


def get_minio_client() -> MinIOClient:
    """Возвращает синглтон клиент MinIO."""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
    return _minio_client
