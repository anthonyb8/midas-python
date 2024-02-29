import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Union
    
class PerformanceStatistics:
    # -- General -- 
    @staticmethod
    def net_profit(trade_log: pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        
        # Perform calculation if checks pass
        return round(trade_log['net_gain/loss'].sum(), 4)
    
    @staticmethod
    def daily_return(equity_curve: np.ndarray):
        """Returns are in decimal format."""
        if not isinstance(equity_curve, np.ndarray):
            raise TypeError("equity_curve must be a numpy array")
        
        # Check for empty array
        if len(equity_curve) == 0:
            return np.array([0])
        else:
            daily_returns_np = np.diff(equity_curve) / equity_curve[:-1] # Calculate daily returns using vectorized operations
            return np.around(daily_returns_np, decimals=4) 

    @staticmethod
    def cumulative_return(equity_curve: np.ndarray):
        """Returns are in decimal format."""
        if not isinstance(equity_curve, np.ndarray):
            raise TypeError("equity_curve must be a numpy array")
        
        # Check for empty array
        if len(equity_curve) == 0:
            return np.array([0])
        else:
            daily_returns = np.diff(equity_curve) / equity_curve[:-1] # Calculate daily returns
            cumulative_returns = np.cumprod(1 + daily_returns) - 1 # Calculate cumulative returns
            return np.around(cumulative_returns, decimals=4)
        
    @staticmethod
    def total_return(equity_curve:np.ndarray):
        """Returns are in decimal format."""
        return PerformanceStatistics.cumulative_return(equity_curve)[-1]  # Returns the latest cumulative return
    
    @staticmethod
    def drawdown(equity_curve: np.ndarray):
        """Drawdown values are in decimal format."""
        if not isinstance(equity_curve, np.ndarray):
            raise TypeError("equity_curve must be a numpy array")
        
        # Check for empty array
        if len(equity_curve) == 0:
            return np.array([0])
        else:
            rolling_max = np.maximum.accumulate(equity_curve)  # Calculate the rolling maximum
            drawdowns = (equity_curve - rolling_max) / rolling_max  # Calculate drawdowns in decimal format
            return np.around(drawdowns, decimals=4)
        
    @staticmethod
    def max_drawdown(equity_curve:np.ndarray):
        """Drawdown values are in decimal format."""
        drawdowns = PerformanceStatistics.drawdown(equity_curve)
        max_drawdown = np.min(drawdowns)  # Find the maximum drawdown
        return max_drawdown

    @staticmethod
    def annual_standard_deviation(equity_curve:np.ndarray):
        """Calculate the annualized standard deviation of returns from a NumPy array of log returns."""
        if not isinstance(equity_curve, np.ndarray):
            raise TypeError("equity_curve must be a numpy array")
        
        # Check for empty array
        if len(equity_curve) == 0:
            return np.array([0])
        else:
            daily_std_dev = np.std(equity_curve, ddof=1)  # Calculate daily standard deviation
            annual_std_dev = round(daily_std_dev * np.sqrt(252), 4)  # Assuming 252 trading days in a year
            return np.around(annual_std_dev, decimals=4)

    # -- Trades -- 
    @staticmethod
    def total_trades(trade_log:pd.DataFrame):
        return len(trade_log)
    
    @staticmethod
    def total_winning_trades(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            return len(trade_log[trade_log['net_gain/loss'] > 0])
    
    @staticmethod
    def total_losing_trades(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            return len(trade_log[trade_log['net_gain/loss'] < 0])
    
    @staticmethod
    def avg_win_percent(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            winning_trades = round(trade_log[trade_log['net_gain/loss'] > 0], 4)
            return np.around(winning_trades['gain/loss (%)'].mean(),decimals=4) if not winning_trades.empty else 0

    @staticmethod
    def avg_loss_percent(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            losing_trades = round(trade_log[trade_log['net_gain/loss'] < 0],4)
            return np.around(losing_trades['gain/loss (%)'].mean(),decimals=4) if not losing_trades.empty else 0
    
    @staticmethod
    def percent_profitable(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            total_winning_trades = PerformanceStatistics.total_winning_trades(trade_log)
            total_trades = len(trade_log)
            return round((total_winning_trades / total_trades) * 100, 2) if total_trades > 0 else 0.0
    
    @staticmethod
    def average_trade_profit(trade_log:pd.DataFrame):
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        else:
            net_profit = PerformanceStatistics.net_profit(trade_log)
            total_trades = PerformanceStatistics.total_trades(trade_log)
            return round(net_profit / total_trades,4) if total_trades > 0 else 0
    
    @staticmethod
    def profit_factor(trade_log:pd.DataFrame):
        """Calculate the Profit Factor."""
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0

        gross_profits = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].sum()
        gross_losses = abs(trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].sum())
        
        if gross_losses > 0:
            return round(gross_profits / gross_losses,4)
        return 0.0

    @staticmethod
    def profit_and_loss_ratio(trade_log:pd.DataFrame):
        """Calculate the ratio of average winning trade to average losing trade."""

        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0

        # Calculate average win
        avg_win = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].mean()
        avg_win = 0 if pd.isna(avg_win) else avg_win
        
        # Calculate average loss
        avg_loss = trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].mean()
        avg_loss = 0 if pd.isna(avg_loss) else avg_loss

        if avg_loss != 0:
            return round(abs(avg_win / avg_loss),4)
        return 0.0
    
    # -- Comparables -- 
    @staticmethod
    def sharpe_ratio(equity_curve:np.ndarray, risk_free_rate=0.04):
        if not isinstance(equity_curve, np.ndarray):
            raise TypeError("equity_curve must be a numpy array")
        
        # Check for empty array
        if len(equity_curve) == 0:
            return np.array([0])
        else:
            daily_returns = PerformanceStatistics.daily_return(equity_curve)
            excess_returns = np.array(daily_returns) - risk_free_rate / 252  # Assuming daily returns, adjust risk-free rate accordingly
            return np.around(np.mean(excess_returns) / np.std(excess_returns, ddof=1),decimals=4) if np.std(excess_returns, ddof=1) != 0 else 0
            
    @staticmethod
    def sortino_ratio(trade_log:pd.DataFrame, target_return=0):
        """Calculate the Sortino Ratio for a given trading log."""
        # Check if the input is a pandas DataFrame
        if not isinstance(trade_log, pd.DataFrame):
            raise TypeError("trade_log must be a pandas DataFrame")
        
        # Check if the 'net_gain/loss' column exists in the DataFrame
        if 'net_gain/loss' not in trade_log.columns:
            raise ValueError("'net_gain/loss' column is missing in trade_log DataFrame")
        
        # Check for empty DataFrame
        if trade_log.empty:
            return 0
        
        negative_returns = trade_log[trade_log['gain/loss (%)'] < target_return]['gain/loss (%)']
        expected_return = trade_log['gain/loss (%)'].mean() - target_return
        downside_deviation = negative_returns.std(ddof=1)
        
        if downside_deviation > 0:
            return round(expected_return / downside_deviation,4)
        return 0.0

    @staticmethod
    def beta(portfolio_equity_curve: np.ndarray, benchmark_equity_curve: np.ndarray) -> float:
        """Calculates the beta of the portfolio based on equity curves."""

        if not isinstance(portfolio_equity_curve, np.ndarray):
            raise TypeError("portfolio_equity_curve must be a numpy array")
        
        if not isinstance(benchmark_equity_curve, np.ndarray):
            raise TypeError("benchmark_equity_curve must be a numpy array")
        
        # Check for empty array
        if len(portfolio_equity_curve) == 0 or len(benchmark_equity_curve) ==0:
            return np.array([0])
        
        portfolio_returns = PerformanceStatistics.daily_return(portfolio_equity_curve)
        benchmark_returns = PerformanceStatistics.daily_return(benchmark_equity_curve)
        
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        variance = np.var(benchmark_returns, ddof=1)  # Using sample variance
        beta_value = covariance / variance
        return round(beta_value,4)

    @staticmethod
    def alpha(portfolio_equity_curve: np.ndarray, benchmark_equity_curve: np.ndarray, risk_free_rate: float) -> float:
        """Calculates the alpha of the portfolio based on equity curves."""

        if not isinstance(portfolio_equity_curve, np.ndarray):
            raise TypeError("portfolio_equity_curve must be a numpy array")
        
        if not isinstance(benchmark_equity_curve, np.ndarray):
            raise TypeError("benchmark_equity_curve must be a numpy array")
        
        if not isinstance(risk_free_rate, (float, int)):
            raise TypeError("risk_free_rate must be a float or int.")
        
        # Check for empty array
        if len(portfolio_equity_curve) == 0 or len(benchmark_equity_curve) ==0:
            return np.array([0])
        
        portfolio_returns = PerformanceStatistics.daily_return(portfolio_equity_curve)
        benchmark_returns = PerformanceStatistics.daily_return(benchmark_equity_curve)

        # Annualize the daily returns
        annualized_portfolio_return = np.mean(portfolio_returns) * 252
        annualized_benchmark_return = np.mean(benchmark_returns) * 252

        # Calculate beta using annualized returns
        beta_value = PerformanceStatistics.beta(portfolio_equity_curve, benchmark_equity_curve)

        # Calculate alpha using annualized returns and annual risk-free rate
        alpha_value = annualized_portfolio_return - (risk_free_rate + beta_value * (annualized_benchmark_return - risk_free_rate))
        return round(alpha_value, 4)
    
    # -- Plots --
    @staticmethod
    def plot_curve(y, title='Title', x_label="Time", y_label="Curve", show_plot=True):
        plt.figure(figsize=(12, 6))
        plt.plot(y, label=y_label)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.axhline(y=0, color='gray', linestyle='--')
        plt.grid()
        plt.legend()
        if show_plot:
            plt.show()