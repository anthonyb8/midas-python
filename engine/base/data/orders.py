from enum import Enum 
from ibapi.order import Order

class OrderType(Enum):
    MARKET = "MKT"
    LIMIT = "LMT"
    STOPLOSS = "STP"

class Direction(Enum):
    LONG = "BUY"
    SHORT = "SELL"
    COVER = "BUY"
    SELL = "SELL"

class BaseOrder:
    def __init__(self, direction: Direction, quantity: float, orderType: OrderType) -> None:
        if direction.value not in ['BUY', 'SELL']:
            raise ValueError("direction must be either 'BUY' or 'SELL'")
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero.")
        
        self.order = Order()
        self.order.action = direction.value
        self.order.orderType = orderType.value
        self.order.totalQuantity = quantity
        
    def __getattr__(self, name):
        try:
            return getattr(self.order, name)
        except AttributeError:
            raise AttributeError(f"{name} not found in BaseOrder or Order")

class MarketOrder(BaseOrder):
    def __init__(self, direction: Direction, quantity: float):
        super().__init__(direction, quantity, OrderType.MARKET)

class LimitOrder(BaseOrder):
    def __init__(self, direction: Direction, quantity: float, limit_price: float):
        if limit_price <= 0:
            raise ValueError("'limit_price' must be greater than zero.")
        
        super().__init__(direction, quantity, OrderType.LIMIT)
        self.order.lmtPrice = limit_price
        
class StopLoss(BaseOrder):
    def __init__(self, direction: Direction, quantity: float, aux_price: float) -> None:
        if aux_price <= 0:
            raise ValueError("'aux_price' must be greater than zero.")
        
        super().__init__(direction, quantity, OrderType.STOPLOSS)
        self.order.auxPrice = aux_price

# Example usage of the classes
