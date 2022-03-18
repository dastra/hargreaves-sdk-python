from logging import Logger

from hargreaves.authentication.login.step_one import *
from hargreaves.authentication.login.step_two import *
from hargreaves.config.models import ApiConfiguration
from hargreaves.utils.timings import ITimeService, TimeService
from hargreaves.web.cookies import HLCookieHelper
from hargreaves.web.session import IWebSession, WebRequestType


class AuthenticationClient:
    __logger: Logger
    __time_service: ITimeService
    __web_session: IWebSession

    def __init__(self,
                 logger: Logger,
                 time_service: ITimeService,
                 web_session: IWebSession
                 ):
        self.__logger = logger
        self.__time_service = time_service
        self.__web_session = web_session

    def login(self, config: ApiConfiguration, redirect_response: Response = None):
        if redirect_response is not None:
            self.__logger.debug(f"STEP-1: Parse 'Security Token'")
            hl_vt = parse_security_token(redirect_response.text)
        else:
            self.__logger.debug("STEP-1: Get Security Token...")
            hl_vt = get_security_token(self.__web_session)

        self.__time_service.sleep(min=1, max=3)
        self.__logger.debug(f"STEP-1: Posting username & dob (Security Token = {hl_vt})...")
        step1_response = post_username_dob(self.__web_session, hl_vt, config)
        self.__logger.debug(f"STEP-1:Parsing secure numbers...")
        secure_numbers_requested = parse_secure_numbers(step1_response.text)

        self.__time_service.sleep(min=1, max=3)
        self.__logger.debug(f"STEP-2: Posting Password & Secure Numbers ({secure_numbers_requested})...")
        step2_response = post_secure_numbers(self.__web_session, hl_vt, config, secure_numbers_requested)
        self.__logger.debug(f"STEP-2: OK, response url = {step2_response.url}...")

        self.__logger.debug(f"Set Logged-In Cookies...")
        HLCookieHelper.set_logged_in_cookies(self.__web_session.cookies)

    def logout(self):
        self.__logger.debug(f"Logging out ...")
        response = self.__web_session.get("https://online.hl.co.uk/my-accounts/logout")
        if response.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Unexpected logout response code ('{response.status_code}')")
        self.__web_session.cookies.clear()


class LoggedInSession(IWebSession):
    LOGIN_URL = 'https://online.hl.co.uk/my-accounts/login-step-one'
    __logger: Logger
    __web_session: IWebSession
    __config: ApiConfiguration

    def __init__(self,
                 logger: Logger,
                 web_session: IWebSession,
                 config: ApiConfiguration
                 ):
        self.__logger = logger
        self.__web_session = web_session
        self.__config = config

    def login_on_redirect(self, response: Response):
        self.__logger.debug("Redirected to login page, let's login ...")

        time_service = TimeService(self.__logger)
        client = AuthenticationClient(self.__logger, time_service, self.__web_session)
        client.login(self.__config, response)

        return response

    def get(self, url: str, request_type: WebRequestType = WebRequestType.Document,
            params=None, headers=None) -> Response:
        response = self.__web_session.get(url=url, request_type=request_type, params=params, headers=headers)
        if response.url != self.LOGIN_URL:
            return response
        logged_in_response = self.login_on_redirect(response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            self.__logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                                f"let's GET original URL '{url}'")
            return self.__web_session.get(url=url, request_type=request_type, params=params, headers=headers)

    def post(self, url: str, request_type: WebRequestType = WebRequestType.Document,
             data=None, headers=None) -> Response:
        response = self.__web_session.post(url=url, request_type=request_type, data=data, headers=headers)
        if response.url != self.LOGIN_URL:
            return response
        logged_in_response = self.login_on_redirect(response)
        if logged_in_response.url == url:
            return logged_in_response
        else:
            self.__logger.debug(f"Unexpected post-login-redirect URL ({logged_in_response.url}), "
                                f"let's POST original URL '{url}'")
            return self.__web_session.post(url=url, request_type=request_type, data=data, headers=headers)

