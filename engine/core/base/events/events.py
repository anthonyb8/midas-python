from typing  import  Dict
from core.base.data import Signal, MarketData
from datetime import datetime

class Event:
    """Base class for events."""
    pass

class MarketDataEvent(Event):
    """
    Event representing market data updates.

    Attributes:
        type (str): The type of the event, here 'MARKET_DATA'.
        market_data (Dict[str, Dict[str, Any]]): Market data for different tickers.
    """
    def __init__(self, market_data: Dict[str, MarketData]):
        self.type = 'MARKET_DATA'
        self.data = market_data
        
    @property
    def timestamp(self):
        """Return the timestamp of the first ticker in the market data."""
        first_ticker= list(self.data.values())[0]
        timestamp = first_ticker.TIMESTAMP

        # Check if the TIMESTAMP is already in a datetime format
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        # Otherwise, assume it's a Unix timestamp and convert it
        else:
            converted_timestamp = datetime.utcfromtimestamp(timestamp)
            return converted_timestamp.isoformat()
        
    def  __str__(self) -> str:
        string = f"\n{self.type} : \n"
        for contract, MarketData in self.data.items():
            string += f" {contract} : {MarketData.__dict__}\n"
        return string
    
    def current_price(self, contract):
        """
        Return the current price of the given contract.

        Parameters:
            contract: The contract for which to retrieve the current price.

        Returns:
            The current price of the contract.
        """
        return self.data[contract.symbol].OPEN #TODO : determine best price to return as current price
    
class SignalEvent(Event):
    """
    Event representing trading signals.

    Attributes:
        type (str): The type of the event, here 'SIGNAL'.
        signal (Signal): The signal associated with this event.
        market_data (object): Market data relevant to the signal.
    """
    def __init__(self, signal: Signal):
        self.type = 'SIGNAL'
        self.signal = signal


    def __str__(self) -> str:
        signal_info = self.signal.to_dict() 
        string = f"\n{self.type} : \n Timestamp: {signal_info['timestamp']}\n"
        for trade in signal_info['trade_instructions']:
            string += f" Trade Instructions:{trade}\n"
        return string

    @property
    def tickers(self):
        """Return list of tickers involved in the signal."""
        return [trade.ticker for trade in self.signal.trades]

    @property
    def directions(self):
        return [trade.direction for trade in self.signal.trades]

    @property
    def allocation_percent(self):
        return self.signal.allocation_percent

    @property
    def trade_ids(self):
        return [trade.trade_id for trade in self.signal.trades]

    @property
    def leg_ids(self):
        return [trade.leg_id for trade in self.signal.trades]

    @property
    def current_prices(self):
        return {trade.ticker: self.market_data[trade.ticker].OPEN for trade in self.signal.trades}

class OrderEvent(Event):
    def __init__(self, timestamp, trade_instructions, direction,contract: object, order: object):
        self.type = 'ORDER'
        self.timestamp = timestamp
        self.trade_instructions = trade_instructions
        self.direction = direction # LONG,SHORT,SELL,COVER
        self.contract = contract
        self.order = order
    
    def __str__(self) -> str:
        string = f"\n{self.type} : \n Timestamp: {self.timestamp}\n Contract: {self.contract}\n Order: {self.order.__dict__}\n Trade Instructions: {self.trade_instructions.__dict__}\n Direction: {self.direction}\n"
        return string


    @property
    def symbol(self):
        return self.contract.symbol

    @property
    def quantity(self):
        return self.order.totalQuantity

    @property
    def is_entry(self):
        return self.direction in ['LONG', 'SHORT']

    @property
    def is_exit(self):
        return self.direction in ['COVER', 'SELL']

# Backtest event to simulate order filled
class ExecutionEvent(Event):
    def __init__(self,timestamp, trade_instructions,direction, contract:object, order: object):
        self.type = 'EXECUTION'
        self.timestamp = timestamp
        self.trade_instructions = trade_instructions
        self.direction = direction
        self.contract= contract
        self.order=order

    def __str__(self) -> str:
        string = f"\n{self.type} : \n Timestamp: {self.timestamp}\n Contract: {self.contract}\n Order: {self.order.__dict__}\n Trade Instructions: {self.trade_instructions.__dict__}\n Direction: {self.direction}\n"
        return string


    @property
    def fill_price(self):
        return self.market_data.OPEN # TODO update to account for slippage

    @property
    def symbol(self):
        return self.contract.symbol
    
    @property
    def quantity(self):
        return self.order.totalQuantity

    @property
    def is_entry(self):
        return self.direction in ['LONG', 'SHORT']

    @property
    def is_exit(self):
        return self.direction in ['COVER', 'SELL']
