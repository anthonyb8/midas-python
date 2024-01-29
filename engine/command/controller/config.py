import os
import queue
from decouple import config
from typing import Union
from core.base.data import Symbol, MarketDataType
from core.oms import OrderManager
from core.strategies import BaseStrategy
from core.order_book import OrderBook
from utilities.portfolio_server import PortfolioServer
from utilities.database import DatabaseClient
from utilities.logger import SystemLogger

DATABASE_KEY = config('LOCAL_API_KEY1')
DATABASE_URL = config('LOCAL_URL')

class Mode:
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"

class Config:
    def __init__(self, mode: Mode):
        self.event_queue = queue.Queue()
        self.mode = mode

        # Clients
        self.data_client = None
        self.broker_client = None
        self.dummy_broker = None

        # Handlers
        self.order_book = None
        self.strategy = None
        self.order_manager = None
        self.contract_handler = None

        #Supporting
        self.database = DatabaseClient(DATABASE_KEY, DATABASE_URL)
        self.logger = SystemLogger(self.strategy_name).logger
        self.portfolio_server = None
        self.dashboard = None

        # Variables
        self.symbols_map = {}
        self.strategy_name : str
        self.symbols : list
        self.start_date : str
        self.end_date : str
        self.capital : float 
        self.strategy_allocation : float
        self.parameters = {'strategy_name': self.strategy_name, 'capital': self.capital, 'strategy_allocation':self.strategy_allocation, 'symbols': [symbol.symbol for symbol in self.symbols]}

        # Set-up
        self.setup()

    def setup(self):
        # self.map_parameters()
        self.initialize_components()

        for symbol in self.symbols:
            self.map_symbol(symbol)

        if self.mode == Mode.LIVE:
            self.load_live_data()
        elif self.mode == Mode.BACKTEST:
            self.load_backtest_data()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    # def map_parameters(self):
    #     self.strategy_allocation = self.parameters['strategy_allocation']
    #     self.capital = self.parameters['capital']
    #     self.start_date = self.parameters['start_date']
    #     self.end_date = self.parameters['end_date']

    def map_symbol(self, symbol: Symbol):
        contract = symbol.to_contract()
        self.symbols_map[symbol.symbol] = contract

        if self.mode == Mode.LIVE and self.contract_handler.validate_contract(contract):
            self.symbols_map[symbol.symbol] = contract

    def initialize_components(self):
        self.order_book = OrderBook()
        self.portfolio_server = PortfolioServer(self.logger, self.mode)
        self.order_manager = OrderManager(self.strategy_allocation, self.symbols_map, self.event_queue, self.order_book, self.portfolio_server)

        if self.mode == Mode.LIVE:
            self._set_live_environment()
        elif self.mode == Mode.BACKTEST:
            self._set_backtest_environment()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        
    def _set_live_environment(self):
        from core.gateways.live import (DataClient, BrokerClient, ContractManager)
        
        # Gateways
        self.data_client = DataClient(self.event_queue, self.logger)
        self.broker_client = BrokerClient(self.event_queue,self.logger,self.portfolio_server)
        self.connect_live_clients()
        
        # Handlers
        self.contract_handler = ContractManager(self.data_client, self.logger) # TODO: CAN ADD to the Data CLIENT AND/OR TRADE CLIENT

    def _set_backtest_environment(self):
        from core.gateways.backtest import (DataClient, BrokerClient, DummyBroker)

        # Gateways
        self.data_client = DataClient(self.event_queue, self.database)
        self.dummy_broker = DummyBroker(self.event_queue,self.order_book, self.capital, self.logger)
        self.broker_client = BrokerClient(self.event_queue, self.logger, self.portfolio_server, self.dummy_broker)
        
    def connect_live_clients(self):
        self.data_client.connect()
        self.broker_client.connect()

    def load_live_data(self):
        for contract in self.contract_handler.validated_contracts.values():
            self.data_client.get_data(data_type=MarketDataType.BAR, contract=contract) # TODO: data type will be passed

    def load_backtest_data(self):
        self.data_client.get_data(self.symbols_map, self.start_date, self.end_date)

    def set_strategy(self, strategy: Union[BaseStrategy, type]):
        if isinstance(strategy, type):
            strategy = strategy(self.symbols_map,order_book = self.order_book,event_queue=self.event_queue)
        self.strategy = strategy