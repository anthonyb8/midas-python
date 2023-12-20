# client.py
import logging
import threading
from .wrapper import BrokerApp
from engine.utils import get_config_for_api

api_config = get_config_for_api()


class BrokerClient():

    def __init__(self, logger:logging.Logger, host=api_config['HOST'], port=api_config['PORT'], clientId=api_config['TRADE_CLIENT_ID'], ib_account =api_config['IB_ACCOUNT']):
        self.logger = logger
        
        self.app = BrokerApp(logger)
        self.host = host
        self.port = port
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
        self.logger.info('Waiting for connection...')
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
    
    # -- Data objects --
    # def create_contract(self, **contract_data:dict):
    #     try:
    #         contract_model = utils.ContractModel(**contract_data)
    #         return contract_model.get_contract()
    #     except ValidationError as e:
    #         raise e
    
    # def validate_contract(self, contract:Contract):
    #     self.app.is_valid_contract = None # Reset incase it has been used
    #     self.app.validate_contract_event.clear()

    #     reqId = self._get_valid_id()
    #     self.app.reqContractDetails(reqId=reqId, contract=contract)
    #     self.app.validate_contract_event.wait()
    #     return self.app.is_valid_contract
    
    # def create_order(self,order_type:Literal['MKT', 'LMT','STP', 'TAIL'], **order_data:dict):
    #     try:
    #         order_model = utils.OrderModel(**order_data)
            
    #         if order_type == 'MKT':
    #             return order_model.market_order()
    #         elif order_type =='LMT':
    #             return order_model.limit_order()
    #         elif order_type == 'STP':
    #             return order_model.stop_order()
    #         elif order_type == 'TAIL':
    #             return order_model.trailingStop_order()
    #         else:
    #             raise ValueError(f"{order_type} not a valid order type.")
    #     except ValidationError as e:
    #         raise f"Validation error while creating order: {e}"
    
    # -- Get Functions --
    # def get_active_orders(self):
    #     return self.app.active_orders
    
    # def get_account_information(self):
    #     return self.app.account_info
    
    # def get_positions(self):
    #     return self.app.positions
    
    # def get_execution_details(self):
    #     return self.app.executed_orders

    # -- Send Functions --
    # def place_order(self,contract:Contract, order:Order):
    #     orderId = self._get_valid_id()
    #     try:
    #         self.app.placeOrder(orderId=orderId, contract=contract, order=order)
    #     except Exception as e:
    #         raise e
        
    # def cancel_order(self, orderId:int):
    #     self.app.cancelOrder(orderId=orderId)
        




