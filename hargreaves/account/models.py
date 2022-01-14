class AccountSummary:
    def __init__(self, account_id: int, account_type: str):
        """
        :param int account_id: The id of the account - i.e. 40
        :param str account_type: The type of the account - i.e. SIPP
        """
        self.__account_id = account_id
        self.__account_type = account_type

    @property
    def account_id(self):
        return self.__account_id

    @property
    def account_type(self):
        return self.__account_type


class Investment:
    __stock_symbol: str
    __stock_name: str
    __sedol_code: str
    __units_held: float
    __price_pence: float
    __value_gbp: float
    __cost_gbp: float
    __gain_loss_gbp: float
    __gain_loss_percentage: float

    def __init__(self, stock_symbol: str, stock_name: str, sedol_code: str, units_held: float, price_pence: float,
                 value_gbp: float, cost_gbp: float, gain_loss_gbp: float, gain_loss_percentage: float):
        """
        :param stock_symbol: str - the stock symbol.  i.e. GOOG
        :param stock_name: str - the name, i.e. "Alphabet Inc NPV A *R"
        :param sedol_code: str - the SEDOL code of the stock, i.e. BYVY8G0
        :param units_held: float - the number of units held.  You can hold fractional units in funds, hence is a float
        :param price_pence: float - the current price in pence
        :param value_gbp: float - the total value of the holding, in pounds
        :param cost_gbp: float - the cost of the holding, in pounds
        :param gain_loss_gbp: object - the gain or loss in pounds
        :param gain_loss_percentage: object - the gain or loss in %
        """
        self.__stock_symbol = stock_symbol
        self.__stock_name = stock_name
        self.__sedol_code = sedol_code
        self.__units_held = units_held
        self.__price_pence = price_pence
        self.__value_gbp = value_gbp
        self.__cost_gbp = cost_gbp
        self.__gain_loss_gbp = gain_loss_gbp
        self.__gain_loss_percentage = gain_loss_percentage

    @property
    def stock_symbol(self):
        return self.__stock_symbol

    @property
    def stock_name(self):
        return self.__stock_name

    @property
    def sedol_code(self):
        return self.__sedol_code

    @property
    def units_held(self):
        return self.__units_held

    @property
    def price_pence(self):
        return self.__price_pence

    @property
    def value_gbp(self):
        return self.__value_gbp

    @property
    def cost_gbp(self):
        return self.__cost_gbp

    @property
    def gain_loss_gbp(self):
        return self.__gain_loss_gbp

    @property
    def gain_loss_percentage(self):
        return self.__gain_loss_percentage


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
