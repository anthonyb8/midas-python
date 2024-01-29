# client.py
import logging
import threading
from .wrapper import BrokerApp
from queue import Queue  
from core.base.events import OrderEvent
from utilities.portfolio_server import PortfolioServer
from decouple import config


class BrokerClient():

    def __init__(self, event_queue: Queue, logger:logging.Logger,portfolio_server: PortfolioServer, host=config('HOST'), port=config('PORT'), clientId=config('TRADE_CLIENT_ID'), ib_account =config('IB_ACCOUNT')):
        self.logger = logger
        self.event_queue = event_queue
        
        self.app = BrokerApp(logger, portfolio_server)
        self.host = host
        self.port = int(port)
        self.clientId = clientId
        self.account = ib_account

        self.lock = threading.Lock()  # create a lock
    
    # -- Helper --
    def _websocket_connection(self):
        self.app.connect(self.host, self.port, self.clientId)
        self.app.run()

    def _get_valid_id(self): 
        with self.lock:
            current_valid_id = self.app.next_valid_order_id
            self.app.next_valid_order_id += 1
            return current_valid_id 
        
    def _manange_subscription_to_account_updates(self, subscribe:bool):
        self.app.reqAccountUpdates(subscribe=subscribe, acctCode=self.account)

    def _get_initial_active_orders(self):
        self.app.reqOpenOrders()

    # -- Connection --
    def connect(self):
        thread = threading.Thread(target=self._websocket_connection, daemon=True)
        thread.start()

        # Waiting for confirmation of connection
        self.logger.info('Waiting For Broker Connection...')
        self.app.connected_event.wait()
        
        #  Waiting for next valid id to be returned
        self.app.valid_id_event.wait()

        # Waiting for initial download of account information and positions
        self._manange_subscription_to_account_updates(subscribe=True)
        self.app.account_download_event.wait()

        # Wating for initial open orders, need to explicatly call, as open orders not autmatically returned if no orders
        self._get_initial_active_orders()
        self.app.open_orders_event.wait()

    def disconnect(self):
        self._manange_subscription_to_account_updates(subscribe=False)
        self.app.disconnect()

    def is_connected(self):
        return self.app.isConnected()
    
    # -- Orders --

    def on_order(self, event: OrderEvent):
        # Convert order to execution here
        contract = event.contract
        order = event.order
        self.handle_order(contract,order) 

    def handle_order(self, contract, order):
        orderId = self._get_valid_id()
        try:
            self.app.placeOrder(orderId=orderId, contract=contract, order=order)

        except Exception as e:
            raise e

    def cancel_order(self, orderId:int):
        self.app.cancelOrder(orderId=orderId)





