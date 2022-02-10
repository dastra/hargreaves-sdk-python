from pathlib import Path

from hargreaves.authentication import *
from hargreaves.account import *
from hargreaves.config import *
from hargreaves.trade import *

if __name__ == '__main__':
    config = load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # Log in
    session = login(config)

    # Lists all of your accounts - i.e. SIPP, ISA.
    session, accounts = list_accounts(session)
    sipp = next((account_summary for account_summary in accounts if account_summary.account_type == AccountType.SIPP),
                None)

    # Fetch the current price for this security
    session, deal_info = get_current_price(session, sipp.account_id, 'B6QH1J2')

    # Get a quote
    buy = Buy(deal_info=deal_info, quantity=100.00, shares_or_value=Buy.SHARE_VALUE, including_charges=True)
    session, price_quote = get_buy_quote(session=session, buy=buy)

    # Wait for confirmation
    print(f"You are about to buy {price_quote.number_of_shares} shares at {price_quote.price} with a total cost of "
          f"{price_quote.total_trade_value} including fees and charges.")

    key_pressed = input('Press Y and enter to continue, anything other key and enter to quit: ')
    if key_pressed == 'Y':
        # Buy it
        try:
            session, deal_confirmation = execute_deal(session=session, price_quote=price_quote)

            print(f"Success!  You just bought {deal_confirmation.number_of_shares} at {deal_confirmation.price} with "
                  f"a total cost of {deal_confirmation.total_trade_value} including fees and charges.")
        except DealFailedError as err:
            print(f"Deal failed with error: {err}")
    else:
        print("Exited without buying")

    # If you're running this in a long-running server environment,
    # make sure to log out to avoid session expiration errors
    logout(session)
