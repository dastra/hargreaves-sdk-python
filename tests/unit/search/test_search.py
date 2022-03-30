import http
from pathlib import Path

import pytest

from hargreaves.search.clients import parse_search_results, SecuritySearchClient, security_filter
from hargreaves.search.errors import SearchFilterError
from hargreaves.search.models import InvestmentTypes, SearchResult, InvestmentCategoryTypes
from hargreaves.utils import clock
from hargreaves.utils.logs import LogHelper
from requests_tracker.mocks import MockWebSession

LogHelper.configure_std_out()
clock.freeze_time()


class SearchResultBuilder():
    _stock_ticker: str
    _security_name: str
    _sedol_code: str
    _internet_allowed: bool
    _category: str

    def __init__(self):
        pass

    def with_overseas(self, stock_ticker: str, security_name: str, sedol_code: str):
        self._stock_ticker = stock_ticker
        self._security_name = security_name
        self._sedol_code = sedol_code
        self._internet_allowed = True
        self._category = InvestmentCategoryTypes.OVERSEAS
        return self

    def with_equity(self, stock_ticker: str, security_name: str, sedol_code: str):
        self._stock_ticker = stock_ticker
        self._security_name = security_name
        self._sedol_code = sedol_code
        self._internet_allowed = True
        self._category = InvestmentCategoryTypes.EQUITIES
        return self

    def build(self) -> SearchResult:
        return SearchResult(
            stock_ticker=self._stock_ticker,
            security_name=self._security_name,
            sedol_code=self._sedol_code,
            internet_allowed=self._internet_allowed,
            category=self._category
        )


def test_submit_search_request_for_shares():
    search_string = 'GOOG'
    investment_types = [InvestmentTypes.SHARES]
    excl_investment_types = ",".join([InvestmentTypes.OVERSEAS, InvestmentTypes.FUNDS, InvestmentTypes.ETFS,
                                      InvestmentTypes.BONDS_AND_GILTS])
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    with MockWebSession() as web_session:

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/stocks.php',
            params={
                'callback': f"jsonp{clock.get_current_time_as_epoch_time(offset_seconds=-10)}",
                'pid': clock.get_current_time_as_epoch_time(),
                'sq': search_string,
                'filters': excl_investment_types,
                'offset': 0,
                'instance': '',
                'format': 'jsonp'
            },
            headers={
                'Referer': 'https://online.hl.co.uk/my-accounts/stock_and_fund_search/action/deal'
            },
            response_text=search_results_found_jsonp,
            status_code=http.HTTPStatus.OK
        )

        client = SecuritySearchClient()
        search_results = client.investment_search(
            web_session=web_session,
            search_string=search_string,
            investment_types=investment_types)

        assert len(search_results) == 2


def test_submit_search_request_for_all():
    search_string = 'GOOG'
    investment_types = InvestmentTypes.ALL
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    with MockWebSession() as web_session:

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/stocks.php',
            params={
                'callback': f"jsonp{clock.get_current_time_as_epoch_time(offset_seconds=-10)}",
                'pid': clock.get_current_time_as_epoch_time(),
                'sq': search_string,
                'filters': '',
                'offset': 0,
                'instance': '',
                'format': 'jsonp'
            },
            headers={
                'Referer': 'https://online.hl.co.uk/my-accounts/stock_and_fund_search/action/deal'
            },
            response_text=search_results_found_jsonp,
            status_code=http.HTTPStatus.OK
        )

        client = SecuritySearchClient()
        search_results = client.investment_search(
            web_session=web_session,
            search_string=search_string,
            investment_types=investment_types)

        assert len(search_results) == 2


def test_parse_search_results_found():
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    search_results = parse_search_results(search_results_found_jsonp)

    assert len(search_results) == 2

    goog = search_results[0]

    assert goog.stock_ticker == 'GOOG'
    assert goog.security_name == 'Alphabet Inc NPV C'
    assert goog.sedol_code == 'BYY88Y7'
    assert goog.internet_allowed
    assert goog.category == 'O'


def test_parse_search_results_found_without_stock_ticker():
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found-without-stock-ticker.jsonp') \
        .read_text()

    search_results = parse_search_results(search_results_found_jsonp)

    assert len(search_results) == 1

    pdg = search_results[0]

    assert pdg.stock_ticker == 'PDG'
    assert pdg.security_name == 'Pendragon Ordinary 5p'
    assert pdg.sedol_code == 'B1JQBT1'
    assert pdg.internet_allowed
    assert pdg.category == 'E'


def test_parse_search_results_not_found():
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-not-found.jsonp').read_text()

    search_results = parse_search_results(search_results_found_jsonp)

    assert len(search_results) == 0


def test_security_filter_by_stock_ticker():
    search_results = [
        SearchResultBuilder().with_overseas(stock_ticker='FB',
                                            security_name='Meta Platforms Inc Com USD0.000006',
                                            sedol_code='B7TL820').build(),
        SearchResultBuilder().with_equity(stock_ticker='FBH',
                                          security_name='FBD Holdings plc Ordinary EUR0.60',
                                          sedol_code='0329028').build(),
        SearchResultBuilder().with_equity(stock_ticker='2FB',
                                          security_name='Leverage Shares Plc 2X Facebook ETP 03/04/67 GBP',
                                          sedol_code='BYX84Z1').build()
    ]

    assert security_filter(search_results=search_results, stock_ticker='FB').stock_ticker == 'FB'
    # assert security_filter(search_results=search_results, stock_ticker='BLAH') is None


def test_security_filter_by_sedol_code():
    search_results = [
        SearchResultBuilder().with_overseas(stock_ticker='FB',
                                            security_name='Meta Platforms Inc Com USD0.000006',
                                            sedol_code='B7TL820').build(),
        SearchResultBuilder().with_equity(stock_ticker='FBH',
                                          security_name='FBD Holdings plc Ordinary EUR0.60',
                                          sedol_code='0329028').build(),
        SearchResultBuilder().with_equity(stock_ticker='2FB',
                                          security_name='Leverage Shares Plc 2X Facebook ETP 03/04/67 GBP',
                                          sedol_code='BYX84Z1').build()
    ]

    assert security_filter(search_results=search_results, sedol_code='0329028').stock_ticker == 'FBH'
    # assert security_filter(search_results=search_results, sedol_code='BLAH') is None


def test_security_filter_by_stock_ticker_and_sedol_code():
    search_results = [
        SearchResultBuilder().with_overseas(stock_ticker='FB',
                                            security_name='Meta Platforms Inc Com USD0.000006',
                                            sedol_code='B7TL820').build(),
        SearchResultBuilder().with_equity(stock_ticker='FBH',
                                          security_name='FBD Holdings plc Ordinary EUR0.60',
                                          sedol_code='0329028').build(),
        SearchResultBuilder().with_equity(stock_ticker='2FB',
                                          security_name='Leverage Shares Plc 2X Facebook ETP 03/04/67 GBP',
                                          sedol_code='BYX84Z1').build()
    ]

    assert security_filter(search_results=search_results, stock_ticker='FB', sedol_code='B7TL820').stock_ticker == 'FB'


def test_security_filter_invalid_cases():
    search_results = [
        SearchResultBuilder().with_overseas(stock_ticker='FB',
                                            security_name='Meta Platforms Inc Com USD0.000006',
                                            sedol_code='B7TL820').build(),
        SearchResultBuilder().with_equity(stock_ticker='FBH',
                                          security_name='FBD Holdings plc Ordinary EUR0.60',
                                          sedol_code='0329028').build(),
        SearchResultBuilder().with_equity(stock_ticker='2FB',
                                          security_name='Leverage Shares Plc 2X Facebook ETP 03/04/67 GBP',
                                          sedol_code='BYX84Z1').build(),
        SearchResultBuilder().with_overseas(stock_ticker='2FB',
                                            security_name='Dummy Duplicate',
                                            sedol_code='123456').build(),

    ]

    with pytest.raises(SearchFilterError, match='Could not find security, results filtered to 0'):
        security_filter(search_results=search_results, stock_ticker='FB', sedol_code='XXX')
    with pytest.raises(SearchFilterError, match='Could not find security, results filtered to 0'):
        security_filter(search_results=search_results, stock_ticker='XXX')
    with pytest.raises(SearchFilterError, match='Could not find security, results filtered to 0'):
        security_filter(search_results=search_results, sedol_code='XXX')
    with pytest.raises(SearchFilterError, match='Could not find security, results filtered to 2'):
        security_filter(search_results=search_results, stock_ticker='2FB')
