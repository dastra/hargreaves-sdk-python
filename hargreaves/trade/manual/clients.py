import http
from logging import Logger

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.errors import DealFailedError
from hargreaves.trade.manual.models import ManualOrder
from hargreaves.trade.manual.parsers import parse_manual_order_confirmation_page, parse_manual_order_entry_page
from hargreaves.web.session import IWebSession, WebRequestType


class ManualOrderClient:
    __logger: Logger
    __web_session: IWebSession

    def __init__(self,
                 logger: Logger,
                 web_session: IWebSession
                 ):
        self.__logger = logger
        self.__web_session = web_session

    def get_manual_order_info(self, account_id: int, sedol_code: str, category_code: str) -> ManualOrder:

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        order_html = self.__web_session.get(url=f"https://online.hl.co.uk/my-accounts/manual_order/"
                                                f"sedol/{sedol_code}/product_no/{account_id}",
                                            headers=request_headers).text

        manual_order_info = parse_manual_order_entry_page(order_html, category_code)
        return manual_order_info

    def submit_manual_order(self, order: ManualOrder):

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
        }

        form = order.as_form_fields()

        if order.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/manual_deal'

        res = self.__web_session.post(request_url,
                                      request_type=WebRequestType.XHR,
                                      data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise DealFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        order_confirmation = parse_manual_order_confirmation_page(confirm_html=res.text)

        return order_confirmation
