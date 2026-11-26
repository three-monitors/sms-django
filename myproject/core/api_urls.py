from django.urls import path
from .views import OrderListAPI, StatisticsAPI

urlpatterns = [
    path("orders/", OrderListAPI.as_view(), name="api_orders"),
    path("statistics/", StatisticsAPI.as_view(), name="api_statistics"),
]
