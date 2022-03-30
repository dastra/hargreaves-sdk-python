import logging

from requests_tracker.session import WebSessionFactory
from requests_tracker.storage import ICookieStorage

from ..config.models import ApiConfiguration
from ..utils.cookies import HLCookieHelper
from ..session.shared import LoggedInSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_session(cookies_storage: ICookieStorage, config: ApiConfiguration):
    """
    Creates a WebSession that will automatically handle login redirects
    :param cookies_storage:
    :param config:
    :return:
    """
    web_session = WebSessionFactory.create(
        cookies_storage,
        default_referer='https://online.hl.co.uk/',
        sensitive_values=[config.username, config.password,
                          config.secure_number, config.date_of_birth],
        sensitive_params=['secure-number['])
    HLCookieHelper.set_default_cookies(web_session.cookies)
    return LoggedInSession(
        web_session=web_session,
        config=config)
