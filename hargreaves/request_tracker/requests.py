from datetime import datetime
from enum import Enum
from http.cookiejar import CookieJar
from typing import List
from urllib.parse import urlparse, parse_qs, urlencode

import requests


class UrlHelper:
    @staticmethod
    def get_origin(url: str):
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.hostname}"

    @staticmethod
    def get_host(url: str):
        parsed_url = urlparse(url)
        return parsed_url.hostname

    @staticmethod
    def get_referrer(previous_url: str):
        parsed_url = urlparse(previous_url)
        return f"{parsed_url.scheme}://{parsed_url.hostname}{parsed_url.path}"


class WebRequestType(Enum):
    Document = 'document'
    XHR = 'xhr'

    def __str__(self):
        return self.name


class HttpRequestEntry:
    _request: requests.Request
    _request_cookies: CookieJar
    _response: requests.Response
    _start_time: datetime
    _server_ip_address: (str, int)
    _local_ip_address: (str, int)

    def __init__(self,
                 request: requests.Request,
                 request_cookies: CookieJar,
                 response: requests.Response,
                 start_time: datetime,
                 server_ip_address: (str, int),
                 local_ip_address: (str, int),
                 ):
        self._request = request
        self._request_cookies = request_cookies
        self._response = response
        self._start_time = start_time
        self._server_ip_address = server_ip_address
        self._local_ip_address = local_ip_address

    @property
    def request(self):
        return self._request

    @property
    def request_cookies(self):
        return self._request_cookies

    @property
    def response(self):
        return self._response

    @property
    def start_time(self):
        return self._start_time

    @property
    def server_ip_address(self):
        return self._server_ip_address

    @property
    def local_ip_address(self):
        return self._local_ip_address

    def get_query_string_parameters(self) -> dict:
        parsed_url = urlparse(self._request.url)
        return parse_qs(parsed_url.query)

    def get_post_param_as_text(self) -> str:
        return urlencode(self._request.params)


class RequestSessionContext:
    _default_referer: str
    _entries: List[HttpRequestEntry]

    def __init__(self, default_referer:str):
        self._default_referer = default_referer
        self._entries = []

    @property
    def entries(self):
        return self._entries

    def append(self, http_entry: HttpRequestEntry):
        return self._entries.append(http_entry)

    def get_last_referer(self) -> str:
        last_response_url = next((http_entry.response.url for http_entry in reversed(self._entries)
                                  if 'ajaxx' not in http_entry.response.url), None)

        if last_response_url is not None:
            return UrlHelper.get_referrer(last_response_url)

        return self._default_referer
