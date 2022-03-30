import logging
import sys
from typing import Union


class LogHelper:
    @staticmethod
    def configure(log_level: Union[int, str]) -> logging.Logger:
        logger = logging.getLogger()
        logging.basicConfig()
        logger.setLevel(log_level)
        return logger

    @staticmethod
    def configure_std_out(log_level: int = 10) -> logging.Logger:
        logger = logging.getLogger()
        logging.basicConfig()
        logger.setLevel(log_level)
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
        return logger
