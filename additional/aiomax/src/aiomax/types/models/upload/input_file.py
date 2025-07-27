from ...enums import UploadType
from pathlib import Path
from typing import Final


DEFAULT_CHUNK_SIZE: Final[int] = 64 * 1024


class InputFile:
    """InputFile class for handling file uploads."""

    def __init__(
        self,
        data: bytes,
        filename: str,
        upload_type: UploadType,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ):
        """Initialize an InputFile instance.

        Args:
            data (bytes): The file data to be uploaded.
            file_name (str): The name of the file.
            upload_type (UploadType): The type of upload (e.g., IMAGE, VIDEO, AUDIO, FILE).
            chunk_size (int, optional): The size of each chunk to read from the file. Defaults to 64 * 1024 bytes (64 KB).
        """
        self._data = data
        self.filename = filename
        self.upload_type = upload_type
        self.chunk_size = chunk_size

    @classmethod
    def from_file(
        cls,
        path: str | Path,
        upload_type: UploadType,
        filename: str | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> "InputFile":
        """Create an InputFile instance from a file path.

        Args:
            path (str | Path): The path to the file to be uploaded.
            upload_type (UploadType): The type of upload (e.g., IMAGE, VIDEO, AUDIO, FILE).
            filename (str | None, optional): The name of the file. If not provided, the name will be derived from the path.
            chunk_size (int, optional): The size of each chunk to read from the file. Defaults to 64 * 1024 bytes (64 KB).

        Raises:
            FileNotFoundError: If the specified file does not exist.

        Returns:
            InputFile: An instance of InputFile containing the file data and metadata.
        """
        if isinstance(path, str):
            path = Path(path)

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "rb") as file:
            data = file.read()

        return cls(
            data=data,
            filename=filename or path.name,
            upload_type=upload_type,
            chunk_size=chunk_size,
        )

    @property
    def data(self) -> bytes:
        """Get the file data."""
        return self._data
