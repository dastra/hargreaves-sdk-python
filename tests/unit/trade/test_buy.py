import re
from datetime import datetime

import pytest
import requests
import requests_mock

from pathlib import Path

from hargreaves.trade.errors import MarketClosedError, DealFailedError
from hargreaves.trade.clients import parse_deal_page, parse_buy_quote_page, parse_confirm_equity_deal_page, \
    session_keepalive
from hargreaves.trade.models import PriceQuote


def test_parse_deal_page_market_closed():
    deal_html = Path(Path(__file__).parent / 'files/deal-page-market-closed.html').read_text()

    with pytest.raises(MarketClosedError):
        parse_deal_page(deal_html)


def test_parse_deal_page_market_open():
    deal_html = Path(Path(__file__).parent / 'files/deal-page-uk-equity.html').read_text()

    deal_info = parse_deal_page(deal_html)

    assert deal_info.hl_vt == '459030661'
    assert deal_info.stock_ticker == 'ANIC'
    assert deal_info.security_name == 'Agronomics Limited'
    assert deal_info.sedol_code == 'B6QH1J2'
    assert deal_info.isin_code == 'IM00B6QH1J21'
    assert deal_info.epic_code == 'ANIC'
    assert deal_info.currency_code == 'GBP'
    assert deal_info.exchange == 'L'
    assert not deal_info.fixed_interest
    assert deal_info.account_id == 70
    assert deal_info.total_cash_available == 1275
    assert deal_info.bid_price == '18.50p'
    assert deal_info.units_held == 250
    assert deal_info.value_gbp == 43.05


def test_parse_quote_page_ok():
    quote_html = Path(Path(__file__).parent / 'files/quote-page-buy-uk-equity.html').read_text()

    price_quote = parse_buy_quote_page(quote_html)

    assert price_quote.session_hl_vt == '3001668598'
    assert price_quote.hl_vt == '2181800191'
    assert price_quote.sedol_code == 'B6QH1J2'
    assert price_quote.number_of_shares == 527
    assert price_quote.price == '18.945p'
    assert price_quote.share_value == 99.84
    assert price_quote.ptm_levy == 1.25
    assert price_quote.commission == 11.95
    assert price_quote.stamp_duty == 5.20
    assert price_quote.settlement_date.strftime('%d/%m/%Y') == '26/01/2022'
    assert price_quote.total_trade_value == 111.79


def test_parse_confirm_equity_deal_page_ok():
    confirm_html = Path(Path(__file__).parent / 'files/deal-confirmation-buy-uk-equity.html').read_text()

    deal_confirmation = parse_confirm_equity_deal_page(confirm_html)

    assert deal_confirmation.sedol_code == 'B6QH1J2'
    assert deal_confirmation.number_of_shares == 479
    assert deal_confirmation.price == '18.35p'
    assert deal_confirmation.share_value == 87.90
    assert deal_confirmation.ptm_levy == 1.25
    assert deal_confirmation.commission == 11.95
    assert deal_confirmation.stamp_duty == 5.20
    assert deal_confirmation.settlement_date.strftime('%d/%m/%Y') == '26/01/2022'
    assert deal_confirmation.total_trade_value == 99.85


def test_parse_confirm_equity_deal_failed():
    confirm_html = Path(Path(__file__).parent / 'files/deal-failed-buy-uk-equity.html').read_text()

    with pytest.raises(DealFailedError, match=r"Unfortunately there has been an error in processing your transaction"):
        parse_confirm_equity_deal_page(confirm_html)


def test_session_keepalive():
    session = requests.Session()
    price_quote = PriceQuote(session_hl_vt='460029272', hl_vt='1128180370', sedol_code='A12345', number_of_shares=100,
                             price='28.85p', share_value=88.05, ptm_levy=1.00, commission=10.95, stamp_duty=0,
                             settlement_date=datetime.strptime('Jan 2 2022', '%b %d %Y'), total_trade_value=100.00)

    with requests_mock.Mocker() as mock_request:
        matcher = re.compile(f'^https://online.hl.co.uk/ajaxx/user.php\\?method=session_timeout_handler&keepalive=1&'
                             'format=jsonp&jsoncallback=jsonp\\d{13}&hl_vt=460029272&initialise=true$')
        mock_request.get(matcher, text='session_timeout_handler(["keptalive"])')

        session_keepalive(session, price_quote)
