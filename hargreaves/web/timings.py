import datetime
import logging
from random import randint
from time import sleep

logger = logging.getLogger(__name__)


class ITimeService:
    def get_current_time(self) -> datetime:
        pass

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0, offset_seconds: int = 0) -> int:
        pass

    def sleep(self, minimum: int = 1, maximum: int = 2):
        pass


class TimeService(ITimeService):

    def __init__(self):
        pass

    def get_current_time(self) -> datetime:
        return datetime.datetime.now()

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0, offset_seconds: int = 0) -> int:
        relative_time = (datetime.datetime.now() + datetime.timedelta(minutes=offset_minutes, seconds=offset_seconds))
        return round(relative_time.timestamp() * 1000)

    def sleep(self, minimum: int = 1, maximum: int = 2):
        sleep_time = randint(minimum, maximum)
        if logger is not None:
            logger.debug(f"Pausing for {sleep_time} seconds ...")
        sleep(sleep_time)
