import logging
import traceback
from pathlib import Path

from hargreaves.config.loader import ConfigLoader
from hargreaves.journey.clients import WebSessionManagerFactory
from hargreaves.search import InvestmentTypes
from hargreaves.utils.logging import LoggerFactory

if __name__ == '__main__':

    logger = LoggerFactory.configure(logging.DEBUG)

    config = ConfigLoader().load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # UK
    stock_ticker = 'PDG'
    investment_types = [InvestmentTypes.SHARES]

    # US
    # stock_ticker = 'TUSK'
    # investment_types = [InvestmentTypes.OVERSEAS]

    # US, SEARCH ALL
    # stock_ticker = 'FB'
    # investment_types = InvestmentTypes.ALL

    web_session_manager = WebSessionManagerFactory.create_with_file_storage()
    try:
        web_session_manager.start_session(config)
        accounts = web_session_manager.get_account_summary()

        search_result = web_session_manager.search_security(stock_ticker, investment_types)
        print(f"Found {len(search_result)} results")
        for search_result in search_result:
            print(search_result)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
