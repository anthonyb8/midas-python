from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include('account.urls')),
    path('backtest/', include('backtest.urls')),
    path('api/', include([
        path('assets/', include('assets.urls')),
        path('price_data/', include('price_data.urls')),
    ])),
]