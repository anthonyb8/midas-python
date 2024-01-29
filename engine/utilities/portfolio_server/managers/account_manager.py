import pandas as pd
from datetime import datetime

class AccountEquity:
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
    
class AccountManager:
    def __init__(self):
        self.account = {}
        self._equity_log = []

    def update_account(self, key, value):
        self.account[key] = value

        if 'EquityValue' == key:
            self._equity_log.append(value)

    def __str__(self) -> str:
        string = ""
        for key, value in self.account.items():
            string += f" {key} : {value} \n"
        return string

    def calculate_return_and_drawdown(self):
        df = pd.DataFrame(self._equity_log)
        df['percent_return'] = round(df['equity_value'].pct_change() * 100,4)
        df['percent_return'].fillna(0, inplace=True)  # Replace NaN with 0 for the first element

        rolling_max = df['equity_value'].cummax()
        df['percent_drawdown'] = round((df['equity_value'] - rolling_max ) / rolling_max * 100, 4)
        df['percent_drawdown'].fillna(0, inplace=True)  # Replace NaN with 0

        return df

    @property
    def equity_log(self):
        """Return the full equity log as a list of dictionaries."""
        df = self.calculate_return_and_drawdown()
        return df.to_dict('records')