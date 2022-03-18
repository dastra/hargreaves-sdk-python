import http
from pathlib import Path

import pytest

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.clients import parse_deal_page, parse_buy_quote_page, parse_confirm_equity_deal_page, TradeClient
from hargreaves.trade.errors import MarketClosedError, DealFailedError
from hargreaves.utils.logging import LoggerFactory
from hargreaves.utils.timings import MockTimeService
from hargreaves.web.mocks import MockWebSession


def test_parse_deal_page_market_closed():
    deal_html = Path(Path(__file__).parent / 'files/deal-page-market-closed.html').read_text()

    with pytest.raises(MarketClosedError):
        parse_deal_page(deal_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)


def test_parse_deal_page_market_open():
    deal_html = Path(Path(__file__).parent / 'files/deal-page-uk-equity.html').read_text()

    deal_info = parse_deal_page(deal_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)

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


def test_parse_quote_buy_uk_equity_page_ok():
    quote_html = Path(Path(__file__).parent / 'files/quote-page-buy-uk-equity.html').read_text()

    price_quote = parse_buy_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.EQUITIES)

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
    assert price_quote.exchange_rate is None
    assert price_quote.conversion_price is None
    assert price_quote.conversion_sub_total is None
    assert price_quote.fx_charge is None
    assert price_quote.category_code == InvestmentCategoryTypes.EQUITIES


def test_parse_quote_buy_us_equity_page_ok():
    quote_html = Path(Path(__file__).parent / 'files/quote-page-buy-us-equity.html').read_text()

    price_quote = parse_buy_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert price_quote.session_hl_vt == '1717986023'
    assert price_quote.hl_vt == '3806305716'
    assert price_quote.sedol_code == 'BDBFK59'
    assert price_quote.number_of_shares == 1.0
    assert price_quote.price == '$1.85'
    assert price_quote.share_value == None
    assert price_quote.ptm_levy == None
    assert price_quote.commission == 5.95
    assert price_quote.stamp_duty == None
    assert price_quote.settlement_date.strftime('%d/%m/%Y') == '18/03/2022'
    assert price_quote.total_trade_value == 7.37
    assert price_quote.exchange_rate == 0.7639
    assert price_quote.conversion_price == 1.4132
    assert price_quote.conversion_sub_total == 1.41
    assert price_quote.fx_charge == 0.01
    assert price_quote.category_code == InvestmentCategoryTypes.OVERSEAS


def test_parse_confirm_uk_equity_deal_page_ok():
    confirm_html = Path(Path(__file__).parent / 'files/deal-confirmation-buy-uk-equity.html').read_text()

    deal_confirmation = parse_confirm_equity_deal_page(confirm_html=confirm_html,
                                                       category_code=InvestmentCategoryTypes.EQUITIES)

    assert deal_confirmation.sedol_code == 'B6QH1J2'
    assert deal_confirmation.number_of_shares == 479
    assert deal_confirmation.price == '18.35p'
    assert deal_confirmation.share_value == 87.90
    assert deal_confirmation.ptm_levy == 1.25
    assert deal_confirmation.commission == 11.95
    assert deal_confirmation.stamp_duty == 5.20
    assert deal_confirmation.settlement_date.strftime('%d/%m/%Y') == '26/01/2022'
    assert deal_confirmation.total_trade_value == 99.85
    assert deal_confirmation.exchange_rate is None
    assert deal_confirmation.conversion_price is None
    assert deal_confirmation.conversion_sub_total is None
    assert deal_confirmation.fx_charge is None


def test_parse_confirm_us_equity_deal_page_ok():
    confirm_html = Path(Path(__file__).parent / 'files/deal-confirmation-buy-us-equity.html').read_text()

    deal_confirmation = parse_confirm_equity_deal_page(confirm_html=confirm_html,
                                                       category_code=InvestmentCategoryTypes.OVERSEAS)

    assert deal_confirmation.sedol_code == 'BDBFK59'
    assert deal_confirmation.number_of_shares == 500
    assert deal_confirmation.price == '£1.5202'
    assert deal_confirmation.share_value == 760.1
    assert deal_confirmation.ptm_levy is None
    assert deal_confirmation.commission == 5.95
    assert deal_confirmation.stamp_duty is None
    assert deal_confirmation.settlement_date is None
    assert deal_confirmation.total_trade_value == 773.65
    assert deal_confirmation.exchange_rate == 0.7601
    assert deal_confirmation.conversion_price == 1.5202
    assert deal_confirmation.conversion_sub_total == 760.10
    assert deal_confirmation.fx_charge == 7.60


def test_parse_confirm_equity_deal_failed():
    confirm_html = Path(Path(__file__).parent / 'files/deal-failed-buy-uk-equity.html').read_text()

    with pytest.raises(DealFailedError, match=r"Unfortunately there has been an error in processing your transaction"):
        parse_confirm_equity_deal_page(confirm_html=confirm_html, category_code=InvestmentCategoryTypes.EQUITIES)


def test_session_keepalive():

    sedol_code = 'A12345'
    session_hl_vt='460029272'

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()
        time_service = MockTimeService()

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/user.php',
            params={
                'method': 'session_timeout_handler',
                'keepalive': "1",
                'format': 'jsonp',
                'jsoncallback': f"jsonp{time_service.get_current_time_as_epoch_time()}",
                'hl_vt': session_hl_vt,
                'initialise': 'true'
            },
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
            },
            text='session_timeout_handler(["keptalive"])',
            status_code=http.HTTPStatus.OK
        )

        client = TradeClient(logger, web_session, time_service)
        client.session_keepalive(sedol_code, session_hl_vt)
