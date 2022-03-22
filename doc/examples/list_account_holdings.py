import logging
from pathlib import Path

from hargreaves.config.loader import ConfigLoader
from hargreaves.journey.clients import WebSessionManagerFactory
from hargreaves.utils.logging import LoggerFactory

if __name__ == '__main__':

    logger = LoggerFactory.create(logging.DEBUG)

    config = ConfigLoader(logger).load_api_config(str(Path(__file__).parent) + "/secrets.json")

    web_session_manager = WebSessionManagerFactory.create_with_file_storage(logger)
    try:
        web_session_manager.start_session(config)
        accounts = web_session_manager.get_account_summary()
        for account_summary in accounts:
            # Fetches information in my-accounts page
            print(account_summary)
        for account_summary in accounts:
            # Fetches information in my-accounts page
            account_detail = web_session_manager.get_account_detail(account_summary)
            print(f'Your {account_detail.account_type} is worth {account_detail.total_value} with the following '
                  f'holdings:')
            for investment in account_detail.investments:
                print(f'\tYou hold {investment.units_held} units of {investment.security_name} worth {investment.value_gbp}')

    except Exception as ex:
        logger.error(ex)
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
