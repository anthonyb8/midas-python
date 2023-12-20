# assets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, EquityViewSet, CommodityViewSet, CryptocurrencyViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'equities', EquityViewSet)
router.register(r'commodities', CommodityViewSet)
router.register(r'cryptocurrencies', CryptocurrencyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
