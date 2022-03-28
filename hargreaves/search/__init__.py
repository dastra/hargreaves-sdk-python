from .clients import SecuritySearchClient
from .models import InvestmentTypes, SearchResult
import logging

from hargreaves.request_tracker.session import IWebSession

logging.getLogger(__name__).addHandler(logging.NullHandler())


def investment_search(web_session: IWebSession, search_string: str, investment_types: list) -> [SearchResult]:
    return SecuritySearchClient().investment_search(
        web_session=web_session,
        search_string=search_string,
        investment_types=investment_types
    )
