import logging

from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.orders.market.models import MarketOrderPosition, MarketOrder, MarketOrderQuote, MarketOrderConfirmation
from hargreaves.session.clients import SessionClient
from hargreaves.request_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def create_client() -> MarketOrderClient:
    return MarketOrderClient(SessionClient())


def get_current_position(web_session: IWebSession,
                         account_id: int,
                         sedol_code: str,
                         category_code: str) -> MarketOrderPosition:
    client = MarketOrderClient(SessionClient())
    return client.get_current_position(
        web_session=web_session,
        account_id=account_id,
        sedol_code=sedol_code,
        category_code=category_code
    )


def get_order_quote(web_session: IWebSession, order: MarketOrder) -> MarketOrderQuote:
    client = MarketOrderClient(SessionClient())
    return client.get_order_quote(
        web_session=web_session,
        order=order
    )


def submit_order(web_session: IWebSession, order_quote: MarketOrderQuote) -> MarketOrderConfirmation:
    client = MarketOrderClient(SessionClient())
    return client.submit_order(
        web_session=web_session,
        order_quote=order_quote
    )

