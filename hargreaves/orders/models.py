from enum import Enum


class OrderAmountType(Enum):
    Quantity = 'quantity'
    Value = 'value'

    def __str__(self):
        return self.name


class OrderPositionType(Enum):
    Buy = 'Buy'
    Sell = 'Sell'

    def __str__(self):
        return self.name


class OrderRequest():
    _sedol_code: str
    _category_code: str
    _position_type: OrderPositionType
    _position_percentage: float
    _account_id: int
    _account_value: float

    def __init__(self,
                 sedol_code: str,
                 category_code: str,
                 position_type: OrderPositionType,
                 position_percentage: float,
                 account_id: int,
                 account_value: float
                 ):
        self._sedol_code = sedol_code
        self._category_code = category_code
        self._position_type = position_type
        self._position_percentage = position_percentage
        self._account_id = account_id
        self._account_value = account_value

    @property
    def sedol_code(self):
        return self._sedol_code

    @property
    def category_code(self):
        return self._category_code

    @property
    def position_type(self):
        return self._position_type

    @property
    def position_percentage(self):
        return self._position_percentage

    @property
    def account_id(self):
        return self._account_id

    @property
    def account_value(self):
        return self._account_value

    def __str__(self):
        return f"""OrderRequest[
            sedol_code={self.sedol_code},
            category_code={self.category_code},
            position_type={self.position_type},
            position_percentage={self.position_percentage},
            account_id={self.account_id},
            account_value={self.account_value}
        ]"""


class IOrderConfirmation():
    """
    Interface for order confirmations
    """


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
