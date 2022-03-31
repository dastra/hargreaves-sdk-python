import logging
import traceback
from pathlib import Path

from requests_tracker import storage
from requests_tracker.storage import CookiesFileStorage

from hargreaves import config, session, account, deals
from hargreaves.account import AccountType
from hargreaves.deals.models import DealRequest
from hargreaves.orders.models import OrderPositionType
from hargreaves.utils.logs import LogHelper

"""
This is the main example for executing buy/sell transactions - instead of specific amounts it will calculate the 
order amount based on the relative percentage:
1) For buy orders this is the % relative to your total account amount (shares + cash)
2) For sell orders this is the % relative to the stock position
"""

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
    position_type = OrderPositionType.Sell
    position_percentage = 100.00
    allow_fill_or_kill = True

    # US
    # stock_ticker = 'TUSK'
    # position_type = OrderPositionType.Buy
    # position_percentage = 0.5
    # allow_fill_or_kill = True

    try:

        # get account (and login if required)
        accounts = account.get_account_summary(web_session=web_session)

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        # create deal request
        deal_request = DealRequest(
            stock_ticker=stock_ticker,
            account_id=sipp.account_id,
            position_type=position_type,
            position_percentage=position_percentage,
            allow_fill_or_kill=allow_fill_or_kill
        )

        # execute deal flow
        order_confirmation = deals.execute_deal(
            web_session=web_session,
            deal_request=deal_request
        )
        print(order_confirmation)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        # persist cookies to local file
        cookies_storage.save(web_session.cookies)
        # writes to 'session-cache/session-DD-MM-YYYY HH-MM-SS.har' file
        storage.write_HAR_to_local_file(session_cache_path, web_session.request_session_context)
        # converts HAR file to markdown file + response files in folder 'session-cache/session-DD-MM-YYYY HH-MM-SS/'
        storage.convert_HAR_to_markdown(session_cache_path, web_session.request_session_context)
