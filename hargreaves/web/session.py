import copy
import logging
from datetime import datetime
from http.client import RemoteDisconnected
from http.cookiejar import CookieJar
from time import sleep

import requests
from requests import Response, Request

from hargreaves.web.headers import IHeaderFactory
from hargreaves.web.requests import WebRequestType, RequestSessionContext, HttpRequestEntry

logger = logging.getLogger(__name__)


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
    _session: requests.Session
    _request_session_context: RequestSessionContext
    _header_factory: IHeaderFactory
    _retry_count: int

    def __init__(self,
                 session: requests.Session,
                 request_session_context: RequestSessionContext,
                 header_factory: IHeaderFactory,
                 retry_count: int = 3):
        self._session = session
        self._request_session_context = request_session_context
        self._header_factory = header_factory
        self._retry_count = retry_count

    @property
    def cookies(self) -> CookieJar:
        return self._session.cookies

    def __exec_request(self, request: requests.Request):
        session = self._session
        request_cookies = copy.deepcopy(session.cookies)

        prepared_req = session.prepare_request(request)

        response = None
        start_time = datetime.now()
        remaining_retries = self._retry_count
        should_retry = True
        while should_retry:
            try:
                response = session.send(prepared_req, stream=True)
                should_retry = False
            except (RemoteDisconnected, requests.ConnectionError) as ex:
                logger.warning(f"RemoteDisconnected error (remaining_retries = {remaining_retries}")
                remaining_retries = remaining_retries - 1
                if remaining_retries > 0:
                    logger.warning(f"Pausing briefly before retrying ...")
                    sleep(1)
                else:
                    raise ex

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

            self._request_session_context.append(HttpRequestEntry(**arguments))

        arguments['response'] = response

        self._request_session_context.append(HttpRequestEntry(**arguments))

        return response

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        logger.debug(f"GET: {url}")
        additional_headers = headers if headers is not None else {}

        if request_type == WebRequestType.XHR:
            merged_headers = self._header_factory.create_for_xhr_get(url, additional_headers)
        else:
            merged_headers = self._header_factory.create_for_doc_get(url, additional_headers)

        req = Request(method='GET', url=url, params=params, headers=merged_headers)
        return self.__exec_request(req)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        logger.debug(f"POST: {url}")
        additional_headers = headers if headers is not None else {}
        if request_type == WebRequestType.XHR:
            merged_headers = self._header_factory.create_for_xhr_post(url, additional_headers, data)
        else:
            merged_headers = self._header_factory.create_for_form_post(url, additional_headers, data)

        req = Request(method='POST', url=url, data=data, headers=merged_headers)
        return self.__exec_request(req)
