
class SearchFilterError(BaseException):
    html: str

    def __init__(self, message: str):
        super().__init__(message)
