from datetime import time
from django import forms
from .models import Client, Service, Order, Inventory


class ClientForm(forms.ModelForm):
    """Форма для створення та редагування клієнта"""

    class Meta:
        model = Client
        fields = ["name", "email", "phone", "date_of_birth", "skin_type"]
        labels = {
            "name": "ПІБ клієнта",
            "email": "Електронна пошта (Email)",
            "phone": "Номер телефону",
            "date_of_birth": "Дата народження",
            "skin_type": "Тип шкіри",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "ПІБ клієнта",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "email@example.com",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+380XXXXXXXXX",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "skin_type": forms.Select(attrs={
                "class": "form-control",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 3:
            raise forms.ValidationError(
                "Ім'я повинно містити щонайменше 3 символи"
            )
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10 or len(digits) > 12:
            raise forms.ValidationError(
                "Введіть коректний номер телефону (10–12 цифр)")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        for domain in (".ru", ".su", ".рф"):
            if email.endswith(domain):
                raise forms.ValidationError(
                    f"Використання email з доменом {domain} заборонено")
        return email

    def clean_date_of_birth(self):
        from datetime import date
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > date.today():
            raise forms.ValidationError(
                "Дата народження не може бути в майбутньому")
        return dob


class ServiceForm(forms.ModelForm):
    """Форма для створення та редагування послуги"""
    duration = forms.TimeField(
        label="Тривалість (год.:хв.:сек.)",
        input_formats=["%H:%M:%S", "%H:%M"],
        widget=forms.TimeInput(
            format="%H:%M:%S",
            attrs={
                "class": "form-control",
                "type": "time",
                "step": "1",
            },
        ),
    )

    class Meta:
        model = Service
        fields = ["name", "description", "price",
                  "duration", "is_active", "image_path"]
        labels = {
            "name": "Назва послуги",
            "description": "Опис послуги",
            "price": "Ціна, грн.",
            "is_active": "Активна послуга",
            "image_path": "Шлях до файлу, наприклад service_01.jpg"
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Назва послуги",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Опис послуги",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "image_path": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "service_01.png",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.duration_hours is not None:
            total_mins = round(self.instance.duration_hours * 60)
            hours = total_mins // 60
            minutes = total_mins % 60
            self.fields["duration"].initial = time(
                hour=hours, minute=minutes, second=0)
        else:
            self.fields["duration"].initial = time(hour=0, minute=30, second=0)

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")
        if duration and duration.hour == 0 and duration.minute == 0 and duration.second == 0:
            raise forms.ValidationError(
                "Тривалість повинна бути більшою за 00:00:00.")
        return duration

    def save(self, commit=True):
        instance = super().save(commit=False)
        duration = self.cleaned_data.get("duration")
        if duration:
            instance.duration_hours = duration.hour + \
                (duration.minute / 60.0) + (duration.second / 3600.0)
        if commit:
            instance.save()
        return instance

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price <= 0:
            raise forms.ValidationError("Ціна повинна бути більше 0")
        return price


class OrderForm(forms.ModelForm):
    """Форма для створення та редагування замовлення"""

    class Meta:
        model = Order
        fields = ["client", "service", "status",
                  "date", "appointment_time", "description", "total_price"]
        labels = {
            "client": "Клієнт",
            "service": "Послуга",
            "status": "Статус",
            "date": "Дата процедури",
            "appointment_time": "Час початку",
            "description": "Примітки",
            "total_price": "Загальна ціна, грн",
        }
        widgets = {
            "client": forms.Select(attrs={
                "class": "form-control",
            }),
            "service": forms.CheckboxSelectMultiple(attrs={
                "class": "form-control",
            }),
            "status": forms.Select(attrs={
                "class": "form-control",
            }),
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "appointment_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
            ),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "total_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
            }),
        }

    def clean_total_price(self):
        price = self.cleaned_data.get("total_price")
        if price is not None and price < 0:
            raise forms.ValidationError("Ціна не може бути від'ємною")
        return price

    def clean_date(self):
        from datetime import date
        order_date = self.cleaned_data.get("date")
        if not self.instance.pk and order_date and order_date < date.today():
            raise forms.ValidationError("Дата запису не може бути в минулому")
        return order_date


class InventoryForm(forms.ModelForm):
    """Форма для створення та редагування інвентарю"""

    class Meta:
        model = Inventory
        fields = ["name", "description", "quantity",
                  "min_quantity", "price_per_unit", "category"]
        labels = {
            "name": "Назва матеріалу / товару",
            "description": "Опис",
            "quantity": "Кількість на складі",
            "min_quantity": "Мінімальний залишок",
            "price_per_unit": "Ціна за одиницю, грн.",
            "category": "Категорія",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Назва товару",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Опис",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "10",
            }),
            "min_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "5",
            }),
            "price_per_unit": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "0.00",
                "step": "0.01",
            }),
            "category": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Категорія",
            }),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity and quantity < 0:
            raise forms.ValidationError(
                "Кількість не може бути від'ємною"
            )
        return quantity
