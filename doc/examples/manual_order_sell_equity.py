import logging
import traceback
from pathlib import Path

from hargreaves import journey
from hargreaves.accounts import AccountType

from hargreaves.config import load_api_config
from hargreaves.search import InvestmentTypes
from hargreaves.orders.manual.models import ManualOrder
from hargreaves.orders.models import OrderPositionType, OrderAmountType
from hargreaves.utils.logging import LogHelper

if __name__ == '__main__':

    logger = LogHelper.configure(logging.DEBUG)

    config = load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # UK
    # stock_ticker = 'PDG'
    # position_type = OrderPositionType.Sell
    # amount_type = OrderAmountType.Quantity
    # stock_quantity = 200  # +/- £49.87 @ 21.852p
    # investment_types = [InvestmentTypes.SHARES]

    # US
    stock_ticker = 'BITF'
    position_type = OrderPositionType.Sell
    amount_type = OrderAmountType.Quantity
    stock_quantity = 50  # +/- £86.19 @ 2.09 USD
    investment_types = [InvestmentTypes.OVERSEAS]

    web_session_manager = journey.create_default_session_manager()
    try:
        web_session_manager.start_session(config)

        # get account (and login if required)
        accounts = web_session_manager.get_account_summary()

        # select the SIPP account
        sipp = next((account_summary for account_summary in accounts
                     if account_summary.account_type == AccountType.SIPP), None)

        # search security
        search_result = web_session_manager.search_security(stock_ticker, investment_types)
        print(f"Found {len(search_result)} results")
        if len(search_result) != 1:
            raise Exception(f"Unexpected number {(len(search_result))} of securities found!")

        print(search_result[0])

        account_id = sipp.account_id
        sedol_code = search_result[0].sedol_code
        category_code = search_result[0].category

        # get current position
        current_position = web_session_manager.get_manual_order_position(account_id=account_id,
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
        order_confirmation = web_session_manager.submit_manual_order(order)
        print(order_confirmation)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
