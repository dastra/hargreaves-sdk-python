from logging import Logger

from hargreaves.session.errors import SessionError
from hargreaves.utils.timings import ITimeService
from hargreaves.web.session import IWebSession, WebRequestType


class SessionClient:
    __logger: Logger
    __web_session: IWebSession
    __time_service: ITimeService

    def __init__(self,
                 logger: Logger,
                 web_session: IWebSession,
                 time_service: ITimeService
                 ):
        self.__logger = logger
        self.__web_session = web_session
        self.__time_service = time_service

    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        self.__logger.debug("Perform 'Session Keepalive'")
        # pid is the time in milliseconds since the epoch
        pid = self.__time_service.get_current_time_as_epoch_time()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        res = self.__web_session.get(f"https://online.hl.co.uk/ajaxx/user.php",
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
