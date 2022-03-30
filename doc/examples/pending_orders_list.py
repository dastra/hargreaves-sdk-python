import logging
import traceback
from pathlib import Path

from requests_tracker import storage
from requests_tracker.storage import CookiesFileStorage

from hargreaves import config, session, account, orders
from hargreaves.account import AccountType

from hargreaves.utils.logs import LogHelper

if __name__ == '__main__':

    logger = LogHelper.configure(logging.DEBUG)

    # load api config
    config = config.load_api_config(str(Path(__file__).parent) + "/secrets.json")
    # create logged-in web session (+ load previous cookies file):
    session_cache_path = Path(__file__).parent.parent.parent.joinpath('session_cache')
    cookies_storage = CookiesFileStorage(session_cache_path)
    web_session = session.create_session(cookies_storage, config)

    try:
        accounts = account.get_account_summary(web_session=web_session)

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        pending_orders = orders.pending.get_pending_orders(
            web_session=web_session,
            account_id=sipp.account_id)

        print(f"Returned {len(pending_orders)} pending order(s) ...")

        for pending_order in pending_orders:
            print(pending_order)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        # persist cookies to local file
        cookies_storage.save(web_session.cookies)
        # writes to 'session-cache/session-DD-MM-YYYY HH-MM-SS.har' file
        storage.write_HAR_to_local_file(session_cache_path, web_session.request_session_context)
        # converts HAR file to markdown file + response files in folder 'session-cache/session-DD-MM-YYYY HH-MM-SS/'
        storage.convert_HAR_to_markdown(session_cache_path, web_session.request_session_context)
