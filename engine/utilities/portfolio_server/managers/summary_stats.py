from pandas import DataFrame
    
class SummaryStats:
    def __init__(self, trade_log: DataFrame, equity_log :DataFrame):
        self.trade_log = trade_log
        self.equity_log = equity_log

        self.total_trades = self._compute_total_trades()
        self.total_winning_trades = self._total_winning_trades()
        self.total_losing_trades = self._total_lossing_trades()
        self.gross_profits = self._compute_gross_profits()
        self.gross_losses = self._compute_gross_losses()
        self.net_profit = self._compute_net_profit()
        self.avg_win_percent = self._avg_win_percent()
        self.avg_loss_percent = self._avg_loss_percent()
        self.max_drawdown = self._max_drawdown()
        self.ending_equity= self._ending_equity()

    
    def _total_winning_trades(self):
        return round(self.trade_log[self.trade_log['net_gain/loss'] > 0],4)

    def _total_lossing_trades(self):
        return round(self.trade_log[self.trade_log['net_gain/loss'] < 0],4)
    
    def _avg_win_percent(self):
        return round(self.total_winning_trades['gain/loss (%)'].mean(),4)

    def _avg_loss_percent(self):
        return round(self.total_losing_trades['gain/loss (%)'].mean(),4)

    def _compute_gross_profits(self):
        return round(self.total_winning_trades['net_gain/loss'].sum(),4)

    def _compute_gross_losses(self):
        return round(abs(self.total_losing_trades['net_gain/loss'].sum()),4)

    def _compute_net_profit(self):
        """Net Profit = gross profits - gross loss (including commissions)."""
        return round(self.gross_profits - self.gross_losses,4)
    
    def _compute_total_trades(self):
        return len(self.trade_log)
    
    def _ending_equity(self):
        return round(self.equity_log['equity_value'].iloc[-1],4)
    
    def _max_drawdown(self):
        """Calculate maximum drawdown."""
        return round(self.equity_log['percent_drawdown'].min(),4)
    
    def total_return(self):
        """Calculate total return from the start to the end of the period."""
        return round(((self.ending_equity / self.equity_log['equity_value'].iloc[0]) - 1) * 100,4)
    
    def profit_to_drawdown(self):
        """Calculate the profit to drawdown ratio."""
        if self.max_drawdown == 0:
            return float('inf')
        return round(self.net_profit / abs(self.max_drawdown),4)
    
    def average_trade_profit(self):
        """Average Trade Profit = Total Net Profit / Total number of trades."""
        return round(round(self.net_profit / self.total_trades, 2),4)

    def percent_profitable(self):
        """Calculate the percentage of profitable trades."""
        return f"{round((len(self.total_winning_trades) / self.total_trades) * 100, 2)}%"
    
    def sortino_ratio(self):
        # Calculate negative asset returns only
        negative_returns = self.trade_log[self.trade_log['gain/loss (%)'] < 0]['gain/loss (%)']
        # Compute the expected return and downside deviation
        expected_return = self.trade_log['gain/loss (%)'].mean()
        downside_deviation = negative_returns.std()
        # Assuming risk-free rate is 0 for simplicity
        if downside_deviation == 0:
            return 0.0
        return 0.0#round(expected_return / downside_deviation,2)

    def annual_standard_deviation(self):
        daily_std_dev = self.equity_log['percent_return'].std()
        return round(daily_std_dev * (252**0.5),4)  # Assuming 252 trading days in a year
    
    def profit_and_loss_ratio(self):
        """Calculate the ratio of average winning trade to average losing trade."""
        if self.avg_loss_percent == 0:
            return 0.0
        return 0.0#round(self.avg_win_percent / abs(self.avg_loss_percent),4)

    def profit_factor(self):
        """Profit Factor = gross profits / gross losses."""
        if self.gross_losses == 0:
            return 0.0
        return 0.0#round(self.gross_profits / self.gross_losses,4)

    def alpha(self):
        return 0.9
    
    def beta(self):
        return 0.57
    
    def total_fees(self):
        return 10000
    
class SummaryStatsManager:
    def __init__(self):
        self._stats = []

    @property
    def log(self):
        return self._stats
    
    def calculate_summary(self, trade_log: DataFrame, equity_log : DataFrame):
        calculator = SummaryStats(trade_log, equity_log)
        
        self._stats.append({
            'total_return' : calculator.total_return(), 
            'total_trades' : calculator.total_trades,
            'total_fees' : calculator.total_fees(),
            'net_profit' : calculator.net_profit,
            'ending_equity' : calculator.ending_equity,
            'max_drawdown' : calculator.max_drawdown,
            # 'avg_win_percent' : calculator.avg_win_percent,
            # 'avg_loss_percent' : calculator.avg_loss_percent,
            'sortino_ratio' : calculator.sortino_ratio(),
            'alpha' : calculator.alpha(),
            'beta' : calculator.beta(),
            'annual_standard_deviation' : calculator.annual_standard_deviation(),
            'profit_and_loss_ratio' : calculator.profit_and_loss_ratio(),
            'profit_factor' : calculator.profit_factor(),
        })

    