import logging
import traceback
from pathlib import Path

from requests_tracker import storage
from requests_tracker.storage import CookiesFileStorage

from hargreaves import config, session, account, search, orders
from hargreaves.account import AccountType
from hargreaves.orders.manual.models import ManualOrder
from hargreaves.orders.models import OrderPositionType, OrderAmountType
from hargreaves.search import InvestmentTypes
from hargreaves.utils.logs import LogHelper

"""
WARNING: This is a test script for manual (fill-or-kill) orders OUT-OF-HOURS - running this inside trading hours
may cause issues. 

It is recommended to use the "deal_execute.py" script for ad-hoc buy/sell transactions as it executes orders similar
to the website (first attempts market orders and then fails over to manual (fill-or-kill) orders if applicable).
"""

if __name__ == '__main__':

    logger = LogHelper.configure(logging.DEBUG)

    # load api config
    config = config.load_api_config(str(Path(__file__).parent) + "/secrets.json")
    # create logged-in web session (+ load previous cookies file):
    session_cache_path = Path(__file__).parent.parent.parent.joinpath('session_cache')
    cookies_storage = CookiesFileStorage(session_cache_path)
    web_session = session.create_session(cookies_storage, config)

    # UK - BUY
    # stock_ticker = 'PDG'
    # position_type = OrderPositionType.Buy
    # amount_type = OrderAmountType.Quantity
    # stock_quantity = 200  # +/- £49.87 @ 21.852p
    # investment_types = [InvestmentTypes.SHARES]

    # UK - SELL
    # stock_ticker = 'PDG'
    # position_type = OrderPositionType.Sell
    # amount_type = OrderAmountType.Quantity
    # stock_quantity = 200  # +/- £49.87 @ 21.852p
    # investment_types = [InvestmentTypes.SHARES]

    # US - BUY
    stock_ticker = 'TUSK'
    position_type = OrderPositionType.Buy
    amount_type = OrderAmountType.Quantity
    stock_quantity = 50  # +/- £86.19 @ 2.09 USD
    investment_types = [InvestmentTypes.OVERSEAS]

    # US - SELL
    # stock_ticker = 'TUSK'
    # position_type = OrderPositionType.Sell
    # amount_type = OrderAmountType.Quantity
    # stock_quantity = 50  # +/- £86.19 @ 2.09 USD
    # investment_types = [InvestmentTypes.OVERSEAS]

    try:
        # get account (and login if required)
        accounts = account.get_account_summary(web_session=web_session)

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        # search security
        search_result = search.investment_search(
            web_session=web_session,
            search_string=stock_ticker,
            investment_types=investment_types)

        print(f"Found {len(search_result)} results")
        if len(search_result) != 1:
            raise Exception(f"Unexpected number {(len(search_result))} of securities found!")

        print(search_result[0])

        account_id = sipp.account_id
        sedol_code = search_result[0].sedol_code
        category_code = search_result[0].category

        # get current position
        current_position = orders.manual.get_current_position(
            web_session=web_session,
            account_id=account_id,
            sedol_code=sedol_code,
            category_code=category_code)

        print(current_position.as_form_fields())

        order = ManualOrder(
            position=current_position,
            position_type=position_type,
            amount_type=amount_type,
            quantity=stock_quantity,
            limit=None)

        # submit order
        order_confirmation = orders.manual.submit_order(
            web_session=web_session,
            order=order)

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
