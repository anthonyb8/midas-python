from queue import Queue
from engine.base.events import ExecutionEvent, OrderEvent
from engine.base.handlers import BaseExecutionHandler  
from engine.backtest.broker_client import BrokerClient

class BacktestExecutionHandler(BaseExecutionHandler):
    """
    Handles the simulation of the execution of orders in the backtest.

    Args:
        BaseExecutionHandler (Object) : The base execution handler, an abstract class.

    """
    def __init__(self, event_queue:Queue):#,  broker_client: BrokerClient):
        """
        Class constructor. 
        
        Args:
            broker_client (BrokerClient) : Simulates the broker for the backtest.
            queue (Queue) : The main event queue. 
        
        """
        self.event_queue = event_queue
        # self. broker_client =  broker_client

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
