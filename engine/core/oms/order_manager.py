from typing import Dict
from queue import Queue
from ibapi.contract import Contract
from core.base.events import  SignalEvent, OrderEvent
from core.order_book import OrderBook
from utilities.portfolio_server import PortfolioServer
from core.base.data import LimitOrder, Direction
from ibapi.contract import Contract

class OrderManager:
    def __init__(self, strategy_allocation:float, symbols_map: Dict[str, Contract], event_queue: Queue, order_book:OrderBook, portfolio_server: PortfolioServer):
        """
        Initialize the strategy with necessary parameters and components.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbol strings to Contract objects.
            event_queue (Queue): Event queue for sending events to other parts of the system.
        """
        self.strategy_allocation = strategy_allocation
        self.symbols_map = symbols_map
        self._event_queue = event_queue 
        self.portfolio_server = portfolio_server
        self.order_book = order_book.book

    def on_signal(self, event: SignalEvent):
        """ 
        Signal listener.
        """
        trade_instructions = event.signal.trade_instructions
        timestamp = event.signal.timestamp

        self.handle_signal(timestamp,trade_instructions)

    def handle_signal(self, timestamp,trade_instructions):
        """
        Converts trade instructions into OrderEvents based on capital and positions.

        Parameters:
            trade_instructions: List of trade instructions.
            market_data: Market data for the trades.
            current_capital: Current available capital.
            positions: Current open positions.

        Returns:
            List[OrderEvent]: The corresponding order events if there is enough capital, otherwise an empty list.
        """
        trade_details = {}
        total_trade_value = 0

        capital = self.portfolio_server.capital
        positions = self.portfolio_server.positions

        for trade in trade_instructions:
            direction, price, quantity = self.create_order_details(trade.contract, Direction[trade.direction], trade.allocation_percent, capital, positions)
            total_trade_value += price * quantity
            trade_details[trade.contract] = {
                'signal': trade,
                'contract': trade.contract,
                'order': LimitOrder(direction=direction, quantity=quantity, limit_price=price)
            }

        order_events = []
        if self.check_capital(capital, total_trade_value):
            for ticker, details in trade_details.items():
                order_event = self.set_order(timestamp, trade, details['signal'].direction, details['contract'], details['order'])
                order_events.append(order_event)
        else:
            print("Not enough capital to execute all orders")

    def set_order(self, timestamp, trade_instruction,direction, contract, order):
        """
        Create and queue an OrderEvent.

        Parameters:
            order_detail: Details of the order to be created and queued.
        """
        order_event = OrderEvent(timestamp, trade_instruction, direction, contract, order)
        self._event_queue.put(order_event)

    def create_order_details(self, contract, direction: Direction, weight: float, current_capital: float, positions: dict):
        """
        Create order details based on trade direction and market data.

        Parameters:
            contract: The trading contract.
            direction (str): Trade direction ('LONG', 'SELL', etc.).
            weight (float): Allocation weight for the trade.
            market_data: Market data for the trade.
            current_capital (float): Current available capital.
            positions (dict): Current open positions.

        Returns:
            Tuple containing direction, fill price, and quantity of the order.
        """
        fill_price = self.order_book[contract]['data']['CLOSE']  # Assuming the order gets filled at the next bar's open price
        if direction in [Direction.LONG, Direction.SHORT]:
            trade_value = (current_capital * self.strategy_allocation) * weight
            quantity = int(round(trade_value / fill_price, 0))
        else:  # 'SELL' or 'COVER'
            quantity = positions[contract].quantity

        return direction, fill_price, quantity
    
    def check_capital(self, current_capital: float, total_trade_value: float) -> bool:
        """
        Check if there is enough capital to execute the proposed trades.

        Parameters:
            current_capital (float): Current available capital.
            total_trade_value (float): Total value of the proposed trades.

        Returns:
            bool: True if there is enough capital, False otherwise.
        """
        return current_capital >= total_trade_value
    
    def get_contract(self, symbol: str) -> Contract:
        """Retrieve contract for a given symbol."""
        return self.symbols_map[symbol]