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
    __request: requests.Request
    __request_cookies: CookieJar
    __response: requests.Response
    __start_time: datetime
    __server_ip_address: (str, int)
    __local_ip_address: (str, int)

    def __init__(self,
                 request: requests.Request,
                 request_cookies: CookieJar,
                 response: requests.Response,
                 start_time: datetime,
                 server_ip_address: (str, int),
                 local_ip_address: (str, int),
                 ):
        self.__request = request
        self.__request_cookies = request_cookies
        self.__response = response
        self.__start_time = start_time
        self.__server_ip_address = server_ip_address
        self.__local_ip_address = local_ip_address

    @property
    def request(self):
        return self.__request

    @property
    def request_cookies(self):
        return self.__request_cookies

    @property
    def response(self):
        return self.__response

    @property
    def start_time(self):
        return self.__start_time

    @property
    def server_ip_address(self):
        return self.__server_ip_address

    @property
    def local_ip_address(self):
        return self.__local_ip_address

    def get_query_string_parameters(self) -> dict:
        parsed_url = urlparse(self.__request.url)
        return parse_qs(parsed_url.query)

    def get_post_param_as_text(self) -> str:
        return urlencode(self.__request.params)


class RequestSessionContext:
    __entries: List[HttpRequestEntry]

    def __init__(self):
        self.__entries = []

    @property
    def entries(self):
        return self.__entries

    def append(self, http_entry: HttpRequestEntry):
        return self.__entries.append(http_entry)

    def get_last_referer(self) -> str:
        last_response_url = next((http_entry.response.url for http_entry in reversed(self.__entries)
                                  if 'ajaxx' not in http_entry.response.url), None)

        if last_response_url is not None:
            return UrlHelper.get_referrer(last_response_url)

        return "https://online.hl.co.uk/"
