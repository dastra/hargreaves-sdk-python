import logging
import sys
from typing import Union


class LoggerFactory:
    @staticmethod
    def create(log_level: Union[int, str]):
        logger = logging.getLogger()
        logging.basicConfig()
        logger.setLevel(log_level)
        return logger

    @staticmethod
    def create_std_out(log_level: int = 10):
        logger = logging.getLogger()
        logging.basicConfig()
        logger.setLevel(log_level)
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
        return logger
