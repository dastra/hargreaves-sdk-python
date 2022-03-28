import logging

from hargreaves.accounts.clients import AccountClient
from hargreaves.deals.clients import DealClient
from hargreaves.deals.models import DealRequest, DealResult
from hargreaves.orders.manual.clients import ManualOrderClient
from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.search.clients import SecuritySearchClient
from hargreaves.session.clients import SessionClient
from hargreaves.request_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def execute_deal(web_session: IWebSession, deal_request: DealRequest) -> DealResult:
    account_client = AccountClient()
    search_client = SecuritySearchClient()
    session_client = SessionClient()
    market_order_client = MarketOrderClient(session_client)
    manual_order_client = ManualOrderClient(session_client)

    deal_client = DealClient(
        account_client=account_client,
        search_client=search_client,
        market_order_client=market_order_client,
        manual_order_client=manual_order_client
    )

    return deal_client.execute_deal(
        web_session=web_session,
        deal_request=deal_request
    )
