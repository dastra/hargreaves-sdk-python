import logging

from hargreaves.session.errors import SessionError
from hargreaves.web.session import IWebSession, WebRequestType
from hargreaves.web.timings import ITimeService

logger = logging.getLogger(__name__)


class ISessionClient:
    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        pass


class MockSessionClient(ISessionClient):
    _was_called = False

    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        self._was_called = True

    @property
    def was_called(self):
        return self._was_called


class SessionClient(ISessionClient):
    _web_session: IWebSession
    _time_service: ITimeService

    def __init__(self,
                 web_session: IWebSession,
                 time_service: ITimeService
                 ):
        self._web_session = web_session
        self._time_service = time_service

    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        logger.debug("Perform 'Session Keepalive'")

        self._time_service.sleep()

        # pid is the time in milliseconds since the epoch
        pid = self._time_service.get_current_time_as_epoch_time()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        res = self._web_session.get(f"https://online.hl.co.uk/ajaxx/user.php",
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
