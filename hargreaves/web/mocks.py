from http.cookiejar import CookieJar
from urllib.parse import urlencode

import requests
from requests import Response, Session
from requests_mock import Mocker

from hargreaves.web.requests import WebRequestType
from hargreaves.web.session import IWebSession


class MockWebSession(IWebSession):
    __session: Session
    __mock_request: Mocker

    def __init__(self):
        self.__session = requests.Session()
        self.__mock_request = Mocker()

    def mock_get(self, url: str, status_code: int, params=None, headers=None, response_text=None):
        params = params if params is not None else {}
        headers = headers if headers is not None else {}
        if params is None:
            request_url = url
        else:
            request_url = f"{url}?{urlencode(params)}"
        self.__mock_request.get(
                url=request_url,
                headers=headers,
                status_code=status_code,
                text=response_text
            )
        return self.__mock_request

    def mock_post(self, url: str, status_code: int, headers=None, response_text=None):
        # data = data if data is not None else {}
        headers = headers if headers is not None else {}
        # self.__mock_request.add_matcher()
        self.__mock_request.post(
                url,
                headers=headers,
                status_code=status_code,
                text=response_text
            )
        return self.__mock_request

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        return self.__session.get(url, params=params, headers=headers)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        return self.__session.post(url, data=data, headers=headers)

    def __enter__(self):
        self.__mock_request.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.__mock_request.__exit__(type, value, traceback)

    @property
    def cookies(self) -> CookieJar:
        return self.__session.cookies
