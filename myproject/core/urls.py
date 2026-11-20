from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("clients/", views.clients_list, name="clients_list"),
    path("clients/<int:client_id>/", views.client_detail, name="client_detail"),
    path("clients/<int:client_id>/orders/",
         views.client_orders, name="client_orders"),
    path("clients/search/", views.client_search, name="client_search"),
    path("services/", views.services_list, name="services_list"),
    path("services/<int:service_id>/",
         views.service_detail, name="service_detail"),
    path("services/search/", views.service_search, name="service_search"),
    path("orders/", views.orders_list, name="orders_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/status/<str:status>/",
         views.orders_by_status, name="orders_by_status"),
    path("inventory/", views.inventory_list, name="inventory_list"),
    path("schedule/", views.schedule, name="schedule"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("about/", views.about, name="about"),
]
