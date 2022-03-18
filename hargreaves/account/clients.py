from logging import Logger
from typing import List

from hargreaves.account.models import AccountSummary, AccountDetail
from hargreaves.account.parsers.parsers import parse_account_list, parse_account_detail
from hargreaves.web.session import IWebSession


class AccountClient:
    __logger: Logger
    __web_session: IWebSession

    def __init__(self,
                 logger: Logger,
                 web_session: IWebSession
                 ):
        self.__logger = logger
        self.__web_session = web_session

    def get_account_summary(self) -> List[AccountSummary]:
        response = self.__web_session.get('https://online.hl.co.uk/my-accounts')
        return parse_account_list(response.text)

    def get_account_detail(self, account_summary: AccountSummary) -> AccountDetail:
        account_id = account_summary.account_id
        self.__logger.debug(f"Fetching the account detail page for account '{account_id}' ...")
        account_detail_html = self.__web_session.get(
            f"https://online.hl.co.uk/my-accounts/account_summary/account/{account_summary.account_id}").text

        self.__logger.debug(f"Fetching the account detail CSV for account '{account_id}' ...")
        csv_response = self.__web_session.get(
            'https://online.hl.co.uk/my-accounts/account_summary_csv/sort/stock/sortdir/asc')

        csv_response.encoding = 'utf-8'  # avoids the 'DEBUG:chardet.charsetprobe' messages from csv reader
        account_detail_csv = csv_response.text

        return parse_account_detail(account_detail_html, account_detail_csv, account_summary)
