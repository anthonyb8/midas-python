import logging
from typing import List, Union
from abc import ABC, abstractmethod
from queue import Queue

from midas.events import  SignalEvent, MarketEvent, TradeInstruction
from midas.order_book import OrderBook
from midas.portfolio import PortfolioServer


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    This class provides a template for developing various trading strategies,
    handling market data, generating signals, and managing orders.
    """

    def __init__(self, portfolio_server: PortfolioServer, order_book: OrderBook, logger:logging.Logger, event_queue: Queue):
        """
        Initialize the strategy with necessary parameters and components.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbol strings to Contract objects.
            event_queue (Queue): Event queue for sending events to other parts of the system.
        """
        # if not isinstance(order_book, OrderBook):
        #     raise TypeError("'order_book' must be of type OrderBook instance.")
        # if not isinstance(event_queue, Queue):
        #     raise TypeError("'event_queue' must be of type Queue instance.")
        
        self._event_queue = event_queue 
        self.order_book = order_book
        self.logger = logger
        self.portfolio_server = portfolio_server
        self.trade_id = 1
    
    def on_market_data(self, event: MarketEvent):
        """
        Handle new market events.

        Parameters:
            event (MarketEvent): The market event to handle.
        """
        if not isinstance(event, MarketEvent):
            raise TypeError("'event' must be of type Market Event instance.")

        self.handle_market_data()

    @abstractmethod
    def handle_market_data(self):
        """ Process market data and generate trading signals. """
        pass

    def set_signal(self, trade_instructions:List[TradeInstruction], trade_capital: Union[int, float], timestamp: Union[int, float]):
        """
        Create and queue signal events based on trading instructions.

        Parameters:
            trade_instructions: Trading instructions generated from the market data.
            market_data: Market data associated with the signals.
            timestamp: Timestamp for the signals.
        """
        try:
            signal_event = SignalEvent(timestamp, trade_capital, trade_instructions)
            self._event_queue.put(signal_event)
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Failed to create or queue SignalEvent due to input error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error when creating or queuing SignalEvent: {e}") from e

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
