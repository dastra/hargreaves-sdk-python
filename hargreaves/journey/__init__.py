import logging
from datetime import datetime

from hargreaves.journey.clients import WebSessionManager
from hargreaves.utils.paths import PathHelper
from hargreaves.request_tracker.storage import CookiesFileStorage, RequestSessionFileStorage

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_default_session_manager() -> WebSessionManager:
    """
    Using local file-based storage for cookies & requests
    :return:
    """

    # create local file-based cookies-storage
    cookies_file_path = PathHelper.get_project_root() \
        .joinpath('session_cache').joinpath('cookies.txt')
    cookies_storage = CookiesFileStorage(cookies_file_path)

    # create local file-based session-history-writer
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
    requests_file_path = PathHelper.get_project_root() \
        .joinpath('session_cache').joinpath(f"session-{dt_string}.har")
    request_session_storage = RequestSessionFileStorage(requests_file_path)

    return WebSessionManager(
        cookies_storage,
        request_session_storage)
