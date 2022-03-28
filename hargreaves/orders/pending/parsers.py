import re
from typing import List

from bs4 import BeautifulSoup

from hargreaves.orders.pending.models import PendingOrder
from hargreaves.utils.input import InputHelper


def parse_pending_orders(account_id: int, pending_orders_html: str) -> List[PendingOrder]:
    pending_orders = []

    soup = BeautifulSoup(pending_orders_html, 'html.parser')
    pending_orders_table = soup.select_one('table[summary="Your current pending orders"]')

    if pending_orders_table is None:
        return pending_orders

    #  Order date	Code	Quantity	Stock	Order type	Limit price	Status	Cance
    header_rows = pending_orders_table.select("thead > tr > th")
    if len(header_rows) != 8:
        raise Exception(
            f"Unexpected number of header rows({len(header_rows)}), see HTML for more details",
            pending_orders_table.text)

    row_data = []

    table_rows = pending_orders_table.select("tbody > tr")
    for table_row in table_rows:

        row_cells = table_row.select("td")
        if len(row_cells) != 8:
            raise Exception(f"Unexpected number of cells({len(row_cells)}), see HTML for more details",
                            pending_orders_table.text)

        cell_data = {}

        for col_index in range(len(header_rows)):
            item_key = header_rows[col_index].get_text(strip=True, separator=' ')
            if item_key == 'Cancel':
                cancel_button = row_cells[col_index].select_one('button')
                item_value = re.findall("value='(\\d*)'", cancel_button.attrs['onclick'])[0]
            else:
                item_value = row_cells[col_index].get_text(strip=True, separator=' ')
            cell_data[item_key] = item_value

        row_data.append(cell_data)

    for row in row_data:
        order_id = InputHelper.parse_int(row['Cancel'])
        order_date = InputHelper.parse_date(input_txt=row['Order date'], date_format='%d/%m/%y')
        trade_type = str(pending_orders_table.select_one(f"input[name='{order_id}_trade_type[]']").attrs['value'])
        sedol_code = str(pending_orders_table.select_one(f"input[name='{order_id}_sedol[]']").attrs['value'])
        stock_title = str(pending_orders_table.select_one(f"input[name='{order_id}_stoktitle[]']").attrs['value'])
        quantity = InputHelper.parse_float(
            pending_orders_table.select_one(f"input[name='{order_id}_quantity[]']").attrs['value'])
        qty_is_money = InputHelper.parse_bool(
            pending_orders_table.select_one(f"input[name='{order_id}_qty_is_money[]']").attrs['value'])
        limit_price = InputHelper.parse_float(row['Limit price'], default_empty=None, empty_values=['', '-'])
        status = str(row['Status'])

        pending_order = PendingOrder(
            account_id=account_id,
            order_id=order_id,
            order_date=order_date,
            trade_type=trade_type,
            sedol_code=sedol_code,
            stock_title=stock_title,
            quantity=quantity,
            qty_is_money=qty_is_money,
            limit_price=limit_price,
            status=status
        )

        pending_orders.append(pending_order)

    return pending_orders
