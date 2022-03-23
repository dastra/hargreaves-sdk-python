from pathlib import Path

import pytest

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.market.errors import MarketClosedError, MarketOrderFailedError, MarketOrderLiveQuoteError
from hargreaves.trade.market.parsers import parse_market_order_entry_page, parse_market_order_confirmation_page


def test_parse_order_entry_uk_market_closed():
    deal_html = Path(Path(__file__).parent / 'files/all/market-order-entry-uk-market-closed.html').read_text()

    with pytest.raises(MarketClosedError) as error:
        parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert error.value.can_place_fill_or_kill_order is True
    assert error.value.can_place_limit_order is True


def test_parse_order_entry_us_market_closed():
    deal_html = Path(Path(__file__).parent / 'files/all/market-order-entry-us-market-closed.html').read_text()

    with pytest.raises(MarketClosedError) as error:
        parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.OVERSEAS)

    assert error.value.can_place_fill_or_kill_order is True
    assert error.value.can_place_limit_order is False


def test_parse_market_order_entry_uk_equity():
    deal_html = Path(Path(__file__).parent / 'files/all/market-order-entry-uk-equity.html').read_text()

    market_order = parse_market_order_entry_page(order_html=deal_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert market_order.hl_vt == '459030661'
    assert market_order.stock_ticker == 'ANIC'
    assert market_order.security_name == 'Agronomics Limited'
    assert market_order.sedol_code == 'B6QH1J2'
    assert market_order.isin_code == 'IM00B6QH1J21'
    assert market_order.epic_code == 'ANIC'
    assert market_order.currency_code == 'GBP'
    assert market_order.exchange == 'L'
    assert not market_order.fixed_interest
    assert market_order.account_id == 70
    assert market_order.total_cash_available == 1275
    assert market_order.bid_price == '18.50p'
    assert market_order.units_held == 250
    assert market_order.value_gbp == 43.05


def test_parse_market_order_confirmation_failed():
    confirm_html = Path(Path(__file__).parent / 'files/all/market-order-confirmation-failed.html').read_text()

    with pytest.raises(MarketOrderFailedError,
                       match=r"Unfortunately there has been an error in processing your transaction"):
        parse_market_order_confirmation_page(confirm_html=confirm_html, category_code=InvestmentCategoryTypes.EQUITIES)


def test_parse_market_order_confirmation_no_live_quote():
    confirm_html = Path(Path(__file__).parent / 'files/all/market-order-confirmation-no-live-quote.html').read_text()

    with pytest.raises(MarketOrderLiveQuoteError,
                       match=r"Unable to retrieve a live quote"):
        parse_market_order_confirmation_page(confirm_html=confirm_html, category_code=InvestmentCategoryTypes.EQUITIES)
