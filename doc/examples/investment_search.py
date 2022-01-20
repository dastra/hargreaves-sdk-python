import requests

from hargreaves.search import *

if __name__ == '__main__':
    session = requests.Session()

    search_results = investment_search(session, search_string='GOOG', investment_types=[InvestmentTypes.OVERSEAS])

    print(f'There were {len(search_results)} results')