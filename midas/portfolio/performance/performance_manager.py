import pandas as pd
from datetime import datetime
from .statistics import PerformanceStatistics
# from midas.command.config import Parameters
# from midas.signals import Signal
import logging

class Backtest:
    def __init__(self):
        self.parameters = {}
        self.summary_stats = []
        self.trade_data = []
        self.equity_data = []
        self.signal_data = []
        self.price_data = []

    def set_strategy_name(self, name):
        self.strategy_name = name

    def set_parameters(self, parameters):
        self.parameters = parameters

    def set_summary_stats(self, summary_stats):
        self.summary_stats = summary_stats

    def set_trade_data(self, trade_data):
        self.trade_data = trade_data

    def set_equity_data(self, equity_data):
        self.equity_data = equity_data

    def set_signals(self, signal_data):
        self.signal_data = signal_data

    def set_price_data(self, price_data):
        self.price_data = price_data
        
    def to_dict(self):
        return {
            "parameters": self.parameters,
            "summary_stats": self.summary_stats,
            "trades": self.trade_data,
            "equity_data":self.equity_data,
            "signals": self.signal_data,
            "price_data": self.price_data,
        }

class Trade:
    def __init__(self, **trade):
        if isinstance(trade['timestamp'], datetime):
            timestamp = timestamp.isoformat()

        self.trade_id = trade['trade_id']
        self.leg_id = trade['leg_id']
        self.timestamp = trade['timestamp']
        self.symbol = trade['symbol']
        self.quantity = trade['quantity']
        self.price = trade['fill_price']
        self.cost = trade['cost']
        self.action = trade['action'].name

class AccountEquity:
    def __init__(self, timestamp, equity_value):
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        self.timestamp = timestamp
        self.equity_value = equity_value
    
class PerformanceManager(PerformanceStatistics):
    def __init__(self, logger:logging.Logger, params) -> None:
        self.logger = logger
        self.params = params
        self.backtest = Backtest()

        self.signals = []
        self.trades = []
        self.stats = []
        self.equity_value = []
        self.price_data = None

    def update_trades(self, **trade):
        new_trade = Trade(**trade)
        if new_trade.__dict__ not in self.trades:
            self.trades.append(new_trade.__dict__)
            self.logger.info(f"\nTrades Updated: \n{self.output_trades()}")

    def aggregate_trades(self) -> pd.DataFrame:

        if not self.trades:
            return []
        
        df = pd.DataFrame(self.trades)

        # Calculate the initial value (entry cost) for each trade (the sum of LONG and SHORT)
        entry_values = df[df['action'].isin(['LONG', 'SHORT'])].groupby('trade_id')['cost'].sum()

        # Calculate the exit value for each trade (the sum of SELL and COVER)
        exit_values = df[df['action'].isin(['SELL', 'COVER'])].groupby('trade_id')['cost'].sum()

        # Group by trade_id and aggregate the required metrics
        aggregated = df.groupby(['trade_id']).agg({
            'timestamp': ['first', 'last']
        })

        aggregated.columns = ['start_date', 'end_date']
        aggregated['entry_value'] = entry_values
        aggregated['exit_value'] = exit_values
        aggregated['net_gain/loss'] = aggregated['exit_value'] + aggregated['entry_value']

        # Calculate percentage gain/loss
        aggregated['gain/loss (%)'] = (aggregated['net_gain/loss'] / aggregated['entry_value'].abs()) * 100

        aggregated.reset_index(inplace=True)

        return aggregated

    def output_trades(self):
        string = ""
        for trade in self.trades:
            string += f" {trade} \n"
        return string

    def update_equity(self, timestamp, equity_value):
        new_equity = AccountEquity(timestamp,equity_value)
        if new_equity.__dict__ not in self.equity_value:
            self.equity_value.append(new_equity.__dict__)
            self.logger.info(f"\nEquity Updated: {self.equity_value[-1]}")

    def update_signals(self, signal: object):
        self.signals.append(signal.to_dict()) 
        self.logger.info(f"\nSignals Updated: {self.output_signals()}")
        
    def output_signals(self):
        string = ""
        for signals in self.signals:
            string += f" {signals} \n"
        return string
 
    def calculate_return_and_drawdown(self):
        df = pd.DataFrame(self.equity_value)
        df['percent_return'] = round(df['equity_value'].pct_change() * 100,4)
        df['percent_return'].fillna(0, inplace=True)  # Replace NaN with 0 for the first element

        rolling_max = df['equity_value'].cummax()
        df['percent_drawdown'] = round((df['equity_value'] - rolling_max ) / rolling_max * 100, 4)
        df['percent_drawdown'].fillna(0, inplace=True)  # Replace NaN with 0

        return df
    
    def calculate_statistics(self):
        aggregated_trades = self.aggregate_trades()
        equity_df = self.calculate_return_and_drawdown()
        self.equity_df = equity_df
                
    # Assuming necessary data is correctly formatted in aggregated_trades and equity_df
        stats = {
            'net_return': self.net_profit(aggregated_trades), 
            'total_trades': self.total_trades(aggregated_trades),
            # 'total_fees': self.total_fees(),  # Assuming this is a method of YourTradingClass
            'net_profit': PerformanceStatistics.net_profit(aggregated_trades),
            'ending_equity': equity_df['equity_value'].iloc[-1],
            'max_drawdown': max(PerformanceStatistics.drawdown(equity_df['equity_value'])),
            'sortino_ratio': PerformanceStatistics.sortino_ratio(aggregated_trades),
            # 'alpha': PerformanceStatistics.alpha(equity_df['equity_value'], benchmark_returns, risk_free_rate),  # Needs benchmark_returns and risk_free_rate
            # 'beta': PerformanceStatistics.beta(equity_df['equity_value'], benchmark_returns),  # Needs benchmark_returns
            # 'annual_standard_deviation': PerformanceStatistics.annual_standard_deviation(equity_df['equity_value']),
            # 'profit_and_loss_ratio': PerformanceStatistics.profit_and_loss_ratio(aggregated_trades),
            # 'profit_factor': PerformanceStatistics.profit_factor(aggregated_trades),
        }

        self.stats.append(stats)

        self.logger.info("Stats Calculated.")

    def create_backtest(self, price_data) -> Backtest:
        # Get the earliest and latest data
        # print(self.params.to_dict())
        # print(self.stats)
        # print(self.trades)
        # print(self.equity_value)
        print(self.signals)



        # parameters['start_date'] = price_data[0]['timestamp']
        # parameters['end_date'] = price_data[-1]['timestamp']

        # Create Backtest Object
        self.backtest.set_parameters(self.params)
        self.backtest.set_summary_stats(self.stats)
        self.backtest.set_trade_data(self.trades)
        self.backtest.set_equity_data(self.equity_value)    
        self.backtest.set_signals(self.signals)
        self.backtest.set_price_data(price_data)

        # return self.backtest

    