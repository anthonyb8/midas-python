import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

    
class PerformanceStatistics:
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
    
    @staticmethod
    def daily_return(equity_curve):
        df = pd.DataFrame({'equity_value': equity_curve})
        df['daily_return'] = df['equity_value'].pct_change().fillna(0)
        return df['daily_return'].tolist()

    @staticmethod
    def cumulative_return(equity_curve):
        df = pd.DataFrame({'equity_value': equity_curve})
        df['cumulative_total_return'] = (1 + df['equity_value'].pct_change()).cumprod().fillna(0) - 1
        df['cumulative_total_return'] *= 100
        return df['cumulative_total_return'].tolist()

    @staticmethod
    def drawdown(equity_curve):
        df = pd.DataFrame({'equity_value': equity_curve})
        rolling_max = df['equity_value'].cummax()
        df['percent_drawdown'] = (df['equity_value'] - rolling_max) / rolling_max * 100
        df['percent_drawdown'].fillna(0, inplace=True)
        return df['percent_drawdown'].tolist()

    @staticmethod
    def sharpe_ratio(equity_curve, risk_free_rate=0.04):
        daily_returns = PerformanceStatistics.daily_return(equity_curve)
        excess_returns = np.array(daily_returns) - risk_free_rate / 252  # Assuming daily returns, adjust risk-free rate accordingly
        return np.mean(excess_returns) / np.std(excess_returns, ddof=1) if np.std(excess_returns, ddof=1) != 0 else 0
        
    @staticmethod
    def total_winning_trades(trade_log:pd.DataFrame):
        return round(trade_log[trade_log['net_gain/loss'] > 0],4)
    
    @staticmethod
    def total_losing_trades(trade_log:pd.DataFrame):
        return round(trade_log[trade_log['net_gain/loss'] < 0],4)
    
    @staticmethod
    def avg_win_percent(trade_log:pd.DataFrame):
        winning_trades = PerformanceStatistics.total_winning_trades(trade_log)
        return winning_trades['gain/loss (%)'].mean() if not winning_trades.empty else 0

    @staticmethod
    def avg_loss_percent(trade_log:pd.DataFrame):
        losing_trades = PerformanceStatistics.total_losing_trades(trade_log)
        return losing_trades['gain/loss (%)'].mean() if not losing_trades.empty else 0

    @staticmethod
    def net_profit(trade_log:pd.DataFrame):
        return trade_log['net_gain/loss'].sum()

    @staticmethod
    def total_trades(trade_log:pd.DataFrame):
        return len(trade_log)
    
    @staticmethod
    def percent_profitable(trade_log:pd.DataFrame):
        total_winning_trades = len(PerformanceStatistics.total_winning_trades(trade_log))
        total_trades = len(trade_log)
        return f"{round((total_winning_trades / total_trades) * 100, 2)}%" if total_trades > 0 else "0%"
    
    @staticmethod
    def average_trade_profit(net_profit, total_trades):
        return net_profit / total_trades if total_trades > 0 else 0

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
    def annual_standard_deviation(equity_log:list):
        """Calculate the annualized standard deviation of returns."""
        daily_std_dev = equity_log['percent_return'].std(ddof=1)
        return round(daily_std_dev * np.sqrt(252), 4)  # Assuming 252 trading days in a year

    @staticmethod
    def profit_and_loss_ratio(trade_log:pd.DataFrame):
        """Calculate the ratio of average winning trade to average losing trade."""
        avg_win = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].mean()
        avg_loss = trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].mean()

        if avg_loss != 0:
            return abs(avg_win / avg_loss)
        return 0.0

    @staticmethod
    def profit_factor(trade_log:pd.DataFrame):
        """Calculate the Profit Factor."""
        gross_profits = trade_log[trade_log['net_gain/loss'] > 0]['net_gain/loss'].sum()
        gross_losses = abs(trade_log[trade_log['net_gain/loss'] < 0]['net_gain/loss'].sum())
        
        if gross_losses > 0:
            return gross_profits / gross_losses
        return 0.0

    # Alpha and Beta calculation would require more parameters including benchmark returns, 
    # risk-free rate, and possibly the portfolio's beta (for alpha calculation).
    # These calculations are more complex and context-dependent than the other metrics.

    @staticmethod
    def calculate_portfolio_returns(equity_curve):
        return PerformanceStatistics.cumulative_return(equity_curve)[-1]  # Returns the latest cumulative return

    @staticmethod
    def beta(portfolio_returns, benchmark_returns):
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        variance = np.var(benchmark_returns)
        beta = covariance / variance
        return beta

    @staticmethod
    def alpha(portfolio_returns, benchmark_returns, risk_free_rate):
        beta = PerformanceStatistics.beta(portfolio_returns, benchmark_returns)
        expected_market_return = np.mean(benchmark_returns)
        alpha = np.mean(portfolio_returns) - (risk_free_rate + beta * (expected_market_return - risk_free_rate))
        return alpha