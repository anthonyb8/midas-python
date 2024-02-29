from datetime import datetime
from .config import Config, Mode
from midas.events import MarketEvent, OrderEvent, SignalEvent, ExecutionEvent


class EventController:
    def __init__(self, config:Config):
        # Initialize instance variables
        self.event_queue = config.event_queue
        self.mode = config.mode

        # Gateways
        # self.live_data_client = config.live_data_client
        self.hist_data_client = config.hist_data_client
        self.broker_client = config.broker_client
        

        # Core Components
        self.order_book = config.order_book
        self.strategy = config.strategy
        self.order_manager = config.order_manager

        # Supporting Components
        self.performance_manager = config.performance_manager
        self.logger = config.logger
        
    def run(self):
        if self.mode == Mode.LIVE:
            self._run_live()
        elif self.mode == Mode.BACKTEST:
            self._run_backtest()
  
    def _run_live(self):
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
          
    def _run_backtest(self):
        current_day = None  # Variable to track the current day

        while self.hist_data_client.data_stream():
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event)

                if isinstance(event, MarketEvent):
                    # event_timestamp = datetime.fromisoformat(event.timestamp)
                    event_timestamp = datetime.fromtimestamp(event.timestamp)
                    event_day = event_timestamp.date() 

                    if current_day is None or event_day != current_day:
                        if current_day is not None:
                            # Perform EOD operations for the previous day
                            self.broker_client.eod_update()
                        # Update the current day
                        current_day = event_day
                    self.order_book.on_market_data(event)
                    self.broker_client.update_equity_value() # Updates equity value of the account with every new price change
                    self.strategy.handle_market_data()

                elif isinstance(event, SignalEvent):
                    self.performance_manager.update_signals(event)
                    self.order_manager.on_signal(event)

                elif isinstance(event, OrderEvent):
                    self.broker_client.on_order(event)

                elif isinstance(event, ExecutionEvent):
                    self.broker_client.on_execution(event)

        # Perform EOD operations for the last trading day
        if current_day is not None:
            self.broker_client.eod_update()
            self.broker_client.liquidate_positions()
            
            # Finalize and save to database
            self.performance_manager.calculate_statistics()
            self.performance_manager.create_backtest()
