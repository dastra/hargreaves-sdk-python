from hargreaves.trade.models import OrderPositionType, OrderAmountType


class PositionCalculator:
    @staticmethod
    def calculate(
            position_type: OrderPositionType,
            position_percentage: float,
            account_value: float,
            units_held: float
    ):
        if position_type == OrderPositionType.Buy:
            amount_type = OrderAmountType.Value
            order_quantity = round(account_value * (position_percentage / 100), 2)
        else:
            amount_type = OrderAmountType.Quantity
            order_quantity = int(round(units_held * (position_percentage / 100), 0))

        return (amount_type, order_quantity)