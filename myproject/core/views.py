from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db import models
from .models import Client, Service, Order, Inventory
from .forms import ClientForm, ServiceForm, OrderForm, InventoryForm
from django.contrib.auth import logout as auth_logout
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClientSerializer, ServiceSerializer, OrderSerializer, InventorySerializer
from django_filters import rest_framework as filters


def home(request):
    """Головна сторінка"""
    low_stock = Inventory.objects.filter(quantity__lt=models.F("min_quantity"))
    recent_orders = Order.objects.all()[:3]

    context = {
        "title": "Beauty Clinic Management",
        "message": "Вітаємо в системі управління салоном краси!",
        "total_clients": Client.objects.count(),
        "total_orders": Order.objects.count(),
        "total_services": Service.objects.count(),
        "recent_orders": recent_orders,
        "low_stock": low_stock,
    }
    return render(request, "core/home.html", context)


def clients_list(request):
    """Список клієнтів"""
    clients = Client.objects.all()

    context = {
        "title": "Клієнти",
        "clients": clients,
    }
    return render(request, "core/clients_list.html", context)


def client_search(request):
    """Пошук клієнта за іменем, телефоном або email"""
    search_term = request.GET.get('client_name', '').strip()
    if search_term:
        clients = Client.objects.filter(
            name__icontains=search_term
        ) | Client.objects.filter(
            phone__icontains=search_term
        ) | Client.objects.filter(
            email__icontains=search_term
        )
    else:
        clients = Client.objects.all()

    context = {
        "title": f"Результати пошуку: {search_term}" if search_term else "Клієнти",
        "clients": clients,
        "search_term": search_term,
    }
    return render(request, "core/clients_list.html", context)


def client_detail(request, client_id):
    """Деталі клієнта"""
    client = get_object_or_404(Client, id=client_id)
    orders = Order.objects.filter(client=client)
    orders_count = orders.count()
    orders_total = sum(order.total_price for order in orders)

    context = {
        "client": client,
        "orders": orders,
        "orders_count": orders_count,
        "orders_total": orders_total,
    }
    return render(request, "core/client_detail.html", context)


def client_orders(request, client_id):
    """Усі замовлення конкретного клієнта"""
    client = get_object_or_404(Client, id=client_id)
    orders = Order.objects.filter(client=client).order_by("-id")

    context = {
        "title": f"Замовлення клієнта: {client.name}",
        "client": client,
        "orders": orders,
    }
    return render(request, "core/client_orders.html", context)


def services_list(request):
    """Список послуг"""
    services = Service.objects.all()

    context = {
        "title": "Послуги",
        "services": services,
    }
    return render(request, "core/services_list.html", context)


def service_detail(request, service_id):
    """Деталі послуги"""
    service = get_object_or_404(Service, id=service_id)

    context = {
        "service": service,
        "duration_minutes": int(service.duration_hours * 60),
    }
    return render(request, "core/service_detail.html", context)


def service_search(request):
    """Пошук послуги за назвою"""
    service_name = request.GET.get('service_name', '').strip()
    if service_name:
        services = Service.objects.filter(name__icontains=service_name)
    else:
        services = Service.objects.all()

    context = {
        "title": f"Результати пошуку: {service_name}" if service_name else "Послуги",
        "services": services,
        "search_term": service_name,
    }
    return render(request, "core/services_list.html", context)


def orders_list(request):
    """Список замовлень з пошуком та фільтрацією за статусом"""
    orders = Order.objects.all().order_by("-date", "-appointment_time", "-id")

    status = request.GET.get("status", "").strip()
    if status:
        orders = orders.filter(status=status)

    search = request.GET.get("search", "").strip()
    if search:
        orders = orders.filter(client__name__icontains=search)

    context = {
        "title": "Замовлення",
        "orders": orders,
        "status": status,
        "search": search,
    }
    return render(request, "core/orders_list.html", context)


def orders_by_status(request, status):
    """Замовлення за статусом"""
    filtered_orders = Order.objects.filter(status=status)

    context = {
        "title": "Замовлення",
        "orders": filtered_orders,
        "status": status,
    }
    return render(request, "core/orders_list.html", context)


def order_detail(request, order_id):
    """Деталі замовлення"""
    order = get_object_or_404(Order, id=order_id)

    context = {
        "title": f"Замовлення #{order_id}",
        "order": order,
    }
    return render(request, "core/order_detail.html", context)


def schedule(request):
    """Графік запису"""
    orders = Order.objects.all().order_by("date", "appointment_time")

    context = {
        "title": "Графік запису",
        "orders": orders,
    }
    return render(request, "core/schedule.html", context)


@login_required
def order_create(request):
    """Створення нового замовлення"""
    form = OrderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        order.save()
        form.save_m2m()  # для many-to-many
        messages.success(request, "✓ Замовлення створене!")
        return redirect("orders_list")

    context = {
        "title": "Нове замовлення",
        "form": form,
    }
    return render(request, "core/order_form.html", context)


@login_required
def order_update(request, order_id):
    """Редагування замовлення"""
    order = get_object_or_404(Order, id=order_id)

    # Перевірка: тільки автор або суперкористувач може редагувати
    if order.created_by != request.user and not request.user.is_superuser:
        return HttpResponse("Доступ заборонено", status=403)

    form = OrderForm(request.POST or None, instance=order)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Замовлення оновлене!")
        return redirect("order_detail", order_id=order.id)

    context = {
        "title": f"Редагувати замовлення #{order.id}",
        "form": form,
        "order": order,
    }
    return render(request, "core/order_form.html", context)


def order_delete(request, order_id):
    """Видалення замовлення"""
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.delete()
        messages.success(request, "✓ Замовлення видалене!")
        return redirect("orders_list")

    context = {
        "title": "Видалення замовлення",
        "order": order,
    }
    return render(request, "core/order_confirm_delete.html", context)


def inventory_list(request):
    """Список інвентарю"""
    inventory = Inventory.objects.all()

    context = {
        "title": "Інвентар",
        "inventory": inventory,
    }
    return render(request, "core/inventory_list.html", context)


def dashboard(request):
    """Дашборд зі статистикою"""
    total_clients = Client.objects.count()
    total_services = Service.objects.count()
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status="completed").count()
    in_progress_orders = Order.objects.filter(status="in_progress").count()
    scheduled_orders = Order.objects.filter(status="new").count()

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


# CREATE - Client
def client_create(request):
    """Створення нового клієнта"""
    form = ClientForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Клієнт створений!")
        return redirect("clients_list")

    context = {
        "title": "Новий клієнт",
        "form": form,
    }
    return render(request, "core/client_form.html", context)


# UPDATE - Client
def client_update(request, client_id):
    """Редагування клієнта"""
    client = get_object_or_404(Client, id=client_id)
    form = ClientForm(request.POST or None, instance=client)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Клієнт оновлений!")
        return redirect("client_detail", client_id=client.id)

    context = {
        "title": f"Редагувати: {client.name}",
        "form": form,
        "client": client,
    }
    return render(request, "core/client_form.html", context)


# DELETE - Client
def client_delete(request, client_id):
    """Видалення клієнта"""
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        client.delete()
        messages.success(request, "✓ Клієнт видалений!")
        return redirect("clients_list")

    context = {
        "title": "Видалення клієнта",
        "client": client,
    }
    return render(request, "core/client_confirm_delete.html", context)


# CREATE - Service
def service_create(request):
    """Створення нової послуги"""
    form = ServiceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Послуга створена!")
        return redirect("services_list")

    context = {
        "title": "Нова послуга",
        "form": form,
    }
    return render(request, "core/service_form.html", context)


# UPDATE - Service
def service_update(request, service_id):
    """Редагування послуги"""
    service = get_object_or_404(Service, id=service_id)
    form = ServiceForm(request.POST or None, instance=service)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Послуга оновлена!")
        return redirect("service_detail", service_id=service.id)

    context = {
        "title": f"Редагувати: {service.name}",
        "form": form,
        "service": service,
    }
    return render(request, "core/service_form.html", context)


# DELETE - Service
def service_delete(request, service_id):
    """Видалення послуги"""
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        service.delete()
        messages.success(request, "✓ Послуга видалена!")
        return redirect("services_list")

    context = {
        "title": "Видалення послуги",
        "service": service,
    }
    return render(request, "core/service_confirm_delete.html", context)


# CREATE - Inventory
def inventory_create(request):
    """Створення нового товару"""
    form = InventoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Товар створений!")
        return redirect("inventory_list")

    context = {
        "title": "Новий товар",
        "form": form,
    }
    return render(request, "core/inventory_form.html", context)


# UPDATE - Inventory
def inventory_update(request, inventory_id):
    """Редагування товару"""
    inventory = get_object_or_404(Inventory, id=inventory_id)
    form = InventoryForm(request.POST or None, instance=inventory)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "✓ Товар оновлений!")
        return redirect("inventory_list")

    context = {
        "title": f"Редагувати: {inventory.name}",
        "form": form,
        "inventory": inventory,
    }
    return render(request, "core/inventory_form.html", context)


# DELETE - Inventory
def inventory_delete(request, inventory_id):
    """Видалення товару"""
    inventory = get_object_or_404(Inventory, id=inventory_id)

    if request.method == "POST":
        inventory.delete()
        messages.success(request, "✓ Товар видалений!")
        return redirect("inventory_list")

    context = {
        "title": "Видалення товару",
        "inventory": inventory,
    }
    return render(request, "core/inventory_confirm_delete.html", context)


def register(request):
    """Реєстрація користувача"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            user = authenticate(username=username,
                                password=form.cleaned_data.get("password1"))
            login(request, user)
            messages.success(request, "✓ Реєстрація успішна!")
            return redirect("home")
    else:
        form = UserCreationForm()

    context = {
        "title": "Реєстрація",
        "form": form,
    }
    return render(request, "registration/register.html", context)


@login_required
def profile(request):
    """Профіль користувача"""
    context = {
        "title": "Профіль",
        "user": request.user,
    }
    return render(request, "registration/profile.html", context)


@login_required
def my_orders(request):
    """Мої замовлення"""
    orders = Order.objects.filter(created_by=request.user).order_by(
        "-date", "-appointment_time")

    context = {
        "title": "Мої замовлення",
        "orders": orders,
    }
    return render(request, "registration/my_orders.html", context)


def logout_view(request):
    """Вихід із системи"""
    if request.method == "POST":
        auth_logout(request)
        return redirect("home")
    return render(request, "registration/logout_confirm.html")


class OrderListAPI(APIView):
    """API для списку замовлень"""
    serializer_class = OrderSerializer

    def get(self, request):
        """Отримати всі замовлення"""
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Створити нове замовлення"""
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatisticsAPI(APIView):
    """API для статистики"""

    def get(self, request):
        """Отримати статистику"""
        from .models import Client, Service, Inventory

        data = {
            "clients": Client.objects.count(),
            "services": Service.objects.count(),
            "orders": Order.objects.count(),
            "inventory": Inventory.objects.count(),
        }
        return Response(data)


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet для клієнтів"""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet для послуг"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    """ViewSet для інвентарю"""
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer


class OrderFilter(filters.FilterSet):
    """Фільтр для замовлень"""
    status = filters.CharFilter(field_name='status')
    date = filters.DateFilter(field_name='date')
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'date']


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для замовлень"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_class = OrderFilter

    def get_queryset(self):
        """Фільтрація за статусом"""
        queryset = Order.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        """Автоматично зберігає автора"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Власний endpoint: завершити замовлення"""
        order = self.get_object()
        order.status = 'completed'
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
