import logging
# from engibase.events import ExecutionEvent
# from portfo.managers import PositionsManager
from queue import Queue
from core.base.events import ExecutionEvent, OrderEvent
from utilities.portfolio_server import PortfolioServer
# from engine.base.handlers import BaseExecutionHandler  
# from engine.backtest.broker_client import BrokerClient

class BrokerClient:
    """
    Simulates the broker, controls the execution of trades and the updating of 'account' data.
    """
    def __init__(self,event_queue: Queue, logger: logging.Logger, portfolio_server: PortfolioServer):
        self.portfolio_server = portfolio_server
        self.logger = logger
        self.event_queue = event_queue
        # self.capital = 10000  # Placeholder, replace with dynamic initialization if necessary

    def on_order(self, event: OrderEvent):
        """
        The Order Event listener, called when a new order event is intercepted in the queue.

        Args:
            OrderEvent (Object) : Event with all the data related to a specific order to be executed.

        """
        contract = event.contract
        order = event.order
        signal = event.signal
        market_data = event.market_data
        self.handle_order(contract,order, signal, market_data)

    def handle_order(self, contract, order, signal, market_data):
        """
        Handles the the execution of the order, simulation the placing of order and creation of execution event.
        
        Args:
            contract (Object) : Class containing the specfics related to the symbol ex. ticker, exchange, currency
            order (Object) : Class that contains all the data related to a specific orde. ex OrderType(market, limit), and assocated data ex. limit price
            signal (Object) : Inititial signal object, used to pass signal data to trade client for updating the portfolio related fields.
            market_data (Object) : Initial MarketDataEvent, used to pass data not included in the signal or order to the trade client for portfolio updating.

        """

        execution_event = ExecutionEvent(contract=contract,order=order,signal=signal,market_data=market_data)
        # self.broker_client.placeOrder(execution_event)

        if execution_event:
            self.event_queue.put(execution_event)


    def on_execution(self, event: ExecutionEvent):
        contract = event.contract
        direction = event.order.action
        price = event.fill_price
        quantity = event.quantity
        timestamp = event.timestamp

        self.portfolio_server.update_positions(contract, direction, price, quantity)
        self.portfolio_server.update_backtest_capital(direction, quantity,price)
        
        # self._update_position(contract, direction, price, quantity)
        # self._update_capital(direction, quantity, price)

    def _update_position(self, contract, direction, price, quantity):
        self.logger.info(f"Updated Position: {contract}")

    def _update_capital(self, direction, quantity, price):
        pass

    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        liquidated_positions = {}

        for contract, position in self.portfolio_server.positions.items():
            liquidated_positions[contract]  = {
                'quantity' :position.quantity * -1,
                'direction' : 'BUY' if position.direction =='SELL' else 'SELL',
            }
        return liquidated_positions
        
    # @property
    # def positions(self):
    #     return self.position_manager.positions