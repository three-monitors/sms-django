from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("clients/", views.clients_list, name="clients_list"),
    path("clients/<int:client_id>/", views.client_detail, name="client_detail"),
    path("services/", views.services_list, name="services_list"),
    path("services/<int:service_id>/", views.service_detail, name="service_detail"),
    path("orders/", views.orders_list, name="orders_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("about/", views.about, name="about"),
]