import random
from urllib.parse import urlencode

from .requests import RequestSessionContext, UrlHelper


class DictionaryHelper:
    @staticmethod
    def merge_with_priority(higher_priority: dict, lower_priority: dict):
        result = lower_priority.copy()
        for key, val in higher_priority.items():
            result[key] = val
        return result


class IHeaderFactory:

    def create_for_doc_get(self, url: str, additional_headers: dict) -> dict:
        pass

    def create_for_xhr_get(self, url: str, additional_headers: dict) -> dict:
        pass

    def create_for_form_post(self, url: str, additional_headers: dict, data: dict) -> dict:
        pass

    def create_for_xhr_post(self, url: str, additional_headers: dict, data: dict) -> dict:
        pass


class HeaderFactory(IHeaderFactory):

    ACCEPT_LANGUAGE = 'en-US,en;q=0.5'
    ACCEPT_ENCODING = 'gzip, deflate, br'

    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36/LGzPQZUn-10',
        'Mozilla/5.0 (Linux; Android 5.1.1; SAMSUNG-SM-G530AZ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; X104-EEA Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 4.4.2; GT-P5220) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 7.0; FRD-L19) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.111 Mobile Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
    ]

    _user_agent: str
    _request_session_context: RequestSessionContext

    def __init__(self, request_session_context: RequestSessionContext, user_agent: str):
        self._request_session_context = request_session_context
        self._user_agent = user_agent

    def create_for_doc_get(self, url: str, additional_headers: dict) -> dict:
        default_headers = {
            'Host': UrlHelper.get_host(url),
            'User-Agent': self._user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': HeaderFactory.ACCEPT_LANGUAGE,
            'Accept-Encoding': HeaderFactory.ACCEPT_ENCODING,
            'Referer': self._request_session_context.get_last_referer(),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1'
        }

        merged_headers = DictionaryHelper.merge_with_priority(additional_headers, default_headers)
        return merged_headers

    def create_for_xhr_get(self, url: str, additional_headers: dict) -> dict:
        default_headers = {
            'Host': UrlHelper.get_host(url),
            'User-Agent': self._user_agent,
            'Accept': 'text/javascript, application/javascript, */*',
            'Accept-Language': HeaderFactory.ACCEPT_LANGUAGE,
            'Accept-Encoding': HeaderFactory.ACCEPT_ENCODING,
            'Referer': self._request_session_context.get_last_referer(),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1',
            'X-Requested-With': 'XMLHttpRequest',
        }

        merged_headers = DictionaryHelper.merge_with_priority(additional_headers, default_headers)
        return merged_headers

    def create_for_form_post(self, url: str, additional_headers: dict, data: dict) -> dict:

        default_headers = {
            'Host': UrlHelper.get_host(url),
            'User-Agent': self._user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': HeaderFactory.ACCEPT_LANGUAGE,
            'Accept-Encoding': HeaderFactory.ACCEPT_ENCODING,
            'Referer': self._request_session_context.get_last_referer(),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': str(len(urlencode(data))),
            'Origin': UrlHelper.get_origin(url),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1'
        }

        merged_headers = DictionaryHelper.merge_with_priority(additional_headers, default_headers)
        return merged_headers

    def create_for_xhr_post(self, url: str, additional_headers: dict, data: dict) -> dict:

        default_headers = {
            'Host': UrlHelper.get_host(url),
            'User-Agent': self._user_agent,
            'Accept': '*/*',
            'Accept-Language': HeaderFactory.ACCEPT_LANGUAGE,
            'Accept-Encoding': HeaderFactory.ACCEPT_ENCODING,
            'Referer': self._request_session_context.get_last_referer(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': str(len(urlencode(data))),
            'Origin': UrlHelper.get_origin(url),
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-GPC': '1'
        }

        merged_headers = DictionaryHelper.merge_with_priority(additional_headers, default_headers)
        return merged_headers

    @staticmethod
    def create(request_session_context: RequestSessionContext):
        random_user_agent = random.choice(HeaderFactory.USER_AGENTS)
        return HeaderFactory(request_session_context, random_user_agent)
