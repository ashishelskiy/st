from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('dealer', 'Дилер'),
        ('service_center', 'Сервисный центр'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='dealer')

    # def __str__(self):
    #     return f"{self.username} ({self.get_role_display()})"
    # если пользователь принадлежит компании
    dealer_company = models.ForeignKey("DealerCompany", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    def __str__(self):
        if self.role == "dealer" and self.dealer_company:
            return f"{self.username} ({self.get_role_display()} - {self.dealer_company.name})"
        return f"{self.username} ({self.get_role_display()})"


class DealerCompany(models.Model):
    code = models.CharField("Код", max_length=50, unique=True)
    name = models.CharField("Наименование", max_length=255)
    inn = models.CharField("ИНН", max_length=20, blank=True, null=True)
    full_name = models.CharField("Полное наименование", max_length=255, blank=True, null=True)
    document = models.CharField("Документ, удостоверяющий личность", max_length=255, blank=True, null=True)
    relation_type = models.CharField("Тип отношений", max_length=50, blank=True, null=True)  # Покупатель / Поставщик
    region = models.CharField("Регион", max_length=100, blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)

    def __str__(self):
        return self.name


class Package(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # дата и время создания пакета
    dealer_company = models.ForeignKey("DealerCompany", on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Пакет #{self.id} — {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def request_count(self):
        # 'requests' — это related_name из RepairRequest.package
        return self.requests.count()


phone_validator = RegexValidator(
    regex=r'^\+?\d{1,4}?[-\s]?\(?\d{1,3}?\)?[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9}$',
    message="Телефон должен быть в формате +7 (999) 123-45-67"
)

class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('accepted_by_dealer', 'Товар принят дилером'),
        ('waiting', 'Ожидает'),
        ('sent_to_service', 'Отправлено в сервисный центр'),
        ('closed', 'Закрыта'),
        ('rejected', 'Отклонена'),
    ]

    status = models.CharField(
        "Статус заявки",
        max_length=20,
        choices=STATUS_CHOICES,
        default='accepted_by_dealer'  # Это значение будет присвоено по умолчанию
    )

    WARRANTY_CHOICES = [
        ('warranty', 'На гарантию'),
        ('paid_repair', 'На платный ремонт'),
        # ('expired', 'Гарантия истекла'),
        ('unknown', 'Неизвестно'),
    ]

    serial_number = models.CharField("Серийный номер товара", max_length=50)
    model_name = models.CharField("Модель товара", max_length=100)
    purchase_date = models.DateField("Дата покупки")
    warranty_status = models.CharField(
        "Статус гарантии",
        max_length=20,
        choices=WARRANTY_CHOICES
    )
    problem_description = models.TextField("Описание неисправности")

    customer_name = models.CharField("ФИО покупателя", max_length=150)
    # customer_phone = models.CharField("Телефон", max_length=30)
    customer_phone = PhoneNumberField("Телефон покупателя", blank=False)
    customer_email = models.EmailField("Email покупателя", blank=True, null=True)

    # dealer_name = models.CharField("Название дилера", max_length=150)
    # dealer_city = models.CharField("Город", max_length=100)

    additional_notes = models.TextField("Дополнительные примечания", blank=True, null=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    # 🔑 Новая связь
    dealer_company = models.ForeignKey(
        "DealerCompany",
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="Компания дилера",
        null=True, blank=True
    )

    created_by = models.ForeignKey(
        "CustomUser",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="created_requests",
        verbose_name="Создана пользователем"
    )
    sent_at = models.DateTimeField("Дата отправки", null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True, related_name="requests")

    def __str__(self):
        return f"Заявка #{self.id} — {self.serial_number}"


class RepairRequestPhoto(models.Model):
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField("Фото товара", upload_to='repair_photos/')

    def __str__(self):
        return f"Фото для {self.repair_request.serial_number}"


class RepairRequestVideo(models.Model):
    repair_request = models.ForeignKey(RepairRequest, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(
        "Видео товара",
        upload_to='repair_videos/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'wmv']),
        ]
    )

    def __str__(self):
        return f"Видео для {self.repair_request.serial_number}"


class RequestHistory(models.Model):
    STATUS_CHOICES = [
        ('accepted_by_dealer', 'Товар принят дилером'),
        ('waiting', 'Ожидает'),
        ('sent_to_service', 'Отправлено в сервисный центр'),
        ('closed', 'Закрыта'),
        ('rejected', 'Отклонена'),
    ]

    repair_request = models.ForeignKey('RepairRequest', on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"История заявки #{self.repair_request.id} — {self.new_status} ({self.changed_at})"

# class SendPackage(models.Model):
#     sent_at = models.DateTimeField(auto_now_add=True)
#     comment = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return f"Пакет {self.id} от {self.sent_at.strftime('%d.%m.%Y %H:%M')}"
