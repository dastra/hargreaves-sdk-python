import logging
import traceback
from pathlib import Path

from requests_tracker import storage
from requests_tracker.storage import CookiesFileStorage

from hargreaves import config, session, search
from hargreaves.search import InvestmentTypes
from hargreaves.utils.logs import LogHelper

if __name__ == '__main__':

    logger = LogHelper.configure(logging.DEBUG)

    # load api config
    config = config.load_api_config(str(Path(__file__).parent) + "/secrets.json")
    # create logged-in web session (+ load previous cookies file):
    session_cache_path = Path(__file__).parent.parent.parent.joinpath('session_cache')
    cookies_storage = CookiesFileStorage(session_cache_path)
    web_session = session.create_session(cookies_storage, config)

    # UK
    stock_ticker = 'PDG'
    investment_types = [InvestmentTypes.SHARES]

    # US
    # stock_ticker = 'TUSK'
    # investment_types = [InvestmentTypes.OVERSEAS]

    # US, SEARCH ALL
    # stock_ticker = 'FB'
    # investment_types = InvestmentTypes.ALL

    try:

        search_result = search.investment_search(
            web_session=web_session,
            search_string=stock_ticker,
            investment_types=investment_types)

        print(f"Found {len(search_result)} results")
        for search_result in search_result:
            print(search_result)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        # persist cookies to local file
        cookies_storage.save(web_session.cookies)
        # writes to 'session-cache/session-DD-MM-YYYY HH-MM-SS.har' file
        storage.write_HAR_to_local_file(session_cache_path, web_session.request_session_context)
        # converts HAR file to markdown file + response files in folder 'session-cache/session-DD-MM-YYYY HH-MM-SS/'
        storage.convert_HAR_to_markdown(session_cache_path, web_session.request_session_context)
