from pathlib import Path
import pytest

from hargreaves.account.clients import *


def test_parse_account_list():
    my_accounts_html = Path(Path(__file__).parent / 'files/my-accounts.html').read_text()

    accounts = parse_account_list(my_accounts_html)

    assert len(accounts) == 4
    isa = accounts[0]
    assert isa.account_id == 22
    assert isa.account_type == 'Stocks & Shares ISA'


def test_parse_account_list_failed():
    with pytest.raises(ValueError, match=r"^List of accounts not present in response$"):
        parse_account_list('<html></html>')


def test_parse_account_detail():
    account_summary_html = Path(Path(__file__).parent / 'files/account-summary.html').read_text()
    account_summary_csv = Path(Path(__file__).parent / 'files/account-summary.csv').read_text()
    account_summary = AccountSummary(account_id=55, account_type="SIPP")
    account_detail = parse_account_detail(account_summary_html, account_summary_csv, account_summary)

    assert account_detail.account_id == account_summary.account_id
    assert account_detail.account_type == account_summary.account_type
    assert account_detail.stock_value == 7454.33
    assert account_detail.total_cash == 1925.44
    assert account_detail.amount_available == 1900.44
    assert account_detail.total_value == 9379.77

    assert len(account_detail.investments) == 3
    goog = account_detail.investments[0]
    assert goog.stock_ticker == 'GOOGL'
    assert goog.security_name == 'Alphabet Inc NPV A *R'
    assert goog.sedol_code == 'BYVY8G0'
    assert goog.units_held == 5
    assert goog.price_pence == 2226.73
    assert goog.value_gbp == 111.34
    assert goog.cost_gbp == 75.5
    assert goog.gain_loss_gbp == 35.84
    assert goog.gain_loss_percentage == 47.47
