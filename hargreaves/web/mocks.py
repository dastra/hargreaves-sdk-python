import datetime
from http.cookiejar import CookieJar
from urllib.parse import urlencode

import requests
from requests import Response, Session
from requests_mock import Mocker

from hargreaves.web.requests import WebRequestType
from hargreaves.web.session import IWebSession
from hargreaves.web.timings import ITimeService


class MockWebSession(IWebSession):
    _session: Session
    _mock_request: Mocker

    def __init__(self):
        self._session = requests.Session()
        self._mock_request = Mocker()

    def mock_get(self, url: str, status_code: int, params=None, headers=None, response_text=None):
        params = params if params is not None else {}
        headers = headers if headers is not None else {}
        if params is None:
            request_url = url
        else:
            request_url = f"{url}?{urlencode(params)}"
        self._mock_request.get(
                url=request_url,
                headers=headers,
                status_code=status_code,
                text=response_text
            )
        return self._mock_request

    def mock_post(self, url: str, status_code: int, headers=None, response_text=None):
        # data = data if data is not None else {}
        headers = headers if headers is not None else {}
        # self.__mock_request.add_matcher()
        self._mock_request.post(
                url,
                headers=headers,
                status_code=status_code,
                text=response_text
            )
        return self._mock_request

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        return self._session.get(url, params=params, headers=headers)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        return self._session.post(url, data=data, headers=headers)

    def __enter__(self):
        self._mock_request.__enter__()
        return self

    def __exit__(self, the_type, value, traceback):
        self._mock_request.__exit__(the_type, value, traceback)

    @property
    def cookies(self) -> CookieJar:
        return self._session.cookies


class MockTimeService(ITimeService):
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
        # do nothing
        pass
