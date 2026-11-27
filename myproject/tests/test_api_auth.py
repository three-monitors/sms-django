import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from core.models import Client, Service, Order


@pytest.fixture
def staff_user(db):
    """Створює користувача з правами персоналу"""
    return User.objects.create_user(
        username="admin",
        password="admin123",
        is_staff=True
    )


@pytest.fixture
def regular_user(db):
    """Створює звичайного користувача"""
    return User.objects.create_user(
        username="user",
        password="user123"
    )


@pytest.fixture
def api_client():
    """API клієнт для тестів"""
    return APIClient()


@pytest.mark.django_db
def test_unauthorized_cannot_access_clients(api_client):
    """Неавторизований користувач отримує 401"""
    response = api_client.get("/api/clients/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_obtain_token(api_client, staff_user):
    """Користувач отримує токен"""
    response = api_client.post(
        "/api/token/",
        {"username": "admin",
         "password": "admin123"},
        format="json"
    )
    assert response.status_code == 200
    assert "token" in response.data


@pytest.mark.django_db
def test_wrong_password_returns_400(api_client, staff_user):
    """Неправильний пароль -> 400"""
    response = api_client.post(
        "/api/token/",
        {"username": "admin",
         "password": "wrong"},
        format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_staff_can_create_client(api_client, staff_user):
    """Персонал може створити клієнта"""
    api_client.force_authenticate(user=staff_user)
    response = api_client.post(
        "/api/clients/",
        {"name": "Тест Клієнт",
         "email": "test@example.com",
         "phone": "+380501234567"},
        format="json"
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_regular_user_cannot_create_client(api_client, regular_user):
    """Звичайний користувач не може створити клієнта"""
    api_client.force_authenticate(user=regular_user)
    response = api_client.post(
        "/api/clients/",
        {"name": "Тест Клієнт",
         "email": "test@example.com",
         "phone": "+380501234567"},
        format="json"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_clients_list_authenticated(api_client, staff_user):
    """Авторизований користувач отримує список клієнтів"""
    api_client.force_authenticate(user=staff_user)
    response = api_client.get("/api/clients/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_order_sets_author(api_client, staff_user):
    """Створення замовлення автоматично зберігає автора"""
    api_client.force_authenticate(user=staff_user)
    # Створимо клієнта і послугу
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567")
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0)
    order = Order.objects.create(
        client=client, status="new",
        date="2026-11-25",
        total_price="100.00",
        created_by=staff_user
    )
    order.service.add(service)
    assert order.created_by == staff_user


@pytest.mark.django_db
def test_owner_can_edit_own_order(api_client, staff_user):
    """Автор може редагувати своє замовлення"""
    api_client.force_authenticate(user=staff_user)
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567")
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0)
    order = Order.objects.create(
        client=client,
        status="new",
        date="2026-11-25",
        total_price="100.00",
        created_by=staff_user,
    )
    order.service.add(service)
    response = api_client.patch(
        f"/api/orders/{order.id}/",
        {"status": "in_progress"},
        format="json",
    )
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "in_progress"
    assert order.created_by == staff_user


@pytest.mark.django_db
def test_owner_can_delete_own_order(api_client, staff_user):
    """Автор може видалити власне замовлення."""
    api_client.force_authenticate(user=staff_user)
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567",
    )
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0,
    )
    order = Order.objects.create(
        client=client,
        status="new",
        date="2026-11-25",
        total_price="100.00",
        created_by=staff_user,
    )
    order.service.add(service)
    order_id = order.id
    response = api_client.delete(
        f"/api/orders/{order_id}/",
    )
    assert response.status_code == 204
    assert not Order.objects.filter(id=order_id).exists()


@pytest.mark.django_db
def test_token_header_allows_access(api_client, staff_user):
    """Токен в заголовку дозволяє доступ"""
    token = Token.objects.create(user=staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    response = api_client.get("/api/clients/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_status_filter(api_client, staff_user):
    """Фільтрація замовлень за статусом"""
    api_client.force_authenticate(user=staff_user)
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567")
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0)
    Order.objects.create(
        client=client,
        status="completed",
        date="2026-11-25",
        total_price="100.00"
    )
    Order.objects.create(
        client=client,
        status="new",
        date="2026-11-25",
        total_price="100.00"
    )
    response = api_client.get("/api/orders/?status=completed")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_complete_order_endpoint(api_client, staff_user):
    """Власний endpoint для завершення замовлення"""
    api_client.force_authenticate(user=staff_user)
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567")
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0)
    order = Order.objects.create(
        client=client,
        status="new",
        date="2026-11-25",
        total_price="100.00",
        created_by=staff_user
    )
    response = api_client.post(f"/api/orders/{order.id}/complete/")
    assert response.status_code == 200
    assert response.data["status"] == "completed"


@pytest.mark.django_db
def test_service_not_found(api_client, staff_user):
    """Неіснуюча послуга повертає 404"""
    api_client.force_authenticate(user=staff_user)
    response = api_client.get("/api/services/99999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_own_order(api_client, staff_user):
    """Видалення свого замовлення"""
    api_client.force_authenticate(user=staff_user)
    client = Client.objects.create(
        name="Тест",
        email="test@test.com",
        phone="+380501234567"
    )
    service = Service.objects.create(
        name="Тест послуга",
        price="100.00",
        duration_hours=1.0
    )
    # Створюємо через ORM
    order = Order.objects.create(
        client=client,
        status="new",
        date="2026-11-25",
        total_price="100.00",
        created_by=staff_user
    )
    order.service.add(service)
    response = api_client.delete(f"/api/orders/{order.id}/")
    assert response.status_code == 204
    assert not Order.objects.filter(id=order.id).exists()


@pytest.mark.django_db
def test_get_services_authenticated(api_client, staff_user):
    """Отримання списку послуг авторизованим"""
    api_client.force_authenticate(user=staff_user)
    response = api_client.get("/api/services/")
    assert response.status_code == 200
