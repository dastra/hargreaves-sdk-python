import http
import re

import requests
from bs4 import BeautifulSoup

from hargreaves.config.models import ApiConfiguration
from hargreaves.utils.cookie_manager import set_cookies


def get_secure_number_request(session: requests.Session):
    session = set_cookies(session)
    stage_two_html = session.get("https://online.hl.co.uk/my-accounts/login-step-two").text

    secure_numbers_requested = parse_secure_numbers(stage_two_html)

    return session, secure_numbers_requested


def parse_secure_numbers(stage_two_html: str) -> list:
    soup = BeautifulSoup(stage_two_html, 'html.parser')

    secure_numbers = []
    for selector in ['secure-number-1', 'secure-number-2', 'secure-number-3']:
        outer = soup.find(id=selector)
        if outer is None:
            raise ValueError(f"Could not find secure number {selector}")
        title = outer.attrs['title']
        if title is None:
            raise ValueError(f"Could not parse secure numbers from {outer}")

        secure_numbers.append(int(re.findall(r'\d+', title)[0]))

    return secure_numbers


def post_secure_numbers(session: requests.Session, hl_vt: str, config: ApiConfiguration,
                        secure_numbers_requested: list):
    session = set_cookies(session)
    body = {
        'hl_vt': hl_vt,
        'online-password-verification': config.password,
        'secure-number[1]': config.secure_number[secure_numbers_requested[0] - 1],
        'secure-number[2]': config.secure_number[secure_numbers_requested[1] - 1],
        'secure-number[3]': config.secure_number[secure_numbers_requested[2] - 1],
    }
    res = session.post('https://online.hl.co.uk/my-accounts/login-step-two', data=body, allow_redirects=False)
    if res.status_code != http.HTTPStatus.FOUND:
        raise ConnectionError(f"Secure Number step response code was {res.status_code}")
    elif "try again" in res.text:
        raise ValueError("An error occurred with posting password and secure number. Check these before continuing")
    return session
