from core.models import Client, PatientProfile, Service, Order, Inventory
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()


# Створити клієнта
client = Client.objects.create(
    name="Іваненко Олег",
    email="ivanenko@example.com",
    phone="+380501234567"
)
print(f"✓ Клієнт створений: {client}")

# Створити послугу
service = Service.objects.create(
    name="Очищення обличчя",
    description="Глибоке очищення шкіри",
    price="850.00",
    duration_hours=0.5
)
print(f"✓ Послуга створена: {service}")

# Створити замовлення
order = Order.objects.create(
    client=client,
    status="new",
    date="2026-11-20",
    total_price="850.00"
)
order.service.add(service)
print(f"✓ Замовлення створене: {order}")

# Створити інвентар
inventory = Inventory.objects.create(
    name="Крем для обличчя",
    description="Зволожуючий крем",
    quantity=10,
    min_quantity=5,
    price_per_unit="450.00",
    category="Косметика"
)
print(f"✓ Інвентар створений: {inventory}")

# Запити
all_clients = Client.objects.all()
print(f"✓ Всього клієнтів: {all_clients.count()}")

ivan_orders = client.orders.all()
print(f"✓ Замовлень клієнта: {ivan_orders.count()}")

print("\nВсі тести пройшли!")
