from ..session.clients import ISessionClient
from requests_tracker.session import IWebSession


class MockSessionClient(ISessionClient):
    _was_called = False

    def session_keepalive(self, web_session: IWebSession, sedol_code: str, session_hl_vt: str):
        self._was_called = True

    @property
    def was_called(self):
        return self._was_called
