from hargreaves.session.clients import ISessionClient


class MockSessionClient(ISessionClient):
    _was_called = False

    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        self._was_called = True

    @property
    def was_called(self):
        return self._was_called