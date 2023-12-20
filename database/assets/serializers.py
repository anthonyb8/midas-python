from rest_framework import serializers
from .models import Asset, Equity, Commodity, Cryptocurrency

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'symbol', 'type', 'created_at', 'updated_at']

class EquitySerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Equity
        fields = ['asset', 'company_name', 'exchange', 'currency', 'industry', 'description', 'market_cap', 'shares_outstanding', 'created_at', 'updated_at']

class CommoditySerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Commodity
        fields = ['asset', 'commodity_name', 'base_future_code', 'expiration_date', 'industry', 'exchange', 'currency', 'description', 'created_at', 'updated_at']

class CryptocurrencySerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Cryptocurrency
        fields = ['asset', 'cryptocurrency_name', 'circulating_supply', 'market_cap', 'total_supply', 'max_supply', 'description', 'created_at', 'updated_at']
