import datetime
from typing import Optional


class PendingOrder:
    _account_id: int
    _order_id: int
    _order_date: datetime.datetime
    _trade_type: str
    _sedol_code: str
    _stock_title: str
    _quantity: float
    _qty_is_money: bool
    _limit_price: Optional[float]
    _status: str

    def __init__(self,
                 account_id: int,
                 order_id: int,
                 order_date: datetime.datetime,
                 trade_type: str,
                 sedol_code: str,
                 stock_title: str,
                 quantity: float,
                 qty_is_money: bool,
                 limit_price: Optional[float],
                 status: str):
        self._account_id = account_id
        self._order_id = order_id
        self._order_date = order_date
        self._trade_type = trade_type
        self._sedol_code = sedol_code
        self._stock_title = stock_title
        self._quantity = quantity
        self._qty_is_money = qty_is_money
        self._limit_price = limit_price
        self._status = status

    @property
    def account_id(self):
        return self._account_id

    @property
    def order_id(self):
        return self._order_id

    @property
    def order_date(self):
        return self._order_date

    @property
    def trade_type(self):
        return self._trade_type

    @property
    def sedol_code(self):
        return self._sedol_code

    @property
    def stock_title(self):
        return self._stock_title

    @property
    def quantity(self):
        return self._quantity

    @property
    def qty_is_money(self):
        return self._qty_is_money

    @property
    def limit_price(self):
        return self._limit_price

    @property
    def status(self):
        return self._status

    def __str__(self):
        return f"""PendingOrder[
            account_id={self._account_id},
            order_id={self._order_id},
            order_date={self._order_date},
            trade_type={self._trade_type},
            sedol_code={self._sedol_code},
            stock_title={self._stock_title},
            quantity={self._quantity},
            qty_is_money={self._qty_is_money},
            limit_price={self._limit_price},
            status={self._status}
        ]"""
