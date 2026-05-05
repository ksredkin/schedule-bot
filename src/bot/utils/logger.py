import logging
import os

from src.bot.core.config import LOGS_PATH


class Logger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.setup_logger()

    def setup_logger(self) -> None:
        self.logger.setLevel(logging.INFO)

        stream = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream.setFormatter(formatter)

        self.logger.addHandler(stream)

    def get_logger(self) -> logging.Logger:
        return self.logger
