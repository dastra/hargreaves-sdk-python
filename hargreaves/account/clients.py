import logging
from typing import List

from ..account.models import AccountSummary, AccountDetail
from ..account.parsers.parsers import parse_account_list, parse_account_detail
from requests_tracker.session import IWebSession

logger = logging.getLogger(__name__)


class IAccountClient:

    def get_account_summary(self, web_session: IWebSession) -> List[AccountSummary]:
        pass

    def get_account_detail(self, web_session: IWebSession, account_summary: AccountSummary) -> AccountDetail:
        pass


class AccountClient(IAccountClient):

    def __init__(self):
        pass

    def get_account_summary(self, web_session: IWebSession) -> List[AccountSummary]:
        logger.debug("Get account summary ...")
        response = web_session.get('https://online.hl.co.uk/my-accounts')
        return parse_account_list(response.text)

    def get_account_detail(self, web_session: IWebSession, account_summary: AccountSummary) -> AccountDetail:
        account_id = account_summary.account_id
        logger.debug(f"Get account ({account_id}) detail page ...")

        account_detail_html = web_session.get(
            f"https://online.hl.co.uk/my-accounts/account_summary/account/{account_summary.account_id}").text

        logger.debug(f"Get account ({account_id}) detail CSV ...")
        csv_response = web_session.get(
            'https://online.hl.co.uk/my-accounts/account_summary_csv/sort/stock/sortdir/asc')

        csv_response.encoding = 'utf-8'  # avoids the 'DEBUG:chardet.charsetprobe' messages from csv reader
        account_detail_csv = csv_response.text

        return parse_account_detail(account_detail_html, account_detail_csv, account_summary)
