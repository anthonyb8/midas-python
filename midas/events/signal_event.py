from typing import List
from datetime import datetime
from dataclasses import dataclass, field
from .order_event import OrderType, Action

@dataclass
class TradeInstruction:
    ticker: str
    order_type: OrderType
    action: Action
    trade_id: int
    leg_id: int
    weight: float

    def __post_init__(self):
        self._data_validation()

    def _data_validation(self):
        if not self.ticker or not isinstance(self.ticker, str):
            raise ValueError("Ticker must be a non-empty string.")
        if not isinstance(self.action, Action):
            raise ValueError("action must be of type action enum.")
        
        if not isinstance(self.trade_id, int) or self.trade_id < 0:
            raise ValueError("Trade ID must be a non-negative integer.")
        
        if not isinstance(self.leg_id, int) or self.leg_id < 0:
            raise ValueError("Leg ID must be a non-negative integer.")
        
        # if not (0 <= allocation_percent <= 100):
        #     raise ValueError("Allocation percent must be between 0 and 100.")

    def __str__(self) -> str:
        return (
            f"Ticker: {self.ticker}, "
            f"Order Type: {self.order_type.name}, "
            f"Action: {self.action.name}, "
            f"Trade ID: {self.trade_id}, "
            f"Leg ID: {self.leg_id}, "
            f"Weight: {self.weight}"
        )
    
class Signal:
    def __init__(self, timestamp: datetime, trade_instructions: List[TradeInstruction]):
        self._data_validation(timestamp,trade_instructions)

        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        self.timestamp = timestamp
        self.trade_instructions = trade_instructions  # List of TradeInstruction instances

    def _data_validation(self, timestamp: datetime, trade_instructions: List[TradeInstruction]):

        if not all(isinstance(instruction, TradeInstruction) for instruction in trade_instructions):
            raise ValueError("All trade instructions must be instances of TradeInstruction.")
        
    def __str__(self) -> str:
        instructions_str = "\n  ".join(str(instruction) for instruction in self.trade_instructions)
        return f"\n Timestamp: {self.timestamp}\n Trade Instructions:\n{instructions_str}"

@dataclass
class SignalEvent:
    """
    Event representing trading signals.
    """
    signal: Signal
    type: str = field(init=False, default='SIGNAL')

    def __str__(self) -> str:
        return f"\n{self.type} Event: {str(self.signal)}"