import logging

from ...orders.manual.clients import ManualOrderClient
from ...orders.manual.models import ManualOrderPosition, ManualOrder
from ...session.clients import SessionClient
from requests_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_current_position(web_session: IWebSession,
                         account_id: int,
                         sedol_code: str,
                         category_code: str) -> ManualOrderPosition:
    client = ManualOrderClient(SessionClient())
    return client.get_current_position(
        web_session=web_session,
        account_id=account_id,
        sedol_code=sedol_code,
        category_code=category_code
    )


def submit_order(web_session: IWebSession, order: ManualOrder):
    client = ManualOrderClient(SessionClient())
    return client.submit_order(
        web_session=web_session,
        order=order
    )
