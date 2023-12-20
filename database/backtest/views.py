from rest_framework import viewsets
from .models import Backtest, SummaryStats, Trade, EquityData, Signal, PriceData
from .serializers import (BacktestSerializer, SummaryStatsSerializer, TradeSerializer, 
                          EquityDataSerializer, SignalSerializer, PriceDataSerializer,  BacktestListSerializer)

class BacktestViewSet(viewsets.ModelViewSet):
    queryset = Backtest.objects.all()
    serializer_class = BacktestSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return BacktestListSerializer
        
        return super().get_serializer_class()
    
class SummaryStatsViewSet(viewsets.ModelViewSet):
    queryset = SummaryStats.objects.all()
    serializer_class = SummaryStatsSerializer

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

class EquityDataViewSet(viewsets.ModelViewSet):
    queryset = EquityData.objects.all()
    serializer_class = EquityDataSerializer

class SignalViewSet(viewsets.ModelViewSet):
    queryset = Signal.objects.all()
    serializer_class = SignalSerializer

class PriceDataViewSet(viewsets.ModelViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer

