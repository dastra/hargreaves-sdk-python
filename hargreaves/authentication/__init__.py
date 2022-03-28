import logging

from requests import Response

from hargreaves.authentication.clients import LoggedInSession, AuthenticationClient
from hargreaves.config.models import ApiConfiguration
from hargreaves.request_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_logged_in_session(web_session: IWebSession, config: ApiConfiguration):
    return LoggedInSession(
        web_session=web_session,
        config=config)


def login(web_session: IWebSession,
          config: ApiConfiguration) -> Response:
    return AuthenticationClient().login(
        web_session=web_session,
        config=config
    )


def logout(web_session: IWebSession):
    return AuthenticationClient().logout(
        web_session=web_session
    )
