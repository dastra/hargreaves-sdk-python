import logging
from pathlib import Path
from typing import List

from hargreaves import orders, deals, authentication, accounts, search
from hargreaves.accounts import AccountSummary, AccountDetail
from hargreaves.request_tracker.har2md import Har2MdController
from hargreaves.authentication.clients import LoggedInSession
from hargreaves.config.models import ApiConfiguration
from hargreaves.deals.models import DealRequest
from hargreaves.orders.manual.clients import ManualOrderClient
from hargreaves.orders.manual.models import ManualOrder
from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.orders.market.models import MarketOrderQuote, MarketOrder
from hargreaves.orders.pending.clients import PendingOrdersClient
from hargreaves.orders.pending.models import PendingOrder
from hargreaves.session.cookies import HLCookieHelper
from hargreaves.request_tracker.session import WebSessionFactory, IWebSession
from hargreaves.request_tracker.storage import ICookieStorage, IRequestSessionStorage

logger = logging.getLogger(__name__)


class WebSessionManager:
    _cookies_storage: ICookieStorage
    _request_session_storage: IRequestSessionStorage
    _web_session: IWebSession
    _logged_in_session: LoggedInSession

    def __init__(self,
                 cookies_storage: ICookieStorage,
                 request_session_storage: IRequestSessionStorage
                 ):
        self._cookies_storage = cookies_storage
        self._request_session_storage = request_session_storage

    def start_session(self, api_config: ApiConfiguration):
        self._web_session = WebSessionFactory.create(self._cookies_storage)
        self._logged_in_session = authentication.create_logged_in_session(self._web_session, api_config)
        HLCookieHelper.set_default_cookies(self._web_session.cookies)

    def get_account_summary(self) -> List[AccountSummary]:
        return accounts.get_account_summary(web_session=self._logged_in_session)

    def get_account_detail(self, account_summary: AccountSummary) -> AccountDetail:
        return accounts.get_account_detail(
            web_session=self._logged_in_session,
            account_summary=account_summary)

    def get_pending_orders(self, account_id) -> List[PendingOrder]:
        return orders.pending.get_pending_orders(
            web_session=self._logged_in_session,
            account_id=account_id)

    def cancel_pending_order(self, cancel_order_id: int, pending_orders: List[PendingOrder]):
        return orders.pending.cancel_pending_order(
            web_session=self._logged_in_session,
            cancel_order_id=cancel_order_id,
            pending_orders=pending_orders
        )

    def search_security(self, search_string: str, investment_types: list):
        return search.investment_search(
            web_session=self._logged_in_session,
            search_string=search_string,
            investment_types=investment_types)

    def get_market_order_position(self, account_id: int, sedol_code: str, category_code: str):
        return orders.market.get_current_position(
            web_session=self._logged_in_session,
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

    def get_market_order_quote(self, order: MarketOrder):
        return orders.market.get_order_quote(
            web_session=self._logged_in_session,
            order=order)

    def execute_market_order(self, price_quote: MarketOrderQuote):
        return orders.market.submit_order(
            web_session=self._logged_in_session,
            order_quote=price_quote)

    def get_manual_order_position(self, account_id: int, sedol_code: str, category_code: str):
        return orders.manual.get_current_position(
            web_session=self._logged_in_session,
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

    def submit_manual_order(self, order: ManualOrder):
        return orders.manual.submit_order(
            web_session=self._logged_in_session,
            order=order)

    def execute_deal(self, deal_request: DealRequest):
        return deals.execute_deal(
            web_session=self._logged_in_session,
            deal_request=deal_request
        )

    def logout(self):
        return authentication.logout(web_session=self._web_session)

    def stop_session(self, api_config: ApiConfiguration):
        self._cookies_storage.save(self._web_session.cookies)
        self._request_session_storage.write(self._web_session.request_session_context, api_config)

    def convert_HAR_to_markdown(self):
        input_file = Path(self._request_session_storage.get_location())
        output_folder = Path.joinpath(input_file.parent, input_file.stem)

        har2md = Har2MdController()
        har2md.exec(str(input_file), str(output_folder), [])
