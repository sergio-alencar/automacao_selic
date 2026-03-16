import logging
from config.settings import LOG_FILE_PATH


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode="a"),
            logging.StreamHandler(),
        ],
    )
