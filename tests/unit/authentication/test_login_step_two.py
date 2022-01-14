import pytest
import requests
import requests_mock
from pathlib import Path
from hargreaves.authentication.login.step_two import *
from hargreaves.config.models import ApiConfiguration

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
    session = requests.Session()

    with requests_mock.Mocker() as m:
        m.post(
            'https://online.hl.co.uk/my-accounts/login-step-two',
            json={"hl_vt": HL_VT, "online-password-verification": "password", "secure-number[1]": 5,
                  "secure-number[2]": 7, "secure-number[3]": 8},
            status_code=http.HTTPStatus.FOUND
        )

        post_secure_numbers(session, HL_VT, config, [1, 3, 4])


def __get_config():
    return ApiConfiguration('test', 'password', '010204', '567890')
