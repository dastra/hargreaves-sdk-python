import json
import time
import requests

from search.models import InvestmentTypes, SearchResult


def investment_search(session: requests.Session, search_string: str, investment_types: list) -> [SearchResult]:
    # pid is the time in milliseconds since the epoch
    pid = time.time_ns()
    # the filters param is actually a list of investment types to be excluded, so we need to reverse what was passed in.
    type_excl = []
    for inv_type in InvestmentTypes.ALL:
        if inv_type not in investment_types:
            type_excl.append(inv_type)

    results_jsonp = session.get(
        f'https://online.hl.co.uk/ajaxx/stocks.php?pid={pid}&sq={search_string}&filters={",".join(type_excl)}&offset'
        f'=0&instance=&format=jsonp').text

    return parse_search_results(results_jsonp)


def parse_search_results(results_jsonp: str) -> [SearchResult]:
    results_json = results_jsonp.split("(", 1)[1].strip(")")  # convert to json, removing callback

    results = json.loads(results_json)

    srs = []
    for result in results['response']['docs']:
        sr = SearchResult(stock_ticker=result['stock_ticker'], stock_name=result['identifier'], sedol_code=result['id'],
                          internet_allowed=result['internet_allowed'] == 'Y', category=result['category'])
        srs.append(sr)

    return srs
