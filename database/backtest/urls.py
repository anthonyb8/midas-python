from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (BacktestViewSet, SummaryStatsViewSet, TradeViewSet, 
                    EquityDataViewSet, SignalViewSet, PriceDataViewSet)

router = DefaultRouter()
router.register(r'', BacktestViewSet)
router.register(r'summary_stats', SummaryStatsViewSet)
router.register(r'trades', TradeViewSet)
router.register(r'equity_data', EquityDataViewSet)
router.register(r'signals', SignalViewSet)
router.register(r'price_data', PriceDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
