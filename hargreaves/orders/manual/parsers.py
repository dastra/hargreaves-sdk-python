from bs4 import BeautifulSoup

from hargreaves.orders.manual.errors import ManualOrderFailedError
from hargreaves.orders.manual.models import ManualOrderConfirmation, ManualOrderPosition
from hargreaves.orders.models import OrderAmountType
from hargreaves.utils.input import InputHelper


def parse_manual_order_entry_page(order_html: str, category_code: str) -> ManualOrderPosition:
    soup = BeautifulSoup(order_html, 'html.parser')

    form = soup.find("form", id="oh_form")

    if form is None:
        raise ManualOrderFailedError(message="Could not find 'oh_form'", html=order_html)

    # Fetch the fields needed for the next step
    tags = {}
    for hidden_tag in form.find_all("input", type="hidden"):
        tags[hidden_tag['name']] = hidden_tag['value']

    return ManualOrderPosition(
        hl_vt=str(tags['hl_vt']),
        security_type=str(tags['type']),
        out_of_hours=InputHelper.parse_bool(tags['out_of_hours']),
        sedol=str(tags['sedol']),
        account_id=InputHelper.parse_int(tags['product_no']),
        available=InputHelper.parse_float(tags['available']),
        holding=InputHelper.parse_float(tags['holding']),
        holding_value=InputHelper.parse_float(tags['holding_value']),
        transfer_units=InputHelper.parse_float(input_txt=tags['transfer_units'], default_empty=None),
        remaining_units=InputHelper.parse_float(tags['remaining_units']),
        remaining_units_value=InputHelper.parse_float(tags['remaining_units_value']),
        isin=str(tags['isin']),
        epic=str(tags['epic']),
        currency_code=str(tags['currency_code']),
        SD_Bid=InputHelper.parse_float(tags['SD_Bid']),
        SD_Ask=InputHelper.parse_float(tags['SD_Ask']),
        fixed_interest=InputHelper.parse_bool(tags['fixed_interest']),
        category_code=category_code)


def parse_manual_order_confirmation_page(confirm_html: str, amount_type: OrderAmountType) -> ManualOrderConfirmation:
    soup = BeautifulSoup(confirm_html, 'html.parser')

    error_box = soup.select_one('div[class="box error-box spacer-bottom"]')
    if error_box is not None:
        raise ManualOrderFailedError(message=error_box.get_text(strip=True), html=confirm_html)

    pending_orders_table = soup.select_one('table[summary="Your current pending orders"]')
    if pending_orders_table is None:
        raise ManualOrderFailedError("Pending Order Table Not Found, see HTML for more details", confirm_html)

    table_columns = pending_orders_table.find_all("th")
    if len(table_columns) != 6:
        raise ManualOrderFailedError(
            f"Unexpected number of header rows({len(table_columns)}), see HTML for more details",
            pending_orders_table.text)

    table_cells = pending_orders_table.find_all("td")
    if len(table_cells) != 6:
        raise ManualOrderFailedError(f"Unexpected number of cells({len(table_cells)}), see HTML for more details",
                                     pending_orders_table.text)
    raw_order_data = {}
    for col_index in range(len(table_columns)):
        item_key = table_columns[col_index].get_text(strip=True)
        item_value = table_cells[col_index].get_text(strip=True)
        raw_order_data[item_key] = item_value

    column_header_map = {
        'Date of order': 'order_date',
        'Stock Code': 'stock_code',
        'Quantity': 'quantity',
        'Order Type': 'order_type',
        'Limit Price': 'limit_price',
        'Order Status': 'order_status',
    }

    params = {
        'amount_type': amount_type
    }

    for key, value in raw_order_data.items():
        param_key = column_header_map[key]
        params[param_key] = value

        if key in ['Date of order']:
            params[param_key] = InputHelper.parse_date(input_txt=value, date_format='%d/%m/%y')
        elif key in ['Quantity', 'Limit Price']:
            params[param_key] = InputHelper.parse_float(input_txt=value, default_empty=None, empty_values=['', '-'])
        else:
            params[param_key] = str(value)

    return ManualOrderConfirmation(**params)
