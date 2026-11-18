from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# Тимчасові дані для Beauty Clinic
CLIENTS = [
    {"id": 1, "name": "Іваненко Олег", "phone": "+380501234567",
        "email": "ivanenko@example.com"},
    {"id": 2, "name": "Петренко Марія", "phone": "+380509876543",
        "email": "petrenko@example.com"},
    {"id": 3, "name": "Коваль Андрій",
        "phone": "+380504567890", "email": "koval@example.com"},
]

SERVICES = [
    {"id": 1, "name": "Очищення обличчя", "price": 850, "duration": 30},
    {"id": 2, "name": "Пілінг", "price": 400, "duration": 20},
    {"id": 3, "name": "Масаж", "price": 600, "duration": 45},
]

ORDERS = [
    {"id": 1, "client_id": 1, "service_id": 1,
        "status": "Виконано", "total_price": 850, "appointment_time": "2026-10-28 10:00"},
    {"id": 2, "client_id": 2, "service_id": 2,
        "status": "У процесі", "total_price": 400, "appointment_time": "2026-11-13 14:00"},
    {"id": 3, "client_id": 1, "service_id": 3,
        "status": "Виконано", "total_price": 600, "appointment_time": "2026-11-09 16:00"},
]

INVENTORY = [
    {"id": 1, "name": "Крем для обличчя",
        "quantity": 2, "unit": "шт.", "price": 450.00},
    {"id": 2, "name": "Олія для масажу",
        "quantity": 1, "unit": "шт.", "price": 800.00},
    {"id": 3, "name": "Маска для обличчя",
        "quantity": 10, "unit": "шт.", "price": 150.00},
    {"id": 4, "name": "Міцелярна вода", "quantity": 5,
        "unit": "шт.", "price": 200.00},
]


def home(request):
    """Головна сторінка"""
    context = {
        "title": "Beauty Clinic Management",
        "message": "Вітаємо в системі управління салоном краси!",
    }
    return render(request, "core/home.html", context)


def clients_list(request):
    """Список клієнтів"""
    context = {
        "title": "Клієнти",
        "clients": CLIENTS,
    }
    return render(request, "core/clients_list.html", context)


def client_detail(request, client_id):
    """Деталі клієнта"""
    client = next((c for c in CLIENTS if c["id"] == client_id), None)
    if client is None:
        return HttpResponse("Клієнт не знайдений", status=404)

    # Знайти замовлення клієнта
    client_orders = [o for o in ORDERS if o["client_id"] == client_id]
    # Знайти кількість замовлень
    orders_count = len(client_orders)
    # Знайти суму замовлень
    orders_total = sum(float(o["total_price"]) for o in client_orders)

    context = {
        "client": client,
        "orders": client_orders,
        "orders_count": orders_count,
        "orders_total": orders_total,
    }
    return render(request, "core/client_detail.html", context)


def client_orders(request, client_id):
    """Усі замовлення конкретного клієнта за маршрутом clients/<id>/orders/"""
    client = next((c for c in CLIENTS if c["id"] == client_id), None)
    if not client:
        return render(request, "core/404.html", {"title": "Не знайдено"}, status=404)

    orders_for_client = []
    for order in ORDERS:
        if order["client_id"] == client_id:
            service = next(
                (s for s in SERVICES if s["id"] == order["service_id"]), None)
            orders_for_client.append({
                "id": order["id"],
                "service_name": service["name"] if service else "Невідомо",
                "status": order["status"],
                "total_price": order["total_price"],
                "appointment_time": order.get("appointment_time", ""),
            })

    context = {
        "title": f"Замовлення клієнта: {client['name']}",
        "client": client,
        "orders": orders_for_client,
    }
    return render(request, "core/client_orders.html", context)


def services_list(request):
    """Список послуг"""
    context = {
        "title": "Послуги",
        "services": SERVICES,
    }
    return render(request, "core/services_list.html", context)


def service_detail(request, service_id):
    """Деталі послуги"""
    service = next((s for s in SERVICES if s["id"] == service_id), None)
    if service is None:
        return HttpResponse("Послуга не знайдена", status=404)

    context = {"service": service}
    return render(request, "core/service_detail.html", context)


def service_search(request):
    """Пошук послуги за назвою"""
    service_name = request.GET.get('service_name', '').strip()
    if service_name:
        filtered_services = [
            s for s in SERVICES if service_name.lower() in s["name"].lower()]
    else:
        filtered_services = SERVICES

    context = {
        "title": f"Результати пошуку: {service_name}" if service_name else "Послуги",
        "services": filtered_services,
    }
    return render(request, "core/services_list.html", context)


def prepare_orders(orders):
    """Додає до замовлень імена клієнтів і назви послуг"""
    orders_with_names = []
    for order in orders:
        client = next(
            (c for c in CLIENTS if c["id"] == order["client_id"]), None)
        service = next(
            (s for s in SERVICES if s["id"] == order["service_id"]), None)
        orders_with_names.append({
            "id": order["id"],
            "client_id": order["client_id"],
            "client_name": (client["name"] if client else "Невідомий"),
            "service_id": order["service_id"],
            "service_name": (service["name"] if service else "Невідомо"),
            "status": order["status"],
            "total_price": order["total_price"],
            "appointment_time": order.get("appointment_time", ""), })
    return orders_with_names


def orders_list(request):
    """Список замовлень"""
    orders_with_names = prepare_orders(ORDERS)
    orders_with_names.sort(key=lambda order: order["id"])

    context = {
        "title": "Замовлення",
        "orders": orders_with_names,
    }
    return render(request, "core/orders_list.html", context)


def order_detail(request, order_id):
    """Деталі замовлення"""
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        return render(request, "core/404.html", {"title": "Не знайдено"}, status=404)

    client = next((c for c in CLIENTS if c["id"] == order["client_id"]), None)
    service = next(
        (s for s in SERVICES if s["id"] == order["service_id"]), None)

    context = {
        "title": f"Замовлення #{order_id}",
        "order": {
            "id": order["id"],
            "client_id": order["client_id"],
            "client_name": client["name"] if client else "Невідомий",
            "service_id": order["service_id"],
            "service_name": service["name"] if service else "Невідомо",
            "status": order["status"],
            "total_price": order["total_price"],
            "appointment_time": order.get("appointment_time", ""),
        },
    }
    return render(request, "core/order_detail.html", context)


def orders_by_status(request, status):
    filtered_orders = [o for o in ORDERS if o["status"] == status]
    orders_with_names = prepare_orders(filtered_orders)

    context = {
        "title": "Замовлення",
        "orders": orders_with_names,
        "status": status,
    }
    return render(request, "core/orders_list.html", context)


def inventory_list(request):
    """Список інвентарю"""
    context = {
        "title": "Інвентар",
        "inventory": INVENTORY,
    }
    return render(request, "core/inventory_list.html", context)


def schedule(request):
    """Графік запису"""
    sorted_orders = sorted(ORDERS, key=lambda order: order["appointment_time"])
    orders_with_names = prepare_orders(sorted_orders)
    context = {
        "title": "Графік запису",
        "orders": orders_with_names,
    }
    return render(request, "core/schedule.html", context)


def dashboard(request):
    """Дашборд зі статистикою"""
    total_clients = len(CLIENTS)
    total_services = len(SERVICES)
    total_orders = len(ORDERS)
    completed_orders = len([o for o in ORDERS if o["status"] == "Виконано"])
    in_progress_orders = len(
        [o for o in ORDERS if o["status"] == "У процесі"])
    scheduled_orders = len([o for o in ORDERS if o["status"] == "Заплановано"])

    context = {
        "title": "Дашборд",
        "total_clients": total_clients,
        "total_services": total_services,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "in_progress_orders": in_progress_orders,
        "scheduled_orders": scheduled_orders,
    }
    return render(request, "core/dashboard.html", context)


def about(request):
    return render(request, "core/about.html", {
        "title": "Про проєкт",
        "text": "Мій проєкт - система управління Beauty Clinic на Django.",
    })
