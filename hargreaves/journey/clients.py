from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import List

import requests

from hargreaves.account import AccountSummary, AccountDetail
from hargreaves.account.clients import AccountClient
from hargreaves.analysis.har2md import Har2MdController
from hargreaves.authentication.clients import LoggedInSession, AuthenticationClient
from hargreaves.config import ApiConfiguration
from hargreaves.journey.storage import CookiesFileStorage, RequestSessionFileStorage
from hargreaves.search import InvestmentTypes
from hargreaves.search.clients import SecuritySearchClient
from hargreaves.session.clients import SessionClient
from hargreaves.trade.clients import PositionCalculator
from hargreaves.trade.manual.clients import ManualOrderClient
from hargreaves.trade.manual.models import ManualOrder
from hargreaves.trade.market.clients import MarketOrderClient
from hargreaves.trade.market.errors import MarketClosedError
from hargreaves.trade.market.models import MarketOrderQuote, MarketOrder
from hargreaves.trade.models import DealRequest, OrderPositionType, DealResult
from hargreaves.utils.paths import PathHelper
from hargreaves.utils.timings import ITimeService, TimeService
from hargreaves.web.cookies import HLCookieHelper
from hargreaves.web.headers import HeaderFactory
from hargreaves.web.session import WebSession, RequestSessionContext
from hargreaves.web.storage import ICookieStorage, IRequestSessionStorage


class WebSessionManager:
    # dependencies
    __logger: Logger
    __time_service: ITimeService
    __cookies_storage: ICookieStorage
    __request_session_storage: IRequestSessionStorage

    # state
    __web_session: WebSession
    __request_session_context: RequestSessionContext

    # module clients
    __authentication_client = AuthenticationClient
    __account_client: AccountClient
    __search_client: SecuritySearchClient
    __session_client: SessionClient
    __market_order_client: MarketOrderClient
    __manual_order_client: ManualOrderClient

    def __init__(self,
                 logger: Logger,
                 time_service: ITimeService,
                 cookies_storage: ICookieStorage,
                 request_session_storage: IRequestSessionStorage
                 ):
        self.__logger = logger
        self.__time_service = time_service
        self.__cookies_storage = cookies_storage
        self.__request_session_storage = request_session_storage

    def start_session(self, api_config: ApiConfiguration):

        self.__request_session_context = RequestSessionContext()
        session = requests.Session()

        self.__cookies_storage.load(session)

        header_factory = HeaderFactory.create(self.__request_session_context)
        self.__web_session = WebSession(self.__logger, session, self.__request_session_context, header_factory)

        self.__logger.debug(f"Set Default Cookies...")
        HLCookieHelper.set_default_cookies(self.__web_session.cookies)

        logged_in_session = LoggedInSession(self.__logger, self.__web_session, api_config)

        self.__search_client = SecuritySearchClient(self.__logger, self.__web_session, self.__time_service)
        self.__authentication_client = AuthenticationClient(self.__logger, self.__time_service, self.__web_session)
        self.__session_client = SessionClient(self.__logger, logged_in_session, self.__time_service)
        self.__account_client = AccountClient(self.__logger, logged_in_session)
        self.__market_order_client = MarketOrderClient(self.__logger, logged_in_session)
        self.__manual_order_client = ManualOrderClient(self.__logger, logged_in_session)

    def get_account_summary(self) -> List[AccountSummary]:
        account_summary = self.__account_client.get_account_summary()
        return account_summary

    def get_account_detail(self, account_summary: AccountSummary) -> AccountDetail:
        account_detail = self.__account_client.get_account_detail(account_summary)
        return account_detail

    def search_security(self, search_string: str, investment_types: list):
        self.__time_service.sleep()
        search_results = self.__search_client.investment_search(search_string, investment_types)
        return search_results

    def get_market_order_position(self, account_id: int, sedol_code: str, category_code: str):
        self.__time_service.sleep()

        self.__logger.debug("Get Current Position")

        current_position = self.__market_order_client.get_current_position(
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

        return current_position

    def get_market_order_quote(self, order: MarketOrder):
        self.__time_service.sleep()

        self.__logger.debug("Perform 'Session Keepalive'")

        self.__session_client.session_keepalive(sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        self.__logger.debug("Get Order Quote")

        order_quote = self.__market_order_client.get_order_quote(order)
        return order_quote

    def execute_market_order(self, price_quote: MarketOrderQuote):
        self.__time_service.sleep(min=2, max=4)

        self.__logger.debug("Perform 'Session Keepalive'")

        self.__session_client.session_keepalive(
            sedol_code=price_quote.sedol_code, session_hl_vt=price_quote.session_hl_vt)

        self.__logger.debug(f"Execute (Confirm) Order ...")

        order_confirmation = self.__market_order_client.execute_order(price_quote)
        return order_confirmation

    def get_manual_order_position(self, account_id: int, sedol_code: str, category_code: str):
        self.__time_service.sleep()

        self.__logger.debug("Get Current Position")

        current_position = self.__manual_order_client.get_current_position(
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

        return current_position

    def submit_manual_order(self, order: ManualOrder):
        self.__time_service.sleep(min=2, max=4)

        self.__logger.debug("Perform 'Session Keepalive'")

        self.__session_client.session_keepalive(sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        self.__logger.debug(f"Submit Order ...")

        order_confirmation = self.__manual_order_client.submit_order(order)
        return order_confirmation

    def execute_smart_deal(self, deal_request: DealRequest):

        self.__logger.debug("Smart Deal - Start")

        sedol_code = None
        category_code = None
        account_value = 0.00

        try:
            self.__logger.debug("Get account current value ...")

            accounts = self.get_account_summary()

            account_summary = next((account_summary for account_summary in accounts
                                    if account_summary.account_id == deal_request.account_id), None)

            account_detail = self.get_account_detail(account_summary)
            account_value = account_detail.total_value
            account_cash = account_detail.total_cash

            self.__logger.debug(f"Account Value = £ {account_value:,.2f}, "
                                f"Cash Available = £ {account_cash:,.2f}")

            self.__logger.debug("Search for security ...")

            search_result = self.search_security(deal_request.stock_ticker, InvestmentTypes.ALL)
            print(f"Found {len(search_result)} results")
            if len(search_result) != 1:
                raise Exception(f"Unexpected number {(len(search_result))} of securities found!")

            self.__logger.debug(search_result[0])

            sedol_code = search_result[0].sedol_code
            category_code = search_result[0].category

            self.__logger.debug("Get current position ...")
            current_position = self.get_market_order_position(
                account_id=deal_request.account_id,
                sedol_code=sedol_code,
                category_code=category_code)

            self.__logger.debug(current_position.as_form_fields())

            self.__logger.debug("Calculate quantity ...")

            (amount_type, order_quantity) = PositionCalculator.calculate(
                position_type=deal_request.position_type,
                position_percentage=deal_request.position_percentage,
                account_value=account_value,
                units_held=current_position.units_held
            )

            self.__logger.debug(f"amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

            self.__logger.debug("Get market-order quote ...")

            order = MarketOrder(
                position=current_position,
                position_type=deal_request.position_type,
                amount_type=amount_type,
                quantity=order_quantity,
                including_charges=(True if deal_request.position_type == OrderPositionType.Buy else False)
            )

            order_quote = self.get_market_order_quote(order)
            self.__logger.debug(order_quote)

            self.__logger.debug("Confirm market-order ...")

            order_confirmation = self.execute_market_order(order_quote)
            self.__logger.debug(order_confirmation)

            return DealResult(deal_request, order_confirmation)

        # TODO -> what about market order which cannot be filled?
        except MarketClosedError as ex:
            if not (deal_request.allow_fill_or_kill and ex.can_place_fill_or_kill_order):
                raise ex

            self.__logger.debug("Get current position ...")
            current_position = self.get_manual_order_position(account_id=deal_request.account_id,
                                                              sedol_code=sedol_code,
                                                              category_code=category_code)
            self.__logger.debug(current_position.as_form_fields())

            self.__logger.debug("Calculate quantity ...")

            (amount_type, order_quantity) = PositionCalculator.calculate(
                position_type=deal_request.position_type,
                position_percentage=deal_request.position_percentage,
                account_value=account_value,
                units_held=current_position.remaining_units
            )

            self.__logger.debug(f"amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

            order = ManualOrder(
                position=current_position,
                position_type=deal_request.position_type,
                amount_type=amount_type,
                quantity=order_quantity,
                limit=None)

            # submit order
            order_confirmation = self.submit_manual_order(order)
            self.__logger.debug(order_confirmation)

            return DealResult(deal_request, order_confirmation)

    def logout(self):
        self.__logger.debug(f"Logging Out ...")
        return self.__authentication_client.logout()

    def stop_session(self, api_config: ApiConfiguration):
        self.__cookies_storage.save(self.__web_session.cookies)
        self.__request_session_storage.write(self.__request_session_context, api_config)

    def convert_HAR_to_markdown(self):
        exclude_patterns = Har2MdController.DEFAULT_EXCLUDE.split(',')
        input_file = Path(self.__request_session_storage.get_location())
        output_folder = Path.joinpath(input_file.parent, input_file.stem)

        har2md = Har2MdController(self.__logger)
        har2md.exec(str(input_file), str(output_folder), exclude_patterns)


class WebSessionManagerFactory:

    @staticmethod
    def create_with_file_storage(logger: Logger):
        time_service = TimeService(logger)

        # create local file-based cookies-storage
        cookies_file_path = PathHelper.get_project_root() \
            .joinpath('session_cache').joinpath('cookies.txt')
        cookies_storage = CookiesFileStorage(logger, cookies_file_path)

        # create local file-based session-history-writer
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
        requests_file_path = PathHelper.get_project_root() \
            .joinpath('session_cache').joinpath(f"session-{dt_string}.har")
        request_session_storage = RequestSessionFileStorage(logger, requests_file_path)

        return WebSessionManager(
            logger,
            time_service,
            cookies_storage,
            request_session_storage)
