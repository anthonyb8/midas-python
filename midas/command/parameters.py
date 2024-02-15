from dataclasses import dataclass, field
from midas.events import MarketDataType
from typing import List, Literal
from midas.symbols import Symbol


@dataclass
class Parameters:
    strategy_name: str
    capital: int
    data_type: MarketDataType
    missing_values_strategy : Literal['drop', 'fill_forward'] = 'fill_forward'
    strategy_allocation: float = 1.0
    train_start: str = None
    train_end: str = None
    test_start: str = None
    test_end: str = None
    symbols: List[Symbol] = field(default_factory=list)
    benchmark: List[str] = None
    # Derived attribute, not directly passed by the user
    tickers: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Populate the tickers list based on the provided symbols
        self.tickers = [symbol.ticker for symbol in self.symbols]

    def to_dict(self):
        return {
            'strategy_name': self.strategy_name, 
            'capital': self.capital, 
            'data_type': self.data_type.name, 
            'strategy_allocation': self.strategy_allocation, 
            'train_start': self.train_start, 
            'train_end': self.train_end, 
            'test_start': self.test_start,
            'test_end': self.test_end,
            'tickers': self.tickers, 
            'benchmark': self.benchmark
        }