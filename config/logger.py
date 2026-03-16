import logging
from config.settings import LOG_FILE_PATH, IS_DEVELOPMENT
from config.constants import LogConfig


def setup_logging() -> None:
    log_level: int = logging.DEBUG if IS_DEVELOPMENT else logging.INFO

    logging.basicConfig(
        level=log_level,
        format=LogConfig.FORMAT,
        handlers=[
            logging.FileHandler(
                LOG_FILE_PATH,
                mode=LogConfig.FILE_MODE,
                encoding=LogConfig.ENCODING,
            ),
            logging.StreamHandler(),
        ],
    )
