from http.cookiejar import CookieJar

import requests

from hargreaves.config import ApiConfiguration
from hargreaves.web.session import RequestSessionContext


class ICookieStorage:

    def load(self, session: requests.Session):
        pass

    def save(self, cookiejar: CookieJar):
        pass


class IRequestSessionStorage:

    def write(self, request_session_context: RequestSessionContext, api_config: ApiConfiguration):
        pass

    def get_location(self) -> str:
        pass
