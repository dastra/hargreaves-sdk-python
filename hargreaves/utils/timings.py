import datetime
from logging import Logger
from random import randint
from time import sleep


class ITimeService:
    def get_current_time(self) -> datetime:
        pass

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0) -> int:
        pass

    def sleep(self, min: int = 1, max: int = 2):
        pass


class TimeService(ITimeService):
    __logger: Logger

    def __init__(self, logger: Logger = None):
        self.__logger = logger

    def get_current_time(self) -> datetime:
        return datetime.datetime.now()

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0) -> int:
        relative_time = (datetime.datetime.now() + datetime.timedelta(minutes=offset_minutes))
        return round(relative_time.timestamp() * 1000)

    def sleep(self, min: int = 1, max: int = 2):
        sleep_time = randint(min, max)
        if self.__logger is not None:
            self.__logger.debug(f"Pausing for {sleep_time} seconds ...")
        sleep(sleep_time)


class MockTimeService(ITimeService):
    """
    Freezes time on init
    """
    __current_time: datetime

    def __init__(self):
        self.__current_time = datetime.datetime.now()

    def get_current_time(self) -> datetime:
        return self.__current_time

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0) -> int:
        relative_time = (self.__current_time + datetime.timedelta(minutes=offset_minutes))
        return round(relative_time.timestamp() * 1000)

    def sleep(self, min: int = 1, max: int = 2):
        # do nothing
        pass
