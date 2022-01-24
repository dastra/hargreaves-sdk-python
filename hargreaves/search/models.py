class InvestmentTypes:
    SHARES = 'shares'           # Shares & other stocks
    OVERSEAS = 'overseas'       # Overseas stocks
    FUNDS = 'funds'             # Funds
    ETFS = 'etfs'               # ETFs

    ALL = [OVERSEAS, FUNDS, ETFS, SHARES]


class SearchResult:
    __stock_ticker: str
    __security_name: str
    __sedol_code: str
    __internet_allowed: bool
    __category: str

    def __init__(self, stock_ticker: str, security_name: str, sedol_code: str, internet_allowed: bool,
                 category: str):
        """
        :param stock_ticker: str - the stock symbol.  i.e. GOOG
        :param security_name: str - the name, i.e. "Alphabet Inc NPV A *R"
        :param sedol_code: str - the SEDOL code of the stock, i.e. BYVY8G0
        :param internet_allowed: bool - whether it can be traded online
        :param category: str - The category of the investment
        """
        self.__stock_ticker = stock_ticker
        self.__security_name = security_name
        self.__sedol_code = sedol_code
        self.__internet_allowed = internet_allowed
        self.__category = category

    @property
    def stock_ticker(self):
        return self.__stock_ticker

    @property
    def security_name(self):
        return self.__security_name

    @property
    def sedol_code(self):
        return self.__sedol_code

    @property
    def internet_allowed(self):
        return self.__internet_allowed

    @property
    def category(self):
        return self.__category
