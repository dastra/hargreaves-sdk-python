import http
import logging
from typing import List

from bs4 import BeautifulSoup

from ...orders.pending.errors import CancelPendingOrderError
from ...orders.pending.models import PendingOrder
from ...orders.pending.parsers import parse_pending_orders
from ...utils import clock
from requests_tracker.request import WebRequestType
from requests_tracker.session import IWebSession

logger = logging.getLogger(__name__)


class PendingOrdersClient:

    def get_pending_orders(self,
                           web_session: IWebSession,
                           account_id: int) -> List[PendingOrder]:

        logger.debug(f"Get pending order for account '{account_id}' ...")

        headers = {
            'Referer': f"https://online.hl.co.uk/my-accounts/account_summary/account/{account_id}"
        }

        pending_order_html = web_session.get(
            url=f'https://online.hl.co.uk/my-accounts/pending_orders/account/{account_id}',
            request_type=WebRequestType.Document,
            headers=headers).text

        return parse_pending_orders(account_id=account_id, pending_orders_html=pending_order_html)

    def cancel_pending_order(self,
                             web_session: IWebSession,
                             cancel_order_id:
                             int, pending_orders: List[PendingOrder]) -> bool:

        logger.debug(f"Cancel Pending Order '{cancel_order_id}' ...")

        clock.sleep_random()

        account_id = pending_orders[0].account_id

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/pending_orders/account/{account_id}'
        }

        form = {
            "action": "cancel",
            "bref": str(cancel_order_id)
        }

        for pending_order in pending_orders:
            order_id = str(pending_order.order_id)
            form[f"{order_id}_trade_type[]"] = str(pending_order.trade_type)
            form[f"{order_id}_sedol[]"] = str(pending_order.sedol_code)
            form[f"{order_id}_stoktitle[]"] = str(pending_order.stock_title)
            form[f"{order_id}_quantity[]"] = str(pending_order.quantity)
            form[f"{order_id}_qty_is_money[]"] = str(int(pending_order.qty_is_money))

        form["cancel"] = "cancel"

        res = web_session.post("https://online.hl.co.uk/my-accounts/pending_orders",
                               request_type=WebRequestType.Document,
                               data=form, headers=request_headers)

        confirm_html = res.text

        if res.status_code != http.HTTPStatus.OK:
            raise CancelPendingOrderError(f"Purchase invalid, HTTP response code was {res.status_code}",
                                          html=confirm_html)

        soup = BeautifulSoup(res.text, 'html.parser')

        first_paragraph = soup.select_one("div[id='content-body-full'] > p")
        message_text = first_paragraph.get_text(strip=True)
        if 'Your cancellation request has been successfully executed.' not in message_text:
            raise CancelPendingOrderError(f"Unexpected response text", html=confirm_html)

        return True
