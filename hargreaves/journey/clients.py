import logging
from datetime import datetime
from pathlib import Path
from typing import List

import requests

from hargreaves.account import AccountSummary, AccountDetail
from hargreaves.account.clients import AccountClient
from hargreaves.analysis import DEFAULT_EXCLUDE
from hargreaves.analysis.har2md import Har2MdController
from hargreaves.authentication.clients import LoggedInSession, AuthenticationClient
from hargreaves.config import ApiConfiguration
from hargreaves.journey.storage import CookiesFileStorage, RequestSessionFileStorage
from hargreaves.search import InvestmentTypes
from hargreaves.search.clients import SecuritySearchClient, security_filter
from hargreaves.session.clients import SessionClient
from hargreaves.orders.manual.clients import ManualOrderClient
from hargreaves.orders.manual.models import ManualOrder
from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.orders.market.models import MarketOrderQuote, MarketOrder
from hargreaves.orders.pending.clients import PendingOrdersClient
from hargreaves.orders.pending.models import PendingOrder
from hargreaves.deals.clients import DealClient
from hargreaves.deals.models import DealRequest
from hargreaves.utils.paths import PathHelper
from hargreaves.web.cookies import HLCookieHelper
from hargreaves.web.headers import HeaderFactory
from hargreaves.web.session import WebSession, RequestSessionContext
from hargreaves.web.storage import ICookieStorage, IRequestSessionStorage
from hargreaves.web.timings import ITimeService, TimeService

logger = logging.getLogger(__name__)


class WebSessionManager:
    # dependencies
    _time_service: ITimeService
    _cookies_storage: ICookieStorage
    _request_session_storage: IRequestSessionStorage

    # state
    _web_session: WebSession
    _request_session_context: RequestSessionContext

    # module clients
    _authentication_client = AuthenticationClient
    _account_client: AccountClient
    _search_client: SecuritySearchClient
    _market_order_client: MarketOrderClient
    _manual_order_client: ManualOrderClient
    _deal_client: DealClient
    _pending_orders_client: PendingOrdersClient

    def __init__(self,
                 time_service: ITimeService,
                 cookies_storage: ICookieStorage,
                 request_session_storage: IRequestSessionStorage
                 ):
        self._time_service = time_service
        self._cookies_storage = cookies_storage
        self._request_session_storage = request_session_storage

    def start_session(self, api_config: ApiConfiguration):
        self._request_session_context = RequestSessionContext()
        session = requests.Session()

        self._cookies_storage.load(session)

        header_factory = HeaderFactory.create(self._request_session_context)

        self._web_session = WebSession(session, self._request_session_context, header_factory)

        HLCookieHelper.set_default_cookies(self._web_session.cookies)

        self._authentication_client = AuthenticationClient(self._time_service, self._web_session)

        logged_in_session = LoggedInSession(self._web_session, self._authentication_client, api_config)

        self._search_client = SecuritySearchClient(logged_in_session, self._time_service)

        self._account_client = AccountClient(logged_in_session)

        session_client = SessionClient(self._web_session, self._time_service)

        self._market_order_client = MarketOrderClient(self._time_service, logged_in_session, session_client)
        self._manual_order_client = ManualOrderClient(self._time_service, logged_in_session, session_client)
        self._deal_client = DealClient(self._market_order_client, self._manual_order_client)

        self._pending_orders_client = PendingOrdersClient(self._time_service, logged_in_session)

    def get_account_summary(self) -> List[AccountSummary]:
        return self._account_client.get_account_summary()

    def get_account_detail(self, account_summary: AccountSummary) -> AccountDetail:
        return self._account_client.get_account_detail(account_summary)

    def get_pending_orders(self, account_id) -> List[PendingOrder]:
        return self._pending_orders_client.get_pending_orders(account_id)

    def cancel_pending_order(self, cancel_order_id: int, pending_orders: List[PendingOrder]):
        return self._pending_orders_client.cancel_pending_order(
            cancel_order_id=cancel_order_id,
            pending_orders=pending_orders
        )

    def search_security(self, search_string: str, investment_types: list):
        return self._search_client.investment_search(search_string, investment_types)

    def get_market_order_position(self, account_id: int, sedol_code: str, category_code: str):
        return self._market_order_client.get_current_position(
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

    def get_market_order_quote(self, order: MarketOrder):
        return self._market_order_client.get_order_quote(order)

    def execute_market_order(self, price_quote: MarketOrderQuote):
        return self._market_order_client.execute_order(price_quote)

    def get_manual_order_position(self, account_id: int, sedol_code: str, category_code: str):
        return self._manual_order_client.get_current_position(
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

    def submit_manual_order(self, order: ManualOrder):
        return self._manual_order_client.submit_order(order)

    def execute_smart_deal(self, deal_request: DealRequest):
        accounts = self.get_account_summary()

        account_summary = next((account_summary for account_summary in accounts
                                if account_summary.account_id == deal_request.account_id), None)

        account_detail = self.get_account_detail(account_summary)

        account_value = account_detail.total_value
        account_cash = account_detail.total_cash

        logger.debug(f"Account Value = £ {account_value:,.2f}, "
                     f"Cash Available = £ {account_cash:,.2f}")

        search_results = self.search_security(deal_request.stock_ticker, InvestmentTypes.ALL)

        print(f"Found {len(search_results)} results, let's filter to 1")

        found_security = security_filter(
            search_results=search_results,
            stock_ticker=deal_request.stock_ticker,
            sedol_code=deal_request.sedol_code)

        sedol_code = found_security.sedol_code
        category_code = found_security.category

        return self._deal_client.execute_smart_deal(
            deal_request=deal_request,
            sedol_code=sedol_code,
            category_code=category_code,
            account_value=account_value
        )

    def logout(self):
        logger.debug(f"Logging Out ...")
        return self._authentication_client.logout()

    def stop_session(self, api_config: ApiConfiguration):
        self._cookies_storage.save(self._web_session.cookies)
        self._request_session_storage.write(self._request_session_context, api_config)

    def convert_HAR_to_markdown(self):
        exclude_patterns = DEFAULT_EXCLUDE.split(',')
        input_file = Path(self._request_session_storage.get_location())
        output_folder = Path.joinpath(input_file.parent, input_file.stem)

        har2md = Har2MdController()
        har2md.exec(str(input_file), str(output_folder), exclude_patterns)


class WebSessionManagerFactory:

    @staticmethod
    def create_with_file_storage():
        time_service = TimeService()

        # create local file-based cookies-storage
        cookies_file_path = PathHelper.get_project_root() \
            .joinpath('session_cache').joinpath('cookies.txt')
        cookies_storage = CookiesFileStorage(cookies_file_path)

        # create local file-based session-history-writer
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
        requests_file_path = PathHelper.get_project_root() \
            .joinpath('session_cache').joinpath(f"session-{dt_string}.har")
        request_session_storage = RequestSessionFileStorage(requests_file_path)

        return WebSessionManager(
            time_service,
            cookies_storage,
            request_session_storage)
