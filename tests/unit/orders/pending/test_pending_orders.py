import http
from pathlib import Path
from urllib.parse import urlencode

from hargreaves.orders.pending.clients import PendingOrdersClient
from hargreaves.orders.pending.models import PendingOrder
from hargreaves.orders.pending.parsers import parse_pending_orders
from hargreaves.utils.input import InputHelper
from hargreaves.utils.logging import LoggerFactory
from hargreaves.web.mocks import MockWebSession, MockTimeService


def test_parse_pending_orders_with_0_orders():
    pending_orders_html = Path(Path(__file__).parent / 'files/pending-orders-0.html').read_text()
    pending_orders = parse_pending_orders(account_id=70, pending_orders_html=pending_orders_html)

    assert len(pending_orders) == 0


def test_parse_pending_orders_with_2_orders():
    pending_orders_html = Path(Path(__file__).parent / 'files/pending-orders-2.html').read_text()
    pending_orders = parse_pending_orders(account_id=70, pending_orders_html=pending_orders_html)

    assert len(pending_orders) == 2

    order1 = pending_orders[0]
    order2 = pending_orders[1]

    assert order1.order_id == 151813955
    assert order1.order_date.strftime('%d/%m/%Y') == '23/03/2022'
    assert order1.trade_type == 'R'
    assert order1.sedol_code == 'BDBFK59'
    assert order1.stock_title == 'Mammoth Energy Services Inc'
    assert order1.quantity == 500.00
    assert order1.qty_is_money is True
    assert order1.limit_price == 1.9
    assert order1.status == 'Pending'

    assert order2.order_id == 151813973
    assert order2.order_date.strftime('%d/%m/%Y') == '23/03/2022'
    assert order2.trade_type == 'B'
    assert order2.sedol_code == 'BGMG7B7'
    assert order2.stock_title == 'Bitfarms Ltd'
    assert order2.quantity == 100.00
    assert order2.qty_is_money is False
    assert order2.limit_price is None
    assert order2.status == 'Pending'


def test_send_search_request():
    account_id = 70
    response_html = Path(Path(__file__).parent / 'files/pending-orders-2.html'). \
        read_text()

    with MockWebSession() as web_session:
        LoggerFactory.configure_std_out()
        time_service = MockTimeService()

        web_session.mock_get(
            url=f'https://online.hl.co.uk/my-accounts/pending_orders/account/{account_id}',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/account_summary/account/{account_id}'
            },
            response_text=response_html,
            status_code=http.HTTPStatus.OK
        )

        client = PendingOrdersClient(time_service, web_session)
        search_results = client.get_pending_orders(account_id=account_id)

        assert len(search_results) == 2


def test_cancel_pending_order_1_out_of_2():
    confirm_html = Path(Path(__file__).parent / 'files/pending-order-cancel-1-out-of-2-confirmation.html'). \
        read_text()

    account_id = 70
    cancel_trade_id = 151813973

    pending_orders = [
        PendingOrder(
            account_id=account_id,
            order_id=151813955,
            order_date=InputHelper.parse_date('23/03/2022'),
            trade_type='R',
            sedol_code='BDBFK59',
            stock_title='Mammoth Energy Services Inc',
            quantity=500.00,
            qty_is_money=True,
            limit_price=None,
            status='Pending'
        ), PendingOrder(
            account_id=account_id,
            order_id=151813973,
            order_date=InputHelper.parse_date('23/03/2022'),
            trade_type='B',
            sedol_code='BGMG7B7',
            stock_title='Bitfarms Ltd',
            quantity=100,
            qty_is_money=False,
            limit_price=None,
            status='Pending'
        )]

    with MockWebSession() as web_session:
        LoggerFactory.configure_std_out()
        time_service = MockTimeService()

        expected_params = {
            "action": "cancel",
            "bref": "151813973",
            "151813955_trade_type[]": "R",
            "151813955_sedol[]": "BDBFK59",
            "151813955_stoktitle[]": "Mammoth Energy Services Inc",
            "151813955_quantity[]": "500.0",
            "151813955_qty_is_money[]": "1",
            "151813973_trade_type[]": "B",
            "151813973_sedol[]": "BGMG7B7",
            "151813973_stoktitle[]": "Bitfarms Ltd",
            "151813973_quantity[]": "100",
            "151813973_qty_is_money[]": "0",
            "cancel": "cancel"
        }
        mock = web_session.mock_post(
            url='https://online.hl.co.uk/my-accounts/pending_orders',
            headers={
                'Referer': f'https://online.hl.co.uk/my-accounts/pending_orders/account/{account_id}'
            },
            response_text=confirm_html,
            status_code=http.HTTPStatus.OK
        )
        client = PendingOrdersClient(time_service, web_session)
        is_ok = client.cancel_pending_order(cancel_order_id=cancel_trade_id, pending_orders=pending_orders)
        actual_param = mock.request_history[0].text

        assert urlencode(expected_params) == actual_param
        assert is_ok is True
