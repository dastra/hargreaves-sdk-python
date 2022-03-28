import logging
import traceback
from pathlib import Path

from hargreaves.account import AccountType
from hargreaves.config.loader import ConfigLoader
from hargreaves.journey.clients import WebSessionManagerFactory
from hargreaves.utils.logging import LoggerFactory

if __name__ == '__main__':

    logger = LoggerFactory.configure(logging.DEBUG)

    config = ConfigLoader().load_api_config(str(Path(__file__).parent) + "/secrets.json")

    web_session_manager = WebSessionManagerFactory.create_with_file_storage()
    try:
        web_session_manager.start_session(config)
        accounts = web_session_manager.get_account_summary()

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        pending_orders = web_session_manager.get_pending_orders(sipp.account_id)
        print(f"Returned {len(pending_orders)} pending order(s) ...")

        for pending_order in pending_orders:
            print(pending_order)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
