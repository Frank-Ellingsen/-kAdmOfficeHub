import logging
import sys
import os

def setup_logger(name: str = "OkAdmOfficeHub") -> logging.Logger:
    """Setter opp en standard formatert logger for konsoll og rapportering."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

logger = setup_logger()

