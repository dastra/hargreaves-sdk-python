import http
from pathlib import Path

from hargreaves.search.clients import parse_search_results, SecuritySearchClient
from hargreaves.search.models import InvestmentTypes
from hargreaves.utils.logging import LoggerFactory
from hargreaves.utils.timings import MockTimeService
from hargreaves.web.mocks import MockWebSession


def test_send_search_request():
    search_string = 'GOOG'
    investment_types = [InvestmentTypes.SHARES]
    excl_investment_types = ",".join([InvestmentTypes.OVERSEAS, InvestmentTypes.FUNDS, InvestmentTypes.ETFS])
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found.jsonp').read_text()

    with MockWebSession() as web_session:
        logger = LoggerFactory.create_std_out()
        time_service = MockTimeService()

        web_session.mock_get(
            url='https://online.hl.co.uk/ajaxx/stocks.php',
            params={
                # 'pid': time.time_ns(),
                'pid': time_service.get_current_time_as_epoch_time(),
                'sq': search_string,
                'filters': excl_investment_types,
                'offset': 0,
                'instance': '',
                'format': 'jsonp'
            },
            headers={
                'Referer': 'https://online.hl.co.uk/my-accounts/stock_and_fund_search/action/deal'
            },
            text=search_results_found_jsonp,
            status_code=http.HTTPStatus.OK
        )

        client = SecuritySearchClient(logger, web_session, time_service)
        search_results = client.investment_search(search_string, investment_types)

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
    search_results_found_jsonp = Path(Path(__file__).parent / 'files/search-results-found-without-stock-ticker.jsonp')\
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
