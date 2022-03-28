import logging

from hargreaves.deals.models import DealRequest, DealResult, PositionCalculator
from hargreaves.orders.manual.clients import IManualOrderClient
from hargreaves.orders.manual.models import ManualOrder
from hargreaves.orders.market.clients import IMarketOrderClient
from hargreaves.orders.market.errors import MarketClosedError, MarketOrderLiveQuoteError
from hargreaves.orders.market.models import MarketOrder
from hargreaves.orders.models import OrderPositionType

logger = logging.getLogger(__name__)


class DealClient():
    _market_order_client: IMarketOrderClient
    _manual_order_client: IManualOrderClient

    def __init__(self,
                 market_order_client: IMarketOrderClient,
                 manual_order_client: IManualOrderClient
                 ):
        self._market_order_client = market_order_client
        self._manual_order_client = manual_order_client

    def _execute_smart_deal_as_market_order(self,
                                            deal_request: DealRequest,
                                            sedol_code: str,
                                            category_code: str,
                                            account_value: float) -> DealResult:

        logger.debug("Executing Smart Deal As Market Order ...")

        current_position = self._market_order_client.get_current_position(
            account_id=deal_request.account_id,
            sedol_code=sedol_code,
            category_code=category_code)

        logger.debug(current_position.as_form_fields())

        (amount_type, order_quantity) = PositionCalculator.calculate(
            position_type=deal_request.position_type,
            position_percentage=deal_request.position_percentage,
            account_value=account_value,
            units_held=current_position.units_held
        )

        logger.debug(f"CALCULATED: amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

        order = MarketOrder(
            position=current_position,
            position_type=deal_request.position_type,
            amount_type=amount_type,
            quantity=order_quantity,
            including_charges=(True if deal_request.position_type == OrderPositionType.Buy else False)
        )

        order_quote = self._market_order_client.get_order_quote(order)

        logger.debug(order_quote)

        order_confirmation = self._market_order_client.execute_order(order_quote)

        logger.debug(order_confirmation)

        return DealResult(deal_request, order_confirmation)

    def _execute_smart_deal_as_manual_order(self,
                                            deal_request: DealRequest,
                                            sedol_code: str,
                                            category_code: str,
                                            account_value: float) -> DealResult:

        logger.debug("Executing Smart Deal As Manual Order ...")

        current_position = self._manual_order_client.get_current_position(
            account_id=deal_request.account_id,
            sedol_code=sedol_code,
            category_code=category_code)

        logger.debug(current_position.as_form_fields())

        (amount_type, order_quantity) = PositionCalculator.calculate(
            position_type=deal_request.position_type,
            position_percentage=deal_request.position_percentage,
            account_value=account_value,
            units_held=current_position.remaining_units
        )

        logger.debug(f"CALCULATED: amount_type = {amount_type}, order_quantity = {order_quantity:,f}...")

        order = ManualOrder(
            position=current_position,
            position_type=deal_request.position_type,
            amount_type=amount_type,
            quantity=order_quantity,
            limit=None)

        # submit order
        order_confirmation = self._manual_order_client.submit_order(order)

        logger.debug(order_confirmation)

        return DealResult(deal_request, order_confirmation)

    def execute_smart_deal(self,
                           deal_request: DealRequest,
                           sedol_code: str,
                           category_code: str,
                           account_value: float
                           ) -> DealResult:

        logger.debug("Executing Smart Deal ...")

        try:

            return self._execute_smart_deal_as_market_order(
                deal_request=deal_request, sedol_code=sedol_code,
                category_code=category_code, account_value=account_value)

        except MarketClosedError as ex:
            logger.warning("Market is closed ...")

            if not (deal_request.allow_fill_or_kill and ex.can_place_fill_or_kill_order):
                raise ex

            return self._execute_smart_deal_as_manual_order(
                deal_request=deal_request, sedol_code=sedol_code,
                category_code=category_code, account_value=account_value)

        except MarketOrderLiveQuoteError:
            logger.warning("Unable to retrieve live-quote ...")

            return self._execute_smart_deal_as_manual_order(
                deal_request=deal_request, sedol_code=sedol_code,
                category_code=category_code, account_value=account_value)
