import logging
from typing import Literal, Optional, Final

COLORED_LEVELS: Final[dict[int, str]] = {
    logging.DEBUG: "\033[36mDEBUG\033[0m",
    logging.INFO: "\033[32mINFO\033[0m",
    logging.WARNING: "\033[33mWARNING\033[0m",
    logging.ERROR: "\033[31mERROR\033[0m",
    logging.CRITICAL: "\033[91mCRITICAL\033[0m",
}


class ColoredFormatter(logging.Formatter):
    """A class to format log messages with colorized level names."""

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool = True,
    ) -> None:
        """Initializes the ColoredFormatter.

        Args:
            fmt (Optional[str], optional): The format string for the log message. Defaults to None.
            datefmt (Optional[str], optional): The format string for the date. Defaults to None.
            style (Literal[, optional): The style of the format string. Defaults to '%'.
            use_colors (bool): Whether to use colors in the log output.
        """
        self.use_colors = use_colors
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Formats the log message.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        if self.use_colors:
            record.levelname = expand_log_field(
                field=COLORED_LEVELS.get(record.levelno, record.levelname),
                symbols=17,
            )

        return super().formatMessage(record)


def expand_log_field(field: str, symbols: int) -> str:
    """Expands a log field to a specified number of symbols by padding with spaces.

    Args:
        field (str): The log field to expand.
        symbols (int): The total number of symbols the field should occupy.

    Returns:
        str: The expanded log field, padded with spaces to the right.
    """
    return field + (" " * (symbols - len(field)))
