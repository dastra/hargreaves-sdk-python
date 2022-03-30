import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.mocks import MockSessionClient
from hargreaves.orders.market.clients import MarketOrderClient
from hargreaves.orders.market.models import MarketOrderQuote, MarketOrderConfirmation
from hargreaves.orders.market.parsers import parse_market_order_quote_page
from hargreaves.utils import clock
from hargreaves.utils.input import InputHelper
from hargreaves.utils.logs import LogHelper
from requests_tracker.mocks import MockWebSession

LogHelper.configure_std_out()
clock.freeze_time()


def test_parse_market_sell_order_quote_uk_equity():
    quote_html = Path(Path(__file__).parent / 'files/sell/market-sell-order-quote-uk-equity.html').read_text()

    price_quote = parse_market_order_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert price_quote.session_hl_vt == '3089455817'
    assert price_quote.hl_vt == '2422340661'
    assert price_quote.sedol_code == 'B1JQBT1'
    assert price_quote.number_of_shares == 100.0
    assert price_quote.price == '25.9504p'
    assert price_quote.share_value == 25.95
    assert price_quote.ptm_levy == 0.0
    assert price_quote.commission == 5.95
    assert price_quote.stamp_duty == 0.0
    assert price_quote.settlement_date.strftime('%d/%m/%Y') == '23/03/2022'
    assert price_quote.total_trade_value == 20.0
    assert price_quote.exchange_rate is None
    assert price_quote.conversion_price is None
    assert price_quote.conversion_sub_total is None
    assert price_quote.fx_charge is None
    assert price_quote.category_code == InvestmentCategoryTypes.EQUITIES


def test_parse_market_sell_order_quote_us_equity():
    quote_html = Path(Path(__file__).parent / 'files/sell/market-sell-order-quote-us-equity.html').read_text()

    price_quote = parse_market_order_quote_page(quote_html=quote_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert price_quote.session_hl_vt == '3164992251'
    assert price_quote.hl_vt == '4288007232'
    assert price_quote.sedol_code == 'BDBFK59'
    assert price_quote.number_of_shares == 100.0
    assert price_quote.price == '$2.02'
    assert price_quote.share_value is None
    assert price_quote.ptm_levy is None
    assert price_quote.commission == 5.95
    assert price_quote.stamp_duty is None
    assert price_quote.settlement_date.strftime('%d/%m/%Y') == '23/03/2022'
    assert price_quote.total_trade_value == 145.57
    assert price_quote.exchange_rate == 0.7577
    assert price_quote.conversion_price == 1.5305
    assert price_quote.conversion_sub_total == 153.05
    assert price_quote.fx_charge == 1.53
    assert price_quote.category_code == InvestmentCategoryTypes.OVERSEAS


def test_execute_market_sell_order_confirmation_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files/sell/market-sell-order-confirmation-uk-equity.html'). \
        read_text()

    market_order_quote = MarketOrderQuote(
        session_hl_vt='3089455817',
        hl_vt='2422340661',
        sedol_code='B1JQBT1',
        number_of_shares=110.00,
        price='25.9504p',
        share_value=25.95,
        ptm_levy=0.00,
        commission=5.95,
        stamp_duty=0.0,
        settlement_date=InputHelper.parse_date('23/03/2022'),
        total_trade_value=20.0,
        exchange_rate=None,
        conversion_price=None,
        conversion_sub_total=None,
        fx_charge=None,
        category_code=InvestmentCategoryTypes.EQUITIES
    )

    with MockWebSession() as web_session:

        expected_params = {
            'hl_vt': '2422340661',
            'sedol': 'B1JQBT1'
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/equity_confirmation',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{market_order_quote.sedol_code}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )

        session_client = MockSessionClient()
        client = MarketOrderClient(session_client)

        order_confirmation = client.submit_order(web_session=web_session, order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
        assert session_client.was_called is True


def test_execute_market_sell_order_confirmation_uk_equity_2():
    confirm_html = Path(Path(__file__).parent / 'files/sell/market-sell-order-confirmation-uk-equity-2.html'). \
        read_text()

    market_order_quote = MarketOrderQuote(
        session_hl_vt='3089455817',
        hl_vt='2422340661',
        sedol_code='B1JQBT1',
        number_of_shares=110.00,
        price='25.9504p',
        share_value=25.95,
        ptm_levy=0.00,
        commission=5.95,
        stamp_duty=0.0,
        settlement_date=InputHelper.parse_date('23/03/2022'),
        total_trade_value=20.0,
        exchange_rate=None,
        conversion_price=None,
        conversion_sub_total=None,
        fx_charge=None,
        category_code=InvestmentCategoryTypes.EQUITIES
    )

    with MockWebSession() as web_session:

        expected_params = {
            'hl_vt': '2422340661',
            'sedol': 'B1JQBT1'
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/equity_confirmation',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{market_order_quote.sedol_code}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )

        session_client = MockSessionClient()
        client = MarketOrderClient(session_client)

        order_confirmation = client.submit_order(web_session=web_session, order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
        assert session_client.was_called is True


def test_execute_market_sell_order_confirmation_us_equity():
    confirm_html = Path(Path(__file__).parent / 'files/sell/market-sell-order-confirmation-us-equity.html'). \
        read_text()

    market_order_quote = MarketOrderQuote(
        session_hl_vt='3164992251',
        hl_vt='4288007232',
        sedol_code='BDBFK59',
        number_of_shares=110.00,
        price='$2.02',
        share_value=None,
        ptm_levy=None,
        commission=5.95,
        stamp_duty=None,
        settlement_date=InputHelper.parse_date('23/03/2022'),
        total_trade_value=145.57,
        exchange_rate=0.7577,
        conversion_price=1.5305,
        conversion_sub_total=153.05,
        fx_charge=1.53,
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    with MockWebSession() as web_session:

        expected_params = {
            'hl_vt': '4288007232',
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

        session_client = MockSessionClient()
        client = MarketOrderClient(session_client)

        order_confirmation = client.submit_order(web_session=web_session, order_quote=market_order_quote)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == MarketOrderConfirmation
        assert session_client.was_called is True
