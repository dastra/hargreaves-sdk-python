import http
import logging

from ...orders.manual.errors import ManualOrderFailedError
from ...orders.manual.models import ManualOrder, ManualOrderPosition
from ...orders.manual.parsers import parse_manual_order_confirmation_page, parse_manual_order_entry_page
from ...orders.models import OrderRequest, IOrderConfirmation, PositionCalculator
from ...search.models import InvestmentCategoryTypes
from ...session.clients import ISessionClient
from ...utils import clock
from requests_tracker.session import IWebSession, WebRequestType

logger = logging.getLogger(__name__)


class IManualOrderClient:

    def get_current_position(self,
                             web_session: IWebSession,
                             account_id: int,
                             sedol_code: str,
                             category_code: str) -> ManualOrderPosition:
        pass

    def submit_order(self, web_session: IWebSession, order: ManualOrder):
        pass

    def execute_order_flow(self, web_session: IWebSession, order_request: OrderRequest) -> IOrderConfirmation:
        pass


class ManualOrderClient(IManualOrderClient):
    _session_client: ISessionClient

    def __init__(self, session_client: ISessionClient):
        self._session_client = session_client

    def get_current_position(self,
                             web_session: IWebSession,
                             account_id: int,
                             sedol_code: str,
                             category_code: str) -> ManualOrderPosition:

        logger.debug("Get Current Position")

        clock.sleep_random()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        order_html = web_session.get(url=f"https://online.hl.co.uk/my-accounts/manual_order/"
                                         f"sedol/{sedol_code}/product_no/{account_id}",
                                     headers=request_headers).text

        current_position = parse_manual_order_entry_page(order_html, category_code)
        return current_position

    def submit_order(self, web_session: IWebSession, order: ManualOrder):

        logger.debug(f"Submit Order ...")

        clock.sleep_random()

        self._session_client.session_keepalive(
            web_session=web_session, sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        clock.sleep_random()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
        }

        form = order.as_form_fields()

        if order.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal'

        res = web_session.post(request_url,
                               request_type=WebRequestType.XHR,
                               data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise ManualOrderFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        order_confirmation = parse_manual_order_confirmation_page(confirm_html=res.text, amount_type=order.amount_type)

        return order_confirmation

    def execute_order_flow(self, web_session: IWebSession, order_request: OrderRequest) -> IOrderConfirmation:

        logger.debug("Executing Deal As Manual Order ...")

        current_position = self.get_current_position(
            web_session=web_session,
            account_id=order_request.account_id,
            sedol_code=order_request.sedol_code,
            category_code=order_request.category_code)

        logger.debug(current_position.as_form_fields())

        (amount_type, order_quantity) = PositionCalculator.calculate(
            position_type=order_request.position_type,
            position_percentage=order_request.position_percentage,
            account_value=order_request.account_value,
            units_held=current_position.remaining_units
        )

        logger.debug(f"CALCULATED: amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

        order = ManualOrder(
            position=current_position,
            position_type=order_request.position_type,
            amount_type=amount_type,
            quantity=order_quantity,
            limit=None)

        # submit order
        order_confirmation = self.submit_order(
            web_session=web_session,
            order=order)

        logger.debug(order_confirmation)

        return order_confirmation
