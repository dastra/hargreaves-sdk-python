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
from hargreaves.search.clients import SecuritySearchClient
from hargreaves.trade.clients import TradeClient
from hargreaves.trade.models import Deal, PriceQuote
from hargreaves.utils.paths import PathHelper
from hargreaves.utils.timings import ITimeService, TimeService
from hargreaves.web.cookies import HLCookieHelper
from hargreaves.web.headers import HeaderFactory
from hargreaves.web.session import WebSession, RequestSessionContext
from hargreaves.web.storage import ICookieStorage, IRequestSessionStorage


class WebSessionManager:
    __logger: Logger
    __time_service: ITimeService
    __cookies_storage: ICookieStorage
    __request_session_storage: IRequestSessionStorage

    __web_session: WebSession
    __logged_in_session: LoggedInSession
    __request_session_context: RequestSessionContext
    __api_config: ApiConfiguration

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
        self.__api_config = api_config

        self.__request_session_context = RequestSessionContext()
        session = requests.Session()

        self.__cookies_storage.load(session)

        header_factory = HeaderFactory.create(self.__request_session_context)
        self.__web_session = WebSession(self.__logger, session, self.__request_session_context, header_factory)

        self.__logger.debug(f"Set Default Cookies...")
        HLCookieHelper.set_default_cookies(self.__web_session.cookies)

        self.__logged_in_session = LoggedInSession(self.__logger, self.__web_session, api_config)

    def get_account_summary(self) -> List[AccountSummary]:
        client = AccountClient(self.__logger, self.__logged_in_session)
        return client.get_account_summary()

    def get_account_detail(self, account_summary: AccountSummary) -> AccountDetail:
        client = AccountClient(self.__logger, self.__logged_in_session)
        return client.get_account_detail(account_summary)

    def search_security(self, search_string: str, investment_types: list):
        self.__time_service.sleep()
        client = SecuritySearchClient(self.__logger, self.__web_session, self.__time_service)
        return client.investment_search(search_string, investment_types)

    def get_security_price(self, account_id: int, sedol_code: str, category_code: str):
        self.__time_service.sleep()
        client = TradeClient(self.__logger, self.__logged_in_session, self.__time_service)
        return client.get_security_price(account_id=account_id,
                                         sedol_code=sedol_code, category_code=category_code)

    def get_quote(self, order: Deal):
        self.__time_service.sleep()
        client = TradeClient(self.__logger, self.__logged_in_session, self.__time_service)
        return client.get_quote(order)

    def execute_deal(self, price_quote: PriceQuote):
        self.__time_service.sleep(min=2, max=4)
        self.__logger.debug(f"execute_deal: OK, lets confirm ...")
        client = TradeClient(self.__logger, self.__logged_in_session, self.__time_service)
        return client.execute_deal(price_quote)

    def logout(self):
        client = AuthenticationClient(self.__logger, self.__time_service, self.__web_session)
        return client.logout()

    def stop_session(self):
        self.__cookies_storage.save(self.__web_session.cookies)
        self.__request_session_storage.write(self.__request_session_context, self.__api_config)

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
