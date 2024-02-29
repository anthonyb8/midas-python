import logging
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Union, TypedDict

from .statistics import PerformanceStatistics
from midas.utils.database import DatabaseClient
from midas.account_data import EquityDetails
from midas.events import SignalEvent
# from midas.command.parameters import Parameters

class ExecutionDetails(TypedDict):
    timestamp: Union[int,float]
    trade_id: int
    leg_id: int
    symbol: str
    quantity: int
    price: float
    cost: float
    action: str
    fees: float

class Backtest:
    def __init__(self, database_client:DatabaseClient):
        self.database_client = database_client
        
        self.parameters = {}
        self.signal_data = []
        self.trade_data = []
        self.static_stats = []
        self.timeseries_stats = []
        
    def to_dict(self):
        return {
            "parameters": self.parameters,
            "static_stats": self.static_stats,
            "timeseries_stats":self.timeseries_stats,
            "signals": self.signal_data,
            "trades": self.trade_data,
        }
    
    def validate_attributes(self):
        if not isinstance(self.parameters, dict):
            raise ValueError("parameters must be a dictionary")
        if not all(isinstance(item, dict) for item in self.static_stats):
            raise ValueError("static_stats must be a list of dictionaries")
        if not all(isinstance(item, dict) for item in self.timeseries_stats):
            raise ValueError("timeseries_stats must be a list of dictionaries")
        if not all(isinstance(item, dict) for item in self.trade_data):
            raise ValueError("trade_data must be a list of dictionaries")
        if not all(isinstance(item, dict) for item in self.signal_data):
            raise ValueError("signal_data must be a list of dictionaries")
    
    def save(self):
        try:
            self.validate_attributes()
            response = self.database_client.create_backtest(self.to_dict())
            if response == 201:
                print("Backtest save successful.")
            else:
                # Log or print the response code for debugging purposes
                print(f"Backtest save failed with response code: {response}")
        except ValueError as e:
            raise ValueError (f"Validation Error: {e}")
        except Exception as e:
            raise Exception(f"Error when saving the backtest: {e}")

class PerformanceManager(PerformanceStatistics):
    def __init__(self, database:DatabaseClient, logger:logging.Logger, params) -> None:
        self.logger = logger
        self.params = params
        self.database = database
        
        self.backtest = Backtest(database)
        self.signals : List[Dict] = []
        self.trades : List[ExecutionDetails] = []
        self.equity_value : List[EquityDetails] = []
        self.static_stats : List[Dict] =  []
        self.timeseries_stats : pd.DataFrame = ()

    def update_trades(self, trade: ExecutionDetails):
        trade['timestamp'] =  datetime.fromtimestamp(trade['timestamp'], timezone.utc).isoformat()
        if trade not in self.trades:
            self.trades.append(trade)
            self.logger.info(f"\nTrades Updated: \n{self.output_trades()}")

    def output_trades(self):
        string = ""
        for trade in self.trades:
            string += f" {trade} \n"
        return string
    
    def update_signals(self, signal: SignalEvent):
        self.signals.append(signal.to_dict()) 
        self.logger.info(f"\nSignals Updated: {self.output_signals()}")
        
    def output_signals(self):
        string = ""
        for signals in self.signals:
            string += f" {signals} \n"
        return string
    
    def update_equity(self, equity_details: EquityDetails):
        equity_details['timestamp'] =  datetime.fromtimestamp(equity_details['timestamp'], timezone.utc).isoformat()
        if equity_details not in self.equity_value:
            self.equity_value.append(equity_details)
            self.logger.info(f"\nEquity Updated: {self.equity_value[-1]}")
    
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

    def total_trade_fees(self):
        return round(sum(trade['fees'] for trade in self.trades),4)
    
    def calculate_return_and_drawdown(self):
        df = pd.DataFrame(self.equity_value)
        equity_curve = df['equity_value'].to_numpy()

        # Adjust daily_return to add a placeholder at the beginning
        daily_returns = self.daily_return(equity_curve)
        daily_returns_adjusted = np.insert(daily_returns, 0, 0)

        # Adjust rolling_cumulative_return to add a placeholder at the beginning
        cumulative_returns = self.cumulative_return(equity_curve)
        cumulative_returns_adjusted = np.insert(cumulative_returns, 0, 0)

        df['daily_return'] = daily_returns_adjusted
        df['cumulative_return'] = cumulative_returns_adjusted
        df['drawdown'] = self.drawdown(equity_curve)
        df.fillna(0, inplace=True)  # Replace NaN with 0 for the first element

        return df
    
    def align_equity_and_benchmark(self, equity_curve:List[dict], benchmark_curve:List[dict]):
        # Convert the equity curve and benchmark to DataFrames
        equity_df = pd.DataFrame(equity_curve)
        benchmark_df = pd.DataFrame(benchmark_curve)
        
        # Convert timestamps to datetime and set as index
        equity_df['timestamp'] = datetime.fromtimestamp(equity_df['timestamp'], timezone.utc).isoformat()
        print(equity_df)
        benchmark_df['timestamp'] = pd.to_datetime(benchmark_df['timestamp'])
        equity_df.set_index('timestamp', inplace=True)
        benchmark_df.set_index('timestamp', inplace=True)
        
        # Resample to daily frequency to standardize, taking last value of the day
        # This step ensures that both datasets have one entry per day
        equity_df = equity_df.resample('D').last()
        benchmark_df = benchmark_df.resample('D').last()
        
        # Drop rows with any NaN values that might have resulted from resampling
        equity_df.dropna(inplace=True)
        benchmark_df.dropna(inplace=True)

        # Align the two datasets, keeping only the dates that exist in both
        # This operation will automatically drop dates that do not align
        combined_df = pd.concat([equity_df, benchmark_df], axis=1, join='inner')

        # Convert the selected columns to NumPy arrays
        equity_values_array = combined_df['equity_value'].to_numpy()
        benchmark_close_array = combined_df['close'].to_numpy()

        equity_values_array =equity_values_array.astype(np.float64)
        benchmark_close_array = benchmark_close_array.astype(np.float64)

        return equity_values_array, benchmark_close_array

    def calculate_statistics(self, risk_free_rate: float= 0.04):
        # Aggregate Trades
        aggregated_trades = self.aggregate_trades()

        # Benchmark Values
        benchmark = self.database.get_benchmark_data(self.params.benchmark, self.params.test_start, self.params.test_end)

        # Align benchmark with equity value on daily time frame
        equity_curve, benchmark_curve= self.align_equity_and_benchmark(self.equity_value, benchmark) 
        
        # Calculate Timeseries Statistics
        self.timeseries_stats = self.calculate_return_and_drawdown()
        self.timeseries_stats = self.timeseries_stats.drop(self.timeseries_stats.index[0])

        stats = {
        # General Statistics
            'net_profit': self.net_profit(aggregated_trades), 
            'total_return':self.total_return(equity_curve),
            'max_drawdown':self.max_drawdown(equity_curve),
            'annual_standard_deviation': self.annual_standard_deviation(equity_curve),
            'ending_equity': equity_curve[-1],
            'total_fees': self.total_trade_fees(),

        # Trade Statistics
            'total_trades': self.total_trades(aggregated_trades),
            "num_winning_trades":self.total_winning_trades(aggregated_trades), 
            "num_lossing_trades":self.total_losing_trades(aggregated_trades),
            "avg_win_percent":self.avg_win_percent(aggregated_trades),
            "avg_loss_percent":self.avg_loss_percent(aggregated_trades),
            "percent_profitable":self.percent_profitable(aggregated_trades),
            "profit_and_loss" :self.profit_and_loss_ratio(aggregated_trades),
            "profit_factor":self.profit_factor(aggregated_trades),
            "avg_trade_profit":self.average_trade_profit(aggregated_trades),

        # Benchmark Statistics
            'sharpe_ratio':PerformanceStatistics.sharpe_ratio(equity_curve),
            'sortino_ratio': PerformanceStatistics.sortino_ratio(aggregated_trades),
            'alpha': PerformanceStatistics.alpha(equity_curve, benchmark_curve, risk_free_rate),  # Needs benchmark_returns and risk_free_rate
            'beta': PerformanceStatistics.beta(equity_curve, benchmark_curve)  # Needs benchmark_returns
        }

        self.static_stats.append(stats)

    def create_backtest(self) -> Backtest:
        # Create Backtest Object
        self.backtest.parameters = self.params.to_dict()
        self.backtest.static_stats = self.static_stats
        self.backtest.timeseries_stats = self.timeseries_stats.to_dict(orient='records')
        self.backtest.trade_data = self.trades
        self.backtest.signal_data = self.signals_

        # Save Backtest Object
        # self.backtest.save()

