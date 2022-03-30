import logging

from requests import Response
from requests_tracker.session import IWebSession

from ..authentication.clients import AuthenticationClient
from ..config.models import ApiConfiguration

logging.getLogger(__name__).addHandler(logging.NullHandler())


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
