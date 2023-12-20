from abc import ABC
from typing import Dict, List
from queue import Queue
from datetime import datetime
from engine.base.handlers import BaseStrategy
from engine.base.data import LimitOrder, Direction, TradeInstruction, MarketData
from ibapi.contract import Contract

class TestStrategy(BaseStrategy):

    def __init__(self, symbols_map: Dict[str, Contract], event_queue: Queue):
        """
        Initialize the TestStrategy with required parameters.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbols to their corresponding contracts.
            event_queue (Queue): Queue for dispatching events.
        """
        super().__init__(symbols_map, event_queue)
        self.strategy_allocation = 1.0  # Allocation percentage of total portfolio
        self.current_position = None
        self.trade_id = 0

    def asset_allocation(self) -> Dict[str, float]:
        """Return allocation percentages for the stocks."""
        return {'AAPL': 0.05, 'MSFT': 0.05}
    
    def entry_signal(self, data: Dict) -> bool:
        """Check conditions for entering a trade."""
        return data['AAPL'].CLOSE < data['MSFT'].CLOSE

    def exit_signal(self, data: Dict) -> bool:
        """Check conditions for exiting a trade."""
        return data['AAPL'].CLOSE > data['MSFT'].CLOSE

    def handle_market_data(self, data: Dict, timestamp: datetime):
        """
        Process market data and generate trade instructions based on entry and exit signals.

        Parameters:
            data (Dict): Market data.
            timestamp (datetime): Timestamp of the data.
        """
        trade_instructions = []

        if self.current_position is None and self.entry_signal(data):
            self.current_position = True
            self.trade_id += 1
            trade_instructions.extend([
                TradeInstruction('AAPL', Direction.LONG, self.trade_id, 1, self.asset_allocation()['AAPL']),
                TradeInstruction('MSFT', Direction.SHORT, self.trade_id, 2, self.asset_allocation()['MSFT'])
            ])

        elif self.current_position and self.exit_signal(data):
            self.current_position = None
            trade_instructions.extend([
                TradeInstruction('AAPL', Direction.SELL, self.trade_id, 1, 1.0),
                TradeInstruction('MSFT', Direction.COVER, self.trade_id, 2, 1.0)
            ])

        if trade_instructions:
            print(trade_instructions)
            self.set_signal(trade_instructions, data, timestamp)

    def get_contract(self, symbol: str) -> Contract:
        """Retrieve contract for a given symbol."""
        return self.symbols_map[symbol]

    def handle_signal(self, trade_instructions, market_data, current_capital, positions):
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

        for trade in trade_instructions:
            contract = self.get_contract(trade.ticker)
            direction, price, quantity = self.create_order_details(contract, Direction[trade.direction], trade.allocation_percent, market_data[trade.ticker], current_capital, positions)

            total_trade_value += price * quantity
            trade_details[trade.ticker] = {
                'signal': trade,
                'contract': contract,
                'order': LimitOrder(direction=direction, quantity=quantity, limit_price=price)
            }

        order_events = []
        if self.check_capital(current_capital, total_trade_value):
            for ticker, details in trade_details.items():
                order_event = self.set_order(details['contract'], details['order'], details['signal'], market_data[ticker])
                order_events.append(order_event)
        else:
            print("Not enough capital to execute all orders")

        # return order_events

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

    def create_order_details(self, contract, direction: Direction, weight: float, market_data: MarketData, current_capital: float, positions: dict):
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
        print(direction)

        fill_price = market_data.CLOSE  # Assuming the order gets filled at the next bar's open price
        if direction in [Direction.LONG, Direction.SHORT]:
            trade_value = (current_capital * self.strategy_allocation) * weight
            print(type(trade_value),type(fill_price))
            quantity = int(round(trade_value / fill_price, 0))
        else:  # 'SELL' or 'COVER'
            quantity = positions[contract].quantity

        return direction, fill_price, quantity