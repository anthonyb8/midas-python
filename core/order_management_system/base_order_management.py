from abc import ABC, abstractmethod
from typing import Dict, List
from queue import Queue
from ibapi.contract import Contract
from engine.base.events import  SignalEvent,OrderEvent

class BaseOrderManagement(ABC):
    """
    Abstract base class for trading strategies.

    This class provides a template for developing various trading strategies,
    handling market data, generating signals, and managing orders.
    """

    def __init__(self, event_queue: Queue, portfolio_server):
        """
        Initialize the strategy with necessary parameters and components.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbol strings to Contract objects.
            event_queue (Queue): Event queue for sending events to other parts of the system.
        """
        self._event_queue = event_queue 
        self.portfolio_server = portfolio_server

    def on_signal(self, capital: float, positions: dict, event: SignalEvent):
        """
        Handle a new signal event, processing it to generate order events.

        Parameters:
            capital (float): Current available capital.
            positions (dict): Current open positions.
            event (SignalEvent): The signal event to handle.
        """
        self.handle_signal(event.signal.trade_instructions, event.market_data, capital, positions)

    def set_order(self, contract, order, signal, market_data):
        """
        Create and queue an OrderEvent.

        Parameters:
            order_detail: Details of the order to be created and queued.
        """
        order_event = OrderEvent(contract, order, signal, market_data)
        self._event_queue.put(order_event)

    @abstractmethod
    def handle_signal(self, trade_instructions, market_data, current_capital: float, positions: dict) -> List:
        """
        Process signal event to generate order details.

        Parameters:
            trade_instructions: Instructions from the signal event.
            market_data: Market data associated with the signal.
            current_capital (float): Current available capital.
            positions (dict): Current positions held.

        Returns:
            List: A list containing order details for each trade instruction.
        """
        pass

    @abstractmethod
    def create_order_details(self):
        """
        Abstract method to create specific order details.
        """
        pass
