from rest_framework import serializers
from .models import Client, Service, Order


class ClientSerializer(serializers.ModelSerializer):
    """Серіалізатор для клієнта"""

    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone"]


class ServiceSerializer(serializers.ModelSerializer):
    """Серіалізатор для послуги"""

    class Meta:
        model = Service
        fields = ["id", "name", "price", "duration_hours"]


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для замовлення з вкладеною серіалізацією"""
    client = ClientSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "client", "services", "status", "date",
                  "appointment_time", "total_price", "created_at"]
