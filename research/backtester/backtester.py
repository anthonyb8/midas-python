import logging
import numpy as np
import pandas as pd
from decouple import config
from midas.utils.database import DatabaseClient
from typing import Tuple, List, Dict, Any

from midas.strategies import BaseStrategy
from midas.performance.statistics import PerformanceStatistics

from research.data import DataProcessing
from research.report.html_report import HTMLReportGenerator
from research.strategies.cointegrationzscore import Cointegrationzscore

logging.basicConfig(level=logging.INFO)
database  = DatabaseClient(config('MIDAS_API_KEY'), config('MIDAS_URL'))

class VectorizedBacktest(PerformanceStatistics):
    def __init__(self, full_data: pd.DataFrame, strategy: BaseStrategy,  report_generator: HTMLReportGenerator,  initial_capital: float = 10000):
        self.strategy = strategy
        self.report_generator = report_generator
        self.initial_capital = initial_capital
        self.full_data = full_data
        self.symbols = full_data.columns.tolist()

        self.equity_curve = None
        self.backtest_data : pd.DataFrame

    def setup(self) -> None:
        """
        Prepares the backtesting environment by optionally calling the strategy's prepare method if it exists.
        The result is then added to the report generator.
        """
        if hasattr(self.strategy, 'prepare'):
            try:
                html_content = self.strategy.prepare(self.full_data)
                self.report_generator.add_html(html_content)
                logging.info("Strategy preparation completed and added to the report.")
            except Exception as e:
                raise Exception(f"Error during strategy preparation: {e}")

    def run_backtest(self, entry_threshold: float, exit_threshold: float) -> None:
        logging.info("Starting backtest...")
        assert self.full_data is not None, "Full data must be provided before running backtest."
        assert self.strategy is not None, "Strategy must be set before running backtest."
        
        try:
            self.backtest_data = self.strategy.generate_signals(entry_threshold, exit_threshold)
            self._calculate_equity_curve()
            self._calculate_metrics()
            logging.info("Backtest completed successfully.")
        except Exception as e:
            logging.error(f"Backtest failed: {e}")
            raise

    def _calculate_equity_curve(self):
        logging.info("Starting equity curve calculation.")
        
        # Initialize a column for aggregate returns
        self.backtest_data['aggregate_returns'] = 0

        # Iterate through each ticker to calculate individual returns
        for ticker in self.symbols:
            price_column, position_column, returns_column = f'{ticker}', f'{ticker}_position', f'{ticker}_returns'
            try:
                # Calculate daily returns for ticker
                self.backtest_data[returns_column] = self.backtest_data[price_column].pct_change()
                
                # Return for postion if holding
                self.backtest_data[f'{ticker}_position_returns'] = self.backtest_data[returns_column] * self.backtest_data[position_column].shift(1)

                # Aggregate the individual strategy returns into the total returns
                self.backtest_data['aggregate_returns'] += self.backtest_data[f'{ticker}_position_returns']
            except Exception as e:
                logging.error(f"Error processing {ticker}: {e}")

        # Calculate the equity curve from aggregate returns
        self.backtest_data['equity_curve'] = (self.backtest_data['aggregate_returns'] + 1).cumprod() * self.initial_capital

        # Fill NaN values for the initial capital in the equity curve
        self.backtest_data['equity_curve'] = self.backtest_data['equity_curve'].fillna(self.initial_capital)


        logging.info("Equity curve calculation completed.")

    def _calculate_metrics(self, risk_free_rate: float= 0.04):
        # Assuming self.equity_curve is a pandas Series of cumulative returns
        equity_values_array = self.backtest_data['equity_curve'].to_numpy()
        equity_curve = equity_values_array.astype(np.float64)
        
        daily_returns = self.daily_return(equity_curve)
        daily_returns_adjusted = np.insert(daily_returns, 0, 0)

        # Adjust rolling_cumulative_return to add a placeholder at the beginning
        cumulative_returns = self.cumulative_return(equity_curve)
        cumulative_returns_adjusted = np.insert(cumulative_returns, 0, 0)
        annual_standard_deviation = self.annual_standard_deviation(equity_curve),
        sharpe_ratio = self.sharpe_ratio(equity_curve),

        self.backtest_data['daily_return'] = daily_returns_adjusted
        self.backtest_data['cumulative_return'] = cumulative_returns_adjusted
        self.backtest_data['drawdown'] = self.drawdown(equity_curve)
        self.backtest_data.fillna(0, inplace=True)  # Replace NaN with 0 for the first element

        tab = "    "
        self.report_generator.add_html("<section class='performance'>")
        self.report_generator.add_html(f"{tab}<h2>Performance Metrics</h2>")
        self.report_generator.add_image(self.plot_curve, indent = 1, y = equity_curve, title = "Equity Curve", x_label="Time", y_label="Equity Value", show_plot=False)
        self.report_generator.add_image(self.plot_curve, indent = 1, y = cumulative_returns_adjusted, title = "Cumulative Return", x_label="Time", y_label = "Return Value", show_plot=False)
        self.report_generator.add_image(self.plot_curve, indent = 1, y = self.backtest_data['drawdown'].tolist(), title = "Drawdown Curve", x_label="Time", y_label="Drawdown Value", show_plot=False)
        self.report_generator.add_html("</section>")

    def sensitivity_analysis(self, entry_thresholds, exit_thresholds):
        results = {}
        # Sensitivity Analysis
        for entry_threshold in entry_thresholds:
            for exit_threshold in exit_thresholds:
                self.run_backtest(entry_threshold, exit_threshold)
                max_drawdown = self.backtest_data['drawdown'].min()
                total_return = self.backtest_data['cumulative_return'].iloc[-1]
                # TODO: get an average sharpe ratio
                results[(entry_threshold, exit_threshold)] = {"total_return":total_return, "max_drawdown": max_drawdown}

        # Add Summary Results to Report
        tab = "    "
        self.report_generator.add_html("<section class='summary'>")
        self.report_generator.add_html(f"{tab}<h2>Sensitivity Results</h2>")
        headers = ["Entry Threshold", "Exit Threshold", "Total Return(%)", "Sharpe Ratio", "Max Drawdown"]
        rows = [
            [entry, exit, f"{metrics['total_return']:.2f}%", f"{0.0:.2f}", f"{metrics['max_drawdown']:.2f}%"]
            for (entry, exit), metrics in results.items()
        ]
        self.report_generator.add_table(headers, rows, indent=1)
        self.report_generator.add_html("</section>")

        return results
    
    def output_report(self):
        self.report_generator.complete_report()

# if __name__ == "__main__":

#     # Step 1 : Set data parameters
#     start_date = "2024-01-06"
#     end_date = "2024-02-07"
#     tickers = ['HE.n.0', 'ZC.n.0']

#     # Step 2 : Retrieve Data
#     data_processing = DataProcessing(database)
#     data_processing.get_data(tickers, start_date,end_date, "drop")
#     data = data_processing.processed_data
#     data.dropna(inplace=True)

#     ## Step 3 : Set up Report
#     strategy_name = "cointegrationzscore"
#     report_generator = HTMLReportGenerator(strategy_name)

#     # Step 3 : Initialize Strategy
#     strategy = Cointegrationzscore()
    
#     # Step 4 : Initialize Backtester
#     backtest = VectorizedBacktest(data, strategy, initial_capital=10000, report_generator=report_generator)
#     backtest.setup()

#     # Step 5 : Set Thresholds
#     entry = [0.0]
#     exit = [2.0]
#     # backtest.run_backtest(entry_threshold=entry, exit_threshold=exit)
#     backtest.sensitivity_analysis(entry, exit)
#     backtest.output_report()

# Example usage
# # Assuming 'full_data' DataFrame has a 'close' column with closing prices
# strategy = SimpleMovingAverageStrategy(short_window=50, long_window=200)

# backtest.run_backtest()
# equity_curve = backtest.get_equity_curve()
# backtest.plot_equity_curve()

