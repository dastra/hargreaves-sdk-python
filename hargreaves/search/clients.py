import json
import logging
from typing import List

from hargreaves.request_tracker.session import IWebSession, WebRequestType
from .errors import SearchFilterError
from .models import InvestmentTypes, SearchResult
from ..utils import clock

logger = logging.getLogger(__name__)


class ISecuritySearchClient:

    def investment_search(self, web_session: IWebSession, search_string: str, investment_types: list) -> [SearchResult]:
        pass


class SecuritySearchClient(ISecuritySearchClient):

    def __init__(self):
        pass

    def investment_search(self, web_session: IWebSession, search_string: str, investment_types: list) -> [SearchResult]:

        logger.debug("Searching Securities ...")

        clock.sleep_random()

        # pid is the time in milliseconds since the epoch
        pid = clock.get_current_time_as_epoch_time()

        # roughly 10 seconds before PID (probably when search page was loaded)
        callback = f"jsonp{clock.get_current_time_as_epoch_time(offset_seconds=-10)}",

        # the filters param is actually a list of investment types to be excluded,
        # so we need to reverse what was passed in (except when it's ALL, then the filter is blank)
        type_excl = []
        if investment_types != InvestmentTypes.ALL:
            for inv_type in InvestmentTypes.ALL:
                if inv_type not in investment_types:
                    type_excl.append(inv_type)

        headers = {
            'Referer': 'https://online.hl.co.uk/my-accounts/stock_and_fund_search/action/deal'
        }

        results_jsonp = web_session.get(
            url=f'https://online.hl.co.uk/ajaxx/stocks.php',
            request_type=WebRequestType.XHR,
            params={
                'callback': callback,
                'pid': pid,
                'sq': search_string,
                'filters': ",".join(type_excl),
                'offset': 0,
                'instance': '',
                'format': 'jsonp'
            },
            headers=headers).text

        return parse_search_results(results_jsonp)


def parse_search_results(results_jsonp: str) -> [SearchResult]:
    results_json = results_jsonp.split("(", 1)[1].strip(")")  # convert to json, removing callback

    results = json.loads(results_json)

    srs = []
    for result in results['response']['docs']:
        stock_ticker = result['stock_ticker'] if 'stock_ticker' in result else result['epic']

        sr = SearchResult(stock_ticker=stock_ticker, security_name=result['identifier'],
                          sedol_code=result['id'],
                          internet_allowed=result['internet_allowed'] == 'Y', category=result['category'])
        srs.append(sr)

    return srs


def security_filter(search_results: List[SearchResult],
                    stock_ticker: str = None, sedol_code: str = None) -> SearchResult:
    current_results = search_results

    current_results = list(search_result for search_result in current_results
                           if
                           (stock_ticker is None or (search_result.stock_ticker.upper() == stock_ticker.upper()))
                           and
                           (sedol_code is None or (search_result.sedol_code.upper() == sedol_code.upper()))
                           )

    if len(current_results) != 1:
        raise SearchFilterError(f"Could not find security, results filtered to {len(current_results)}")

    return current_results[0]
