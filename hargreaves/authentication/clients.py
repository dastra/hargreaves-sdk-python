
from hargreaves.authentication.login.step_one import *
from hargreaves.authentication.login.step_two import *
from hargreaves.config.models import ApiConfiguration


def login(config: ApiConfiguration) -> requests.Session:
    session = requests.Session()

    session, hl_vt = get_security_token(session)

    session = post_username_dob(session, hl_vt, config)

    session, secure_numbers_requested = get_secure_number_request(session)

    post_secure_numbers(session, hl_vt, config, secure_numbers_requested)

    return session


def logout(session: requests.Session):
    session.cookies.clear()
