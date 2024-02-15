import queue
from decouple import config
from typing import Union
from midas.symbols import Symbol
from midas.order_manager import OrderManager
from midas.strategies import BaseStrategy
from midas.order_book import OrderBook
from midas.portfolio import PortfolioServer, PerformanceManager
from midas.tools import DatabaseClient
from midas.utils.logger import SystemLogger
from .parameters import Parameters


DATABASE_KEY = config('MIDAS_API_KEY')
DATABASE_URL = config('MIDAS_URL')

class Mode:
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"

class Config:   
    def __init__(self, mode: Mode, params: Parameters):
        self.mode = mode
        self.params = params
        self.event_queue = queue.Queue()
        self.database = DatabaseClient(DATABASE_KEY, DATABASE_URL)
        self.logger = SystemLogger(self.params.strategy_name).logger

        # Handlers
        self.order_book: OrderBook
        self.strategy: BaseStrategy
        self.order_manager: OrderManager
        self.portfolio_server: PortfolioServer
        self.performance_manager: PerformanceManager

        # Variables
        self.data_client = None
        self.broker_client = None
        self.dummy_broker = None
        self.contract_handler = None
        self.symbols_map = {}

        # Set-up
        self.setup()

    def setup(self):
        # self.map_parameters()
        self.initialize_components()

        #
        for symbol in self.params.symbols:
            self.map_symbol(symbol)
        
        # Load historical data if the strategy requires a train period
        if self.params.train_start:
            self.load_train_data()

        # Set-up data subscriptions based on mode
        if self.mode == Mode.LIVE:
            self.load_live_data()
        elif self.mode == Mode.BACKTEST:
            self.load_backtest_data()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def map_symbol(self, symbol: Symbol):
        if self.mode == Mode.BACKTEST:
            self.symbols_map[symbol.ticker] = symbol
        elif self.mode == Mode.LIVE and self.contract_handler.validate_contract(symbol.contract):
            self.symbols_map[symbol.ticker] = symbol

    def initialize_components(self):
        self.order_book = OrderBook(data_type=self.params.data_type)
        self.performance_manager = PerformanceManager(self.database,self.logger, self.params)
        self.portfolio_server = PortfolioServer(self.symbols_map, self.logger, self.performance_manager)
        self.order_manager = OrderManager(self.params.strategy_allocation, self.symbols_map, self.event_queue, self.order_book, self.portfolio_server, self.logger)

        if self.mode == Mode.LIVE:
            self._set_live_environment()
        elif self.mode == Mode.BACKTEST:
            self._set_backtest_environment()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")
        
    def _set_live_environment(self):
        from midas.gateways.live import (DataClient, BrokerClient, ContractManager)
        
        # Gateways
        self.data_client = DataClient(self.event_queue, self.logger)
        self.broker_client = BrokerClient(self.event_queue,self.logger,self.portfolio_server)
        self.connect_live_clients()
        
        # Handlers
        self.contract_handler = ContractManager(self.data_client, self.logger) # TODO: CAN ADD to the Data CLIENT AND/OR TRADE CLIENT

    def _set_backtest_environment(self):
        from midas.gateways.backtest import (DataClient, BrokerClient, DummyBroker)

        # Gateways
        self.data_client = DataClient(self.event_queue, self.database)
        self.dummy_broker = DummyBroker(self.symbols_map, self.event_queue,self.order_book, self.params.capital, self.logger)
        self.broker_client = BrokerClient(self.event_queue, self.logger, self.portfolio_server, self.dummy_broker)
        
    def connect_live_clients(self):
        self.data_client.connect()
        self.broker_client.connect()

    def load_live_data(self):
        for symbol in self.symbols_map: 
            self.data_client.get_data(data_type=self.params.data_type, contract=symbol.contract) 

    def load_backtest_data(self):
        self.data_client.get_data(self.symbols_map, self.params.test_start, self.params.test_end,self.params.missing_values_strategy)

    def load_train_data(self):
        """
        Retrieves data from the database and initates the data processing. Stores initial data response in self.price_log.

        Args:
            symbols (List[str]) : A list of tickers ex. ['AAPL', 'MSFT']
            start_date (str) : Beginning date for the backtest ex. "2023-01-01"
            end_date (str) : End date for the backtest ex. "2024-01-01"
        """
        self.data_client.get_data(self.symbols_map, self.params.test_start, self.params.test_end,self.params.missing_values_strategy)
        train_data = self.data_client.data

        # # Extract contract details for mapping
        contracts_map = {symbol: self.symbols_map[symbol].contract for symbol in self.symbols_map}
        train_data['contract'] = train_data['symbol'].map(contracts_map)

        # # Sorting the DataFrame by the 'timestamp' column in ascending order
        train_data = train_data.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
        self.train_data = train_data.pivot(index='timestamp', columns='symbol', values='close')
        # print(self.train_data)

        # print(train_data)
        # # Convert the 'timestamp' column to datetime objects
        # train_data['timestamp'] = pd.to_datetime(train_data['timestamp'])
        # print(train_data)
        # for col in train_data:
        #     train_data[col] = train_data[col].astype(float)

    def set_strategy(self, strategy: Union[BaseStrategy, type]):
        if isinstance(strategy, type):
            strategy = strategy(self.symbols_map,self.train_data,portfolio_server=self.portfolio_server, logger = self.logger,order_book = self.order_book,event_queue=self.event_queue)
        self.strategy = strategy