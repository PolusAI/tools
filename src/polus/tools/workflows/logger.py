"""Logger factory."""

import logging
from os import environ

logging.basicConfig(format="%(name)-8s - %(levelname)-8s - %(message)s")
POLUS_LOG = getattr(logging, environ.get("POLUS_LOG", "INFO"))


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger.

    Args:
        name: logger's name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(POLUS_LOG)
    return logger
