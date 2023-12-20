import queue
from typing import Union
from engine.base.handlers import BaseStrategy
from database import DatabaseClient
from engine.base.data import Symbol, MarketDataType
from engine.utils import setup_logger
import os
from decouple import config

DATABASE_KEY = config('MIDAS_API_KEY')
DATABASE_URL = config('MIDAS_URL')

class Mode:
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"

class Config:
    def __init__(self, mode: Mode):
        self.event_queue = queue.Queue()
        self.mode = mode
        self.strategy_name : str
        self.parameters : {}

        # Clients
        self.data_client = None
        self.broker_client = None

        # Handlers
        self.data_handler = None
        self.strategy = None
        self.portfolio_handler = None
        self.execution_handler = None
        self.performance_handler = None
        self.contract_handler = None

        #Supporting
        self.database = None
        self.dashboard = None

        # Variables
        self.symbols_map = {}
        self.capital = None
        self.start_date = None
        self.end_date = None

        # Logger
        self.logger = None

        # Set-up
        self.setup()

    def setup(self):
        self.set_logger()
        self.map_parameters()
        self.initialize_components()

        for symbol in self.parameters['symbols']:
            self.map_symbol(symbol)

        if self.mode == Mode.LIVE:
            self.load_live_data()
        elif self.mode == Mode.BACKTEST:
            self.load_backtest_data()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def map_parameters(self):
        self.capital = self.parameters['capital']
        self.start_date = self.parameters['start_date']
        self.end_date = self.parameters['end_date']

    def map_symbol(self, symbol: Symbol):
        contract = symbol.to_contract()
        self.symbols_map[symbol.symbol] = contract
        print(self.contract_handler)
        if self.mode == Mode.LIVE and self.contract_handler.validate_contract(contract):
            self.symbols_map[symbol.symbol] = contract

    def set_logger(self):
        # Define the log directory path
        current_dir = os.path.dirname(__file__)
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        log_dir = os.path.join(base_dir, 'strategies', self.strategy_name, 'logs')

        # Create the log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Set up the logger
        log_file_name = os.path.join(log_dir, f'{self.strategy_name}.log')
        self.logger = setup_logger(f'{self.strategy_name}_logger', log_file_name)

        self.logger.info("Logger setup complete.")

    def initialize_components(self):
        if self.mode == Mode.LIVE:
            self._set_live_environment()
        elif self.mode == Mode.BACKTEST:
            self._set_backtest_environment()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        
    def _set_live_environment(self):
        from engine.live import (DataClient, BrokerClient, LiveExecutionHandler, LivePortfolioHandler, LiveDataHandler, ContractManager)
        
        # Clients
        self.data_client = DataClient(self.event_queue, self.logger)
        self.broker_client = BrokerClient(self.logger)
        self.connect_live_clients()
        
        # Handlers
        self.data_handler = LiveDataHandler(self.data_client, self.logger)
        self.portfolio_handler = LivePortfolioHandler(self.broker_client)
        self.execution_handler = LiveExecutionHandler(self.event_queue, self.broker_client)
        self.contract_handler = ContractManager(self.data_client)

    def _set_backtest_environment(self):
        from engine.backtest import (DataClient, BrokerClient, BacktestDataHandler, BacktestPortfolioHandler, BacktestExecutionHandler, BacktestPerformanceHandler)

        # Clients
        self.data_client = DataClient(DATABASE_KEY,DATABASE_URL)
        self.broker_client = BrokerClient(self.logger)

        # Handlers
        self.data_handler = BacktestDataHandler(self.event_queue, self.data_client)
        self.portfolio_handler = BacktestPortfolioHandler(self.broker_client)
        self.execution_handler = BacktestExecutionHandler(self.event_queue)
        self.performance_handler = BacktestPerformanceHandler(self.broker_client, self.logger)

    def connect_live_clients(self):
        self.data_client.connect()
        self.broker_client.connect()
        # self.load_live_data()

    def load_live_data(self):
        for contract in self.contract_handler.validated_contracts.values():
            self.data_handler.get_data(data_type=MarketDataType.BAR, contract=contract) # TODO: data type will be passed

    def load_backtest_data(self):
        self.data_handler.get_data(list(self.symbols_map.keys()), self.start_date, self.end_date)

    def set_strategy(self, strategy: Union[BaseStrategy, type]):
        if isinstance(strategy, type):
            strategy = strategy(symbols_map=self.symbols_map, event_queue=self.event_queue)
        self.strategy = strategy
