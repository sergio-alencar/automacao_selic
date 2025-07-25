# AutomacaoSelic/logger_config.py

import logging
import config


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.PATH_ARQUIVO_LOG, mode="a"),
            logging.StreamHandler(),
        ],
    )
