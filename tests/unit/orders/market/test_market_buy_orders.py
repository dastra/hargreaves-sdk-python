import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.mocks import MockSessionClient
from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.orders.market.models import MarketOrderQuote, MarketOrderConfirmation
from hargreaves.orders.market.parsers import parse_market_order_quote_page, \
    parse_market_order_confirmation_page
from hargreaves.utils.input import InputHelper
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession, MockTimeService


def test_parse_market_buy_order_entry_us_equity():
    quote_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-quote-uk-equity.html').read_text()

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


def test_parse_market_buy_order_quote_us_equity():
    quote_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-quote-us-equity.html').read_text()

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


def test_parse_market_buy_order_confirmation_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-confirmation-uk-equity.html')\
        .read_text()

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


def test_parse_market_buy_order_confirmation_us_equity():
    confirm_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-confirmation-us-equity.html')\
        .read_text()

    order_confirmation = parse_market_order_confirmation_page(confirm_html=confirm_html,
                                                              category_code=InvestmentCategoryTypes.OVERSEAS)

    assert order_confirmation.sedol_code == 'BDBFK59'
    assert order_confirmation.number_of_shares == 1450
    assert order_confirmation.price == '£1.4762'
    assert order_confirmation.share_value == 2140.49
    assert order_confirmation.ptm_levy is None
    assert order_confirmation.commission == 5.95
    assert order_confirmation.stamp_duty is None
    assert order_confirmation.settlement_date is None
    assert order_confirmation.total_trade_value == 2.0
    assert order_confirmation.exchange_rate == 0.757
    assert order_confirmation.conversion_price == 1.4762
    assert order_confirmation.conversion_sub_total == 140.49
    assert order_confirmation.fx_charge == 21.4


def test_execute_market_buy_order_confirmation_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-confirmation-uk-equity.html').\
        read_text()

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
        LoggerFactory.configure_std_out()

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
        time_service = MockTimeService()
        session_client = MockSessionClient()
        client = MarketOrderClient(time_service, web_session, session_client)

        order_confirmation = client.execute_order(market_order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
        assert session_client.was_called is True


def test_execute_market_buy_order_confirmation_us_equity():
    confirm_html = Path(Path(__file__).parent / 'files/buy/market-buy-order-confirmation-us-equity.html'). \
        read_text()

    market_order_quote = MarketOrderQuote(
        session_hl_vt='1717986023',
        hl_vt='3806305716',
        sedol_code='BDBFK59',
        number_of_shares=1450,
        price='$1.93',
        share_value=None,
        ptm_levy=None,
        commission=5.95,
        stamp_duty=None,
        settlement_date=InputHelper.parse_date('23/03/2022'),
        total_trade_value=7.37,
        exchange_rate=0.757,
        conversion_price=1.4132,
        conversion_sub_total=2140.49,
        fx_charge=21.40,
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    with MockWebSession() as web_session:
        LoggerFactory.configure_std_out()

        expected_params = {
            'hl_vt': '3806305716',
            'sedol': 'BDBFK59'
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/equity_confirmation_overseas',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{market_order_quote.sedol_code}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )
        time_service = MockTimeService()
        session_client = MockSessionClient()
        client = MarketOrderClient(time_service, web_session, session_client)

        order_confirmation = client.execute_order(market_order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
        assert session_client.was_called is True
