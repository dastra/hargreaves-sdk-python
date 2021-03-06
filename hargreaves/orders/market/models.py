import datetime
from typing import Optional

from ...orders.models import OrderPositionType, OrderAmountType, IOrderConfirmation


class MarketOrderPosition:
    _hl_vt: str
    _stock_ticker: str
    _security_name: str
    _sedol_code: str
    _isin_code: str
    _epic_code: str
    _currency_code: str
    _exchange: str
    _fixed_interest: bool
    _account_id: int
    _total_cash_available: float
    _bid_price: str
    _units_held: float
    _value_gbp: float
    _category_code: str

    def __init__(self, hl_vt: str, stock_ticker: str, security_name: str, sedol_code: str, isin_code: str,
                 epic_code: str, currency_code: str, exchange: str, fixed_interest: bool, account_id: int,
                 total_cash_available: float, bid_price: str, units_held: float, value_gbp: float,
                 category_code: str
                 ):
        """
        :param hl_vt: str The security code
        :param stock_ticker: str ANIC - Stock ticker
        :param security_name: str Agronomics Limited - OK
        :param sedol_code: str B6QH1J2 - OK
        :param isin_code: str IM00B6QH1J21  - The ISIN code
        :param epic_code: str ANIC          - The EPIC code
        :param currency_code: str GBP       - currency
        :param exchange: str L
        :param fixed_interest: bool 0
        :param account_id: int 70 - Account id
        :param total_cash_available: float 60398.57 - total cash
        :param bid_price: str 20.00p - buy/sell price
        :param units_held: float 69930 - current holding, in number of shares
        :param value_gbp: float 13986    #  current holding value in GBP
        """
        self._hl_vt = hl_vt
        self._stock_ticker = stock_ticker
        self._security_name = security_name
        self._sedol_code = sedol_code
        self._isin_code = isin_code
        self._epic_code = epic_code
        self._currency_code = currency_code
        self._exchange = exchange
        self._fixed_interest = fixed_interest
        self._account_id = account_id
        self._total_cash_available = total_cash_available
        self._bid_price = bid_price
        self._units_held = units_held
        self._value_gbp = value_gbp
        self._category_code = category_code

    def as_form_fields(self) -> dict:
        return {
            'hl_vt': self.hl_vt,
            'sedol': self.sedol_code,
            'security_name': self.security_name,
            'product_no': str(self.account_id),
            'available': str(self.total_cash_available),
            'bid': str(self.bid_price),
            'holding': str(self.units_held),
            'holding_value': str(self.value_gbp),
            'isin': str(self.isin_code),
            'epic': str(self.epic_code),
            'currency_code': str(self.currency_code),
            'exchange': str(self.exchange),
            'fixed_interest': str(int(self.fixed_interest)),
            'ticker': str(self.stock_ticker),
            'remaining_holding': str(self.units_held),
            'remaining_holding_value': str(self.remaining_value_pence),
        }

    @property
    def hl_vt(self):
        return self._hl_vt

    @property
    def stock_ticker(self):
        return self._stock_ticker

    @property
    def security_name(self):
        return self._security_name

    @property
    def sedol_code(self):
        return self._sedol_code

    @property
    def account_id(self):
        return self._account_id

    @property
    def total_cash_available(self):
        return self._total_cash_available

    @property
    def bid_price(self):
        return self._bid_price

    @property
    def units_held(self):
        return self._units_held

    @property
    def value_gbp(self):
        return self._value_gbp

    @property
    def remaining_value_pence(self):
        return int(self._value_gbp * 100)

    @property
    def isin_code(self):
        return self._isin_code

    @property
    def epic_code(self):
        return self._epic_code

    @property
    def currency_code(self):
        return self._currency_code

    @property
    def exchange(self):
        return self._exchange

    @property
    def fixed_interest(self):
        return self._fixed_interest

    @property
    def category_code(self):
        return self._category_code


class MarketOrder():
    _position: MarketOrderPosition
    _position_type: OrderPositionType
    _amount_type: OrderAmountType
    _quantity: float
    _including_charges: bool

    def __init__(self,
                 position: MarketOrderPosition,
                 position_type: OrderPositionType,
                 amount_type: OrderAmountType,
                 quantity: float,
                 including_charges: bool = False):
        self._position = position
        self._position_type = position_type
        self._amount_type = amount_type
        self._quantity = quantity
        self._including_charges = including_charges

    def as_form_fields(self) -> dict:
        position_fields = self._position.as_form_fields()

        buy_fields = {
            'bs': self._position_type.value,
            'quantity': str(self.quantity),
            'qs': self._amount_type.value
        }
        if self._amount_type == OrderAmountType.Value:
            buy_fields['inc_chrgs'] = '1' if self.including_charges else '0'

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
    def hl_vt(self):
        return self._position.hl_vt

    @property
    def sedol(self):
        return self._position.sedol_code

    @property
    def category_code(self):
        return self._position.category_code

    @property
    def including_charges(self):
        return self._including_charges


class MarketOrderQuote():
    _session_hl_vt: str
    _hl_vt: str
    _sedol_code: str
    _number_of_shares: float
    _price: str
    _share_value: float
    _ptm_levy: float
    _commission: float
    _stamp_duty: float
    _settlement_date: datetime.date
    _total_trade_value: float
    _exchange_rate: float
    _conversion_price: float
    _conversion_sub_total: float
    _fx_charge: float
    category_code: str

    def __init__(self,
                 session_hl_vt: str,
                 hl_vt: str,
                 sedol_code: str,
                 number_of_shares: float,
                 price: str,
                 share_value: Optional[float],
                 ptm_levy: Optional[float],
                 commission: float,
                 stamp_duty: Optional[float],
                 settlement_date: datetime.date,
                 total_trade_value: float,
                 exchange_rate: Optional[float],
                 conversion_price: Optional[float],
                 conversion_sub_total: Optional[float],
                 fx_charge: Optional[float],
                 category_code: str
                 ):
        """
        :param session_hl_vt: str - The security code to be used for session keepalive
        :param hl_vt: str - The security code
        :param sedol_code: str B6QH1J2
        :param number_of_shares: float.  The number of shares being traded
        :param price: str.  The price in pence which they are being traded at - i.e. 18.454p
        :param share_value: float The amount in GBP of the shares being traded
        :param ptm_levy: float Panel of Takeovers and Mergers Levy is a ??1 government levy that is automatically charged
            to investors when they buy or sell shares for more than ??10k
        :param commission: float The commission HL will take for the trade in GBP
        :param stamp_duty: float The amount of stamp duty chargeable
        :param settlement_date: datetime.date The date the trade will be settled
        :param total_trade_value: The total amount of the trade, including share_value and all taxes and fees
        """
        self._session_hl_vt = session_hl_vt
        self._hl_vt = hl_vt
        self._sedol_code = sedol_code
        self._number_of_shares = number_of_shares
        self._price = price
        self._share_value = share_value
        self._ptm_levy = ptm_levy
        self._commission = commission
        self._stamp_duty = stamp_duty
        self._settlement_date = settlement_date
        self._total_trade_value = total_trade_value
        self._exchange_rate = exchange_rate
        self._conversion_price = conversion_price
        self._conversion_sub_total = conversion_sub_total
        self._fx_charge = fx_charge
        self._category_code = category_code

    @property
    def session_hl_vt(self):
        return self._session_hl_vt

    @property
    def hl_vt(self):
        return self._hl_vt

    @property
    def sedol_code(self):
        return self._sedol_code

    @property
    def number_of_shares(self):
        return self._number_of_shares

    @property
    def price(self):
        return self._price

    @property
    def share_value(self):
        return self._share_value

    @property
    def ptm_levy(self):
        return self._ptm_levy

    @property
    def commission(self):
        return self._commission

    @property
    def stamp_duty(self):
        return self._stamp_duty

    @property
    def settlement_date(self):
        return self._settlement_date

    @property
    def total_trade_value(self):
        return self._total_trade_value

    @property
    def exchange_rate(self):
        return self._exchange_rate

    @property
    def conversion_price(self):
        return self._conversion_price

    @property
    def conversion_sub_total(self):
        return self._conversion_sub_total

    @property
    def fx_charge(self):
        return self._fx_charge

    @property
    def category_code(self):
        return self._category_code

    def __str__(self):
        return f"""MarketOrderQuote[
            session_hl_vt={self.session_hl_vt},
            hl_vt={self.hl_vt},
            sedol_code={self.sedol_code},
            number_of_shares={self.number_of_shares},
            price={self.price},
            share_value={self.share_value},
            ptm_levy={self.ptm_levy},
            commission={self.commission}, 
            stamp_duty={self.stamp_duty},
            settlement_date={self.settlement_date},
            total_trade_value={self.total_trade_value},
            exchange_rate={self.exchange_rate},
            conversion_price={self.conversion_price},
            conversion_sub_total={self.conversion_sub_total},
            fx_charge={self.fx_charge},
            category_code={self.category_code}
        ]"""


class MarketOrderConfirmation(IOrderConfirmation):
    _sedol_code: str
    _number_of_shares: float
    _price: str
    _share_value: float
    _ptm_levy: float
    _commission: float
    _stamp_duty: float
    _settlement_date: datetime.date
    _total_trade_value: float
    _exchange_rate: float
    _conversion_price: float
    _conversion_sub_total: float
    _fx_charge: float
    category_code: str

    def __init__(self,
                 sedol_code: str,
                 number_of_shares: float,
                 price: str,
                 share_value: Optional[float],
                 ptm_levy: Optional[float],
                 commission: float,
                 stamp_duty: Optional[float],
                 settlement_date: datetime.date,
                 total_trade_value: float,
                 exchange_rate: Optional[float],
                 conversion_price: Optional[float],
                 conversion_sub_total: Optional[float],
                 fx_charge: Optional[float],
                 category_code: str
                 ):
        self._sedol_code = sedol_code
        self._number_of_shares = number_of_shares
        self._price = price
        self._share_value = share_value
        self._ptm_levy = ptm_levy
        self._commission = commission
        self._stamp_duty = stamp_duty
        self._settlement_date = settlement_date
        self._total_trade_value = total_trade_value
        self._exchange_rate = exchange_rate
        self._conversion_price = conversion_price
        self._conversion_sub_total = conversion_sub_total
        self._fx_charge = fx_charge
        self._category_code = category_code

    @property
    def sedol_code(self):
        return self._sedol_code

    @property
    def number_of_shares(self):
        return self._number_of_shares

    @property
    def price(self):
        return self._price

    @property
    def share_value(self):
        return self._share_value

    @property
    def ptm_levy(self):
        return self._ptm_levy

    @property
    def commission(self):
        return self._commission

    @property
    def stamp_duty(self):
        return self._stamp_duty

    @property
    def settlement_date(self):
        return self._settlement_date

    @property
    def total_trade_value(self):
        return self._total_trade_value

    @property
    def exchange_rate(self):
        return self._exchange_rate

    @property
    def conversion_price(self):
        return self._conversion_price

    @property
    def conversion_sub_total(self):
        return self._conversion_sub_total

    @property
    def fx_charge(self):
        return self._fx_charge

    @property
    def category_code(self):
        return self._category_code

    def __str__(self):
        return f"""MarketOrderConfirmation[
            sedol_code={self.sedol_code},
            number_of_shares={self.number_of_shares},
            price={self.price},
            share_value={self.share_value},
            ptm_levy={self.ptm_levy},
            commission={self.commission}, 
            stamp_duty={self.stamp_duty},
            settlement_date={self.settlement_date},
            total_trade_value={self.total_trade_value},
            exchange_rate={self.exchange_rate},
            conversion_price={self.conversion_price},
            conversion_sub_total={self.conversion_sub_total},
            fx_charge={self.fx_charge},
            category_code={self.category_code}
        ]"""
