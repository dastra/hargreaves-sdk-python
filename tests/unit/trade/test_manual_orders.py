import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.trade.manual.clients import ManualOrderClient
from hargreaves.trade.manual.models import ManualOrder, ManualBuyOrder, ManualOrderConfirmation
from hargreaves.trade.manual.parsers import parse_manual_order_entry_page, parse_manual_order_confirmation_page
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession
from hargreaves.search.models import InvestmentCategoryTypes


def test_parse_manual_buy_order_entry_uk_equity_ok():
    order_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-entry-uk-equity.html').read_text()

    order_info = parse_manual_order_entry_page(order_html=order_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert order_info.hl_vt == "2491884284"
    assert order_info.type == "equity"
    assert order_info.out_of_hours is True
    assert order_info.sedol == "3092725"
    assert order_info.product_no == 70
    assert order_info.available == 179515.7
    assert order_info.holding == 0
    assert order_info.holding_value == 0
    assert order_info.transfer_units is None
    assert order_info.remaining_units == 0
    assert order_info.remaining_units_value == 0
    assert order_info.isin == "GB0030927254"
    assert order_info.epic == ""
    assert order_info.currency_code == "GBX"
    assert order_info.SD_Bid == 0.00
    assert order_info.SD_Ask == 0.00
    assert order_info.fixed_interest is False
    assert order_info.category_code == InvestmentCategoryTypes.EQUITIES


def test_parse_manual_buy_order_entry_us_equity_ok():
    order_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-entry-us-equity.html').read_text()

    order_info = parse_manual_order_entry_page(order_html=order_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert order_info.hl_vt == "3430162972"
    assert order_info.type == "equity"
    assert order_info.out_of_hours is True
    assert order_info.sedol == "BLR7B52"
    assert order_info.product_no == 70
    assert order_info.available == 177721.1
    assert order_info.holding == 0
    assert order_info.holding_value == 0
    assert order_info.transfer_units is None
    assert order_info.remaining_units == 0
    assert order_info.remaining_units_value == 0
    assert order_info.isin == "US5657881067"
    assert order_info.epic == ""
    assert order_info.currency_code == "USD"
    assert order_info.SD_Bid == 0.00
    assert order_info.SD_Ask == 0.00
    assert order_info.fixed_interest is False
    assert order_info.category_code == InvestmentCategoryTypes.OVERSEAS


def test_parse_manual_buy_order_confirmation_uk_equity_ok():
    confirm_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-confirmation-uk-equity.html').read_text()

    order_confirmation = parse_manual_order_confirmation_page(confirm_html=confirm_html)

    assert order_confirmation.order_date.strftime('%d/%m/%Y') == '20/03/2022'
    assert order_confirmation.stock_code == 'ASC'
    assert order_confirmation.quantity == 100.0
    assert order_confirmation.order_type == 'Buy'
    assert order_confirmation.limit_price == 1800.0
    assert order_confirmation.order_status == 'Pending'


def test_parse_manual_buy_order_confirmation_us_equity_ok():
    confirm_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-confirmation-us-equity.html').read_text()

    order_confirmation = parse_manual_order_confirmation_page(confirm_html=confirm_html)

    assert order_confirmation.order_date.strftime('%d/%m/%Y') == '20/03/2022'
    assert order_confirmation.stock_code == 'MARA'
    assert order_confirmation.quantity == 100.0
    assert order_confirmation.order_type == 'Buy'
    assert order_confirmation.limit_price is None
    assert order_confirmation.order_status == 'Pending'


def test_submit_manual_buy_order_confirmation_uk_equity():
    confirm_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-confirmation-uk-equity.html').read_text()

    base_order = ManualOrder(
        hl_vt="2491884284",
        type="equity",
        out_of_hours=True,
        sedol="3092725",
        product_no=70,
        available=179515.7,
        holding=0,
        holding_value=0,
        transfer_units=None,
        remaining_units=0,
        remaining_units_value=0,
        isin="GB0030927254",
        epic="",
        currency_code="GBX",
        SD_Bid=0.00,
        SD_Ask=0.00,
        fixed_interest=False,
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    order = ManualBuyOrder(
        base_order=base_order,
        quantity=100,
        shares_or_value=ManualOrder.SHARE_QUANTITY,
        limit=1800,
        earmark_orders_confirm=False)

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()

        expected_params = {
            'hl_vt': "2491884284",
            'type': "equity",
            'out_of_hours': "1",
            'sedol': "3092725",
            'product_no': "70",
            'available': "179515.7",
            'holding': "0",
            'holding_value': "0",
            'transfer_units': "",
            'remaining_units': "0",
            'remaining_units_value': "0",
            'isin': "GB0030927254",
            'epic': "",
            'currency_code': "GBX",
            'SD_Bid': "0.00",
            'SD_Ask': "0.00",
            'fixed_interest': "0",
            'bs': "Buy",
            'quantity': "100",
            'qs': "quantity",
            'limit': "1800",
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
        order_confirmation = client.submit_manual_order(order=order)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == ManualOrderConfirmation


def test_submit_manual_buy_order_confirmation_us_equity():
    confirm_html = Path(Path(__file__).parent / 'files_manual_orders/manual-buy-order-confirmation-us-equity.html').read_text()

    base_order = ManualOrder(
        hl_vt="3430162972",
        type="equity",
        out_of_hours=True,
        sedol="BLR7B52",
        product_no=70,
        available=177721.1,
        holding=0,
        holding_value=0,
        transfer_units=None,
        remaining_units=0,
        remaining_units_value=0,
        isin="US5657881067",
        epic="",
        currency_code="USD",
        SD_Bid=0.00,
        SD_Ask=0.00,
        fixed_interest=False,
        category_code=InvestmentCategoryTypes.OVERSEAS
    )

    # TODO earmark order - get from page

    order = ManualBuyOrder(
        base_order=base_order,
        quantity=100,
        shares_or_value=ManualOrder.SHARE_QUANTITY,
        limit=None,
        earmark_orders_confirm=False)

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()

        expected_params = {
            'hl_vt': "3430162972",
            'type': "equity",
            'out_of_hours': "1",
            'sedol': "BLR7B52",
            'product_no': "70",
            'available': "177721.1",
            'holding': "0",
            'holding_value': "0",
            'transfer_units': "",
            'remaining_units': "0",
            'remaining_units_value': "0",
            'isin': "US5657881067",
            'epic': "",
            'currency_code': "USD",
            'SD_Bid': "0.00",
            'SD_Ask': "0.00",
            'fixed_interest': "0",
            'bs': "Buy",
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
        order_confirmation = client.submit_manual_order(order=order)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert type(order_confirmation) == ManualOrderConfirmation
