import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.manual.clients import ManualOrderClient
from hargreaves.trade.manual.models import ManualOrder, ManualOrderConfirmation, ManualOrderPosition
from hargreaves.trade.manual.parsers import parse_manual_order_confirmation_page
from hargreaves.trade.models import OrderPositionType, OrderAmountType
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession


def test_parse_manual_sell_order_confirmation_uk_equity_ok():
    confirm_html = Path(Path(__file__).parent / 'files/sell/manual-sell-order-confirmation-uk-equity.html') \
        .read_text()

    order_confirmation = parse_manual_order_confirmation_page(confirm_html=confirm_html)

    assert order_confirmation.order_date.strftime('%d/%m/%Y') == '21/03/2022'
    assert order_confirmation.stock_code == 'PDG'
    assert order_confirmation.quantity == 100.0
    assert order_confirmation.order_type == 'Sell'
    assert order_confirmation.limit_price is None
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
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    order = ManualOrder(
        position=current_position,
        position_type=OrderPositionType.Sell,
        amount_type=OrderAmountType.Quantity,
        quantity=100,
        limit=None,
        earmark_orders_confirm=False)

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()

        expected_params = {
            'hl_vt': "1601575001",
            'type': "equity",
            'out_of_hours': "1",
            'sedol': "B1JQBT1",
            'product_no': "70",
            'available': "179681.27",
            'holding': "300",
            'holding_value': "77.40",
            'transfer_units': "0.0000",
            'remaining_units': "300",
            'remaining_units_value': "77.40",
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
            url='https://online.hl.co.uk/my-accounts/manual_deal_overseas',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )
        client = ManualOrderClient(logger, web_session)
        order_confirmation = client.submit_order(order=order)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == ManualOrderConfirmation
