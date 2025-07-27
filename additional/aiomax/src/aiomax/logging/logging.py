import logging
import sys
from .formatter import ColoredFormatter


def get_logger(
    name: str, level: int = logging.INFO, user_colors: bool = True
) -> logging.Logger:
    """Get a logger with the specified name and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    main_handler = logging.StreamHandler(stream=sys.stderr)
    main_handler.setFormatter(
        ColoredFormatter(
            fmt="%(asctime)s %(levelname)8s - %(message)s",
            use_colors=user_colors,
        )
    )
    logger.addHandler(main_handler)
    return logger
