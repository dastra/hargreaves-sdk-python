class AccountType:

    SIPP = 'SIPP'
    ISA = 'Stocks & Shares ISA'
    JUNIOR_ISA = 'Junior ISA'
    SHARE_ACCOUNT = 'Fund & Share Account'

    ALL = (SIPP, ISA, JUNIOR_ISA, SHARE_ACCOUNT)


class AccountSummary:
    _account_id: int
    _account_type: str

    def __init__(self, account_id: int, account_type: str):
        """
        :param int account_id: The id of the account - i.e. 40
        :param str account_type: The type of the account - i.e. SIPP
        """
        self._account_id = account_id
        self._account_type = account_type

    @property
    def account_id(self):
        return self._account_id

    @property
    def account_type(self):
        return self._account_type

    def __str__(self):
        return f"""AccountSummary[account_id={self._account_id}, account_type={self._account_type}]"""


class Investment:
    _stock_ticker: str
    _security_name: str
    _sedol_code: str
    _units_held: float
    _price_pence: float
    _value_gbp: float
    _cost_gbp: float
    _gain_loss_gbp: float
    _gain_loss_percentage: float

    def __init__(self, stock_ticker: str, security_name: str, sedol_code: str, units_held: float, price_pence: float,
                 value_gbp: float, cost_gbp: float, gain_loss_gbp: float, gain_loss_percentage: float):
        """
        :param stock_ticker: str - the stock symbol.  i.e. GOOG
        :param security_name: str - the name, i.e. "Alphabet Inc NPV A *R"
        :param sedol_code: str - the SEDOL code of the stock, i.e. BYVY8G0
        :param units_held: float - the number of units held.  You can hold fractional units in funds, hence is a float
        :param price_pence: float - the current price in pence
        :param value_gbp: float - the total value of the holding, in pounds
        :param cost_gbp: float - the cost of the holding, in pounds
        :param gain_loss_gbp: object - the gain or loss in pounds
        :param gain_loss_percentage: object - the gain or loss in %
        """
        self._stock_ticker = stock_ticker
        self._security_name = security_name
        self._sedol_code = sedol_code
        self._units_held = units_held
        self._price_pence = price_pence
        self._value_gbp = value_gbp
        self._cost_gbp = cost_gbp
        self._gain_loss_gbp = gain_loss_gbp
        self._gain_loss_percentage = gain_loss_percentage

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
    def units_held(self):
        return self._units_held

    @property
    def price_pence(self):
        return self._price_pence

    @property
    def value_gbp(self):
        return self._value_gbp

    @property
    def cost_gbp(self):
        return self._cost_gbp

    @property
    def gain_loss_gbp(self):
        return self._gain_loss_gbp

    @property
    def gain_loss_percentage(self):
        return self._gain_loss_percentage


class AccountDetail:
    __account_id: int
    __account_type: str
    __stock_value: float
    __total_cash: float
    __amount_available: float
    __total_value: float
    __investments: [Investment]

    def __init__(self, account_id: int, account_type: str, stock_value: float, total_cash: float,
                 amount_available: float, total_value: float, investments: [Investment]):
        """
        :param int account_id: The id of the account - i.e. 40
        :param str account_type: The type of the account - i.e. SIPP
        :param float stock_value: The value of total stock holdings
        :param float total_cash: Total cash held in account
        :param float amount_available: Amount available to invest
        :param float total_value: Total value of stock and cash
        :param [investments] investments: The list of current holdings
        """

        self.__account_id = account_id
        self.__account_type = account_type
        self.__stock_value = stock_value
        self.__total_cash = total_cash
        self.__amount_available = amount_available
        self.__total_value = total_value
        self.__investments = investments

    @property
    def account_id(self):
        return self.__account_id

    @property
    def account_type(self):
        return self.__account_type

    @property
    def stock_value(self):
        return self.__stock_value

    @property
    def total_cash(self):
        return self.__total_cash

    @property
    def amount_available(self):
        return self.__amount_available

    @property
    def total_value(self):
        return self.__total_value

    @property
    def investments(self):
        return self.__investments
