from .managers import PositionManager, Position
from .managers import TradeManager, Trade
from .managers import AccountManager
from .managers import SummaryStats, SummaryStatsManager
from .managers import ActiveOrder, OrderManager
from core.base.events import MarketDataEvent
import pandas as pd
import logging

class PortfolioServer:
    """
    Interacts with the portfolio client, retrieves commonly needed data, that would be stored in the portfolio client.

    Args:
        BasePortfolioHandler : Abstract portfolio class.
    """
    def __init__(self, logger:logging.Logger, mode):
        """
        Class constructor.

        Args:
            portfolio_client (PortfolioClient) : Inheritres the backtest portfolio client, so it can easily return portfoli related data to the engine.
        """
        self.capital = None
        self.logger = logger
        self.positions_manager = PositionManager()
        self.account_manager = AccountManager()

        # Backtest 
        # self.backtest = BacktestManager() if mode == "BACKTEST" else None
        self.trades_manager = TradeManager()
        self.summary_stats_manager = SummaryStatsManager()

        # Live
        self.orders_manager = OrderManager()

    @property
    def positions(self):
        return self.positions_manager.positions
    
    @property
    def account(self):
        return self.account_manager.account
    
    @property
    def trades(self):
        return self.trades_manager.trades
    
    @property
    def equity_log(self):
        return self.account_manager.equity_log
    
    @property
    def summary_stats(self):
        return self.summary_stats_manager.log
    
    def update_positions(self,contract, position_data):
        self.positions_manager.update(contract, position_data)
        self.logger.info(f"\nPositions Updated: \n{self.positions_manager}")

    def update_trades(self, **trade):
        self.trades_manager.update(**trade)
        self.logger.info(f"\nTrades Updated: \n{self.trades_manager}")

    def update_account(self,key, val):
        self.account_manager.update_account(key, val)
        self.update_capital(float(self.account_manager.account['AvailableFunds']))
        self.logger.info(f"\nAccount Updated: \n{self.account_manager}")

    def update_orders(self,**open_order):
        self.orders_manager.update_active_orders(open_order)
        self.logger.info(f"\nOrder Updated: \n{self.orders_manager}")

    def update_capital(self, capital):
        self.capital = capital
        self.logger.info(f"\nCapital Updated: \n{self.capital}")

    def calculate_statistics(self):
        aggregated_trades = self.trades_manager.aggregate_trades()
        equity_df = pd.DataFrame(self.account_manager.equity_log)
        self.summary_stats_manager.calculate_summary(aggregated_trades, equity_df)
        self.logger.info(f"Stats Calculated.")
