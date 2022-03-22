from enum import Enum


class OrderAmountType(Enum):
    Quantity = 'quantity'
    Value = 'value'

    def __str__(self):
        return self.name


class OrderPositionType(Enum):
    Buy = 'Buy'
    Sell = 'Sell'

    def __str__(self):
        return self.name
