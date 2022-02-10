import http
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from hargreaves.trade.errors import MarketClosedError, DealFailedError
from hargreaves.trade.models import Deal, Buy, PriceQuote, DealConfirmation
from utils.cookie_manager import set_cookies


def get_current_price(session: requests.Session, account_id: int, sedol_code: str) -> [requests.Session, Deal]:
    # Fetches the deal page where you say whether you're buying or selling.
    session = set_cookies(session)
    deal_html = session.get(
        f"https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}/account/{account_id}").text

    deal_info = parse_deal_page(deal_html)

    return session, deal_info


def parse_deal_page(deal_html: str) -> Deal:
    soup = BeautifulSoup(deal_html, 'html.parser')

    # Is the market closed?   We cannot rely on the "Market closed" text being shown as it's always present in the HTML.
    # Instead, we need to work out whether deal form is present
    form = soup.find("form", id="order_entry")
    if form is None:
        raise MarketClosedError

    # Fetch the fields needed for the next step
    tags = {}
    for hidden_tag in form.find_all("input", type="hidden"):
        tags[hidden_tag['name']] = hidden_tag['value']

    return Deal(hl_vt=tags['hl_vt'], stock_ticker=tags['ticker'], security_name=tags['security_name'],
                sedol_code=tags['sedol'], isin_code=tags['isin'], epic_code=tags['epic'],
                currency_code=tags['currency_code'], exchange=tags['exchange'],
                fixed_interest=bool(tags['fixed_interest'] == '1'), account_id=int(tags['product_no']),
                total_cash_available=float(tags['available']), bid_price=tags['bid'],
                units_held=float(tags['holding']), value_gbp=float(tags['holding_value'])
                )


def get_buy_quote(session: requests.Session, buy: Buy) -> [requests.Session, PriceQuote]:
    session = set_cookies(session)

    res = session.post('https://online.hl.co.uk/my-accounts/confirm_equity_deal',
                       data=buy.as_form_fields(), allow_redirects=False)

    if res.status_code != http.HTTPStatus.OK:
        raise ConnectionError(f"Buy quote invalid, HTTP response code was {res.status_code}")
    elif "another account open" in res.text:
        raise ValueError("An error occurred with the sequence of calls - the wrong hl_vt was passed in.")

    price_quote = parse_buy_quote_page(res.text)

    return session, price_quote


# Maps the row names on the HTML form to variable names
QUOTE_MAP = {
    'Value:': 'share_value',
    'PTM levy:': 'ptm_levy',
    'Commission:': 'commission',
    'Stamp duty:': 'stamp_duty',
    'Settlement date:': 'settlement_date',
    'Total value of trade:': 'total_trade_value',
}


def parse_buy_quote_page(quote_html: str) -> PriceQuote:
    soup = BeautifulSoup(quote_html, 'html.parser')

    form = soup.find("form", id="dealform")
    if form is None:
        raise MarketClosedError

    # var security_token = '3729677934';
    session_hl_vt = re.findall("var security_token = '(\\d+)';", quote_html)[0]

    vals = {
        'session_hl_vt': session_hl_vt,
        'hl_vt': form.find('input', {'type': 'hidden', 'name': 'hl_vt'})['value'],
        'sedol_code': form.find('input', {'type': 'hidden', 'name': 'sedol'})['value']
    }

    quote_quantity = soup.find_all("div", {"class": "quote_quantity"})[0]

    # Buy 527
    deal_type = quote_quantity.find_all("span", {"class": "deal_type_text"})[0].text
    vals['number_of_shares'] = float(re.findall(".*?([\\d.]+)$", deal_type)[0])

    # 18.945p
    buy_price_span = quote_quantity.select('span')[2].get_text(strip=True)
    buy_price_matches = re.findall("^([\\d.]+)p$", buy_price_span)
    if len(buy_price_matches) == 0:
        raise ValueError(f"Invalid format for buy price: {buy_price_span}")
    # vals['price'] = float(buy_price_matches[0])
    vals['price'] = buy_price_span

    for row in form.find("table").find("tbody").find_all("tr"):
        cols = row.find_all("td")
        name = cols[0].find("span").get_text(strip=True)

        if name in ['PTM levy:', 'Commission:', 'Stamp duty:']:
            vals[QUOTE_MAP[name]] = float(re.findall("£([\\d.]+)$", cols[1].text)[0])
        elif name == 'Settlement date:':
            vals[QUOTE_MAP[name]] = datetime.strptime(cols[1].get_text(strip=True), '%d/%m/%Y')
        elif name in ['Value:', 'Total value of trade:']:
            vals[QUOTE_MAP[name]] = float(re.findall("£([\\d.]+)$", cols[1].find("span").text)[0])

    return PriceQuote(**vals)


# Keeps the session alive.  The __dat and ADRUM_BT cookies are set in the response
def session_keepalive(session: requests.Session, price_quote: PriceQuote):
    pid = time.time_ns() // 1_000_000

    request_headers = {
        'Accept': 'text/javascript, application/javascript, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{price_quote.sedol_code}'
    }

    res = session.get(f"https://online.hl.co.uk/ajaxx/user.php?method=session_timeout_handler&keepalive=1&format=jsonp"
                f"&jsoncallback=jsonp{pid}&hl_vt={price_quote.session_hl_vt}&initialise=true", headers=request_headers)

    if res.text != 'session_timeout_handler(["keptalive"])':
        raise DealFailedError('Session could not be kept alive', res.text)

    return session


def execute_deal(session: requests.Session, price_quote: PriceQuote) -> [requests.Session, DealConfirmation]:

    # Perform keepalive call
    session = session_keepalive(session=session, price_quote=price_quote)

    form = {
        'hl_vt': price_quote.hl_vt,
        'sedol_code': price_quote.sedol_code
    }
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{price_quote.sedol_code}'
    }

    # None of this seems to help.  Still getting an error.
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="__mkt", value="1", path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="app_hasJS", value="yes", path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="at_check", value="true", path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="check", value="true", path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="hl_cookie_consent", value='{"ao": true, "tp": true}', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="hl_cp", value='1', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="s_cam", value='EO849_Graham_UK_Shares_19.06.20', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="s_cc", value='true', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="s_extCh", value='email_hl', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="s_v20", value='P', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="s_v32", value='C', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="theSource", value='EI579', path='/'))
    # session.cookies.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="partialRefreshToken",
    #                                                  value='664cd532-af4d-4299-8b8f-f1bc140ed627', path='/',
    #                                                  secure=True, rest={'HttpOnly': True}))

    res = session.post('https://online.hl.co.uk/my-accounts/equity_confirmation', data=form, allow_redirects=False,
                       headers=headers)

    if res.status_code != http.HTTPStatus.OK:
        raise DealFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

    deal_confirmation = parse_confirm_equity_deal_page(res.text)

    return session, deal_confirmation


def parse_confirm_equity_deal_page(confirm_html: str) -> DealConfirmation:
    soup = BeautifulSoup(confirm_html, 'html.parser')

    qc = soup.find("div", id="quote_content")
    if qc is None:
        err = soup.select_one('div#content-body-full > div > div.dialog_content')
        if err is None:
            raise DealFailedError("Unexpected Error, see HTML for more details", confirm_html)
        else:
            raise DealFailedError(err.get_text(strip=True), confirm_html)

    vals = {
        'sedol_code': qc.get('data-trade-sedol'),
        'number_of_shares': int(qc.get('data-trade-quantity')),
        'share_value': float(qc.get('data-trade-total-net')),
        'commission': float(qc.get('data-trade-commission')),
        'total_trade_value': float(qc.get('data-trade-total-gross'))
    }

    buy_price_span = qc.select('p > span:nth-child(5)')[0].get_text(strip=True)
    buy_price_matches = re.findall("^([\\d.]+)p$", buy_price_span)
    if len(buy_price_matches) == 0:
        raise ValueError(f"Invalid format for buy price: {buy_price_span}")
    # TODO - this should be an int, but wait until we test on other currencies
    # vals['price'] = float(buy_price_matches[0])
    vals['price'] = buy_price_span

    for row in qc.find("table").find("tbody").find_all("tr"):
        cols = row.find_all("td")
        name = cols[0].find("span").get_text(strip=True)

        if name in ['PTM levy:', 'Stamp duty:']:
            vals[QUOTE_MAP[name]] = float(re.findall("£([\\d.]+)$", cols[1].text)[0])
        elif name == 'Settlement date:':
            vals[QUOTE_MAP[name]] = datetime.strptime(cols[1].get_text(strip=True), '%d/%m/%Y')

    return DealConfirmation(**vals)
