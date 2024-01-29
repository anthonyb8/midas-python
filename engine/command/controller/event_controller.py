from .config import Config, Mode
from core.base.events import MarketDataEvent, OrderEvent, SignalEvent, ExecutionEvent
from core.base.data import BacktestManager
from datetime import datetime

class EventController:
    def __init__(self, config:Config):
        # Initialize instance variables from config
        self._initialize_from_config(config)
        
    def _initialize_from_config(self, config:Config):
        # Initialize instance variables
        self.event_queue = config.event_queue
        self.symbols_map = config.symbols_map
        self.strategy_name = config.strategy_name
        # self.parameters = config.parameters
        self.mode = config.mode

        # Gateways
        self.data_client = config.data_client
        self.broker_client = config.broker_client
        self.contract_handler = config.contract_handler
        
        # Core Components
        self.order_book = config.order_book
        self.strategy = config.strategy
        self.order_manager = config.order_manager

        # Supporting Components
        self.database = config.database
        self.portfolio_server =config.portfolio_server
        self.dashboard = config.dashboard
        self.logger = config.logger

        # Backtest-specific variables
        self.dummy_broker = config.dummy_broker
        self._capital = config.capital
        self._start_date = config.start_date
        self._end_date = config.end_date
        self.symbols = config.symbols
        self.parameters = config.parameters

    def run(self):
        if self.mode == Mode.LIVE:
            self.run_live()
        elif self.mode == Mode.BACKTEST:
            self.backtest = BacktestManager()
            self.run_backtest()
  
    def run_live(self):
        while True:
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event)

                if isinstance(event, MarketDataEvent):
                    self.order_book.on_market_data(event)
                    self.strategy.handle_market_data()

                elif isinstance(event, SignalEvent):
                    self.order_manager.on_signal(event)

                elif isinstance(event, OrderEvent):
                    self.broker_client.on_order(event)
          
    def run_backtest(self):
        while self.data_client.data_stream():
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event)

                if isinstance(event, MarketDataEvent):
                    self.order_book.on_market_data(event)
                    self.broker_client.update_EquityValue()
                    self.strategy.handle_market_data()

                elif isinstance(event, SignalEvent):
                    self.order_manager.on_signal(event)

                elif isinstance(event, OrderEvent):
                    self.broker_client.on_order(event)

                elif isinstance(event, ExecutionEvent):
                    self.broker_client.on_execution(event)
        
        self.broker_client.liquidate_positions()
        self.finalize_backtest()

    def finalize_backtest(self):
        self.portfolio_server.calculate_statistics()
        
        # Collect data from components
        summary_stats = self.portfolio_server.summary_stats
        trade_log = self.portfolio_server.trades
        equity_log = self.portfolio_server.equity_log
        signal_log = self.strategy.signals_log
        price_log = self.data_client.price_log

        # Sort the list by timestamp
        sorted_price_data = sorted(price_log, key=lambda x: x['timestamp'])

        # Get the earliest and latest data
        self.parameters['start_date'] = sorted_price_data[0]['timestamp']
        self.parameters['end_date'] = sorted_price_data[-1]['timestamp']

        # Create Backtest Object
        self.backtest.set_parameters(self.parameters)
        self.backtest.set_summary_stats(summary_stats)
        self.backtest.set_trade_data(trade_log)
        self.backtest.set_equity_data(equity_log)    
        self.backtest.set_price_data(price_log)
        self.backtest.set_signals(signal_log)
        print(self.backtest.to_dict())


        # Finalize and save to database
        response = self.database.create_backtest(self.backtest.to_dict())
            