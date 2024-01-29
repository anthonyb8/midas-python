import pandas as pd
from datetime import datetime

class Trade:
    def __init__(self, **trade):
        print(trade)

        if isinstance(trade['timestamp'], datetime):
            timestamp = timestamp.isoformat()

        self.trade_id = trade['trade_id']
        self.leg_id = trade['leg_id']
        self.timestamp = trade['timestamp']
        self.symbol = trade['symbol']
        self.quantity = trade['quantity']
        self.price = trade['price']
        self.cost = trade['cost']
        self.direction = trade['direction']

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

class TradeManager:
    def __init__(self):
        self.trades = []

    def update(self, **trade):
        new_trade = Trade(**trade)
        if new_trade.to_dict() not in self.trades:
            self.trades.append(new_trade.to_dict())

    def __str__(self) -> str:
        string = ""
        for trade in self.trades:
            string += f" {trade} \n"
        return string
    
    def aggregate_trades(self) -> pd.DataFrame:

        if not self.trades:
            return []
        
        df = pd.DataFrame(self.trades)

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

