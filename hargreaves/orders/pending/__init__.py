import logging
from typing import List

from hargreaves.orders.pending.clients import PendingOrdersClient
from hargreaves.orders.pending.models import PendingOrder
from hargreaves.request_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_pending_orders(web_session: IWebSession,
                       account_id: int) -> List[PendingOrder]:

    return PendingOrdersClient().get_pending_orders(
        web_session=web_session,
        account_id=account_id
    )


def cancel_pending_order(web_session: IWebSession,
                         cancel_order_id:
                         int, pending_orders: List[PendingOrder]) -> bool:

    return PendingOrdersClient().cancel_pending_order(
        web_session=web_session,
        cancel_order_id=cancel_order_id,
        pending_orders=pending_orders
    )
