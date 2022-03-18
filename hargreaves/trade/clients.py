import http
import re
import time
from datetime import datetime
from logging import Logger

from bs4 import BeautifulSoup

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.errors import MarketClosedError, DealFailedError
from hargreaves.trade.models import Deal, PriceQuote, DealConfirmation
from hargreaves.utils.timings import ITimeService
from hargreaves.web.session import IWebSession, WebRequestType


class TradeClient:
    __logger: Logger
    __web_session: IWebSession
    __time_service: ITimeService

    def __init__(self,
                 logger: Logger,
                 web_session: IWebSession,
                 time_service: ITimeService
                 ):
        self.__logger = logger
        self.__web_session = web_session
        self.__time_service = time_service

    def get_security_price(self, account_id: int, sedol_code: str, category_code: str) -> Deal:
        # selects account & security
        # Fetches the deal page where you say whether you're buying or selling.

        deal_html = self.__web_session.get(f"https://online.hl.co.uk/my-accounts/account_select/"
                                           f"account/{account_id}/sedol/{sedol_code}/rq/select/type/trade").text
        deal_info = parse_deal_page(deal_html, category_code)
        return deal_info

    # Keeps the session alive.  The __dat and ADRUM_BT cookies are set in the response
    def session_keepalive(self, sedol_code: str, session_hl_vt: str):
        # pid is the time in milliseconds since the epoch
        pid = self.__time_service.get_current_time_as_epoch_time()

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{sedol_code}'
        }

        res = self.__web_session.get(f"https://online.hl.co.uk/ajaxx/user.php",
                                     params={
                                         'method': 'session_timeout_handler',
                                         'keepalive': "1",
                                         'format': 'jsonp',
                                         'jsoncallback': f"jsonp{pid}",
                                         'hl_vt': session_hl_vt,
                                         'initialise': 'true'
                                     },
                                     headers=request_headers, request_type=WebRequestType.XHR)

        if res.text != 'session_timeout_handler(["keptalive"])':
            raise DealFailedError('Session could not be kept alive', res.text)

    def get_quote(self, deal: Deal) -> PriceQuote:
        self.__logger.debug("Perform 'Session Keepalive'")
        self.session_keepalive(sedol_code=deal.sedol_code, session_hl_vt=deal.hl_vt)

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{deal.sedol_code}'
        }

        if deal.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/confirm_equity_deal'

        res = self.__web_session.post(request_url,
                                      request_type=WebRequestType.XHR, data=deal.as_form_fields(),
                                      headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise ConnectionError(f"Buy quote invalid, HTTP response code was {res.status_code}")
        elif "another account open" in res.text:
            raise ValueError("An error occurred with the sequence of calls - the wrong hl_vt was passed in.")

        price_quote = parse_buy_quote_page(res.text, category_code=deal.category_code)
        return price_quote

    def execute_deal(self, price_quote: PriceQuote) -> DealConfirmation:
        self.__logger.debug("Perform 'Session Keepalive'")
        self.session_keepalive(sedol_code=price_quote.sedol_code, session_hl_vt=price_quote.session_hl_vt)

        request_headers = {
            'Referer': f'https://online.hl.co.uk/my-accounts/security_deal/sedol/{price_quote.sedol_code}'
        }

        form = {
            'hl_vt': price_quote.hl_vt,
            'sedol': price_quote.sedol_code
        }

        if price_quote.category_code == InvestmentCategoryTypes.OVERSEAS:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation_overseas'
        else:
            request_url = 'https://online.hl.co.uk/my-accounts/equity_confirmation'

        res = self.__web_session.post(request_url,
                                      request_type=WebRequestType.XHR,
                                      data=form, headers=request_headers)

        if res.status_code != http.HTTPStatus.OK:
            raise DealFailedError(f"Purchase invalid, HTTP response code was {res.status_code}")

        deal_confirmation = parse_confirm_equity_deal_page(confirm_html=res.text,
                                                           category_code=price_quote.category_code)

        return deal_confirmation


def parse_deal_page(deal_html: str, category_code: str) -> Deal:
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


def parse_buy_quote_page(quote_html: str, category_code: str) -> PriceQuote:
    soup = BeautifulSoup(quote_html, 'html.parser')

    form = soup.find("form", id="dealform")
    if form is None:
        raise MarketClosedError

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

    return PriceQuote(**vals)


def parse_confirm_equity_deal_page(confirm_html: str, category_code: str) -> DealConfirmation:
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
        'total_trade_value': float(qc.get('data-trade-total-gross')),
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
    buy_price_matches = re.findall("^([\\d.]+p$)", buy_price_span)
    if len(buy_price_matches) != 1:
        buy_price_matches = re.findall("^£([\\d.]+$)", buy_price_span)
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

    return DealConfirmation(**vals)