import datetime
from typing import Optional


class InputHelper:

    @staticmethod
    def parse_int(input_txt: str, default_empty: int = 0) -> int:
        if input_txt == '':
            return default_empty
        return int(input_txt)

    @staticmethod
    def parse_float(input_txt: str, default_empty: Optional[float] = 0, empty_values: Optional[list] = None) -> float:
        if empty_values is None:
            if input_txt == '':
                return default_empty
        else:
            if input_txt in empty_values:
                return default_empty
        return float(input_txt.replace(',', ''))

    @staticmethod
    def parse_bool(input_txt: str) -> bool:
        bool_values = ['1', 'true', 'True']
        return (input_txt in bool_values)

    @staticmethod
    def parse_date(input_txt: str, date_format: str = '%d/%m/%Y'):
        if input_txt is None:
            return None
        return datetime.datetime.strptime(input_txt, date_format).date()
