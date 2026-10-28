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
        "status": "Виконано", "total_price": 600},
    {"id": 2, "client_id": 2, "service_id": 2,
        "status": "У процесі", "total_price": 400},
    {"id": 3, "client_id": 3, "service_id": 3,
        "status": "Виконано", "total_price": 600},
]


def home(request):
    """Головна сторінка"""
    context = {
        "title": "Beauty Clinic Management",
        "message": "Вітаємо в системі управління салоном краси!",
    }
    return render(request, "core/base.html", context)


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
        return HttpResponse("Клієнт не знайден", status=404)

    # Знайти замовлення клієнта
    client_orders = [o for o in ORDERS if o["client_id"] == client_id]

    context = {
        "client": client,
        "orders": client_orders,
    }
    return render(request, "core/client_detail.html", context)


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


def orders_list(request):
    """Список замовлень"""
    context = {
        "title": "Замовлення",
        "orders": ORDERS,
    }
    return render(request, "core/orders_list.html", context)


def order_detail(request, order_id):
    """Деталі замовлення"""
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if order is None:
        return HttpResponse("Замовлення не знайдено", status=404)

    context = {"order": order}
    return render(request, "core/order_detail.html", context)


def about(request):
    return render(request, "core/base.html", {
        "title": "Про проєкт",
        "text": "Мій проєкт — система управління Beauty Clinic на Django.",
    })
