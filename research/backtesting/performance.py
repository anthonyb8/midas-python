import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textwrap import dedent
from typing import Tuple, List, Dict, Any

class BacktestPerformance:
    @staticmethod
    def sharpe_ratio(equity_curve: list, risk_free_rate: float = 0.04):
        daily_returns =  BacktestPerformance.daily_return(equity_curve)
        excess_returns = [r - risk_free_rate for r in daily_returns]

        if np.std(excess_returns) != 0:
            return np.mean(excess_returns) / np.std(excess_returns)
        else: 
            return 0
        
    @staticmethod
    def daily_return(equity_curve: list):
        df = pd.DataFrame({'equity_value': equity_curve})
        df['daily_return'] = df['equity_value'].pct_change()  # Decimal format
        df['daily_return'].fillna(0, inplace=True)  # Replace NaN with 0 for the first element
        return df['daily_return'].tolist()

    @staticmethod
    def cumulative_return(equity_curve: list):
        df = pd.DataFrame({'equity_value': equity_curve})
        df['daily_return'] = df['equity_value'].pct_change()
        df['cumulative_total_return'] = (1 + df['daily_return']).cumprod() - 1
        df['cumulative_total_return'].fillna(0, inplace=True)
        # Convert to percentage
        df['cumulative_total_return'] *= 100
        return df['cumulative_total_return'].tolist()

    @staticmethod
    def drawdown(equity_curve:list):
        df = pd.DataFrame({'equity_value': equity_curve})
        rolling_max = df['equity_value'].cummax()
        df['percent_drawdown'] = round((df['equity_value'] - rolling_max ) / rolling_max * 100, 4)
        df['percent_drawdown'].fillna(0, inplace=True)  # Replace NaN with 0
        return df['percent_drawdown'].tolist()
    
    @staticmethod
    def plot_data_with_signals(data, signals, show_plot=True):
        plt.figure(figsize=(15, 7))

        for symbol in data.columns:
            plt.plot(data.index, data[symbol], label=symbol)

        for signal in signals:
            color = 'green' if signal['direction'] == 1 else 'red'
            plt.scatter(signal['timestamp'], signal['price'], color=color, marker='o' if signal['direction'] == 1 else 'x')

        plt.legend()
        plt.title("Price Data with Trade Signals")
        plt.xlabel("Timestamp")
        plt.ylabel("Price")

        if show_plot:
            plt.show()

    @staticmethod
    def plot_price_and_spread(price_data:pd.DataFrame, spread:list, signals: list, split_date=None, show_plot=True):
        """
        Plot multiple ticker data on the left y-axis and spread with mean and standard deviations on the right y-axis.
        
        Parameters:
            price_data (pd.DataFrame): DataFrame containing the data with timestamps as index and multiple ticker columns.
            spread (pd.Series): Series containing the spread data.
        """
        # Extract data from the DataFrame
        timestamps = price_data.index
        spread = pd.Series(spread, index=timestamps) 

        # Create a figure and primary axis for price data (left y-axis)
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Plot each ticker on the left y-axis
        colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange']  # Extend this list as needed
        for i, ticker in enumerate(price_data.columns):
            color = colors[i % len(colors)]  # Cycle through colors
            ax1.plot(timestamps, price_data[ticker], label=ticker, color=color, linewidth=2)

        ax1.set_yscale('linear')
        ax1.set_ylabel('Price')
        ax1.legend(loc='upper left')

        # Calculate mean and standard deviations for spread
        spread_mean = spread.rolling(window=20).mean()  # Adjust the window size as needed
        spread_std_1 = spread.rolling(window=20).std()  # 1 standard deviation
        spread_std_2 = 2 * spread.rolling(window=20).std()  # 2 standard deviations

        # Create a secondary axis for the spread with mean and standard deviations (right y-axis)
        ax2 = ax1.twinx()

        # Plot Spread on the right y-axis
        ax2.plot(timestamps, spread, label='Spread', color='purple', linewidth=2)
        ax2.plot(timestamps, spread_mean, label='Mean', color='orange', linestyle='--')
        ax2.fill_between(timestamps, spread_mean - spread_std_1, spread_mean + spread_std_1, color='gray', alpha=0.2, label='1 Std Dev')
        ax2.fill_between(timestamps, spread_mean - spread_std_2, spread_mean + spread_std_2, color='gray', alpha=0.4, label='2 Std Dev')
        ax2.set_yscale('linear')
        ax2.set_ylabel('Spread and Statistics')
        ax2.legend(loc='upper right')


        # Plot signals
        for signal in signals:
            ts = pd.to_datetime(signal['timestamp'])
            price = signal['price']
            action = signal['action']
            if action in ['LONG', 'COVER']:
                marker = '^'
                color = 'lime'
            elif action in ['SHORT', 'SELL']:
                marker = 'v'
                color = 'red'
            else:
                # Default marker for undefined actions
                marker = 'o'
                color = 'gray'
            ax1.scatter(ts, price, marker=marker, color=color, s=100)

        # Draw a dashed vertical line to separate test and training data
        if split_date is not None:
            split_date = pd.to_datetime(split_date)
            ax1.axvline(x=split_date, color='black', linestyle='--', linewidth=1)

        # Add grid lines
        ax1.grid(True)

        # Format x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.xlabel('Timestamp')

        # Title
        plt.title('Price Data, Spread, and Statistics Over Time')

        # Show the plot
        plt.tight_layout()

        if show_plot:
            plt.show()

    @staticmethod
    def plot_equity_curve(equity_curve, show_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(equity_curve, label='Equity Curve')
        plt.title(f"Equity Curve")
        plt.xlabel('Time')
        plt.ylabel('Equity')
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.grid()
        plt.legend()
        
        if show_plot:
            plt.show()
    
    @staticmethod
    def plot_drawdown_curve(drawdown, show_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(drawdown, label='Drawdown Curve')
        plt.title(f"Drawdown Curve")
        plt.xlabel('Time')
        plt.ylabel('Drawdown (%)')
        plt.axhline(y=0, color='red', linestyle='--')
        plt.grid()
        plt.legend()
               
        if show_plot:
            plt.show()

    @staticmethod
    def plot_return_curve(drawdown, show_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(drawdown, label='Return Curve')
        plt.title(f"Return Curve")
        plt.xlabel('Time')
        plt.ylabel('Return (%)')
        plt.axhline(y=0, color='blue', linestyle='--')
        plt.grid()
        plt.legend()
               
        if show_plot:
            plt.show()
    
    # @staticmethod
    # def calculate_metrics(equity_curve):
    #     cum_return_curve = BacktestPerformance.cumulative_return(equity_curve)
    #     drawdown_curve = BacktestPerformance.drawdown(equity_curve)

    #     BacktestPerformance.plot_equity_curve(equity_curve)
    #     BacktestPerformance.plot_return_curve(cum_return_curve)
    #     BacktestPerformance.plot_drawdown_curve(drawdown_curve)

    #     # Calculate Sharpe ratio using daily returns
    #     sharpe_ratio = BacktestPerformance.sharpe_ratio(equity_curve)
    #     max_drawdown = min(drawdown_curve)
    #     total_return = cum_return_curve[-1]

    #     return {'Total Return(%)': total_return, 'Sharpe Ratio': sharpe_ratio, 'Max Drawdown(%)': max_drawdown}