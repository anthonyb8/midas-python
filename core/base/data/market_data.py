from abc import ABC
from enum import Enum, auto
from typing import Optional
import pandas as pd

class MarketDataType(Enum):
    TICK = auto()
    BAR = auto()

class MarketData(ABC):
    """Abstract base class for market data types."""
    pass

class TickData(MarketData):
    """Class representing tick data."""
    def __init__(self):
        self.TIMESTAMP: Optional[float] = None
        self.ASK: Optional[float] = None
        self.ASK_SIZE: Optional[int] = None
        self.BID: Optional[float] = None
        self.BID_SIZE: Optional[int] = None

class BarData(MarketData):
    """Class representing bar data."""
    def __init__(self, timestamp: pd.Timestamp, open: float, high: float, low: float, close: float, volume: float):
        self.TIMESTAMP = timestamp
        self.OPEN = open
        self.HIGH = high
        self.LOW = low
        self.CLOSE = close
        self.VOLUME = volume

    @property
    def current_price(self) -> float:
        """Returns the best current price estimate."""
        # TODO: Implement logic for no look ahead bias
        return self.OPEN

    @classmethod
    def from_series(cls, series):
        """Create an instance from a data series."""
        return cls(
            timestamp=series['timestamp'],
            open=series['open'],
            high=series['high'],
            low=series['low'],
            close=series['close'],
            volume=series['volume'],
        )


