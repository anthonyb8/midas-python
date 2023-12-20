from engine.driver.config import Config, Mode
from engine.base.data import BacktestResult
from engine.base.events import MarketDataEvent, OrderEvent, SignalEvent, ExecutionEvent

class EventDriver:
    def __init__(self, config:Config):
        # Initialize instance variables from config
        self._initialize_from_config(config)
        
    def _initialize_from_config(self, config:Config):
         # Initialize instance variables
        self.event_queue = config.event_queue
        self.symbols_map = config.symbols_map
        self.strategy_name = config.strategy_name
        self.parameters = config.parameters
        self.mode = config.mode

        # Clients
        self.data_client = config.data_client
        self.broker_client = config.broker_client
        
        # Handlers
        self.strategy = config.strategy
        self.data_handler = config.data_handler
        self.portfolio_handler = config.portfolio_handler
        self.execution_handler = config.execution_handler
        self.performance_handler = config.performance_handler
        self.contract_handler = config.contract_handler

        # Supporting apps
        self.database = config.database
        self.dashboard = config.dashboard

        # Backtest-only variables
        self._capital = config.capital
        self._start_date = config.start_date
        self._end_date = config.end_date
        
        # Loggers 
        self.logger = config.logger

    def run(self):
        if self.mode == Mode.LIVE:
            self.run_live()
        elif self.mode == Mode.BACKTEST:
            self.backtest = BacktestResult()
            self.run_backtest()
  
    def run_live(self):
        while True:
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event.__dict__)

                
                if isinstance(event, MarketDataEvent):
                    self.strategy.on_market_data(event)

                elif isinstance(event, SignalEvent):
                    capital = self.portfolio_handler.get_cash()
                    positions = self.portfolio_handler.get_positions()
                    self.strategy.on_signal(capital, positions, event)

                elif isinstance(event, OrderEvent):
                    self.execution_handler.on_order(event)
          
                    
    def run_backtest(self):
        while self.data_handler.data_stream():
            while not self.event_queue.empty():
                event = self.event_queue.get()
                self.logger.info(event.__dict__)

                if isinstance(event, MarketDataEvent):
                    self.performance_handler.update_equity_value(event)
                    self.strategy.on_market_data(event)

                elif isinstance(event, SignalEvent):
                    capital = self.broker_client.capital
                    positions = self.broker_client.positions
                    self.strategy.on_signal(capital, positions, event)

                elif isinstance(event, OrderEvent):
                    self.execution_handler.on_order(event)

                elif isinstance(event, ExecutionEvent):
                    self.broker_client.on_execution(event)
                    self.performance_handler.update_trades(event)
        
        # TODO : Complete liquidation handling
        # last_bar = self.data_handler.get_last_bar()
        # liquidated_positions = self.broker_client.liquidate_positions()
        # self.performance_handler.updated_liquidations(liquidated_positions,last_bar)
                    

        self.finalize_backtest()

    def finalize_backtest(self):
        self.parameters['symbols'] = [symbol.symbol for symbol in self.parameters['symbols']]
        self.performance_handler.calculate_statistics()
        
        # Collect data from components
        strategy = self.strategy_name
        parameters = self.parameters
        summary_stats = self.performance_handler.summary_stats_manager.log
        trade_log = self.performance_handler.trades_manager.log
        equity_log = self.performance_handler.equity_manager.log
        signal_log = self.strategy.signals_log
        price_log = self.data_handler.price_log

        # Create Backtest Object
        self.backtest.set_strategy_name(strategy)
        self.backtest.set_parameters(parameters)
        self.backtest.set_summary_stats(summary_stats)
        self.backtest.set_trade_data(trade_log)
        self.backtest.set_equity_data(equity_log)    
        self.backtest.set_price_data(price_log)
        self.backtest.set_signals(signal_log)

        # Finalize and save to database
        response = self.database.create_backtest(self.backtest.to_dict())
            