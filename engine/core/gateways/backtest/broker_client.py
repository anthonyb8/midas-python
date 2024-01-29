import logging
from queue import Queue
from core.base.events import ExecutionEvent, OrderEvent
from core.order_book import OrderBook
from utilities.portfolio_server import PortfolioServer
from .dummy_broker import DummyBroker

class BrokerClient:
    """
    Simulates the broker, controls the execution of trades and the updating of 'account' data.
    """
    def __init__(self,event_queue: Queue, logger: logging.Logger, portfolio_server: PortfolioServer, broker:DummyBroker):
        # Subscriptions
        self.portfolio_server = portfolio_server
        self.broker = broker
        self.logger = logger
        self.event_queue = event_queue

        self.update_AvailableFunds()

    def on_order(self, event: OrderEvent):
        """
        The Order Event listener, called when a new order event is intercepted in the queue.

        Args:
            OrderEvent (Object) : Event with all the data related to a specific order to be executed.

        """
        contract = event.contract
        order = event.order
        timestamp = event.timestamp
        trade_instructions = event.trade_instructions
        direction= event.direction

        self.handle_order(timestamp, trade_instructions,direction,contract,order)

    def handle_order(self, timestamp, trade_instructions, direction ,contract, order):
        """
        Handles the the execution of the order, simulation the placing of order and creation of execution event.
        
        Args:
            contract (Object) : Class containing the specfics related to the symbol ex. ticker, exchange, currency
            order (Object) : Class that contains all the data related to a specific orde. ex OrderType(market, limit), and assocated data ex. limit price
            signal (Object) : Inititial signal object, used to pass signal data to trade client for updating the portfolio related fields.
            market_data (Object) : Initial MarketDataEvent, used to pass data not included in the signal or order to the trade client for portfolio updating.

        """

        self.broker.placeOrder(timestamp, trade_instructions, direction ,contract, order)

    def on_execution(self, event:ExecutionEvent):
        self.update_positions()
        self.update_AvailableFunds()
        self.update_trades()
  
    def update_positions(self):
        positions = self.broker.return_positions()
        for contract, position_data in positions.items():
            self.portfolio_server.update_positions(contract, position_data)

    def update_AvailableFunds(self):
        key, value = self.broker.return_AvailableFunds()
        self.portfolio_server.update_account(key, value)

    def update_EquityValue(self):
        self.broker.update_equity_value()
        key, value = self.broker.return_EquityValue()
        self.portfolio_server.update_account(key, value)

    def update_trades(self):
        last_trades = self.broker.return_ExecutedTrade()
        for contract in last_trades:
            self.portfolio_server.update_trades(**last_trades[contract])

    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        self.update_positions()
        self.update_AvailableFunds()
        self.update_EquityValue()
        self.broker.liquidate_positions()
        self.update_trades()