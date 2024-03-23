import queue
import logging
from enum import Enum
from typing import Union
from decouple import config
from midas_database import DatabaseClient

from .parameters import Parameters
from midas.order_book import OrderBook
from midas.symbols.symbols import Symbol
from midas.strategies import BaseStrategy
from midas.utils.logger import SystemLogger
from midas.portfolio import PortfolioServer
from midas.order_manager import OrderManager
from midas.performance import PerformanceManager


DATABASE_KEY = config('MIDAS_API_KEY')
DATABASE_URL = config('MIDAS_URL')

class Mode(Enum):
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"

class Config:   
    def __init__(self, mode: Mode, params: Parameters, logger_output="file", logger_level=logging.INFO):
        if not isinstance(mode, Mode):
            raise ValueError(f"'mode' must be of type Mode enum.")
        
        if not isinstance(params, Parameters):
            raise ValueError(f"'params' must be of type Parameters instance.")

        self.mode = mode
        self.params = params
        self.event_queue = queue.Queue()
        self.database = DatabaseClient(DATABASE_KEY, DATABASE_URL)
        self.logger = SystemLogger(params.strategy_name, output=logger_output, level=logger_level).logger

        # Handlers
        self.order_book: OrderBook
        self.strategy: BaseStrategy
        self.order_manager: OrderManager
        self.portfolio_server: PortfolioServer
        self.performance_manager: PerformanceManager

        # Variables
        self.live_data_client = None
        self.hist_data_client = None
        self.broker_client = None
        self.dummy_broker = None
        self.contract_handler = None
        self.symbols_map = {}
        self.data_ticker_map = {}

        # Set-up
        self.setup()

    def setup(self):
        # Map ticker to symbol object
        for symbol in self.params.symbols:
            self.map_symbol(symbol)

        self.logger.info(f"Test {self.symbols_map}")
        self._initialize_components()
        self.logger.info("test2")

        
        # Load historical data if the strategy requires a train period
        if self.params.train_start:
            self.load_train_data()

        # Set-up data subscriptions based on mode
        if self.mode == Mode.LIVE:
            self.load_live_data()
        elif self.mode == Mode.BACKTEST:
            self.load_backtest_data()

    def map_symbol(self, symbol: Symbol):
        self.data_ticker_map[symbol.data_ticker] = symbol.ticker

        self.symbols_map[symbol.ticker] = symbol
        # if self.mode == Mode.BACKTEST:
        # elif self.mode == Mode.LIVE and self.contract_handler.validate_contract(symbol.contract):
        #     self.symbols_map[symbol.ticker] = symbol

    def _initialize_components(self):
        self.order_book = OrderBook(data_type=self.params.data_type)
        self.performance_manager = PerformanceManager(self.database,self.logger, self.params)
        self.portfolio_server = PortfolioServer(self.symbols_map, self.logger)
        self.order_manager = OrderManager(self.symbols_map, self.event_queue, self.order_book, self.portfolio_server, self.logger)

        if self.mode == Mode.LIVE:
            self._set_live_environment()
        elif self.mode == Mode.BACKTEST:
            self._set_backtest_environment()
        
    def _set_live_environment(self):
        from midas.gateways.live import (DataClient, BrokerClient, ContractManager)
        
        # Gateways
        self.live_data_client = DataClient(self.event_queue, self.logger)
        self.broker_client = BrokerClient(self.event_queue,self.logger,self.portfolio_server, self.performance_manager)
        self._connect_live_clients()
        
        # Handlers
        self.contract_handler = ContractManager(self.live_data_client, self.logger) # TODO: CAN ADD to the Data CLIENT AND/OR TRADE CLIENT

        for ticker, symbol in self.symbols_map.items():
            if not self.contract_handler.validate_contract(symbol.contract):
                raise RuntimeError(f"{ticker} invalid contract.")

    def _set_backtest_environment(self):
        from midas.gateways.backtest import (DataClient, BrokerClient, DummyBroker)

        # Gateways
        self.hist_data_client = DataClient(self.event_queue, self.database)
        self.dummy_broker = DummyBroker(self.symbols_map, self.event_queue,self.order_book, self.params.capital, self.logger)
        self.broker_client = BrokerClient(self.event_queue, self.logger, self.portfolio_server, self.performance_manager, self.dummy_broker)
        
    def _connect_live_clients(self):
        self.live_data_client.connect()
        self.broker_client.connect()

    def load_live_data(self):
        try:
            for _, symbol in self.symbols_map.items():
                self.live_data_client.get_data(data_type=self.params.data_type, contract=symbol.contract) 
        except ValueError:
            raise ValueError(f"Error loading live data for symbol {symbol.ticker}.")

    def load_backtest_data(self):
        tickers = list(self.data_ticker_map.keys())
        response  = self.hist_data_client.get_data(tickers, self.params.test_start, self.params.test_end,self.params.missing_values_strategy)

        if response:
            self.logger.info(f"Backtest data loaded.")
        else:
            raise RuntimeError("Backtest data did not load.")

    def load_train_data(self):
        """
        Retrieves data from the database and initates the data processing. Stores initial data response in self.price_log.

        Args:
            symbols (List[str]) : A list of tickers ex. ['AAPL', 'MSFT']
            start_date (str) : Beginning date for the backtest ex. "2023-01-01"
            end_date (str) : End date for the backtest ex. "2024-01-01"
        """
        # If live the dataclient from teh backtest need to get historical dat
        if not self.hist_data_client:
            from midas.gateways.backtest import (DataClient)
            self.hist_data_client = DataClient(self.event_queue, self.database)

        # Get historical data
        tickers = list(self.data_ticker_map.keys())
        self.hist_data_client.get_data(tickers, self.params.train_start, self.params.train_end,self.params.missing_values_strategy)
        train_data = self.hist_data_client.data

        # # Extract contract details for mapping
        contracts_map = {symbol.data_ticker: symbol.ticker for symbol in self.symbols_map.values()}
        train_data['symbol'] = train_data['symbol'].map(contracts_map)

        # # Sorting the DataFrame by the 'timestamp' column in ascending order
        train_data = train_data.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
        self.train_data = train_data.pivot(index='timestamp', columns='symbol', values='close')

    def set_strategy(self, strategy: Union[BaseStrategy, type]):
        # Check if 'strategy' is a class and a subclass of BaseStrategy
        if not isinstance(strategy, type) or not issubclass(strategy, BaseStrategy):
            raise ValueError(f"'strategy' must be a class and a subclass of BaseStrategy.")

        try:
            strategy = strategy(symbols_map= self.symbols_map, train_data = self.train_data, portfolio_server=self.portfolio_server, logger = self.logger,order_book = self.order_book,event_queue=self.event_queue)
            self.strategy = strategy
        except:
            raise RuntimeError("Error creating strategy instance.")