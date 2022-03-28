import http
import logging

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.clients import ISessionClient
from hargreaves.orders.manual.errors import ManualOrderFailedError
from hargreaves.orders.manual.models import ManualOrder, ManualOrderPosition
from hargreaves.orders.manual.parsers import parse_manual_order_confirmation_page, parse_manual_order_entry_page
from hargreaves.web.session import IWebSession, WebRequestType
from hargreaves.web.timings import ITimeService

logger = logging.getLogger(__name__)


class IManualOrderClient:

    def get_current_position(self, account_id: int, sedol_code: str, category_code: str) -> ManualOrderPosition:
        pass

    def submit_order(self, order: ManualOrder):
        pass


class ManualOrderClient(IManualOrderClient):
    _time_service: ITimeService
    _web_session: IWebSession
    _session_client: ISessionClient

    def __init__(self,
                 time_service: ITimeService,
                 web_session: IWebSession,
                 session_client: ISessionClient
                 ):
        self._time_service = time_service
        self._web_session = web_session
        self._session_client = session_client

    def get_current_position(self, account_id: int, sedol_code: str, category_code: str) -> ManualOrderPosition:

        logger.debug("Get Current Position")

        self._time_service.sleep()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        order_html = self._web_session.get(url=f"https://online.hl.co.uk/my-accounts/manual_order/"
                                               f"sedol/{sedol_code}/product_no/{account_id}",
                                           headers=request_headers).text

        current_position = parse_manual_order_entry_page(order_html, category_code)
        return current_position

    def submit_order(self, order: ManualOrder):

        logger.debug(f"Submit Order ...")

        self._time_service.sleep()

        self._session_client.session_keepalive(sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        self._time_service.sleep()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
        }

        form = order.as_form_fields()

        if order.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal'

        res = self._web_session.post(request_url,
                                     request_type=WebRequestType.XHR,
                                     data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise ManualOrderFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        order_confirmation = parse_manual_order_confirmation_page(confirm_html=res.text, amount_type=order.amount_type)

        return order_confirmation
