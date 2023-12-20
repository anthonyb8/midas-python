import pandas as pd
from datetime import datetime

class Trade:
    def __init__(self, trade_id, leg_id, timestamp, symbol, quantity, price, cost, direction):

        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        self.trade_id = trade_id
        self.leg_id = leg_id
        self.timestamp = timestamp
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.cost = cost
        self.direction = direction

    def to_dict(self):
        return {
            'trade_id': self.trade_id,
            'leg_id': self.leg_id,
            'timestamp': self.timestamp,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'cost': self.cost,
            'direction': self.direction
        }

class TradesManager:
    def __init__(self):
        self.trade_log = []

    @property
    def log(self):
        return self.trade_log

    def add_trade(self, trade: Trade):
        self.trade_log.append(trade.to_dict())

    def aggregate_trades(self) -> pd.DataFrame:

        if not self.trade_log:
            return []
        
        df = pd.DataFrame(self.log)

        # Calculate the initial value (entry cost) for each trade (the sum of LONG and SHORT)
        entry_values = df[df['direction'].isin(['LONG', 'SHORT'])].groupby('trade_id')['cost'].sum()

        # Calculate the exit value for each trade (the sum of SELL and COVER)
        exit_values = df[df['direction'].isin(['SELL', 'COVER'])].groupby('trade_id')['cost'].sum()

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

