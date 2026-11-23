from django.contrib import admin
from .models import Client, PatientProfile, Service, Order, Inventory


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "created_at"]
    search_fields = ["name", "email", "phone"]
    list_filter = ["created_at"]


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ["client", "preferred_procedures"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "duration_hours", "is_active"]
    search_fields = ["name"]
    list_filter = ["is_active"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "client", "status", "date", "total_price"]
    search_fields = ["client__name", "id"]
    list_filter = ["status", "date"]
    date_hierarchy = "date"
    filter_horizontal = ["service"]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "quantity", "category", "is_low_stock"]
    search_fields = ["name", "category"]
    list_filter = ["category"]
