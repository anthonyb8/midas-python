from rest_framework import serializers
from .models import EquityBarData, CommodityBarData, CryptocurrencyBarData
from assets.models import Asset  # Importing Asset model

class EquityBarDataSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(write_only=True)

    class Meta:
        model = EquityBarData
        fields = ['id','symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume']

    def to_representation(self, instance):
        """Modify the representation for read operations to include the symbol."""
        ret = super().to_representation(instance)
        ret['symbol'] = instance.asset.symbol
        return ret

    def create(self, validated_data):
        # Convert symbol to asset
        asset = self.get_asset_by_symbol(validated_data.pop('symbol'))
        validated_data['asset'] = asset
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert symbol to asset
        asset = self.get_asset_by_symbol(validated_data.pop('symbol'))
        validated_data['asset'] = asset
        return super().update(instance, validated_data)

    @staticmethod
    def get_asset_by_symbol(symbol):
        try:
            return Asset.objects.get(symbol=symbol)
        except Asset.DoesNotExist:
            raise serializers.ValidationError(f"Asset with symbol {symbol} does not exist")

class CommodityBarDataSerializer(serializers.ModelSerializer):
    symbol = serializers.SerializerMethodField()

    class Meta:
        model = CommodityBarData
        fields = ['asset','symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume']
    
    def get_symbol(self, obj):
        return obj.asset.symbol 


class CryptocurrencyBarDataSerializer(serializers.ModelSerializer):
    symbol = serializers.SerializerMethodField()

    class Meta:
        model = CryptocurrencyBarData
        fields = ['asset','symbol', 'timestamp', 'open', 'close', 'high', 'low', 'volume']

    def get_symbol(self, obj):
        return obj.asset.symbol 

