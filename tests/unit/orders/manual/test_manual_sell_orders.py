import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.mocks import MockSessionClient
from hargreaves.orders.manual.clients import ManualOrderClient
from hargreaves.orders.manual.models import ManualOrder, ManualOrderConfirmation, ManualOrderPosition
from hargreaves.orders.manual.parsers import parse_manual_order_confirmation_page
from hargreaves.orders.models import OrderPositionType, OrderAmountType
from hargreaves.utils import clock
from hargreaves.utils.logs import LogHelper
from requests_tracker.mocks import MockWebSession

LogHelper.configure_std_out()
clock.freeze_time()


def test_parse_manual_sell_order_confirmation_uk_equity_ok():
    confirm_html = Path(Path(__file__).parent / 'files/sell/manual-sell-order-confirmation-uk-equity.html') \
        .read_text()

    order_confirmation = parse_manual_order_confirmation_page(confirm_html=confirm_html,
                                                              amount_type=OrderAmountType.Quantity)

    assert order_confirmation.order_date.strftime('%d/%m/%Y') == '21/03/2022'
    assert order_confirmation.stock_code == 'PDG'
    assert order_confirmation.quantity == 100.0
    assert order_confirmation.order_type == 'Sell'
    assert order_confirmation.limit_price is None
    assert order_confirmation.order_status == 'Pending'


def test_parse_manual_sell_order_confirmation_us_equity_ok():
    confirm_html = Path(Path(__file__).parent / 'files/sell/manual-sell-order-confirmation-us-equity.html') \
        .read_text()

    order_confirmation = parse_manual_order_confirmation_page(confirm_html=confirm_html,
                                                              amount_type=OrderAmountType.Quantity)

    assert order_confirmation.order_date.strftime('%d/%m/%Y') == '23/03/2022'
    assert order_confirmation.stock_code == 'TUSK'
    assert order_confirmation.quantity == 500.0
    assert order_confirmation.order_type == 'Sell'
    assert order_confirmation.limit_price == 1.9
    assert order_confirmation.order_status == 'Pending'


def test_submit_manual_sell_order_confirmation_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files/sell/manual-sell-order-confirmation-uk-equity.html') \
        .read_text()

    current_position = ManualOrderPosition(
        hl_vt="1601575001",
        security_type="equity",
        out_of_hours=True,
        sedol="B1JQBT1",
        account_id=70,
        available=179681.27,
        holding=300,
        holding_value=77.40,
        transfer_units=0,
        remaining_units=300,
        remaining_units_value=77.40,
        isin="GB00B1JQBT10",
        epic="",
        currency_code="GBX",
        SD_Bid=0.00,
        SD_Ask=0.00,
        fixed_interest=False,
        category_code=InvestmentCategoryTypes.EQUITIES
    )

    order = ManualOrder(
        position=current_position,
        position_type=OrderPositionType.Sell,
        amount_type=OrderAmountType.Quantity,
        quantity=100,
        limit=None,
        earmark_orders_confirm=False)

    with MockWebSession() as web_session:

        expected_params = {
            'hl_vt': "1601575001",
            'type': "equity",
            'out_of_hours': "1",
            'sedol': "B1JQBT1",
            'product_no': "70",
            'available': "179681.27",
            'holding': "300",
            'holding_value': "77.4",
            'transfer_units': "0.0000",
            'remaining_units': "300",
            'remaining_units_value': "77.4",
            'isin': "GB00B1JQBT10",
            'epic': "",
            'currency_code': "GBX",
            'SD_Bid': "0.00",
            'SD_Ask': "0.00",
            'fixed_interest': "0",
            'bs': "Sell",
            'quantity': "100",
            'qs': "quantity",
            'limit': "",
            'earmark_orders_confirm': "false",
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/manual_deal',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )
        session_client = MockSessionClient()
        client = ManualOrderClient(session_client)

        order_confirmation = client.submit_order(web_session=web_session, order=order)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == ManualOrderConfirmation
        assert session_client.was_called is True


def test_submit_manual_sell_order_confirmation_us_equity():
    confirm_html = Path(Path(__file__).parent / 'files/sell/manual-sell-order-confirmation-us-equity.html') \
        .read_text()

    current_position = ManualOrderPosition(
        hl_vt="1496180636",
        security_type="equity",
        out_of_hours=True,
        sedol="BDBFK59",
        account_id=70,
        available=164629.62,
        holding=7635,
        holding_value=11093.562582535,
        transfer_units=0,
        remaining_units=7635,
        remaining_units_value=11093.562582535,
        isin="US56155L1089",
        epic="",
        currency_code="USD",
        SD_Bid=0.00,
        SD_Ask=0.00,
        fixed_interest=False,
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    order = ManualOrder(
        position=current_position,
        position_type=OrderPositionType.Sell,
        amount_type=OrderAmountType.Value,
        quantity=500,
        limit=1.9,
        earmark_orders_confirm=False)

    with MockWebSession() as web_session:

        expected_params = {
            'hl_vt': "1496180636",
            'type': "equity",
            'out_of_hours': "1",
            'sedol': "BDBFK59",
            'product_no': "70",
            'available': "164629.62",
            'holding': "7635",
            'holding_value': "11093.562582535",
            'transfer_units': "0.0000",
            'remaining_units': "7635",
            'remaining_units_value': "11093.562582535",
            'isin': "US56155L1089",
            'epic': "",
            'currency_code': "USD",
            'SD_Bid': "0.00",
            'SD_Ask': "0.00",
            'fixed_interest': "0",
            'bs': "Sell",
            'quantity': "500",
            'qs': "value",
            'limit': "1.9",
            'earmark_orders_confirm': "false",
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/manual_deal_overseas',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )

        session_client = MockSessionClient()
        client = ManualOrderClient(session_client)

        order_confirmation = client.submit_order(web_session=web_session, order=order)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == ManualOrderConfirmation
        assert session_client.was_called is True
