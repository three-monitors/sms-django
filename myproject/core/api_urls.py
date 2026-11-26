from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ServiceViewSet, OrderViewSet, InventoryViewSet, StatisticsAPI

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='client')
router.register('services', ServiceViewSet, basename='service')
router.register('orders', OrderViewSet, basename='order')
router.register('inventory', InventoryViewSet, basename='inventory')

urlpatterns = [
    path("", include(router.urls)),
    path("statistics/", StatisticsAPI.as_view(), name="api_statistics"),
]
