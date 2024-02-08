from typing import Dict
from queue import Queue
from ibapi.contract import Contract
from midas.events import  SignalEvent, OrderEvent
from midas.order_book import OrderBook
from midas.portfolio import PortfolioServer
from .data import LimitOrder, MarketOrder, StopLoss, Action, OrderType
from midas.symbols import Symbol, Future, Equity
import logging

class OrderManager:
    def __init__(self, strategy_allocation:float, symbols_map: Dict[str, Symbol], event_queue: Queue, order_book:OrderBook, portfolio_server: PortfolioServer, logger:logging.Logger):
        """
        Initialize the strategy with necessary parameters and components.

        Parameters:
            symbols_map (Dict[str, Contract]): Mapping of symbol strings to Contract objects.
            event_queue (Queue): Event queue for sending events to other parts of the system.
        """
        self.trade_allocation = strategy_allocation # percentage of available capital allowed on a given trade
        self.symbols_map = symbols_map
        self._event_queue = event_queue 
        self.portfolio_server = portfolio_server
        self.order_book = order_book
        self.logger = logger 

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

        orders = []
        total_capital_required = 0
        # capital = self.portfolio_server.capital
        # margin_requirement = self.portfolio_server.margin_requirement
        # margin = self.portfolio_server.margin

        position_allocation = self.trade_allocation * self.portfolio_server.account['AvailableFunds'] # capital available for the next trade( all legs)

        for trade in trade_instructions:
            if isinstance(self.symbols_map[trade.ticker], Future):
                order, capital_required = self.futures_order_details(trade, position_allocation)
            # elif isinstance(self.symbols_map[trade.ticker], Equity):
            #     price, quantity = self.equity_order_details(trade.contract, action[trade.action], trade.weight, capital, positions)
            #     total_trade_value += price * quantity
            else:
                raise ValueError(f"Symbol not of valid type : {self.symbols_map[trade.ticker]}")
            
            order_details = {
                'trade_insructions': trade,
                'action' : trade.action, 
                'contract': self.symbols_map[trade.ticker].contract, 
                'order' : order

            }
            
            orders.append(order_details)
            total_capital_required += capital_required

        if (total_capital_required + self.portfolio_server.account['RequiredMargin']) <= (self.portfolio_server.account['AvailableFunds'] + self.portfolio_server.account['CurrentMargin']):
            for order in orders:
                self.set_order(timestamp, order['trade_insructions'], order['action'], order['contract'],order['order'])
        else:
            self.logger.info("Not enough capital to execute all orders")

    def create_order(self, order_type: OrderType, action : Action, quantity: float, limit_price: float=None, aux_price:float=None):
        if order_type == OrderType.MARKET:
            return MarketOrder(action=action, quantity=quantity)
        elif order_type == OrderType.LIMIT:    
            return LimitOrder(action=action, quantity=quantity, limit_price=limit_price)
        elif order_type == OrderType.STOPLOSS:
            return StopLoss(action=action, quantity=quantity,aux_price=aux_price)
        else:
            raise ValueError(f"OrderType not of valid type : {order_type}")

    def equity_order_details(self, contract, action: Action, weight: float, current_capital: float, positions: dict):
        """
        Create order details based on trade action and market data.

        Parameters:
            contract: The trading contract.
            action (str): Trade action ('LONG', 'SELL', etc.).
            weight (float): Allocation weight for the trade.
            market_data: Market data for the trade.
            current_capital (float): Current available capital.
            positions (dict): Current open positions.

        Returns:
            Tuple containing action, fill price, and quantity of the order.
        """
        fill_price = self.order_book[contract]['data']['CLOSE']  # Assuming the order gets filled at the next bar's open price
        if action in [action.LONG, action.SHORT]:
            trade_value = (current_capital * self.strategy_allocation) * weight
            quantity = int(round(trade_value / fill_price, 0))
        else:  # 'SELL' or 'COVER'
            quantity = positions[contract].quantity

        return action, fill_price, quantity
    
    def futures_order_details(self, trade_instruction, position_allocation):
        ticker = trade_instruction.ticker
        action = trade_instruction.action
        weight = trade_instruction.weight
        current_price = self.order_book.current_price(ticker=ticker)
        contract_size = self.symbols_map[ticker].contractSize

        order_allocation = position_allocation * abs(weight)  # Assuming weight can be negative

        self.logger.info(f"\nOrder Allocation: {order_allocation}")

        # Adjust quantity based on the trade allocation
        if action in [Action.LONG, Action.SHORT]:  # Entry signal
            quantity = order_allocation / (current_price * contract_size)
            if action == Action.LONG:
                quantity_factor = 1
            elif action == Action.SHORT:
                quantity_factor = -1
        elif action in [Action.SELL, Action.COVER]:  # Exit signal
            quantity = self.portfolio_server.positions[ticker].quantity
            if action == Action.SELL:
                quantity_factor = 1
            elif action == Action.COVER:
                quantity_factor = -1
        
        quantity = quantity * quantity_factor
        margin_required = abs(quantity) * self.symbols_map[ticker].initialMargin

        order = self.create_order(trade_instruction.order_type,action,quantity) #TODO: update logic for different types of orders
        
        return order, margin_required
    
    def set_order(self, timestamp, trade_instruction,action, contract, order):
        """
        Create and queue an OrderEvent.

        Parameters:
            order_detail: Details of the order to be created and queued.
        """
        order_event = OrderEvent(timestamp, trade_instruction, action, contract, order)
        self._event_queue.put(order_event)
        
    
    # def check_capital(self, current_capital: float, total_trade_value: float) -> bool:
    #     """
    #     Check if there is enough capital to execute the proposed trades.

    #     Parameters:
    #         current_capital (float): Current available capital.
    #         total_trade_value (float): Total value of the proposed trades.

    #     Returns:
    #         bool: True if there is enough capital, False otherwise.
    #     """
    #     return current_capital >= total_trade_value
    
    # def get_contract(self, symbol: str) -> Contract:
    #     """Retrieve contract for a given symbol."""
    #     return self.symbols_map[symbol].contract