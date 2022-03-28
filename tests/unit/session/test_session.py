import http

from hargreaves.session.clients import SessionClient
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession, MockTimeService


def test_session_keepalive():
    sedol_code = 'A12345'
    session_hl_vt = '460029272'

    with MockWebSession() as web_session:
        LoggerFactory.configure_std_out()
        time_service = MockTimeService()

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/user.php',
            params={
                'method': 'session_timeout_handler',
                'keepalive': "1",
                'format': 'jsonp',
                'jsoncallback': f"jsonp{time_service.get_current_time_as_epoch_time()}",
                'hl_vt': session_hl_vt,
                'initialise': 'true'
            },
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
            },
            response_text='session_timeout_handler(["keptalive"])',
            status_code=http.HTTPStatus.OK
        )

        client = SessionClient(web_session, time_service)
        client.session_keepalive(sedol_code, session_hl_vt)
