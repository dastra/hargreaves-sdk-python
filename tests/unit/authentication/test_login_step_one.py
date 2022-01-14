import pytest
import requests_mock
from pathlib import Path
from hargreaves.authentication.login.step_one import *
from hargreaves.config.models import ApiConfiguration

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
    session = requests.Session()

    with requests_mock.Mocker() as mock_request:
        mock_request.post(
            'https://online.hl.co.uk/my-accounts/login-step-one',
            json={"hl_vt": HL_VT, "username": "test", "date-of-birth": "010204"},
            status_code=http.HTTPStatus.FOUND
        )

        post_username_dob(session, HL_VT, config)


def __get_config():
    return ApiConfiguration('test', 'password', '010204', '567890')
