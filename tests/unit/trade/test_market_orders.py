import http
import pytest
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.trade.market.clients import MarketOrderClient
from hargreaves.trade.market.models import MarketOrderQuote, MarketOrderConfirmation
from hargreaves.trade.market.parsers import parse_market_order_entry_page, parse_market_order_quote_page, \
    parse_market_order_confirmation_page
from hargreaves.utils.input import InputHelper
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession
from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.errors import MarketClosedError, DealFailedError


def test_parse_deal_page_uk_market_closed():
    deal_html = Path(Path(__file__).parent / 'files_market_orders/deal-page-uk-market-closed.html').read_text()

    with pytest.raises(MarketClosedError) as error:
        parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert error.value.can_place_fill_or_kill_order is True
    assert error.value.can_place_limit_order is True


def test_parse_deal_page_us_market_closed():
    deal_html = Path(Path(__file__).parent / 'files_market_orders/deal-page-us-market-closed.html').read_text()

    with pytest.raises(MarketClosedError) as error:
        parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert error.value.can_place_fill_or_kill_order is True
    assert error.value.can_place_limit_order is False


def test_parse_deal_page_market_open():
    deal_html = Path(Path(__file__).parent / 'files_market_orders/deal-page-uk-equity.html').read_text()

    market_order = parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert market_order.hl_vt == '459030661'
    assert market_order.stock_ticker == 'ANIC'
    assert market_order.security_name == 'Agronomics Limited'
    assert market_order.sedol_code == 'B6QH1J2'
    assert market_order.isin_code == 'IM00B6QH1J21'
    assert market_order.epic_code == 'ANIC'
    assert market_order.currency_code == 'GBP'
    assert market_order.exchange == 'L'
    assert not market_order.fixed_interest
    assert market_order.account_id == 70
    assert market_order.total_cash_available == 1275
    assert market_order.bid_price == '18.50p'
    assert market_order.units_held == 250
    assert market_order.value_gbp == 43.05


def test_parse_quote_buy_uk_equity_page_ok():
    quote_html = Path(Path(__file__).parent / 'files_market_orders/quote-page-buy-uk-equity.html').read_text()

    price_quote = parse_market_order_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.EQUITIES)

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
    quote_html = Path(Path(__file__).parent / 'files_market_orders/quote-page-buy-us-equity.html').read_text()

    price_quote = parse_market_order_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert price_quote.session_hl_vt == '1717986023'
    assert price_quote.hl_vt == '3806305716'
    assert price_quote.sedol_code == 'BDBFK59'
    assert price_quote.number_of_shares == 1.0
    assert price_quote.price == '$1.85'
    assert price_quote.share_value is None
    assert price_quote.ptm_levy is None
    assert price_quote.commission == 5.95
    assert price_quote.stamp_duty is None
    assert price_quote.settlement_date.strftime('%d/%m/%Y') == '18/03/2022'
    assert price_quote.total_trade_value == 7.37
    assert price_quote.exchange_rate == 0.7639
    assert price_quote.conversion_price == 1.4132
    assert price_quote.conversion_sub_total == 1.41
    assert price_quote.fx_charge == 0.01
    assert price_quote.category_code == InvestmentCategoryTypes.OVERSEAS


def test_parse_confirm_uk_equity_deal_page_ok():
    confirm_html = Path(Path(__file__).parent / 'files_market_orders/deal-confirmation-buy-uk-equity.html').read_text()

    order_confirmation = parse_market_order_confirmation_page(confirm_html=confirm_html,
                                                              category_code=InvestmentCategoryTypes.EQUITIES)

    assert order_confirmation.sedol_code == 'B6QH1J2'
    assert order_confirmation.number_of_shares == 479
    assert order_confirmation.price == '18.35p'
    assert order_confirmation.share_value == 87.90
    assert order_confirmation.ptm_levy == 1.25
    assert order_confirmation.commission == 11.95
    assert order_confirmation.stamp_duty == 5.20
    assert order_confirmation.settlement_date.strftime('%d/%m/%Y') == '26/01/2022'
    assert order_confirmation.total_trade_value == 99.85
    assert order_confirmation.exchange_rate is None
    assert order_confirmation.conversion_price is None
    assert order_confirmation.conversion_sub_total is None
    assert order_confirmation.fx_charge is None


def test_parse_confirm_us_equity_deal_page_ok():
    confirm_html = Path(Path(__file__).parent / 'files_market_orders/deal-confirmation-buy-us-equity.html').read_text()

    order_confirmation = parse_market_order_confirmation_page(confirm_html=confirm_html,
                                                              category_code=InvestmentCategoryTypes.OVERSEAS)

    assert order_confirmation.sedol_code == 'BDBFK59'
    assert order_confirmation.number_of_shares == 500
    assert order_confirmation.price == '£1.5202'
    assert order_confirmation.share_value == 760.1
    assert order_confirmation.ptm_levy is None
    assert order_confirmation.commission == 5.95
    assert order_confirmation.stamp_duty is None
    assert order_confirmation.settlement_date is None
    assert order_confirmation.total_trade_value == 773.65
    assert order_confirmation.exchange_rate == 0.7601
    assert order_confirmation.conversion_price == 1.5202
    assert order_confirmation.conversion_sub_total == 760.10
    assert order_confirmation.fx_charge == 7.60


def test_parse_confirm_equity_deal_failed():
    confirm_html = Path(Path(__file__).parent / 'files_market_orders/deal-failed-buy-uk-equity.html').read_text()

    with pytest.raises(DealFailedError, match=r"Unfortunately there has been an error in processing your transaction"):
        parse_market_order_confirmation_page(confirm_html=confirm_html, category_code=InvestmentCategoryTypes.EQUITIES)


def test_execute_market_buy_order_quote_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files_market_orders/deal-confirmation-buy-uk-equity.html').read_text()

    market_order_quote = MarketOrderQuote(
        session_hl_vt='3001668598',
        hl_vt='2181800191',
        sedol_code='B6QH1J2',
        number_of_shares=527,
        price='18.945p',
        share_value=99.84,
        ptm_levy=1.25,
        commission=11.95,
        stamp_duty=5.20,
        settlement_date=InputHelper.parse_date('26/01/2022'),
        total_trade_value=111.79,
        exchange_rate=None,
        conversion_price=None,
        conversion_sub_total=None,
        fx_charge=None,
        category_code=InvestmentCategoryTypes.EQUITIES
    )

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()

        expected_params = {
            'hl_vt': '2181800191',
            'sedol': 'B6QH1J2'
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/equity_confirmation',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{market_order_quote.sedol_code}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )
        client = MarketOrderClient(logger, web_session)
        order_confirmation = client.execute_market_order(market_order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
