import pandas as pd
from datetime import datetime

class EquityValue:
    def __init__(self, timestamp, equity_value):
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        self.timestamp = timestamp
        self.equity_value = equity_value

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'equity_value': self.equity_value,
        }
    
class EquityManager:
    def __init__(self):
        self.equity_log = []

    def add_equity(self, equity: EquityValue):
        self.equity_log.append(equity.to_dict())

    def calculate_return_and_drawdown(self):
        df = pd.DataFrame(self.equity_log)
        df['percent_return'] = round(df['equity_value'].pct_change() * 100,6)
        df['percent_return'].fillna(0, inplace=True)  # Replace NaN with 0 for the first element

        rolling_max = df['equity_value'].cummax()
        df['percent_drawdown'] = round((df['equity_value'] - rolling_max ) / rolling_max * 100, 6)
        df['percent_drawdown'].fillna(0, inplace=True)  # Replace NaN with 0

        return df

    @property
    def log(self):
        """Return the full equity log as a list of dictionaries."""
        df = self.calculate_return_and_drawdown()
        return df.to_dict('records')
