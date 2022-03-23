from enum import Enum
from typing import Optional


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


class DealRequest():
    _stock_ticker: str
    _account_id: int
    _position_type: OrderPositionType
    _position_percentage: float
    _allow_fill_or_kill: bool
    _security_name: Optional[str]
    _sedol_code: Optional[str]

    def __init__(self,
                 stock_ticker: str,
                 account_id: int,
                 position_type: OrderPositionType,
                 position_percentage: float,
                 allow_fill_or_kill: bool = True,
                 security_name: str = None,
                 sedol_code: str = None
                 ):
        """
        :param stock_ticker: str - the stock ticker code
        :param account_id: int - HL Account ID
        :param position_type: OrderPositionType - Buy / Sell
        :param position_percentage: float  - BUY: this is the % of the account. SELL: this is the % of the position
        :param allow_fill_or_kill: bool - Will attempt realtime market order first, if true can also place manual order
        :param security_name: str - Optional, when the search returns multiple results this will be used to narrow down
        :param sedol_code: str - Optional, when the search returns multiple results this will be used to narrow down
        """
        self._stock_ticker = stock_ticker
        self._account_id = account_id
        self._position_type = position_type
        self._position_percentage = position_percentage
        self._allow_fill_or_kill = allow_fill_or_kill
        self._security_name = security_name
        self._sedol_code = sedol_code

    @property
    def stock_ticker(self):
        return self._stock_ticker

    @property
    def account_id(self):
        return self._account_id

    @property
    def position_type(self):
        return self._position_type

    @property
    def position_percentage(self):
        return self._position_percentage

    @property
    def allow_fill_or_kill(self):
        return self._allow_fill_or_kill

    @property
    def security_name(self):
        return self._security_name

    @property
    def sedol_code(self):
        return self._sedol_code

    def __str__(self):
        return f"""DealRequest[
            stock_ticker={self.stock_ticker},
            account_id={self.account_id},
            position_type={self.position_type},
            position_percentage={self.position_percentage},
            allow_fill_or_kill={self.allow_fill_or_kill},
            security_name={self.security_name},
            sedol_code={self.sedol_code}
        ]"""


class IOrderConfirmation():
    """
    Interface for order confirmations
    """


class DealResult():
    _request: DealRequest
    _result: IOrderConfirmation

    def __init__(self, request: DealRequest, result: IOrderConfirmation):
        self._request = request
        self._result = result

    @property
    def request(self):
        return self._request

    @property
    def result(self):
        return self._result

    def __str__(self):
        return f"""DealResult[
            request={self.request},
            result={self.result}
        ]"""
