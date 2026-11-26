from rest_framework import serializers
from .models import Client, Service, Order, Inventory


class ClientSerializer(serializers.ModelSerializer):
    """Серіалізатор для клієнта"""

    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone",
                  "date_of_birth", "skin_type", "created_at"]


class ServiceSerializer(serializers.ModelSerializer):
    """Серіалізатор для послуги"""

    class Meta:
        model = Service
        fields = ["id", "name", "description", "price",
                  "duration_hours", "is_active", "image_path"]


class InventorySerializer(serializers.ModelSerializer):
    """Серіалізатор для інвентарю"""

    class Meta:
        model = Inventory
        fields = ["id", "name", "description", "quantity",
                  "min_quantity", "price_per_unit", "category"]


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор для замовлення з вкладеною серіалізацією"""
    client = ClientSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "client", "services", "status", "date",
                  "appointment_time", "description", "total_price", "created_at"]
