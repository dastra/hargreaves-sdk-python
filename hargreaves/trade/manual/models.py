import datetime
from typing import Optional

from hargreaves.trade.models import OrderPositionType, OrderAmountType


class ManualOrderPosition:
    _hl_vt: str
    _security_type: str
    _out_of_hours: bool
    _sedol: str
    _account_id: int
    _available: float
    _holding: float
    _holding_value: float
    _transfer_units: Optional[float]
    _remaining_units: float
    _remaining_units_value: float
    _isin: str
    _epic: str
    _currency_code: str
    _SD_Bid: float
    _SD_Ask: float
    _fixed_interest: bool

    def __init__(self,
                 hl_vt: str,
                 security_type: str,
                 out_of_hours: bool,
                 sedol: str,
                 account_id: int,
                 available: float,
                 holding: float,
                 holding_value: float,
                 transfer_units: Optional[float],
                 remaining_units: float,
                 remaining_units_value: float,
                 isin: str,
                 epic: str,
                 currency_code: str,
                 SD_Bid: float,
                 SD_Ask: float,
                 fixed_interest: bool,
                 category_code: str
                 ):
        self._hl_vt = hl_vt
        self._security_type = security_type
        self._out_of_hours = out_of_hours
        self._sedol = sedol
        self._account_id = account_id
        self._available = available
        self._holding = holding
        self._holding_value = holding_value
        self._transfer_units = transfer_units
        self._remaining_units = remaining_units
        self._remaining_units_value = remaining_units_value
        self._isin = isin
        self._epic = epic
        self._currency_code = currency_code
        self._SD_Bid = SD_Bid
        self._SD_Ask = SD_Ask
        self._fixed_interest = fixed_interest
        self._category_code = category_code

    def as_form_fields(self) -> dict:
        return {
            'hl_vt': self._hl_vt,
            'type': self._security_type,
            'out_of_hours': str(int(self._out_of_hours)),
            'sedol': self._sedol,
            'product_no': str(self._account_id),
            'available': str(self._available),
            'holding': str(self._holding),
            'holding_value': "{:.2f}".format(self._holding_value),
            'transfer_units': '' if self._transfer_units is None else "{:.4f}".format(self._transfer_units),
            'remaining_units': self._remaining_units,
            'remaining_units_value': "{:.2f}".format(self._remaining_units_value),
            'isin': self._isin,
            'epic': self._epic,
            'currency_code': self._currency_code,
            'SD_Bid': "{:.2f}".format(self._SD_Bid),
            'SD_Ask': "{:.2f}".format(self._SD_Ask),
            'fixed_interest': str(int(self._fixed_interest))
        }

    @property
    def hl_vt(self):
        return self._hl_vt

    @property
    def type(self):
        return self._security_type

    @property
    def out_of_hours(self):
        return self._out_of_hours

    @property
    def sedol(self):
        return self._sedol

    @property
    def product_no(self):
        return self._account_id

    @property
    def available(self):
        return self._available

    @property
    def holding(self):
        return self._holding

    @property
    def holding_value(self):
        return self._holding_value

    @property
    def transfer_units(self):
        return self._transfer_units

    @property
    def remaining_units(self):
        return self._remaining_units

    @property
    def remaining_units_value(self):
        return self._remaining_units_value

    @property
    def isin(self):
        return self._isin

    @property
    def epic(self):
        return self._epic

    @property
    def currency_code(self):
        return self._currency_code

    @property
    def SD_Bid(self):
        return self._SD_Bid

    @property
    def SD_Ask(self):
        return self._SD_Ask

    @property
    def fixed_interest(self):
        return self._fixed_interest

    @property
    def category_code(self):
        return self._category_code


class ManualOrder():
    _position: ManualOrderPosition
    _position_type: OrderPositionType
    _amount_type: OrderAmountType
    _quantity: float
    _limit: float
    _earmark_orders_confirm: bool
    # ear-marked orders are other pending orders that already exists -> when trying to add another pending order
    # it will return an error, although judging by the code you could override this and place the order anyway

    def __init__(self,
                 position: ManualOrderPosition,
                 position_type: OrderPositionType,
                 amount_type: OrderAmountType,
                 quantity: float,
                 limit: Optional[float],
                 earmark_orders_confirm: bool = False):
        self._position = position
        self._position_type = position_type
        self._amount_type = amount_type
        self._quantity = quantity
        self._limit = limit
        self._earmark_orders_confirm = earmark_orders_confirm

    def as_form_fields(self) -> dict:
        position_fields = self._position.as_form_fields()

        buy_fields = {
            'bs': self._position_type.value,
            'quantity': str(self.quantity),
            'qs': self._amount_type.value,
            'limit': '' if self._limit is None else str(self._limit),
            'earmark_orders_confirm': str(self._earmark_orders_confirm).lower()
        }

        return {**position_fields, **buy_fields}

    @property
    def position_type(self):
        return self._position_type

    @property
    def quantity(self):
        return self._quantity

    @property
    def amount_type(self):
        return self._amount_type

    @property
    def limit(self):
        return self._limit

    @property
    def earmark_orders_confirm(self):
        return self._earmark_orders_confirm

    @property
    def hl_vt(self):
        return self._position.hl_vt

    @property
    def sedol(self):
        return self._position.sedol

    @property
    def category_code(self):
        return self._position.category_code

    def __str__(self):
        return f"""ManualOrder[
            {self.as_form_fields()}
        ]"""


class ManualOrderConfirmation():
    _order_date: datetime.date
    _stock_code: str
    _quantity: float
    _order_type: str
    _limit_price: float
    _order_status: str

    def __init__(self,
                 order_date: datetime.date,
                 stock_code: str,
                 quantity: float,
                 order_type: str,
                 limit_price: float,
                 order_status: str
                 ):
        self._order_date = order_date
        self._stock_code = stock_code
        self._quantity = quantity
        self._order_type = order_type
        self._limit_price = limit_price
        self._order_status = order_status

    @property
    def order_date(self):
        return self._order_date

    @property
    def stock_code(self):
        return self._stock_code

    @property
    def quantity(self):
        return self._quantity

    @property
    def order_type(self):
        return self._order_type

    @property
    def limit_price(self):
        return self._limit_price

    @property
    def order_status(self):
        return self._order_status

    def __str__(self):
        return f"""ManualOrderConfirmation[
            order_date={self._order_date},
            stock_code={self._stock_code},
            quantity={self._quantity},
            order_type={self._order_type},
            limit_price={self._limit_price},
            order_status={self._order_status}
        ]"""
