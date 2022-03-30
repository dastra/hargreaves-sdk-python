import csv
import re
from typing import List

from bs4 import BeautifulSoup
from io import StringIO

from ...account.models import AccountSummary, AccountDetail, Investment


def parse_account_list(my_accounts_html: str) -> List[AccountSummary]:
    accounts = []

    soup = BeautifulSoup(my_accounts_html, 'html.parser')
    rows = soup.select('table[class="accounts-table"] tbody tr')
    if len(rows) == 0:
        raise ValueError("List of accounts not present in response")

    for row in rows:
        # <a href="https://online.hl.co.uk/my-accounts/account_summary/account/26" title="View your SIPP"
        # class="product-name">SIPP<span class="arrow-icon"></span></a>
        anchor = row.select_one('td:nth-child(1) a')
        account_id = int(re.findall('.+?(\\d+)$', anchor['href'])[0])
        account_type = re.findall('View your (.+)$', anchor['title'])[0]

        accounts.append(AccountSummary(account_id=account_id, account_type=account_type))

    return accounts


def parse_account_detail(account_detail_html: str, account_detail_csv: str, account_summary: AccountSummary) \
        -> AccountDetail:
    soup = BeautifulSoup(account_detail_html, 'html.parser')

    f = StringIO(account_detail_csv)
    reader = csv.reader(f, delimiter=',')
    try:
        in_holdings = False
        investments = []
        stock_value = total_cash = amount_available = total_value = None
        for row in reader:
            if len(row) >= 2:
                if row[0] == 'Stock value:':
                    stock_value = _to_float(row[1])
                elif row[0] == 'Total cash:':
                    total_cash = _to_float(row[1])
                elif row[0] == 'Amount available to invest:':
                    amount_available = _to_float(row[1])
                elif row[0] == 'Total value:':
                    total_value = _to_float(row[1])
                elif row[0] == 'Code':
                    in_holdings = True
                elif in_holdings and row[0] == '' and row[1] == 'Totals':
                    in_holdings = False
                elif in_holdings:
                    try:
                        # Fetch the stock symbol and SEDOL code from the HTML
                        # Could also be of the format live_price_value_$CODE-L
                        live_price_value = soup.find(id=re.compile(f'^live_price_value_{row[0]}'))
                        tr = live_price_value.parent.parent
                        # https://online.hl.co.uk/my-accounts/security_deal/sedol/2588173
                        href = tr.find("a", class_="deal-button")['href']
                        sedol = re.findall('([^/]+$)', href)[0]
                    except AttributeError as e:
                        raise ValueError("Could not find the sedol code in the my-accounts page for stock symbol {} "
                                         "with error {}".format(row[0], e))

                    investments.append(Investment(stock_ticker=row[0], security_name=row[1], sedol_code=sedol,
                                                  units_held=_to_float(row[2]), price_pence=_to_float(row[3]),
                                                  value_gbp=_to_float(row[4]), cost_gbp=_to_float(row[5]),
                                                  gain_loss_gbp=_to_float(row[6]),
                                                  gain_loss_percentage=_to_float(row[7])))

    except csv.Error as e:
        raise ValueError("Could not parse CSV file line {}: {}".format(reader.line_num, e))

    return AccountDetail(account_id=account_summary.account_id, account_type=account_summary.account_type,
                         stock_value=stock_value, total_cash=total_cash, amount_available=amount_available,
                         total_value=total_value, investments=investments
                         )


def _to_float(cell: str):
    return float(cell.replace(',', ''))
