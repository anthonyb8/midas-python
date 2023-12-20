from rest_framework import serializers
from .models import Backtest, SummaryStats, Trade, EquityData, Signal, PriceData, TradeInstruction
from .services import create_backtest


class SummaryStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryStats
        fields = ['total_return', 'total_trades', 'total_fees', 'net_profit', 
                  'ending_equity', 'max_drawdown', 'avg_win_percent', 
                  'avg_loss_percent', 'sortino_ratio', 'alpha', 'beta', 
                  'annual_standard_deviation', 'profit_and_loss_ratio', 
                  'profit_factor'] 
        
class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['trade_id', 'leg_id', 'timestamp', 'symbol', 'quantity', 'price', 'cost', 'direction']

class EquityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquityData
        fields = ['timestamp', 'equity_value', 'percent_drawdown', 'percent_return']

class TradeInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeInstruction
        fields = ['ticker', 'direction', 'trade_id', 'leg_id', 'allocation_percent']

class SignalSerializer(serializers.ModelSerializer):
    trade_instructions = TradeInstructionSerializer(many=True)

    class Meta:
        model = Signal
        fields = ['timestamp', 'trade_instructions']

    def create(self, validated_data):
        trade_instructions_data = validated_data.pop('trade_instructions', [])
        signal = Signal.objects.create(**validated_data)
        for ti_data in trade_instructions_data:
            TradeInstruction.objects.create(signal=signal, **ti_data)
        return signal
    
class PriceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceData
        fields = ['symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume']

class BacktestSerializer(serializers.ModelSerializer):
    parameters = serializers.JSONField()
    summary_stats = SummaryStatsSerializer(many=True)
    trades = TradeSerializer(many=True)
    equity_data = EquityDataSerializer(many=True)
    signals = SignalSerializer(many=True)
    price_data = PriceDataSerializer(many=True)

    class Meta:
        model = Backtest
        fields = ['id', 'strategy_name', 'parameters', 'summary_stats', 'trades', 'equity_data', 'signals', 'price_data']

    def create(self, validated_data):
        return create_backtest(validated_data)
    
class BacktestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backtest
        fields = ['id', 'strategy_name', 'parameters']
