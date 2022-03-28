import http

from bs4 import BeautifulSoup
from requests import Response

from hargreaves.config.models import ApiConfiguration
from hargreaves.request_tracker.session import IWebSession


def get_security_token(web_session: IWebSession):
    stage_one_html = web_session.get("https://online.hl.co.uk/my-accounts/login-step-one").text
    hl_vt = parse_security_token(stage_one_html)
    return hl_vt


def parse_security_token(stage_one_html: str) -> str:
    soup = BeautifulSoup(stage_one_html, 'html.parser')
    soup.find(id="link3")
    node = soup.find('input', {'name': 'hl_vt'})
    hl_vt = None
    if node is not None:
        hl_vt = node.get('value')
    if hl_vt is None:
        raise ValueError("Unable to parse HL_VT")
    return hl_vt


def post_username_dob(web_session: IWebSession, hl_vt: str, config: ApiConfiguration) -> Response:
    body = {'hl_vt': hl_vt, 'username': config.username, 'date-of-birth': config.date_of_birth}
    res = web_session.post('https://online.hl.co.uk/my-accounts/login-step-one', data=body)
    if res.status_code != http.HTTPStatus.OK:
        raise ConnectionError(f"Username/DOB step response code was {res.status_code}")
    elif "try again" in res.text:
        raise ValueError("An error occurred with posting Username & DoB. Check these before continuing")
    return res
