from pathlib import Path

from hargreaves.authentication import *
from hargreaves.account import *
from hargreaves.config import *

if __name__ == '__main__':
    config = load_api_config(str(Path(__file__).parent) + "/secrets.json")

    # Log in
    session = login(config)

    # Lists all of your accounts - i.e. SIPP, ISA.
    session, accounts = list_accounts(session)

    for account_summary in accounts:
        # Fetches information in my-accounts page
        account_detail = get_account_detail(session, account_summary)
        print(f'Your {account_detail.account_type} is worth {account_detail.total_value} with the following holdings:')
        for investment in account_detail.investments:
            print(f'\tYou hold {investment.units_held} units of {investment.stock_name} worth {investment.value_gbp}')

    # If you're running this in a long running server environment,
    # make sure to log out to avoid session expiration errors
    logout(session)