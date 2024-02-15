from typing  import  Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from midas.events import TradeInstruction, Action
from ibapi.contract import Contract
from ibapi.order import Order

@dataclass
class Trade:
    trade_id: str
    leg_id: str
    timestamp: datetime
    symbol: str
    quantity: int
    price: float
    cost: float
    action: str
    fees: float

    def __post_init__(self):
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()

@dataclass
class ExecutionEvent:
    timestamp: Any  # Replace Any with the appropriate type, e.g., datetime or str
    trade_instructions: TradeInstruction 
    action: Action 
    contract: Contract
    order: Order
    trade_details: Trade
    type: str = field(init=False, default='EXECUTION')

    def __str__(self) -> str:
        # Modify string representation according to actual attributes' structure
        string = f"\n{self.type} : \n Timestamp: {self.timestamp}\n Trade Instructions: {self.trade_instructions.__dict__}\n Contract: {self.contract}\n Order: {self.order.__dict__}\n Execution Details: {self.trade_details}\n"
        return string