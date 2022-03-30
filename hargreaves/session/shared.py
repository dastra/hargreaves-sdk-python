import logging
from http.cookiejar import CookieJar

from requests import Response
from requests_tracker.request import WebRequestType, RequestSessionContext
from requests_tracker.session import IWebSession

from ..authentication import AuthenticationClient
from ..config.models import ApiConfiguration

logger = logging.getLogger(__name__)


class LoggedInSession(IWebSession):
    _web_session: IWebSession
    _config: ApiConfiguration

    def __init__(self, web_session: IWebSession, config: ApiConfiguration):
        self._web_session = web_session
        self._config = config

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        response = self._web_session.get(url=url, request_type=request_type, params=params, headers=headers)
        if response.url != AuthenticationClient.LOGIN_URL:
            return response
        logger.debug("Redirected to login page, let's login ...")
        logged_in_response = AuthenticationClient().login(self._web_session, self._config, response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                         f"let's GET original URL '{url}'")
            return self._web_session.get(url=url, request_type=request_type, params=params, headers=headers)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        response = self._web_session.post(url=url, request_type=request_type, data=data, headers=headers)
        if response.url != AuthenticationClient.LOGIN_URL:
            return response
        logger.debug("Redirected to login page, let's login ...")
        logged_in_response = AuthenticationClient().login(self._web_session, self._config, response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                         f"let's POST original URL '{url}'")
            return self._web_session.post(url=url, request_type=request_type, data=data, headers=headers)

    @property
    def cookies(self) -> CookieJar:
        return self._web_session.cookies

    @property
    def request_session_context(self) -> RequestSessionContext:
        return self._web_session.request_session_context
