import logging
import sys

logger = logging.getLogger("qshift")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)
