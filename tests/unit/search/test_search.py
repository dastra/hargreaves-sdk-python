from pathlib import Path

import requests
import requests_mock

from hargreaves.search.clients import parse_search_results, investment_search
from hargreaves.search.models import InvestmentTypes


def test_send_search_request():
    session = requests.Session()
    search_string = 'GOOG'
    investment_types = [InvestmentTypes.SHARES]
    excl_investment_types = ",".join([InvestmentTypes.OVERSEAS, InvestmentTypes.FUNDS, InvestmentTypes.ETFS])
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    with requests_mock.Mocker() as mock_request:
        mock_request.get(
            f'https://online.hl.co.uk/ajaxx/stocks.php?sq={search_string}&filters={excl_investment_types}&offset=0'
            f'&instance=&format=jsonp',
            text=search_results_found_jsonp
        )

        search_results = investment_search(session, search_string, investment_types)

        assert len(search_results) == 2


def test_parse_search_results_found():
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    search_results = parse_search_results(search_results_found_jsonp)

    assert len(search_results) == 2

    goog = search_results[0]

    assert goog.stock_ticker == 'GOOG'
    assert goog.stock_name == 'Alphabet Inc NPV C'
    assert goog.sedol_code == 'BYY88Y7'
    assert goog.internet_allowed
    assert goog.category == 'O'


def test_parse_search_results_not_found():
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-not-found.jsonp').read_text()

    search_results = parse_search_results(search_results_found_jsonp)

    assert len(search_results) == 0
