from django.db import models
import json


class Backtest(models.Model):
    strategy_name = models.CharField(max_length=255)
    parameters = models.TextField() 

    def save(self, *args, **kwargs):
        if isinstance(self.parameters, dict):
            self.parameters = json.dumps(self.parameters)
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "strategy_name": self.strategy_name,
            "parameters": json.loads(self.parameters),
            "summary_stats": [stat.to_dict() for stat in self.summary_stats.all()],
            "trades": [trade.to_dict() for trade in self.trades.all()],
            "equity_data": [equity.to_dict() for equity in self.equity_data.all()],
            "signals": [signal.to_dict() for signal in self.signals.all()],
            "price_data": [price.to_dict() for price in self.price_data.all()]
        }

class SummaryStats(models.Model):
    backtest = models.ForeignKey(Backtest, related_name='summary_stats', on_delete=models.CASCADE)
    total_return = models.FloatField(null=True)
    total_trades = models.IntegerField(null=True)
    total_fees = models.FloatField(null=True)
    net_profit = models.FloatField(null=True)
    ending_equity = models.FloatField(null=True)
    max_drawdown = models.FloatField(null=True)
    avg_win_percent = models.FloatField(null=True)
    avg_loss_percent = models.FloatField(null=True)
    sortino_ratio = models.FloatField(null=True)
    alpha = models.FloatField(null=True)
    beta = models.FloatField(null=True)
    annual_standard_deviation = models.FloatField(null=True)
    profit_and_loss_ratio = models.FloatField(null=True)
    profit_factor = models.FloatField(null=True)

class Trade(models.Model):
    backtest = models.ForeignKey(Backtest, related_name='trades', on_delete=models.CASCADE)
    trade_id = models.CharField(max_length=100)  
    leg_id = models.CharField(max_length=100)    
    timestamp = models.DateTimeField()
    symbol = models.CharField(max_length=50)     
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    direction = models.CharField(max_length=10)  # Assuming 'direction' is a string like 'buy' or 'sell'

class EquityData(models.Model):
    backtest = models.ForeignKey(Backtest, related_name='equity_data', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    equity_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    percent_drawdown = models.DecimalField(max_digits=15, decimal_places=6, default=0.0)
    percent_return = models.DecimalField(max_digits=15, decimal_places=6, default=0.0)


    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'equity_value': self.equity_value,

        }

class Signal(models.Model):
    backtest = models.ForeignKey(Backtest, related_name='signals', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

class TradeInstruction(models.Model):
    ticker = models.CharField(max_length=100)
    direction = models.CharField(max_length=10)  # 'BUY' or 'SELL'
    trade_id = models.PositiveIntegerField()
    leg_id = models.PositiveIntegerField()
    allocation_percent = models.FloatField()
    signal = models.ForeignKey(Signal, related_name='trade_instructions', on_delete=models.CASCADE)


class PriceData(models.Model):
    backtest = models.ForeignKey(Backtest, related_name='price_data', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()