import logging
import traceback
from pathlib import Path

from hargreaves.account import AccountType
from hargreaves.config.loader import ConfigLoader
from hargreaves.journey.clients import WebSessionManagerFactory
from hargreaves.trade.models import OrderPositionType, DealRequest
from hargreaves.utils.logging import LoggerFactory

if __name__ == '__main__':

    logger = LoggerFactory.create(logging.DEBUG)

    config = ConfigLoader(logger).load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # UK
    stock_ticker = 'PDG'
    position_type = OrderPositionType.Sell
    position_percentage = 50.00
    allow_fill_or_kill = True

    # US
    # stock_ticker = 'TUSK'
    # position_type = OrderPositionType.Buy
    # position_percentage = 0.5
    # allow_fill_or_kill = True

    web_session_manager = WebSessionManagerFactory.create_with_file_storage(logger)
    try:
        web_session_manager.start_session(config)

        # get account (and login if required)
        accounts = web_session_manager.get_account_summary()

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

        # execute
        order_confirmation = web_session_manager.execute_smart_deal(deal_request)
        print(order_confirmation)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session(config)
        web_session_manager.convert_HAR_to_markdown()
