from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import EquityBarData, CommodityBarData, CryptocurrencyBarData
from .serializers import EquityBarDataSerializer, CommodityBarDataSerializer, CryptocurrencyBarDataSerializer
from assets.models import Asset
import datetime

class EquityBarDataViewSet(viewsets.ModelViewSet):
    queryset = EquityBarData.objects.all()
    serializer_class = EquityBarDataSerializer

    @action(methods=['post'], detail=False)
    def bulk_create(self, request, *args, **kwargs):
        equity_data_list = request.data

        if not isinstance(equity_data_list, list):
            return Response({'error': 'Input data should be a list'}, status=status.HTTP_400_BAD_REQUEST)

        created_objects = []

        with transaction.atomic():
            for equity_data in equity_data_list:
                symbol = equity_data.get('symbol')
                if not symbol:
                    return Response({'error': 'symbol is required for each item'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    asset = Asset.objects.get(symbol=symbol)
                except Asset.DoesNotExist:
                    return Response({'error': f'Asset not found for symbol {symbol}'}, status=status.HTTP_404_NOT_FOUND)

                equity_data['asset'] = asset
                serializer = self.get_serializer(data=equity_data)
                serializer.is_valid(raise_exception=True)
                created_objects.append(serializer.save())

        return Response(self.get_serializer(created_objects, many=True).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super().get_queryset()
        symbols = self.request.query_params.get('symbols')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if symbols:
            symbol_list = symbols.split(',')
            assets = Asset.objects.filter(symbol__in=symbol_list)
            queryset = queryset.filter(asset__in=assets)

        if start_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__gte=start_date)

        if end_date:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

class CommodityBarDataViewSet(viewsets.ModelViewSet):
    queryset = CommodityBarData.objects.all()
    serializer_class = CommodityBarDataSerializer

class CryptocurrencyBarDataViewSet(viewsets.ModelViewSet):
    queryset = CryptocurrencyBarData.objects.all()
    serializer_class = CryptocurrencyBarDataSerializer
