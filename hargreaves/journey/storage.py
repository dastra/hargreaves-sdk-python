import os
from http.cookiejar import CookieJar, LWPCookieJar, Cookie
from logging import Logger
from os import path
from pathlib import Path

import requests

from hargreaves.analysis.clients import HARHttpRequestEntryRenderer
from hargreaves.config import ApiConfiguration
from hargreaves.web.session import RequestSessionContext
from hargreaves.web.storage import ICookieStorage, IRequestSessionStorage


class StringHelper:
    @staticmethod
    def hide_sensitive_variables(input_str: str, sensitive_variables: list):
        output_str = input_str
        for sensitive_var in sensitive_variables:
            output_str = output_str.replace(sensitive_var, '*' * len(sensitive_var))
        return output_str


class CookiesFileStorage(ICookieStorage):
    _logger: Logger
    _cookies_file_path: Path

    def __init__(self,
                 logger: Logger,
                 cookies_file_path: Path):
        self._logger = logger
        self._cookies_file_path = cookies_file_path

    def load(self, session: requests.Session):
        file_path = self._cookies_file_path

        session_folder = self._cookies_file_path.parent
        if not path.exists(session_folder):
            self._logger.debug(f"creating folder '{session_folder}'...")
            os.makedirs(session_folder)

        if not path.exists(file_path):
            self._logger.debug(f"cookies file ('{file_path}') does not exist ...")
            return

        try:
            self._logger.debug(f"loading cookies from file ({file_path})...")

            lwp_cookiejar = LWPCookieJar()
            lwp_cookiejar.load(str(file_path), ignore_discard=True)
            for c in lwp_cookiejar:
                # noinspection PyTypeChecker
                args = dict(vars(c).items())
                args['rest'] = args['_rest']
                del args['_rest']
                c = Cookie(**args)
                self._logger.debug(c)
                session.cookies.set_cookie(c)

        except Exception as ex:
            self._logger.warning(f"could not load cookies from file ({file_path}): ({ex})")

    def save(self, cookiejar: CookieJar):
        file_path = self._cookies_file_path
        self._logger.debug(f"saving cookies to file ({file_path}) ...")

        lwp_cookiejar = LWPCookieJar()
        for c in cookiejar:
            # noinspection PyTypeChecker
            args = dict(vars(c).items())
            # noinspection PyUnresolvedReferences
            args['rest'] = args["_rest"]
            del args['_rest']
            c = Cookie(**args)
            lwp_cookiejar.set_cookie(c)

        lwp_cookiejar.save(str(file_path), ignore_discard=True, ignore_expires=True)


class RequestSessionFileStorage(IRequestSessionStorage):
    _logger: Logger
    _requests_file_path: Path

    def __init__(self,
                 logger: Logger,
                 requests_file_path: Path):
        self._logger = logger
        self._requests_file_path = requests_file_path

    def write(self, request_session_context: RequestSessionContext, api_config: ApiConfiguration):
        session_folder = self._requests_file_path.parent
        if not path.exists(session_folder):
            self._logger.debug(f"creating folder '{session_folder}'...")
            os.makedirs(session_folder)

        analyser = HARHttpRequestEntryRenderer(self._logger)
        py_file_contents = analyser.rendering(http_entries=request_session_context.entries)

        self._logger.debug(f'hiding sensitive variables ...')

        py_file_contents = StringHelper.hide_sensitive_variables(py_file_contents, [
            api_config.username,
            api_config.password,
            api_config.date_of_birth
        ])

        self._logger.debug(f'saving file {self._requests_file_path}')

        with open(self._requests_file_path, 'w') as f:
            f.write(py_file_contents)

    def get_location(self) -> str:
        return str(self._requests_file_path)
