# from .managers import BasePortfolioHandler
# from engine.backtest.broker_client import BrokerClient
from .managers import PositionsManager, Position
from .managers import TradesManager, Trade
from .managers import AccountInfoManager
from .managers import EquityValue, EquityManager
from .managers import SummaryStats, SummaryStatsManager
from core.base.events import MarketDataEvent, ExecutionEvent
import pandas as pd
import logging

class PortfolioServer:
    """
    Interacts with the portfolio client, retrieves commonly needed data, that would be stored in the portfolio client.

    Args:
        BasePortfolioHandler : Abstract portfolio class.
    """
    def __init__(self, capital:float, logger:logging.Logger):
        """
        Class constructor.

        Args:
            portfolio_client (PortfolioClient) : Inheritres the backtest portfolio client, so it can easily return portfoli related data to the engine.
        """
        self.capital = capital
        self.logger = logger
        self.positions_manager = PositionsManager()
        self.account_info_manager = AccountInfoManager()
        self.trades_manager = TradesManager()
        self.equity_manager = EquityManager()
        self.summary_stats_manager = SummaryStatsManager()

    @property
    def positions(self):
        return self.positions_manager.positions
    
    @property
    def account(self):
        return self.account_info_manager.account_info
    
    @property
    def trades(self):
        return self.trades_manager.trade_log
    
    @property
    def equity_log(self):
        return self.equity_manager.log
    
    @property
    def summary_stats_log(self):
        return self.summary_stats_manager.log
    
    def update_positions(self, contract, direction, price, quantity):
        self.positions_manager.update(contract, direction, price, quantity)

    def update_account_info(self, new_info):
        self.account_info_manager.update(new_info)

    def update_trades(self, new_trade):
        self.trades_manager.update(new_trade)

    def update_backtest_capital(self, direction, quantity, price):
        """
        For backtests
        """
        multiplier = 0

        if direction == 'BUY':
            multiplier = 1
        elif direction == 'SELL':
            multiplier = -1
        else:
            raise ValueError(f"Direction: {direction} not in ['BUY','SELL']")

        self.capital += (multiplier * quantity) * price 
        self.logger.info(f"Updated Capital: {self.capital}")

    def update_equity_value(self, event: MarketDataEvent):
        total_positions_value = 0

        for contract, position in self.positions.items():
            if contract.symbol in event.data.keys():


                current_bar = event.data[contract.symbol]  # Get the current BarData for the symbol
                current_price = current_bar.current_price  # Extract current price from BarData
                position_value = self._calculate_position_value(position, current_price)
                total_positions_value += position_value
        

        daily_equity = round(self.capital + total_positions_value, 2)
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
        self.trades_manager.update(trade)
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




    # def get_account_information(self):
    #     """
    #     Gets account information ex. capital, margin available

    #     Return:
    #         dict : Contains the key-value relationship for accoutn specfic data.
    #     """
    #     return self.broker_client.account_info
    
    # def get_cash(self):
    #     """
    #     Gets just cash amount. 

    #     Return:
    #         int : Cash available to trade.
    #     """
    #     return self.broker_client.capital
    
    # def get_positions(self):
    #     """
    #     Gets positions dictionary.

    #     Return:
    #         dict : Contains the current positions in the portfolio.
    #     """
    #     return self.broker_client.positions
    
    # def get_execution_details(self):
    #     """
    #     Gets executed trades. #TODO : not sure if needed
    #     """
    #     return self.broker_client.executed_orders
    
    # def get_total_portfolio_value(self) -> float:
    #     """
    #     Not sure if needed in backtest.
    #     """
    #     account_info = self.get_account_information()
    #     return float(account_info.get('NetLiquidation', 0))


