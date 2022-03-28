import logging
import traceback
from pathlib import Path

from hargreaves import journey
from hargreaves.accounts import AccountType

from hargreaves.config import load_api_config
from hargreaves.utils.logging import LogHelper

if __name__ == '__main__':

    logger = LogHelper.configure(logging.DEBUG)

    config = load_api_config(str(Path(__file__).parent) + "/secrets.json")

    web_session_manager = journey.create_default_session_manager()
    try:
        web_session_manager.start_session(config)
        accounts = web_session_manager.get_account_summary()

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        while True:
            pending_orders = web_session_manager.get_pending_orders(sipp.account_id)
            print(f"Returned {len(pending_orders)} pending order(s) ...")
            if (len(pending_orders) == 0):
                break
            for pending_order in pending_orders:
                print(pending_order)

            web_session_manager.cancel_pending_order(cancel_order_id=pending_orders[0].order_id,
                                                     pending_orders=pending_orders)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
