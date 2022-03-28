import datetime
import logging
from random import randint
from time import sleep

logger = logging.getLogger(__name__)


class IClock:
    def get_current_time(self) -> datetime.datetime:
        pass

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0, offset_seconds: int = 0) -> int:
        pass

    def sleep(self, minimum: int = 1, maximum: int = 2):
        pass


class Clock(IClock):

    def __init__(self):
        pass

    def get_current_time(self) -> datetime.datetime:
        return datetime.datetime.now()

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0, offset_seconds: int = 0) -> int:
        relative_time = (datetime.datetime.now() + datetime.timedelta(minutes=offset_minutes, seconds=offset_seconds))
        return round(relative_time.timestamp() * 1000)

    def sleep(self, minimum: int = 1, maximum: int = 2):
        sleep_time = randint(minimum, maximum)
        logger.debug(f"Pausing for {sleep_time} seconds ...")
        sleep(sleep_time)


class MockClock(IClock):
    """
    Freezes time on init
    """
    _current_time: datetime

    def __init__(self):
        self._current_time = datetime.datetime.now()

    def get_current_time(self) -> datetime:
        return self._current_time

    def get_current_time_as_epoch_time(self, offset_minutes: int = 0, offset_seconds: int = 0) -> int:
        relative_time = (self._current_time + datetime.timedelta(minutes=offset_minutes, seconds=offset_seconds))
        return round(relative_time.timestamp() * 1000)

    def sleep(self, minimum: int = 1, maximum: int = 2):
        sleep_time = randint(minimum, maximum)
        logger.debug(f"Mock Pausing for {sleep_time} seconds ...")


class ClockManager:
    _instance: IClock

    def __init__(self):
        self._instance = Clock()

    def get_instance(self):
        return self._instance

    def set_instance(self, clock: IClock):
        self._instance = clock


manager = ClockManager()


def sleep_random(minimum: int = 1, maximum: int = 2):
    return manager.get_instance().sleep(minimum=minimum, maximum=maximum)


def get_current_time_as_epoch_time(offset_minutes: int = 0, offset_seconds: int = 0) -> int:
    clock = manager.get_instance()
    relative_time = (clock.get_current_time() + datetime.timedelta(minutes=offset_minutes, seconds=offset_seconds))
    return round(relative_time.timestamp() * 1000)


def freeze_time():
    """
    Useful in unit tests
    :return:
    """
    manager.set_instance(MockClock())
