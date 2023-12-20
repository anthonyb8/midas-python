# urls.py in your price_data app

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquityBarDataViewSet, CommodityBarDataViewSet, CryptocurrencyBarDataViewSet

router = DefaultRouter()
router.register(r'equitybardata', EquityBarDataViewSet)
router.register(r'commoditybardata', CommodityBarDataViewSet)
router.register(r'cryptocurrencybardata', CryptocurrencyBarDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
