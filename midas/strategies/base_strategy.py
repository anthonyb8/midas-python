from typing import List
from abc import ABC, abstractmethod
from queue import Queue
from midas.events import  SignalEvent, MarketEvent, Signal, TradeInstruction
from midas.order_book import OrderBook

class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    This class provides a template for developing various trading strategies,
    handling market data, generating signals, and managing orders.
    """

    def __init__(self, order_book: OrderBook, event_queue: Queue):
        """
        Initialize the strategy with necessary parameters and components.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbol strings to Contract objects.
            event_queue (Queue): Event queue for sending events to other parts of the system.
        """
        self._event_queue = event_queue 
        self.order_book = order_book
        
        self.trade_id = 1
        self.current_position = None
    
    def on_market_data(self, event: MarketEvent):
        """
        Handle new market data events.

        Parameters:
            event (MarketDataEvent): The market data event to handle.
        """
        timestamp = event.timestamp
        data = event.data

        self.handle_market_data()

    @abstractmethod
    def handle_market_data(self):
        """
        Process market data and generate trading signals.

        Parameters:
            data (Dict): The market data.
            timestamp (str): The timestamp of the data.
        """
        pass

    def set_signal(self, trade_instructions:List[TradeInstruction], timestamp):
        """
        Create and queue signal events based on trading instructions.

        Parameters:
            trade_instructions: Trading instructions generated from the market data.
            market_data: Market data associated with the signals.
            timestamp: Timestamp for the signals.
        """
        signal = Signal(timestamp, trade_instructions)
        self._event_queue.put(SignalEvent(signal))

    @abstractmethod
    def entry_signal(self):
        """
        Generate an entry signal based on market data.

        Parameters:
            data (Dict): Market data used for generating the entry signal.
        """
        pass

    @abstractmethod
    def exit_signal(self):
        """
        Generate an exit signal based on market data.

        Parameters:
            data (Dict): Market data used for generating the exit signal.
        """
        pass

    @abstractmethod
    def asset_allocation(self):
        """
        Define the asset allocation strategy.
        """
        pass
