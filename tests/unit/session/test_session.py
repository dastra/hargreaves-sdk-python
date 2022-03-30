import http

from hargreaves.session.clients import SessionClient
from hargreaves.utils import clock
from hargreaves.utils.logs import LogHelper
from requests_tracker.mocks import MockWebSession

LogHelper.configure_std_out()
clock.freeze_time()


def test_session_keepalive():
    sedol_code = 'A12345'
    session_hl_vt = '460029272'

    with MockWebSession() as web_session:

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/user.php',
            params={
                'method': 'session_timeout_handler',
                'keepalive': "1",
                'format': 'jsonp',
                'jsoncallback': f"jsonp{clock.get_current_time_as_epoch_time()}",
                'hl_vt': session_hl_vt,
                'initialise': 'true'
            },
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
            },
            response_text='session_timeout_handler(["keptalive"])',
            status_code=http.HTTPStatus.OK
        )

        client = SessionClient()
        client.session_keepalive(
            web_session=web_session,
            sedol_code=sedol_code,
            session_hl_vt=session_hl_vt)
