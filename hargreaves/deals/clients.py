import logging

from hargreaves.accounts.clients import IAccountClient
from hargreaves.deals.models import DealRequest, DealResult
from hargreaves.orders.manual.clients import IManualOrderClient
from hargreaves.orders.market.clients import IMarketOrderClient
from hargreaves.orders.market.errors import MarketClosedError, MarketOrderLiveQuoteError
from hargreaves.orders.models import OrderRequest
from hargreaves.search import InvestmentTypes
from hargreaves.search.clients import security_filter, ISecuritySearchClient
from hargreaves.request_tracker.session import IWebSession

logger = logging.getLogger(__name__)


class DealClient():
    _account_client: IAccountClient
    _search_client: ISecuritySearchClient
    _market_order_client: IMarketOrderClient
    _manual_order_client: IManualOrderClient

    def __init__(self,
                 account_client: IAccountClient,
                 search_client: ISecuritySearchClient,
                 market_order_client: IMarketOrderClient,
                 manual_order_client: IManualOrderClient
                 ):
        self._account_client = account_client
        self._search_client = search_client
        self._market_order_client = market_order_client
        self._manual_order_client = manual_order_client

    def execute_deal(self, web_session: IWebSession, deal_request: DealRequest) -> DealResult:

        accounts = self._account_client.get_account_summary(web_session=web_session)

        account_summary = next((account_summary for account_summary in accounts
                                if account_summary.account_id == deal_request.account_id), None)

        account_detail = self._account_client.get_account_detail(
            web_session=web_session, account_summary=account_summary)

        account_value = account_detail.total_value
        account_cash = account_detail.total_cash

        logger.debug(f"Account Value = £ {account_value:,.2f}, "
                     f"Cash Available = £ {account_cash:,.2f}")

        search_results = self._search_client.investment_search(
            web_session=web_session,
            search_string=deal_request.stock_ticker,
            investment_types=InvestmentTypes.ALL)

        print(f"Found {len(search_results)} results, let's filter to 1")

        found_security = security_filter(
            search_results=search_results,
            stock_ticker=deal_request.stock_ticker,
            sedol_code=deal_request.sedol_code)

        order_request = OrderRequest(
            sedol_code=found_security.sedol_code,
            category_code=found_security.category,
            position_type=deal_request.position_type,
            position_percentage=deal_request.position_percentage,
            account_id=deal_request.account_id,
            account_value=account_value
        )

        logger.debug("Executing Smart Deal ...")

        try:

            order_confirmation = self._market_order_client.execute_order_flow(
                web_session=web_session, order_request=order_request)
            return DealResult(order_request=order_request, order_confirmation=order_confirmation)

        except MarketClosedError as ex:
            logger.warning("Market is closed ...")

            if not (deal_request.allow_fill_or_kill and ex.can_place_fill_or_kill_order):
                raise ex

            order_confirmation = self._manual_order_client.execute_order_flow(
                web_session=web_session, order_request=order_request)
            return DealResult(order_request=order_request, order_confirmation=order_confirmation)

        except MarketOrderLiveQuoteError:
            logger.warning("Unable to retrieve live-quote ...")

            order_confirmation = self._manual_order_client.execute_order_flow(
                web_session=web_session, order_request=order_request)
            return DealResult(order_request=order_request, order_confirmation=order_confirmation)
