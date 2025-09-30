from django.db import models


class RepairRequest(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В обработке'),
        ('closed', 'Закрыта'),
        ('rejected', 'Отклонена'),
        ('waiting', 'Ожидает'),
    ]

    status = models.CharField(
        "Статус заявки",
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'  # Это значение будет присвоено по умолчанию
    )

    WARRANTY_CHOICES = [
        ('warranty', 'На гарантии'),
        ('expired', 'Гарантия истекла'),
        ('unknown', 'Неизвестно'),
    ]

    serial_number = models.CharField("Серийный номер", max_length=50)
    model_name = models.CharField("Модель товара", max_length=100)
    purchase_date = models.DateField("Дата покупки")
    warranty_status = models.CharField(
        "Статус гарантии",
        max_length=20,
        choices=WARRANTY_CHOICES
    )
    problem_description = models.TextField("Описание неисправности")

    customer_name = models.CharField("ФИО покупателя", max_length=150)
    customer_phone = models.CharField("Телефон", max_length=30)
    customer_email = models.EmailField("Email", blank=True, null=True)

    dealer_name = models.CharField("Название дилера", max_length=150)
    dealer_city = models.CharField("Город", max_length=100)

    additional_notes = models.TextField("Дополнительно", blank=True, null=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    def __str__(self):
        return f"Заявка #{self.id} — {self.serial_number}"
