import logging
from http.cookiejar import CookieJar
from urllib.parse import urlencode

import requests
from requests import Response, Session
from requests_mock import Mocker

from .requests import WebRequestType
from .session import IWebSession

logger = logging.getLogger(__name__)


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
