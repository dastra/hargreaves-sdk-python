from pathlib import Path
from urllib.parse import urlencode

import pytest
from requests import Response

from hargreaves.authentication.login.step_two import *
from hargreaves.config.models import ApiConfiguration
from hargreaves.request_tracker.mocks import MockWebSession

HL_VT = '1670432745'


def test_parse_secure_numbers():
    stage_two_html = Path(Path(__file__).parent / 'files/stage-two-login-mock.html').read_text()

    secure_numbers = parse_secure_numbers(stage_two_html)

    assert secure_numbers == [1, 2, 5]


def test_parse_secure_numbers_failed():
    with pytest.raises(ValueError, match=r"^Could not find secure number"):
        parse_secure_numbers('<html></html>')


def test_post_secure_numbers():
    config = __get_config()

    with MockWebSession() as web_session:

        expected_params = {
            "hl_vt": HL_VT,
            "online-password-verification": "password",
            "secure-number[1]": 5,
            "secure-number[2]": 7,
            "secure-number[3]": 8,
            "submit": " Log in   "
        }

        mock = web_session.mock_post(
            'https://online.hl.co.uk/my-accounts/login-step-two',
            status_code=http.HTTPStatus.OK
        )

        actual_response = post_secure_numbers(web_session, HL_VT, config, [1, 3, 4])
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(actual_response) == Response


def __get_config():
    return ApiConfiguration('test', 'password', '010204', '567890')
