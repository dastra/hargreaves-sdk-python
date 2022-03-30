import logging
from typing import List

from .clients import AccountClient
from .models import AccountType, AccountSummary, AccountDetail
from requests_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_account_summary(web_session: IWebSession) -> List[AccountSummary]:
    return AccountClient().get_account_summary(web_session=web_session)


def get_account_detail(web_session: IWebSession, account_summary: AccountSummary) -> AccountDetail:
    return AccountClient().get_account_detail(
        web_session=web_session,
        account_summary=account_summary)
