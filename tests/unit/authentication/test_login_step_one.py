from pathlib import Path
from urllib.parse import urlencode

import pytest

from hargreaves.authentication.login.step_one import *
from hargreaves.config.models import ApiConfiguration
from requests_tracker.mocks import MockWebSession

HL_VT = '1670432745'


def test_parse_security_token():
    stage_one_html = Path(Path(__file__).parent / 'files/stage-one-login-mock.html').read_text()

    hl_vt = parse_security_token(stage_one_html)

    assert hl_vt == '1670432745'


def test_parse_security_token_failed():
    with pytest.raises(ValueError, match=r"^Unable to parse HL_VT$"):
        parse_security_token('<html></html>')


def test_post_username_dob():
    config = __get_config()

    with MockWebSession() as web_session:
        expected_params = {
            "hl_vt": HL_VT,
            "username": "test",
            "date-of-birth": "010204"
        }

        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/login-step-one',
            status_code=http.HTTPStatus.OK
        )

        actual_response = post_username_dob(web_session, HL_VT, config)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(actual_response) == Response


def __get_config():
    return ApiConfiguration('test', 'password', '010204', '567890')
