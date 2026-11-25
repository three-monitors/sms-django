from datetime import datetime, timedelta
from django.db import models


class Client(models.Model):
    """Пацієнт клініки"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    skin_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("oily", "Жирна"),
            ("dry", "Суха"),
            ("combination", "Комбінована"),
            ("sensitive", "Чутлива"),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Пацієнт"
        verbose_name_plural = "Пацієнти"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PatientProfile(models.Model):
    """Медична карта пацієнта"""
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    allergies = models.TextField(blank=True)
    previous_treatments = models.TextField(blank=True)
    preferred_procedures = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профіль {self.client.name}"


class Service(models.Model):
    """Послуга, яку пропонує клініка"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.FloatField()
    is_active = models.BooleanField(default=True)
    image_path = models.CharField(
        max_length=255, blank=True, help_text="Шлях до фото в static/img, наприклад: service_01.jpg")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration_minutes(self):
        return round(self.duration_hours * 60)

    @property
    def duration_formatted(self):
        total_mins = self.duration_minutes
        hours = total_mins // 60
        mins = total_mins % 60
        if hours and mins:
            return f"{hours} год. {mins} хв."
        elif hours:
            return f"{hours} год."
        return f"{mins} хв."

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.price} ₴)"


class Order(models.Model):
    """Запис на процедуру"""
    STATUS_CHOICES = [
        ("new", "Новий"),
        ("in_progress", "У процесі"),
        ("completed", "Готово"),
        ("cancelled", "Скасовано"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    service = models.ManyToManyField(Service, related_name="orders")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )
    date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-date", "-appointment_time"]

    @property
    def end_time(self):
        """Автоматичний розрахунок часу завершення процедури"""
        if not self.appointment_time:
            return None
        total_minutes = sum(s.duration_minutes for s in self.service.all())
        start_dt = datetime.combine(self.date, self.appointment_time)
        end_dt = start_dt + timedelta(minutes=total_minutes)
        return end_dt.time()

    def __str__(self):
        return f"Замовлення #{self.id} - {self.client.name}"


class Inventory(models.Model):
    """Запчастини / матеріали на складі"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    min_quantity = models.IntegerField(default=5)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запас"
        verbose_name_plural = "Запаси"
        ordering = ["-quantity"]

    def __str__(self):
        return f"{self.name} ({self.quantity} шт.)"

    def is_low_stock(self):
        """Чи низький залишок"""
        return self.quantity < self.min_quantity
