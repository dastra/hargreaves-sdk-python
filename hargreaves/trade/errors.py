

class MarketClosedError(BaseException):
    def __init__(self):
        super().__init__("Market is currently closed")


class DealFailedError(BaseException):
    html: str

    def __init__(self, message: str, html: str = None):
        self.html = html
        super().__init__(message)
