import http
from logging import Logger

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.session.clients import ISessionClient
from hargreaves.trade.market.errors import MarketOrderFailedError
from hargreaves.trade.market.models import MarketOrderPosition, MarketOrderQuote, MarketOrderConfirmation, MarketOrder
from hargreaves.trade.market.parsers import parse_market_order_entry_page, parse_market_order_quote_page, \
    parse_market_order_confirmation_page
from hargreaves.utils.timings import ITimeService
from hargreaves.web.session import IWebSession, WebRequestType


class IMarketOrderClient:

    def get_current_position(self, account_id: int, sedol_code: str, category_code: str) -> MarketOrderPosition:
        pass

    def get_order_quote(self, order: MarketOrder) -> MarketOrderQuote:
        pass

    def execute_order(self, market_order_quote: MarketOrderQuote) -> MarketOrderConfirmation:
        pass


class MarketOrderClient(IMarketOrderClient):
    _logger: Logger
    _time_service: ITimeService
    _web_session: IWebSession
    _session_client: ISessionClient

    def __init__(self,
                 logger: Logger,
                 time_service: ITimeService,
                 web_session: IWebSession,
                 session_client: ISessionClient
                 ):
        self._logger = logger
        self._time_service = time_service
        self._web_session = web_session
        self._session_client = session_client

    def get_current_position(self, account_id: int, sedol_code: str, category_code: str) -> MarketOrderPosition:

        self._logger.debug("Get Current Position")

        self._time_service.sleep()

        order_html = self._web_session.get(f"https://online.hl.co.uk/my-accounts/account_select/"
                                            f"account/{account_id}/sedol/{sedol_code}/rq/select/type/trade").text
        order_info = parse_market_order_entry_page(order_html, category_code)
        return order_info

    def get_order_quote(self, order: MarketOrder) -> MarketOrderQuote:

        self._logger.debug("Get Order Quote")

        self._time_service.sleep()

        self._session_client.session_keepalive(sedol_code=order.sedol, session_hl_vt=order.hl_vt)

        self._time_service.sleep()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{order.sedol}'
        }

        if order.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_deal'

        res = self._web_session.post(request_url,
                                     request_type=WebRequestType.XHR, data=order.as_form_fields(),
                                     headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Buy quote invalid, HTTP response code was {res.status_code}")
        elif "another account open" in res.text:
            raise ValueError("An error occurred with the sequence of calls - the wrong hl_vt was passed in.")

        price_quote = parse_market_order_quote_page(res.text, category_code=order.category_code)
        return price_quote

    def execute_order(self, market_order_quote: MarketOrderQuote) -> MarketOrderConfirmation:

        self._logger.debug(f"Execute (Confirm) Order ...")

        self._time_service.sleep()

        self._session_client.session_keepalive(
            sedol_code=market_order_quote.sedol_code, session_hl_vt=market_order_quote.session_hl_vt)

        self._time_service.sleep()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{market_order_quote.sedol_code}'
        }

        form = {
            'hl_vt': market_order_quote.hl_vt,
            'sedol': market_order_quote.sedol_code
        }

        if market_order_quote.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation'

        res = self._web_session.post(request_url,
                                     request_type=WebRequestType.XHR,
                                     data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise MarketOrderFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        order_confirmation = parse_market_order_confirmation_page(confirm_html=res.text,
                                                                  category_code=market_order_quote.category_code)

        return order_confirmation
