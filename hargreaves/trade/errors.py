

class MarketClosedError(BaseException):
    __can_place_fill_or_kill_order: bool
    __can_place_limit_order: bool

    def __init__(self,
                 can_place_fill_or_kill_order: bool,
                 can_place_limit_order: bool):
        super().__init__("Market is currently closed")
        self.__can_place_fill_or_kill_order = can_place_fill_or_kill_order
        self.__can_place_limit_order = can_place_limit_order

    @property
    def can_place_fill_or_kill_order(self):
        return self.__can_place_fill_or_kill_order

    @property
    def can_place_limit_order(self):
        return self.__can_place_limit_order


class DealFailedError(BaseException):
    html: str

    def __init__(self, message: str, html: str = None):
        self.html = html
        super().__init__(message)
