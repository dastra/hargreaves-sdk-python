import logging
import traceback
from pathlib import Path

from hargreaves.account import AccountType
from hargreaves.config.loader import ConfigLoader
from hargreaves.journey.clients import WebSessionManagerFactory
from hargreaves.search import InvestmentTypes
from hargreaves.trade.market.models import MarketBuyOrder
from hargreaves.utils.logging import LoggerFactory

if __name__ == '__main__':

    logger = LoggerFactory.create(logging.DEBUG)

    config = ConfigLoader(logger).load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # US
    # stock_ticker = 'TUSK'
    # stock_quantity = 50  # +/- £86.19 @ 2.09 USD
    # investment_types = [InvestmentTypes.OVERSEAS]

    # UK
    stock_ticker = 'PDG'
    stock_quantity = 200  # +/- £49.87 @ 21.852p
    investment_types = [InvestmentTypes.SHARES]

    web_session_manager = WebSessionManagerFactory.create_with_file_storage(logger)
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

        # navigate to the security and select the account
        deal_info = web_session_manager.get_market_order_info(account_id=account_id,
                                                              sedol_code=sedol_code, category_code=category_code)
        print(deal_info.as_form_fields())

        # Get a quote
        deal = MarketBuyOrder(order_info=deal_info, quantity=stock_quantity,
                              shares_or_value=MarketBuyOrder.SHARE_QUANTITY)
        price_quote = web_session_manager.get_market_order_quote(deal)
        print(price_quote)

        # Confirm deal
        deal_confirmation = web_session_manager.execute_market_order(price_quote)
        print(deal_confirmation)

    except Exception as ex:
        logger.error(traceback.print_exc())
    finally:
        web_session_manager.stop_session()
        web_session_manager.convert_HAR_to_markdown()