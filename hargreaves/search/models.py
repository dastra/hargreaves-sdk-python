class InvestmentTypes:
    SHARES = 'shares'           # Shares & other stocks
    OVERSEAS = 'overseas'       # Overseas stocks
    FUNDS = 'funds'             # Funds
    ETFS = 'etfs'               # ETFs

    ALL = (OVERSEAS, FUNDS, ETFS, SHARES)


class InvestmentCategoryTypes:
    OVERSEAS = 'O'
    EQUITIES = 'E'
    TRUSTS = 'H'  # not sure about this one, saw it one "ASCI", seems to use normal "equity" page


class SearchResult:
    _stock_ticker: str
    _security_name: str
    _sedol_code: str
    _internet_allowed: bool
    _category: str

    def __init__(self, stock_ticker: str, security_name: str, sedol_code: str, internet_allowed: bool,
                 category: str):
        """
        :param stock_ticker: str - the stock symbol.  i.e. GOOG
        :param security_name: str - the name, i.e. "Alphabet Inc NPV A *R"
        :param sedol_code: str - the SEDOL code of the stock, i.e. BYVY8G0
        :param internet_allowed: bool - whether it can be traded online
        :param category: str - The category of the investment
        """
        self._stock_ticker = stock_ticker
        self._security_name = security_name
        self._sedol_code = sedol_code
        self._internet_allowed = internet_allowed
        self._category = category

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
    def internet_allowed(self):
        return self._internet_allowed

    @property
    def category(self):
        return self._category

    def __str__(self):
        return f"""SearchResult[stock_ticker={self._stock_ticker}, security_name={self._security_name},
        sedol_code={self._sedol_code}, internet_allowed={self._internet_allowed}, category={self._category}]"""
