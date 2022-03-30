import logging

from ..session.errors import SessionError
from ..utils import clock
from requests_tracker.session import IWebSession, WebRequestType

logger = logging.getLogger(__name__)


class ISessionClient:
    def session_keepalive(self, web_session: IWebSession, sedol_code: str, session_hl_vt: str):
        pass


class SessionClient(ISessionClient):

    def __init__(self):
        pass

    def session_keepalive(self, web_session: IWebSession, sedol_code: str, session_hl_vt: str):
        logger.debug("Perform 'Session Keepalive'")

        clock.sleep_random()

        # pid is the time in milliseconds since the epoch
        pid = clock.get_current_time_as_epoch_time()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        res = web_session.get(f"https://online.hl.co.uk/ajaxx/user.php",
                              params={
                                  'method': 'session_timeout_handler',
                                  'keepalive': "1",
                                  'format': 'jsonp',
                                  'jsoncallback': f"jsonp{pid}",
                                  'hl_vt': session_hl_vt,
                                  'initialise': 'true'
                              },
                              headers=request_headers, request_type=WebRequestType.XHR)

        if res.text != 'session_timeout_handler(["keptalive"])':
            raise SessionError('Session could not be kept alive', res.text)
