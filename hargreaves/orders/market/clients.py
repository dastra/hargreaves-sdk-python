import http
import logging

from hargreaves.orders.market.errors import MarketOrderFailedError
from hargreaves.orders.market.models import MarketOrderPosition, MarketOrderQuote, MarketOrderConfirmation, MarketOrder
from hargreaves.orders.market.parsers import parse_market_order_entry_page, parse_market_order_quote_page, \
    parse_market_order_confirmation_page
from hargreaves.orders.models import PositionCalculator, OrderRequest, IOrderConfirmation, OrderPositionType
from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.clients import ISessionClient
from hargreaves.utils import clock
from hargreaves.request_tracker.session import IWebSession, WebRequestType

logger = logging.getLogger(__name__)


class IMarketOrderClient:

    def get_current_position(self,
                             web_session: IWebSession,
                             account_id: int,
                             sedol_code: str,
                             category_code: str) -> MarketOrderPosition:
        pass

    def get_order_quote(self, web_session: IWebSession, order: MarketOrder) -> MarketOrderQuote:
        pass

    def submit_order(self, web_session: IWebSession, order_quote: MarketOrderQuote) -> MarketOrderConfirmation:
        pass

    def execute_order_flow(self, web_session: IWebSession, order_request: OrderRequest) -> IOrderConfirmation:
        pass


class MarketOrderClient(IMarketOrderClient):
    _session_client: ISessionClient

    def __init__(self, session_client: ISessionClient):
        self._session_client = session_client

    def get_current_position(self,
                             web_session: IWebSession,
                             account_id: int,
                             sedol_code: str,
                             category_code: str) -> MarketOrderPosition:

        logger.debug("Get Current Position")

        clock.sleep_random()

        order_html = web_session.get(f"https://online.hl.co.uk/my-accounts/account_select/"
                                     f"account/{account_id}/sedol/{sedol_code}/rq/select/type/trade").text
        order_info = parse_market_order_entry_page(order_html, category_code)
        return order_info

    def get_order_quote(self, web_session: IWebSession, order: MarketOrder) -> MarketOrderQuote:

        logger.debug("Get Order Quote")

        clock.sleep_random()

        self._session_client.session_keepalive(
            web_session=web_session, sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        clock.sleep_random()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
        }

        if order.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_deal'

        res = web_session.post(request_url,
                               request_type=WebRequestType.XHR, data=order.as_form_fields(),
                               headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Buy quote invalid, HTTP response code was {res.status_code}")
        elif "another account open" in res.text:
            raise ValueError("An error occurred with the sequence of calls - the wrong hl_vt was passed in.")

        price_quote = parse_market_order_quote_page(res.text, category_code=order.category_code)
        return price_quote

    def submit_order(self, web_session: IWebSession, order_quote: MarketOrderQuote) -> MarketOrderConfirmation:

        logger.debug(f"Execute (Confirm) Order ...")

        clock.sleep_random()

        self._session_client.session_keepalive(
            web_session=web_session,
            sedol_code=order_quote.sedol_code,
            session_hl_vt=order_quote.session_hl_vt)

        clock.sleep_random()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order_quote.sedol_code}'
        }

        form = {
            'hl_vt': order_quote.hl_vt,
            'sedol': order_quote.sedol_code
        }

        if order_quote.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation'

        res = web_session.post(request_url,
                               request_type=WebRequestType.XHR,
                               data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise MarketOrderFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        order_confirmation = parse_market_order_confirmation_page(confirm_html=res.text,
                                                                  category_code=order_quote.category_code)

        return order_confirmation

    def execute_order_flow(self, web_session: IWebSession, order_request: OrderRequest) -> IOrderConfirmation:

        logger.debug("Executing Deal As Market Order ...")

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
            units_held=current_position.units_held
        )

        logger.debug(f"CALCULATED: amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

        order = MarketOrder(
            position=current_position,
            position_type=order_request.position_type,
            amount_type=amount_type,
            quantity=order_quantity,
            including_charges=(True if order_request.position_type == OrderPositionType.Buy else False)
        )

        order_quote = self.get_order_quote(
            web_session=web_session,
            order=order)

        logger.debug(order_quote)

        order_confirmation = self.submit_order(
            web_session=web_session,
            order_quote=order_quote)

        logger.debug(order_confirmation)

        return order_confirmation
