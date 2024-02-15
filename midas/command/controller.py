from datetime import datetime
from .config import Config, Mode
from midas.events import MarketEvent, OrderEvent, SignalEvent, ExecutionEvent


class EventController:
    def __init__(self, config:Config):
        # Initialize instance variables from config
        self._initialize_from_config(config)
        
    def _initialize_from_config(self, config:Config):
        # Initialize instance variables
        self.event_queue = config.event_queue
        self.symbols_map = config.symbols_map
        self.mode = config.mode
        self.params = config.params

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
        self.performance_manager = config.performance_manager
        self.logger = config.logger

        # Backtest-specific variables
        self.dummy_broker = config.dummy_broker
        
    def run(self):
        if self.mode == Mode.LIVE:
            self.run_live()
        elif self.mode == Mode.BACKTEST:
            self.run_backtest()
  
    def run_live(self):
        while True:
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event)

                if isinstance(event, MarketEvent):
                    self.order_book.on_market_data(event)
                    self.strategy.handle_market_data()

                elif isinstance(event, SignalEvent):
                    self.order_manager.on_signal(event)

                elif isinstance(event, OrderEvent):
                    self.broker_client.on_order(event)
          
    def run_backtest(self):
        current_day = None  # Variable to track the current day

        while self.data_client.data_stream():
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event)

                if isinstance(event, MarketEvent):
                    event_timestamp = datetime.fromisoformat(event.timestamp)
                    event_day = event_timestamp.date() 

                    if current_day is None or event_day != current_day:
                        if current_day is not None:
                            # Perform EOD operations for the previous day
                            self.broker_client.eod_update()
                        # Update the current day
                        current_day = event_day
                    self.order_book.on_market_data(event)
                    self.broker_client.update_EquityValue() # Updates equity value of the account with every new price change
                    self.strategy.handle_market_data()

                elif isinstance(event, SignalEvent):
                    self.performance_manager.update_signals(event.signal)
                    self.order_manager.on_signal(event)

                elif isinstance(event, OrderEvent):
                    self.broker_client.on_order(event)

                elif isinstance(event, ExecutionEvent):
                    self.broker_client.on_execution(event)

        # Perform EOD operations for the last trading day
        if current_day is not None:
            self.broker_client.eod_update()

        self.broker_client.liquidate_positions()
        self.performance_manager.calculate_statistics()
        self.performance_manager.create_backtest()
        
        
        
        # print(backtest_obj.to_dict())
        
        # Finalize and save to database
        # response = self.database.create_backtest(self.backtest.to_dict())
