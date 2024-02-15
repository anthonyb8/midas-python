import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

    
class PerformanceStatistics:
    # -- General -- 
    @staticmethod
    def net_profit(trade_log: pd.DataFrame):
        return trade_log['net_gain/loss'].sum()
    
    @staticmethod
    def daily_return(equity_curve: np.ndarray):
        daily_returns_np = np.diff(equity_curve) / equity_curve[:-1] # Calculate daily returns using vectorized operations
        daily_returns_np = np.insert(daily_returns_np, 0, 0) # Prepend a 0 for the first day's return
        return daily_returns_np

    @staticmethod
    def cumulative_return(equity_curve: np.ndarray):
        daily_returns = np.diff(equity_curve) / equity_curve[:-1] # Calculate daily returns
        cumulative_returns = np.cumprod(1 + daily_returns) - 1 # Calculate cumulative returns
        cumulative_returns = np.insert(cumulative_returns * 100, 0, 0) # Convert to percentage and prepend a 0 for the initial day
        return cumulative_returns
        
    @staticmethod
    def total_return(equity_curve:np.ndarray):
        return PerformanceStatistics.cumulative_return(equity_curve)[-1]  # Returns the latest cumulative return
    
    @staticmethod
    def drawdown(equity_curve:np.ndarray):
        rolling_max = np.maximum.accumulate(equity_curve) # Calculate the rolling maximum
        drawdowns = (equity_curve - rolling_max) / rolling_max * 100 # Calculate drawdowns
        drawdowns[0] = 0 if drawdowns[0] == -np.inf else drawdowns[0] # Fill the first position with 0 if needed (assuming equity_curve starts at a peak)
        return drawdowns
    
    @staticmethod
    def max_drawdown(equity_curve:np.ndarray):
        drawdowns = PerformanceStatistics.drawdown(equity_curve)
        max_drawdown = np.min(drawdowns)  # Find the maximum drawdown
        return max_drawdown

    @staticmethod
    def annual_standard_deviation(equity_curve:np.ndarray):
        """Calculate the annualized standard deviation of returns from a NumPy array of log returns."""
        daily_std_dev = np.std(equity_curve, ddof=1)  # Calculate daily standard deviation
        annual_std_dev = round(daily_std_dev * np.sqrt(252), 4)  # Assuming 252 trading days in a year
        return annual_std_dev

    # -- Trades -- 
    @staticmethod
    def total_trades(trade_log:pd.DataFrame):
        return len(trade_log)
    
    @staticmethod
    def total_winning_trades(trade_log:pd.DataFrame):
        return len(trade_log[trade_log['net_gain/loss'] > 0])
    
    @staticmethod
    def total_losing_trades(trade_log:pd.DataFrame):
        return len(trade_log[trade_log['net_gain/loss'] < 0])
    
    @staticmethod
    def avg_win_percent(trade_log:pd.DataFrame):
        winning_trades = round(trade_log[trade_log['net_gain/loss'] > 0], 4)
        return winning_trades['gain/loss (%)'].mean() if not winning_trades.empty else 0

    @staticmethod
    def avg_loss_percent(trade_log:pd.DataFrame):
        losing_trades = round(trade_log[trade_log['net_gain/loss'] < 0],4)
        return losing_trades['gain/loss (%)'].mean() if not losing_trades.empty else 0
    
    @staticmethod
    def percent_profitable(trade_log:pd.DataFrame):
        total_winning_trades = PerformanceStatistics.total_winning_trades(trade_log)
        total_trades = len(trade_log)
        return f"{round((total_winning_trades / total_trades) * 100, 2)}%" if total_trades > 0 else "0%"
    
    @staticmethod
    def average_trade_profit(trade_log:pd.DataFrame):
        net_profit = PerformanceStatistics.net_profit(trade_log)
        total_trades = PerformanceStatistics.total_trades(trade_log)
        return net_profit / total_trades if total_trades > 0 else 0
    
    @staticmethod
    def profit_factor(trade_log:pd.DataFrame):
        """Calculate the Profit Factor."""
        gross_profits = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].sum()
        gross_losses = abs(trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].sum())
        
        if gross_losses > 0:
            return gross_profits / gross_losses
        return 0.0

    @staticmethod
    def profit_and_loss_ratio(trade_log:pd.DataFrame):
        """Calculate the ratio of average winning trade to average losing trade."""
        avg_win = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].mean()
        avg_loss = trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].mean()

        if avg_loss != 0:
            return abs(avg_win / avg_loss)
        return 0.0
    
    # -- Comparables -- 
    @staticmethod
    def sharpe_ratio(equity_curve:np.ndarray, risk_free_rate=0.04):
        daily_returns = PerformanceStatistics.daily_return(equity_curve)
        excess_returns = np.array(daily_returns) - risk_free_rate / 252  # Assuming daily returns, adjust risk-free rate accordingly
        return np.mean(excess_returns) / np.std(excess_returns, ddof=1) if np.std(excess_returns, ddof=1) != 0 else 0
        
    @staticmethod
    def sortino_ratio(trade_log:pd.DataFrame, target_return=0):
        """Calculate the Sortino Ratio for a given trading log."""
        negative_returns = trade_log[trade_log['gain/loss (%)'] < target_return]['gain/loss (%)']
        expected_return = trade_log['gain/loss (%)'].mean() - target_return
        downside_deviation = negative_returns.std(ddof=1)
        
        if downside_deviation > 0:
            return expected_return / downside_deviation
        return 0.0

    @staticmethod
    def beta(portfolio_equity_curve: np.ndarray, benchmark_equity_curve: np.ndarray) -> float:
        """Calculates the beta of the portfolio based on equity curves."""
        portfolio_returns = PerformanceStatistics.daily_return(portfolio_equity_curve)
        benchmark_returns = PerformanceStatistics.daily_return(benchmark_equity_curve)
        
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        variance = np.var(benchmark_returns, ddof=1)  # Using sample variance
        beta_value = covariance / variance
        return beta_value

    @staticmethod
    def alpha(portfolio_equity_curve: np.ndarray, benchmark_equity_curve: np.ndarray, risk_free_rate: float) -> float:
        """Calculates the alpha of the portfolio based on equity curves."""
        portfolio_returns = PerformanceStatistics.daily_return(portfolio_equity_curve)
        benchmark_returns = PerformanceStatistics.daily_return(benchmark_equity_curve)

        beta_value = PerformanceStatistics.beta(portfolio_equity_curve, benchmark_equity_curve)
        expected_market_return = np.mean(benchmark_returns)
        alpha_value = np.mean(portfolio_returns) - (risk_free_rate + beta_value * (expected_market_return - risk_free_rate))
        return alpha_value
    
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