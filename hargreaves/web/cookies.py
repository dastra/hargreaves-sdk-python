import json
from http.cookiejar import CookieJar
from random import randint

from requests import cookies

from hargreaves.utils.timings import TimeService


class HLCookieHelper:
    @staticmethod
    def find_cookie(cookie_jar: CookieJar, name: str):
        return next((cookie for cookie in cookie_jar if cookie.name == name), None)

    @staticmethod
    def create_invest_cookie():
        cookie_value = {"amount_lump": "0", "amount_regular": "0", "investment": [], "vmp_matrix": ""}
        encode_value = json.dumps(cookie_value)
        return cookies.create_cookie(domain=".hl.co.uk", name="invest",
                                     value=encode_value, path='/')

    @staticmethod
    def create_consent_cookie():
        cookie_value = {"ao": True, "tp": True}
        encode_value = json.dumps(cookie_value)
        return cookies.create_cookie(domain=".hl.co.uk", name="hl_cookie_consent",
                                     value=encode_value, path='/')

    @staticmethod
    def create_hltimer_cookie(is_logged_in: bool):
        """
        As per https://online.hl.co.uk/global/scr/timeout.js?v=2.9
        :return:
        """
        time_service = TimeService()
        random_window_name = f"HLWN{randint(520000, 750000)}"
        cookie_value = {
            # when the timeout will occur for the overall session # default seems to be 14 min (840000 sec)
            "tom": time_service.get_current_time_as_epoch_time(offset_minutes=14) if is_logged_in else 0,
            "ot": "900",  # onlineTimeoutSeconds (15 mins)
            "tos": 0,
            "smc": 0,
            random_window_name: {
                # when the timeout will occur for the window # default seems to be 14 min (840000 sec)
                "to": time_service.get_current_time_as_epoch_time(offset_minutes=14),
                "li": int(is_logged_in),   # logged-in
                "im": 1,   # in_MAAD
                "ia": 0,   # Is the window in an application?
                "ir": 0,   # Is the window in a registration?
                "rp": 0,   # retirement plannet
                "sm": 0,   # is current page the SMC compose page
                "lp": 0,   # starting value 0, not sure when it becomes 1
                "lu": time_service.get_current_time_as_epoch_time()    # last updated
            }
        }
        encoded_value = json.dumps(cookie_value)
        return cookies.create_cookie(domain=".hl.co.uk", name="hltimer",
                                     value=encoded_value, path='/')

    @staticmethod
    def set_default_cookies(cookie_jar: CookieJar):
        cookie_jar.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="at_check", value="true", path='/'))
        cookie_jar.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="jsCheck", value="yes", path='/'))
        cookie_jar.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="hl_cp", value="1", path='/'))
        cookie_jar.set_cookie(HLCookieHelper.create_invest_cookie())
        cookie_jar.set_cookie(HLCookieHelper.create_consent_cookie())
        if HLCookieHelper.find_cookie(cookie_jar, "hltimer") is None:
            cookie_jar.set_cookie(HLCookieHelper.create_hltimer_cookie(is_logged_in=False))

    @staticmethod
    def set_logged_in_cookies(cookie_jar: CookieJar):
        cookie_jar.set_cookie(cookies.create_cookie(domain=".hl.co.uk", name="__mkt", value="1", path='/'))
        cookie_jar.set_cookie(HLCookieHelper.create_hltimer_cookie(is_logged_in=True))
