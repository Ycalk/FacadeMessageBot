from abc import ABC, abstractmethod
from .models import Image, ShownMessage
from datetime import datetime
from uuid import UUID


class BaseStorage(ABC):
    @abstractmethod
    async def save_image(self, image: Image) -> UUID:
        """Saves an image to the storage.

        Args:
            image (Image): The image to be saved.

        Returns:
            UUID: The unique identifier of the saved image.
        """

    @abstractmethod
    async def save_shown_message(self, message: ShownMessage) -> UUID:
        """Saves a shown message to the storage.

        Args:
            message (ShownMessage): The shown message to be saved.

        Returns:
            UUID: The unique identifier of the saved message.
        """
        ...

    @abstractmethod
    async def find_images_by_created_time(
        self, start: datetime, end: datetime
    ) -> list[Image]:
        """Finds images created within a specific time range.

        Args:
            start (datetime): Start of the time range.
            end (datetime): End of the time range.

        Returns:
            list[Image]: List of images created within the specified time range.
        """
        ...

    @abstractmethod
    async def find_shown_messages_by_show_at_time(
        self, start: datetime, end: datetime
    ) -> list[ShownMessage]:
        """Finds shown messages within a specific time range.

        Args:
            start (datetime): Start of the time range.
            end (datetime): End of the time range.

        Returns:
            list[ShownMessage]: List of shown messages within the specified time range.
        """
        ...

    @abstractmethod
    async def get_shown_messages(self) -> list[ShownMessage]:
        """Retrieves all shown messages from the storage.

        Returns:
            list[ShownMessage]: List of all shown messages.
        """
        ...

    @abstractmethod
    async def delete_image(self, image: Image | UUID) -> None:
        """Deletes an image from the storage.

        Args:
            image (Image | UUID): The image to be deleted, either as an Image object or its UUID.
        """
        ...

    @abstractmethod
    async def delete_shown_message(self, message: ShownMessage | UUID) -> None:
        """Deletes a shown message from the storage.

        Args:
            message (ShownMessage | UUID): The shown message to be deleted, either as a ShownMessage object or its UUID.
        """
        ...

    @abstractmethod
    async def delete_old_images(self, to_date: datetime) -> None:
        """Deletes images older than a specified date.

        Args:
            to_date (datetime): The date before which images will be deleted.
        """
        ...

    @abstractmethod
    async def delete_old_shown_messages(self, to_date: datetime) -> list[ShownMessage]:
        """Deletes shown messages older than a specified date.

        Args:
            to_date (datetime): The date before which shown messages will be deleted.

        Returns:
            list[ShownMessage]: List of shown messages that were deleted.
        """
        ...
