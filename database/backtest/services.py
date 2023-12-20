from django.db import transaction
from .models import Backtest, SummaryStats, Trade, EquityData, Signal, PriceData, TradeInstruction

def create_backtest(validated_data):
    with transaction.atomic():
        # Extract nested data
        summary_stats_data = validated_data.pop('summary_stats', [])
        trades_data = validated_data.pop('trades', [])
        equity_data_data = validated_data.pop('equity_data', [])
        signals_data = validated_data.pop('signals', [])
        price_data_data = validated_data.pop('price_data', [])

        # Create the Backtest instance
        backtest = Backtest.objects.create(**validated_data)

        # Nested object creation for SummaryStats
        for stat_data in summary_stats_data:
            SummaryStats.objects.create(backtest=backtest, **stat_data)

        # Nested object creation for Trades
        for trade_data in trades_data:
            Trade.objects.create(backtest=backtest, **trade_data)

        # Nested object creation for EquityData
        for equity_data in equity_data_data:
            EquityData.objects.create(backtest=backtest, **equity_data)

        # Nested object creation for Signals and their TradeInstructions
        for signal_data in signals_data:
            trade_instructions_data = signal_data.pop('trade_instructions', [])
            signal_instance = Signal.objects.create(backtest=backtest, **signal_data)
            for ti_data in trade_instructions_data:
                TradeInstruction.objects.create(signal=signal_instance, **ti_data)

        # Nested object creation for PriceData
        for price_data in price_data_data:
            PriceData.objects.create(backtest=backtest, **price_data)

        return backtest
