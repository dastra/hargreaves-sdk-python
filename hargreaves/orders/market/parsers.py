import re
from datetime import datetime

from bs4 import BeautifulSoup

from ...orders.market.errors import MarketClosedError, MarketOrderFailedError, MarketOrderLiveQuoteError, \
    MarketOrderQuoteError
from ...orders.market.models import MarketOrderPosition, MarketOrderQuote, MarketOrderConfirmation
from ...utils.input import InputHelper


def parse_market_order_entry_page(order_html: str, category_code: str) -> MarketOrderPosition:
    soup = BeautifulSoup(order_html, 'html.parser')

    # Is the market closed?   We cannot rely on the "Market closed" text being shown as it's always present in the HTML.
    # Instead, we need to work out whether order form is present
    form = soup.find("form", id="order_entry")
    if form is None:
        raise MarketClosedError(
            can_place_fill_or_kill_order=(len(soup.select('a[title="Place fill or kill"]')) == 1),
            can_place_limit_order=(len(soup.select('a[title="Place limit order"]')) == 1)
        )

    # Fetch the fields needed for the next step
    tags = {}
    for hidden_tag in form.find_all("input", type="hidden"):
        tags[hidden_tag['name']] = hidden_tag['value']

    return MarketOrderPosition(hl_vt=tags['hl_vt'], stock_ticker=tags['ticker'], security_name=tags['security_name'],
                               sedol_code=tags['sedol'], isin_code=tags['isin'], epic_code=tags['epic'],
                               currency_code=tags['currency_code'], exchange=tags['exchange'],
                               fixed_interest=bool(tags['fixed_interest'] == '1'), account_id=int(tags['product_no']),
                               total_cash_available=float(tags['available']), bid_price=tags['bid'],
                               units_held=float(tags['holding']), value_gbp=float(tags['holding_value']),
                               category_code=category_code
                               )


# Maps the row names on the HTML form to variable names
QUOTE_MAP = {
    'Exchange rate': 'exchange_rate',  # US
    'Price': 'conversion_price',  # US
    'Sub total': 'conversion_sub_total',  # US
    'Value:': 'share_value',  # UK
    'PTM levy:': 'ptm_levy',  # UK
    'Commission:': 'commission',  # UK
    'Commission': 'commission',  # US
    'FX charge': 'fx_charge',  # US
    'Stamp duty:': 'stamp_duty',  # US
    'Settlement date:': 'settlement_date',  # UK
    'Settlement date': 'settlement_date',  # US
    'Total value of trade:': 'total_trade_value',  # US, UK
}


def parse_market_order_quote_page(quote_html: str, category_code: str) -> MarketOrderQuote:
    soup = BeautifulSoup(quote_html, 'html.parser')

    form = soup.find("form", id="dealform")
    if form is None:
        err = soup.select_one('div.dialog_content')
        error_text = err.get_text(separator=' ', strip=True) if err is not None else "Unknown, check HTML"
        if 'Unable to retrieve a live quote' in error_text:
            raise MarketOrderLiveQuoteError(error_text, quote_html)
        else:
            raise MarketOrderQuoteError(error_text, quote_html)

    # var security_token = '3729677934';
    session_hl_vt = re.findall("var security_token = '(\\d+)';", quote_html)[0]

    vals = {
        'session_hl_vt': session_hl_vt,
        'hl_vt': form.find('input', {'type': 'hidden', 'name': 'hl_vt'})['value'],
        'sedol_code': form.find('input', {'type': 'hidden', 'name': 'sedol'})['value'],
        'category_code': category_code,
        # optional:
        'exchange_rate': None,
        'conversion_price': None,
        'conversion_sub_total': None,
        'share_value': None,
        'ptm_levy': None,
        'fx_charge': None,
        'stamp_duty': None
    }

    quote_quantity = soup.find_all("div", {"class": "quote_quantity"})[0]

    # Buy 527
    deal_type = quote_quantity.find_all("span", {"class": "deal_text_lg"})[0].text
    vals['number_of_shares'] = float(re.findall(".*?([\\d.]+)$", deal_type)[0])

    # 18.945p
    buy_price_span = quote_quantity.select('span')[2].get_text(strip=True)
    buy_price_matches = re.findall("([\\d.]+)", buy_price_span)
    if len(buy_price_matches) == 0:
        raise ValueError(f"Invalid format for buy price: {buy_price_span}")
    # vals['price'] = float(buy_price_matches[0])
    vals['price'] = buy_price_span

    for row in form.find("table").find("tbody").find_all("tr"):
        cols = row.find_all("td")
        name = cols[0].find("span").get_text(strip=True)

        # print(f"{name} = {cols[1].text}")
        if name in ['PTM levy:', 'Commission:', 'Commission', 'Stamp duty:', 'Exchange rate', 'Price', 'Sub total',
                    'FX charge']:
            vals[QUOTE_MAP[name]] = float(re.findall("([\\d.]+)$", cols[1].text)[0])
        elif name in ['Settlement date:', 'Settlement date']:
            vals[QUOTE_MAP[name]] = datetime.strptime(cols[1].get_text(strip=True), '%d/%m/%Y')
        elif name in ['Value:', 'Total value of trade:']:
            vals[QUOTE_MAP[name]] = float(re.findall("([\\d.]+)", cols[1].find("span").text)[0])

    return MarketOrderQuote(**vals)


def parse_market_order_confirmation_page(confirm_html: str, category_code: str) -> MarketOrderConfirmation:
    soup = BeautifulSoup(confirm_html, 'html.parser')

    qc = soup.find("div", id="quote_content")
    if qc is None:
        err = soup.select_one('div.dialog_content')
        if err is None:
            raise MarketOrderFailedError("Unexpected Error, see HTML for more details", confirm_html)
        else:
            error_text = err.get_text(separator=' ', strip=True)

            if 'Unable to retrieve a live quote' in error_text:
                raise MarketOrderLiveQuoteError(error_text, confirm_html)
            else:
                raise MarketOrderFailedError(error_text, confirm_html)

    vals = {
        'sedol_code': qc.get('data-trade-sedol'),
        'number_of_shares': InputHelper.parse_int(qc.get('data-trade-quantity')),
        'share_value': InputHelper.parse_float(qc.get('data-trade-total-net')),
        'commission': InputHelper.parse_float(qc.get('data-trade-commission')),
        'total_trade_value': InputHelper.parse_float(qc.get('data-trade-total-gross')),
        'category_code': category_code,
        # optional:
        'exchange_rate': None,
        'conversion_price': None,
        'conversion_sub_total': None,
        'ptm_levy': None,
        'fx_charge': None,
        'stamp_duty': None,
        'settlement_date': None,
    }

    buy_price_span = qc.select('span[class="label-bold deal_text_lg"]')[2].get_text(strip=True)
    buy_price_matches = re.findall("^([\\d.,]+p$)", buy_price_span)
    if len(buy_price_matches) != 1:
        buy_price_matches = re.findall("^£([\\d.,]+$)", buy_price_span)
        if len(buy_price_matches) != 1:
            raise ValueError(f"Invalid format for buy price: {buy_price_span}")

    vals['price'] = buy_price_span

    for row in qc.find("table").find("tbody").find_all("tr"):
        cols = row.find_all("td")
        name = cols[0].find("span").get_text(strip=True)

        if name in ['PTM levy:', 'Commission:', 'Commission', 'Stamp duty:', 'Exchange rate', 'Price', 'Sub total',
                    'FX charge']:
            vals[QUOTE_MAP[name]] = float(re.findall("([\\d.]+)$", cols[1].text)[0])
        elif name in ['Settlement date:', 'Settlement date']:
            vals[QUOTE_MAP[name]] = datetime.strptime(cols[1].get_text(strip=True), '%d/%m/%Y')
        elif name in ['Value:', 'Total value of trade:']:
            vals[QUOTE_MAP[name]] = float(re.findall("([\\d.]+)", cols[1].find("span").text)[0])

    return MarketOrderConfirmation(**vals)
