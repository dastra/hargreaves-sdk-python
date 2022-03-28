import logging

from hargreaves.authentication.login.step_one import *
from hargreaves.authentication.login.step_two import *
from hargreaves.config.models import ApiConfiguration
from hargreaves.web.cookies import HLCookieHelper
from hargreaves.web.session import IWebSession, WebRequestType
from hargreaves.web.timings import ITimeService

logger = logging.getLogger(__name__)


class AuthenticationClient:
    _time_service: ITimeService
    _web_session: IWebSession

    def __init__(self,
                 time_service: ITimeService,
                 web_session: IWebSession
                 ):
        self._time_service = time_service
        self._web_session = web_session

    def login(self, config: ApiConfiguration, redirect_response: Response = None) -> Response:
        if redirect_response is not None:
            logger.debug(f"STEP-1: Parse 'Security Token'")
            hl_vt = parse_security_token(redirect_response.text)
        else:
            logger.debug("STEP-1: Get Security Token...")
            hl_vt = get_security_token(self._web_session)

        self._time_service.sleep(minimum=1, maximum=3)
        logger.debug(f"STEP-1: Posting username & dob (Security Token = {hl_vt})...")
        step1_response = post_username_dob(self._web_session, hl_vt, config)
        logger.debug(f"STEP-1:Parsing secure numbers...")
        secure_numbers_requested = parse_secure_numbers(step1_response.text)

        self._time_service.sleep(minimum=1, maximum=3)
        logger.debug(f"STEP-2: Posting Password & Secure Numbers ({secure_numbers_requested})...")
        step2_response = post_secure_numbers(self._web_session, hl_vt, config, secure_numbers_requested)
        logger.debug(f"STEP-2: OK, response url = {step2_response.url}...")

        logger.debug(f"Set Logged-In Cookies...")
        HLCookieHelper.set_logged_in_cookies(self._web_session.cookies)

        return step2_response

    def logout(self):
        logger.debug(f"Logging out ...")
        response = self._web_session.get("https://online.hl.co.uk/my-accounts/logout")
        if response.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Unexpected logout response code ('{response.status_code}')")
        self._web_session.cookies.clear()


class LoggedInSession(IWebSession):
    LOGIN_URL = 'https://online.hl.co.uk/my-accounts/login-step-one'
    _web_session: IWebSession
    _authentication_client: AuthenticationClient
    _config: ApiConfiguration

    def __init__(self,
                 web_session: IWebSession,
                 authentication_client: AuthenticationClient,
                 config: ApiConfiguration
                 ):
        self._web_session = web_session
        self._authentication_client = authentication_client
        self._config = config

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        response = self._web_session.get(url=url, request_type=request_type, params=params, headers=headers)
        if response.url != self.LOGIN_URL:
            return response
        logger.debug("Redirected to login page, let's login ...")
        logged_in_response = self._authentication_client.login(self._config, response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                         f"let's GET original URL '{url}'")
            return self._web_session.get(url=url, request_type=request_type, params=params, headers=headers)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        response = self._web_session.post(url=url, request_type=request_type, data=data, headers=headers)
        if response.url != self.LOGIN_URL:
            return response
        logger.debug("Redirected to login page, let's login ...")
        logged_in_response = self._authentication_client.login(self._config, response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                         f"let's POST original URL '{url}'")
            return self._web_session.post(url=url, request_type=request_type, data=data, headers=headers)
