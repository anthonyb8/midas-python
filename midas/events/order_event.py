from typing  import  Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum 
from ibapi.order import Order
from ibapi.contract import Contract
# from midas.events import TradeInstruction

class Action(Enum):
    """ Long and short are treated as entry actions and short/cover are treated as exit actions. """
    LONG = 'LONG'  # BUY
    COVER = 'COVER' # BUY
    SHORT = 'SHORT' # SELL
    SELL = 'SELL'  # SELL

    def to_broker_standard(self):
        """Converts the enum to the standard BUY or SELL action for the broker."""
        if self in [Action.LONG, Action.COVER]:
            return 'BUY'
        elif self in [Action.SHORT, Action.SELL]:
            return 'SELL'
        else:
            raise ValueError(f"Invalid action: {self}")
        
class OrderType(Enum):
    """ Interactive Brokers Specific """
    MARKET = "MKT"
    LIMIT = "LMT"
    STOPLOSS = "STP"

class BaseOrder:
    """ 
    Base class for order creation. Should not be used directly, access through a subclass.
    """
    def __init__(self, action: Action, quantity: float, orderType: OrderType) -> None:
        broker_action = action.to_broker_standard()
        
        if broker_action  not in ['BUY', 'SELL']:
            raise ValueError("action must be either 'BUY' or 'SELL'")
        if quantity == 0:
            raise ValueError("quantity must not be zero.")
        
        self.order = Order()
        self.order.action = broker_action 
        self.order.orderType = orderType.value
        self.order.totalQuantity = abs(quantity)
    
    @property
    def quantity(self):
        return self.order.totalQuantity if self.order.action == 'BUY' else -self.order.totalQuantity

    def __getattr__(self, name):
        try:
            return getattr(self.order, name)
        except AttributeError:
            raise AttributeError(f"{name} not found in BaseOrder or Order")

class MarketOrder(BaseOrder):
    def __init__(self, action: Action, quantity: float):
        super().__init__(action, quantity, OrderType.MARKET)

class LimitOrder(BaseOrder):
    def __init__(self, action: Action, quantity: float, limit_price: float):
        if limit_price <= 0:
            raise ValueError("'limit_price' must be greater than zero.")
        
        super().__init__(action, quantity, OrderType.LIMIT)
        self.order.lmtPrice = limit_price
        
class StopLoss(BaseOrder):
    def __init__(self, action: Action, quantity: float, aux_price: float) -> None:
        if aux_price <= 0:
            raise ValueError("'aux_price' must be greater than zero.")
        
        super().__init__(action, quantity, OrderType.STOPLOSS)
        self.order.auxPrice = aux_price

@dataclass
class OrderEvent:
    timestamp: Any  # Use the appropriate type, e.g., datetime or str
    trade_instructions: Any 
    # direction: Optional[str] = None  # Uncomment and adjust the type as necessary
    contract: Contract 
    order: Order  
    type: str = field(init=False, default='ORDER')

    def __str__(self) -> str:
        # Assuming trade_instructions and order have a __dict__ or similar method to convert to a dictionary
        # If not, you might need to adjust how you represent these objects as strings
        string = f"\n{self.type} : \n Timestamp: {self.timestamp}\n Trade Instructions: {self.trade_instructions.__dict__}\n Contract: {self.contract}\n Order: {self.order.__dict__}\n"
        return string
    