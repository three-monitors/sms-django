from django.contrib import admin
from .models import Client, PatientProfile, Service, Order, Inventory


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "created_at"]
    search_fields = ["name", "email", "phone"]
    list_filter = ["created_at"]
    ordering = ["-created_at", "name"]


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ["client", "preferred_procedures", "created_at"]
    search_fields = ["client__name"]
    ordering = ["-created_at"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "price",
                    "duration_hours", "is_active", "image_path"]
    search_fields = ["name"]
    list_filter = ["is_active"]
    ordering = ["name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "client", "status",
                    "date", "appointment_time", "total_price"]
    search_fields = ["client__name", "id"]
    list_filter = ["status", "date"]
    date_hierarchy = "date"
    filter_horizontal = ["service"]
    ordering = ["-date", "-appointment_time"]
    list_per_page = 25
    list_editable = ["status"]
    readonly_fields = ["created_at", "completed_at"]
    autocomplete_fields = ["client"]

    fieldsets = (
        ("Основна інформація", {
            "fields": ("client", "service", "status", "date", "appointment_time")
        }),
        ("Деталі", {
            "fields": ("description", "total_price")
        }),
        ("Системні поля", {
            "fields": ("created_at", "completed_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "quantity", "category", "price_per_unit"]
    search_fields = ["name", "category"]
    list_filter = ["category"]
    ordering = ["name"]


admin.site.site_header = "Beauty Clinic Administration"
admin.site.site_title = "Beauty Clinic"
admin.site.index_title = "Керування салоном краси"
