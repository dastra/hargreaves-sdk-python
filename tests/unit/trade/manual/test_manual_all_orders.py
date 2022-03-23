from pathlib import Path

import pytest

from hargreaves.search.models import InvestmentCategoryTypes
from hargreaves.trade.manual.errors import ManualOrderFailedError
from hargreaves.trade.manual.parsers import parse_manual_order_entry_page, parse_manual_order_confirmation_page
from hargreaves.trade.models import OrderAmountType


def test_parse_manual_order_entry_uk_equity_ok():
    order_html = Path(Path(__file__).parent / 'files/all/manual-order-entry-uk-equity.html').read_text()

    current_position = parse_manual_order_entry_page(order_html=order_html, category_code=InvestmentCategoryTypes.EQUITIES)

    assert current_position.hl_vt == "2491884284"
    assert current_position.type == "equity"
    assert current_position.out_of_hours is True
    assert current_position.sedol == "3092725"
    assert current_position.product_no == 70
    assert current_position.available == 179515.7
    assert current_position.holding == 0
    assert current_position.holding_value == 0
    assert current_position.transfer_units is None
    assert current_position.remaining_units == 0
    assert current_position.remaining_units_value == 0
    assert current_position.isin == "GB0030927254"
    assert current_position.epic == ""
    assert current_position.currency_code == "GBX"
    assert current_position.SD_Bid == 0.00
    assert current_position.SD_Ask == 0.00
    assert current_position.fixed_interest is False
    assert current_position.category_code == InvestmentCategoryTypes.EQUITIES


def test_parse_manual_order_entry_us_equity_ok():
    order_html = Path(Path(__file__).parent / 'files/all/manual-order-entry-us-equity.html').read_text()

    current_position = parse_manual_order_entry_page(order_html=order_html,
                                                     category_code=InvestmentCategoryTypes.OVERSEAS)

    assert current_position.hl_vt == "3430162972"
    assert current_position.type == "equity"
    assert current_position.out_of_hours is True
    assert current_position.sedol == "BLR7B52"
    assert current_position.product_no == 70
    assert current_position.available == 177721.1
    assert current_position.holding == 0
    assert current_position.holding_value == 0
    assert current_position.transfer_units is None
    assert current_position.remaining_units == 0
    assert current_position.remaining_units_value == 0
    assert current_position.isin == "US5657881067"
    assert current_position.epic == ""
    assert current_position.currency_code == "USD"
    assert current_position.SD_Bid == 0.00
    assert current_position.SD_Ask == 0.00
    assert current_position.fixed_interest is False
    assert current_position.category_code == InvestmentCategoryTypes.OVERSEAS


def test_parse_manual_order_entry_error():
    confirm_html = Path(Path(__file__).parent / 'files/all/manual-order-entry-error.html').read_text()

    with pytest.raises(ManualOrderFailedError,
                       match=r"We have found an unprocessed order for this stock."):
        parse_manual_order_confirmation_page(confirm_html=confirm_html, amount_type=OrderAmountType.Quantity)
