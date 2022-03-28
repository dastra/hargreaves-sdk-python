
class CancelPendingOrderError(BaseException):
    html: str

    def __init__(self, message: str, html: str = None):
        self.html = html
        super().__init__(message)
