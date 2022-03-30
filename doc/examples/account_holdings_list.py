import logging
import traceback
from pathlib import Path

from requests_tracker import storage
from requests_tracker.storage import CookiesFileStorage

from hargreaves import account, config, session
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
        for account_summary in accounts:
            # Fetches information in my-accounts page
            print(account_summary)
        for account_summary in accounts:
            # Fetches information in my-accounts page
            account_detail = account.get_account_detail(web_session=web_session, account_summary=account_summary)
            print(f'Your {account_detail.account_type} is worth {account_detail.total_value} with the following '
                  f'holdings:')
            for investment in account_detail.investments:
                print(f'\tYou hold {investment.units_held} units of {investment.security_name} '
                      f'worth {investment.value_gbp}')

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        # persist cookies to local file
        cookies_storage.save(web_session.cookies)
        # writes to 'session-cache/session-DD-MM-YYYY HH-MM-SS.har' file
        storage.write_HAR_to_local_file(session_cache_path, web_session.request_session_context)
        # converts HAR file to markdown file + response files in folder 'session-cache/session-DD-MM-YYYY HH-MM-SS/'
        storage.convert_HAR_to_markdown(session_cache_path, web_session.request_session_context)
