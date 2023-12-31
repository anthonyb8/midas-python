import pandas as pd
# from engine.base.handlers import BasePerformanceHandler
from portfolio_server.managers import Trade, TradesManager
# from engine.base.data import EquityManager, SummaryStatsManager, EquityValue, BacktestResult, SignalsManager
from engine.base.events import ExecutionEvent, MarketDataEvent
from .broker_client import BrokerClient
import logging

class BacktestPerformanceHandler:

    """
    TODO : class may just be reposnibel for creatign backtets object and return to the egnie to save using the database client.
    
    """

    def __init__(self, broker_client: BrokerClient, logger:logging.Logger):
        self.broker_client = broker_client
        self.logger = logger


        self.equity_manager = EquityManager()
        self.trades_manager = TradesManager()
        self.summary_stats_manager = SummaryStatsManager()


    @property
    def equity_log(self):
        return self.equity_manager.log
    
    @property
    def trades_log(self):
        return self.trades_manager.log
    
    @property
    def summary_stats_log(self):
        return self.summary_stats_manager.log

    def update_equity_value(self, event: MarketDataEvent):
        total_positions_value = 0

        for contract, position in self.broker_client.positions.items():
            if contract.symbol in event.data.keys():


                current_bar = event.data[contract.symbol]  # Get the current BarData for the symbol
                current_price = current_bar.current_price  # Extract current price from BarData
                position_value = self._calculate_position_value(position, current_price)
                total_positions_value += position_value
        

        daily_equity = round(self.broker_client.capital + total_positions_value, 2)
        self.equity_manager.add_equity(EquityValue(event.timestamp, daily_equity))
        self.logger.info(f"Equity: {daily_equity}")


    def _calculate_position_value(self, position, current_price):
        return position.quantity * current_price
    
    def update_trades(self, event: ExecutionEvent):
        trade = Trade(
            trade_id=event.signal.trade_id,
            leg_id=event.signal.leg_id,
            timestamp=event.timestamp,
            symbol=event.contract.symbol,
            quantity=event.order.totalQuantity,
            price=event.fill_price,
            cost=event.fill_price * event.order.totalQuantity * (-1 if event.order.action == 'BUY' else 1),
            direction=event.signal.direction
        )
        self.trades_manager.add_trade(trade)
        self.logger.info(f"Trade Added: {trade}")

    def updated_liquidations(self, liquidated_positions:dict, event:MarketDataEvent):
        print(self.trades_manager.trade_log)
        for contract, details in liquidated_positions.items():
            trade = Trade(
                trade_id=event.signal.trade_id,
                leg_id=event.signal.leg_id,
                timestamp=event.timestamp,
                symbol=contract.symbol,
                quantity=details.quantity,
                price=event.current_price,
                cost=event.current_price * details.quantity * (-1 if details.direction == 'BUY' else 1),
                direction=details.direction
            )
            self.trades_manager.add_trade(trade)
        self.logger.info(f"Trade Added: {trade}")

    
    def calculate_statistics(self):
        aggregated_trades = self.trades_manager.aggregate_trades()
        equity_df = pd.DataFrame(self.equity_manager.log)
        print(equity_df)
        print(aggregated_trades)
        self.summary_stats_manager.calculate_summary(aggregated_trades, equity_df)
        self.logger.info(f"Stats Calculated.")