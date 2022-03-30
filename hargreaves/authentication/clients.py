import logging

from ..authentication.login.step_one import *
from ..authentication.login.step_two import *
from ..config.models import ApiConfiguration
from ..utils.cookies import HLCookieHelper
from ..utils import clock

logger = logging.getLogger(__name__)


class AuthenticationClient:
    LOGIN_URL = 'https://online.hl.co.uk/my-accounts/login-step-one'

    def __init__(self):
        pass

    def login(self,
              web_session: IWebSession,
              config: ApiConfiguration,
              redirect_response: Response = None) -> Response:

        if redirect_response is not None:
            logger.debug(f"STEP-1: Parse 'Security Token'")
            hl_vt = parse_security_token(redirect_response.text)
        else:
            logger.debug("STEP-1: Get Security Token...")
            hl_vt = get_security_token(web_session)

        clock.sleep_random(minimum=1, maximum=3)
        logger.debug(f"STEP-1: Posting username & dob (Security Token = {hl_vt})...")
        step1_response = post_username_dob(web_session, hl_vt, config)
        logger.debug(f"STEP-1:Parsing secure numbers...")
        secure_numbers_requested = parse_secure_numbers(step1_response.text)

        clock.sleep_random(minimum=1, maximum=3)
        logger.debug(f"STEP-2: Posting Password & Secure Numbers ({secure_numbers_requested})...")
        step2_response = post_secure_numbers(web_session, hl_vt, config, secure_numbers_requested)
        logger.debug(f"STEP-2: OK, response url = {step2_response.url}...")

        logger.debug(f"Set Logged-In Cookies...")
        HLCookieHelper.set_logged_in_cookies(web_session.cookies)

        return step2_response

    def logout(self, web_session: IWebSession):
        logger.debug(f"Logging out ...")
        response = web_session.get("https://online.hl.co.uk/my-accounts/logout")
        if response.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Unexpected logout response code ('{response.status_code}')")
        web_session.cookies.clear()
