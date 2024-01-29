import pandas as pd
from typing import List, Dict
from core.base.data import Direction
from datetime import datetime

class TradeInstruction:
    def __init__(self, contract:dict, direction: Direction, trade_id: int, leg_id: int, allocation_percent: float):
        self._data_validation(contract, direction, trade_id, leg_id, allocation_percent)

        self.contract = contract
        self.direction = direction.name
        self.trade_id = trade_id
        self.leg_id = leg_id
        self.allocation_percent = allocation_percent

    def _data_validation(self, ticker: str, direction: Direction, trade_id: int, leg_id: int, allocation_percent: float):
        # if not ticker or not isinstance(ticker, str):
        #     raise ValueError("Ticker must be a non-empty string.")
        
        if not isinstance(direction, Direction):
            raise ValueError("Direction must be of type Direction enum.")
        
        if not isinstance(trade_id, int) or trade_id < 0:
            raise ValueError("Trade ID must be a non-negative integer.")
        
        if not isinstance(leg_id, int) or leg_id < 0:
            raise ValueError("Leg ID must be a non-negative integer.")
        
        # if not (0 <= allocation_percent <= 100):
        #     raise ValueError("Allocation percent must be between 0 and 100.")
        
    def to_dict(self) -> Dict:
        return {
            'ticker': self.contract.symbol,
            'direction' : self.direction,
            'trade_id':self.trade_id,
            'leg_id':self.leg_id,
            'allocation_percent':self.allocation_percent,
        }


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
        
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'trade_instructions': [instruction.to_dict() for instruction in self.trade_instructions]
        }

class SignalsManager:
    def __init__(self):
        self.signals_log = []

    def add_signal(self, signal: Signal):
        self.signals_log.append(signal.to_dict()) 
        
    @property
    def log(self):
        return self.signals_log

