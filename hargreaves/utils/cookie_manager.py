import requests
from requests import cookies


def set_cookies(session: requests.Session):
    session.cookies.set_cookie(
        cookies.create_cookie(domain=".hl.co.uk", name="jsCheck", value="yes", path='/'))

    return session
