import copy
from datetime import datetime
from http.cookiejar import CookieJar
from logging import Logger

import requests
from requests import Response, Request

from hargreaves.web.headers import IHeaderFactory
from hargreaves.web.requests import WebRequestType, RequestSessionContext, HttpRequestEntry


class IWebSession():

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        pass

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        pass

    # noinspection PyPropertyDefinition
    @property
    def cookies(self) -> CookieJar:
        pass


class WebSession(IWebSession):
    __logger: Logger
    __session: requests.Session
    __request_session_context: RequestSessionContext
    __header_factory: IHeaderFactory

    def __init__(self,
                 logger: Logger,
                 session: requests.Session,
                 request_session_context: RequestSessionContext,
                 header_factory: IHeaderFactory):
        self.__logger = logger
        self.__session = session
        self.__request_session_context = request_session_context
        self.__header_factory = header_factory

    @property
    def cookies(self) -> CookieJar:
        return self.__session.cookies

    def __exec_request(self, request: requests.Request):
        session = self.__session
        request_cookies = copy.deepcopy(session.cookies)

        prepared_req = session.prepare_request(request)

        start_time = datetime.now()
        response = session.send(prepared_req, stream=True)

        socket = response.raw.connection.sock

        # tuples (ip, port)
        local_ip_address = socket.getsockname() if socket is not None else None
        server_ip_address = socket.getpeername() if socket is not None else None

        arguments = {
            'request_cookies': request_cookies,
            'request': request,
            'start_time': start_time,
            'local_ip_address': local_ip_address,
            'server_ip_address': server_ip_address
        }

        # in case of HTTP redirects:
        for history_response in response.history:
            arguments['response'] = history_response

            self.__request_session_context.append(HttpRequestEntry(**arguments))

        arguments['response'] = response

        self.__request_session_context.append(HttpRequestEntry(**arguments))

        return response

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        self.__logger.debug(f"GET: {url}")
        additional_headers = headers if headers is not None else {}

        if request_type == WebRequestType.XHR:
            merged_headers = self.__header_factory.create_for_xhr_get(url, additional_headers)
        else:
            merged_headers = self.__header_factory.create_for_doc_get(url, additional_headers)

        req = Request(method='GET', url=url, params=params, headers=merged_headers)
        return self.__exec_request(req)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        self.__logger.debug(f"POST: {url}")
        additional_headers = headers if headers is not None else {}
        if request_type == WebRequestType.XHR:
            merged_headers = self.__header_factory.create_for_xhr_post(url, additional_headers, data)
        else:
            merged_headers = self.__header_factory.create_for_form_post(url, additional_headers, data)

        req = Request(method='POST', url=url, data=data, headers=merged_headers)
        return self.__exec_request(req)
