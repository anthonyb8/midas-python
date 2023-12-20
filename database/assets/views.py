from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Asset, Equity, Commodity, Cryptocurrency
from .serializers import AssetSerializer, EquitySerializer, CommoditySerializer, CryptocurrencySerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        symbol = self.request.query_params.get('symbol')

        if symbol:
            return queryset.filter(symbol__iexact=symbol.upper())  # Assuming symbol is case-insensitive

        return queryset

class EquityViewSet(viewsets.ModelViewSet):
    queryset = Equity.objects.all()
    serializer_class = EquitySerializer

class CommodityViewSet(viewsets.ModelViewSet):
    queryset = Commodity.objects.all()
    serializer_class = CommoditySerializer

class CryptocurrencyViewSet(viewsets.ModelViewSet):
    queryset = Cryptocurrency.objects.all()
    serializer_class = CryptocurrencySerializer
