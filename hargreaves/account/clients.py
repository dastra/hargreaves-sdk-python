import requests

from hargreaves.account.models import AccountSummary, AccountDetail
from hargreaves.account.parsers.parsers import parse_account_list, parse_account_detail
from hargreaves.utils.cookie_manager import set_cookies


def list_accounts(session: requests.Session) -> [requests.Session, list[AccountSummary]]:
    session = set_cookies(session)
    my_accounts_html = session.get("https://online.hl.co.uk/my-accounts").text

    return session, parse_account_list(my_accounts_html)


def get_account_detail(session: requests.Session, account_summary: AccountSummary) -> AccountDetail:
    session = set_cookies(session)
    # Fetching the account detail page
    session.get("https://online.hl.co.uk/my-accounts/account_summary/account/" + str(account_summary.account_id))
    # Fetching the account detail CSV
    account_detail_csv = session.get(
        'https://online.hl.co.uk/my-accounts/account_summary_csv/sort/stock/sortdir/asc').text

    return parse_account_detail(account_detail_csv, account_summary)
