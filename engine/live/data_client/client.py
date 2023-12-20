# client.py
import threading
import logging
from queue import Queue
from .wrapper import DataApp
from engine.utils import get_config_for_api

api_config = get_config_for_api()


class DataClient:

    def __init__(self, event_queue:Queue, logger:logging.Logger, host=api_config['HOST'], port=api_config['PORT'], clientId=api_config['DATA_CLIENT_ID'], ib_account =api_config['IB_ACCOUNT'],):
        self.logger = logger
        self.app = DataApp(event_queue, logger)
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

    # -- Connection --
    def connect(self):
        thread = threading.Thread(target=self._websocket_connection, daemon=True)
        thread.start()

        # Waiting for confirmation of connection
        self.logger.info('Waiting for connection...')
        self.app.connected_event.wait()
        
        #  Waiting for next valid id to be returned
        self.app.valid_id_event.wait()

    def disconnect(self):
        self.app.disconnect()

    def is_connected(self):
        return self.app.isConnected()
    