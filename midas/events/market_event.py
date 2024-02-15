from abc import ABC
from enum import Enum
from typing  import  Dict, Optional
from dataclasses import dataclass, field
import pandas as pd
from datetime import datetime


class MarketDataType(Enum):
    TICK = 'TICK'
    BAR = 'BAR'

@dataclass
class MarketData(ABC):
    """Abstract base class for market data types."""
    pass

@dataclass
class TickData(MarketData):
    TIMESTAMP: Optional[float] = None
    ASK: Optional[float] = None
    ASK_SIZE: Optional[int] = None
    BID: Optional[float] = None
    BID_SIZE: Optional[int] = None

@dataclass
class BarData(MarketData):
    TIMESTAMP: pd.Timestamp
    OPEN: float
    HIGH: float
    LOW: float
    CLOSE: float
    VOLUME: float

    def current_price(self) -> float:
        """Returns the best current price estimate."""
        # Your implementation here
        return self.OPEN

    @classmethod
    def from_series(cls, series: pd.Series):
        """Create an instance from a data series."""
        return cls(
            TIMESTAMP=series['timestamp'],
            OPEN=series['open'],
            HIGH=series['high'],
            LOW=series['low'],
            CLOSE=series['close'],
            VOLUME=series['volume'],
        )

@dataclass
class MarketEvent:
    """
    Event representing market data updates.
    """
    data: Dict[str, MarketData]
    type: str = field(init=False, default='MARKET_DATA')

    def __str__(self) -> str:
        string = f"\n{self.type} : \n"
        for contract, market_data in self.data.items():
            string += f" {contract} : {market_data.__dict__}\n"
        return string
    
    @property
    def timestamp(self) -> str:
        """Return the timestamp of the first ticker in the market data."""
        first_ticker = list(self.data.values())[0]
        timestamp = first_ticker.TIMESTAMP
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        else:
            converted_timestamp = datetime.utcfromtimestamp(timestamp)
            return converted_timestamp.isoformat()