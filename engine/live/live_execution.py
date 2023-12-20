from queue import Queue  
from engine.live.broker_client import BrokerClient
from engine.base.handlers import BaseExecutionHandler 
from engine.base.events import ExecutionEvent, OrderEvent

class LiveExecutionHandler(BaseExecutionHandler): 

    def __init__(self, event_queue: Queue, broker_client: BrokerClient):
        self.broker_client = broker_client
        self.app = self.broker_client.app
        self.event_queue = event_queue

    def on_order(self, event: OrderEvent):
        # Convert order to execution here
        contract = event.contract
        order = event.order
        signal = event.signal
        market_data = event.market_data
        self.handle_order(contract,order, signal, market_data)

        # execution_event = self.handle_order(order_event)
        # if execution_event:
        #     self.event_queue.put(execution_event)

    def handle_order(self, contract, order, signal, market_data):
    
        orderId = self.broker_client._get_valid_id()
        try:
            self.app.placeOrder(orderId=orderId, contract=contract, order=order)
            execution_event = ExecutionEvent(contract=contract,order=order,signal=signal,market_data=market_data)
        
            if execution_event:
                self.event_queue.put(execution_event)

        except Exception as e:
            raise e

    def cancel_order(self, orderId:int):
        self.app.cancelOrder(orderId=orderId)
