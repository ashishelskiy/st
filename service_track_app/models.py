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
    dealer_company = models.ForeignKey("DealerCompany", on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="users")

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
    relation_type = models.CharField("Тип отношений", max_length=50, blank=True, null=True)
    region = models.CharField("Регион", max_length=100, blank=True, null=True)
    is_active = models.BooleanField("Активен", default=True)

    def __str__(self):
        return self.name


class Package(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Отправлен производителю'),
        ('accepted', 'Принят производителем'),
        ('returned', 'Возвращен дилеру'),
        ('processing', 'В обработке у производителя'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    dealer_company = models.ForeignKey("DealerCompany", on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey("CustomUser", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent', verbose_name="Статус пакета")
    returned_at = models.DateTimeField("Дата возврата", null=True, blank=True)
    return_reason = models.TextField("Причина возврата", blank=True, null=True)

    def __str__(self):
        return f"Пакет #{self.id} — {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def request_count(self):
        return self.requests.count()


phone_validator = RegexValidator(
    regex=r'^\+?\d{1,4}?[-\s]?\(?\d{1,3}?\)?[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9}$',
    message="Телефон должен быть в формате +7 (999) 123-45-67"
)


class Product(models.Model):
    PRODUCT_CATEGORIES = [
        ('subwoofer', 'Сабвуфер'),
        ('amplifier', 'Усилитель'),
        ('speaker', 'Динамик'),
        ('component', 'Компонентная акустика'),
        ('coaxial', 'Коаксиальная акустика'),
        ('midrange', 'Мидрейндж'),
        ('tweeter', 'Твитер'),
        ('accessory', 'Аксессуар'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название модели", unique=True)
    brand = models.CharField(max_length=100, verbose_name="Бренд", blank=True, null=True)
    series = models.CharField(max_length=100, verbose_name="Серия", blank=True, null=True)
    category = models.CharField(max_length=50, choices=PRODUCT_CATEGORIES, verbose_name="Категория",
                                default='subwoofer')
    size = models.CharField(max_length=50, verbose_name="Размер", blank=True, null=True)
    power_rms = models.CharField(max_length=50, verbose_name="Мощность RMS", blank=True, null=True)
    power_max = models.CharField(max_length=50, verbose_name="Мощность MAX", blank=True, null=True)
    external_id = models.CharField(max_length=50, verbose_name="Внешний ID", blank=True, null=True)
    external_url = models.URLField(verbose_name="Ссылка на товар", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['brand', 'name']

    def __str__(self):
        if self.brand:
            return f"{self.brand} {self.name}"
        return self.name

    def display_name(self):
        parts = []
        if self.brand:
            parts.append(self.brand)
        parts.append(self.name)
        if self.size:
            parts.append(f"({self.size})")
        if self.power_rms:
            parts.append(f"{self.power_rms} RMS")
        return " ".join(parts)


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
        default='accepted_by_dealer'
    )

    WARRANTY_CHOICES = [
        ('warranty', 'На гарантию'),
        ('paid_repair', 'На платный ремонт'),
        ('diagnostics', 'На диагностику/ремонт'),
    ]

    serial_number = models.CharField("Серийный номер товара", max_length=50)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Товар",
        related_name='repair_requests'
    )
    purchase_date = models.DateField("Дата покупки")
    warranty_status = models.CharField(
        "Статус гарантии",
        max_length=20,
        choices=WARRANTY_CHOICES
    )
    problem_description = models.TextField("Описание неисправности")
    customer_name = models.CharField("ФИО покупателя", max_length=150, blank=True, null=True)
    customer_phone = PhoneNumberField("Телефон покупателя", blank=True, null=True)
    customer_email = models.EmailField("Email покупателя", blank=True, null=True)
    additional_notes = models.TextField("Дополнительные примечания", blank=True, null=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)
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

    # ========== НАЧАЛО: ДОБАВЛЕННЫЕ ПОЛЯ ДЛЯ ДИАГНОСТИКИ ==========
    diagnosis_date = models.DateField("Дата диагностики", null=True, blank=True)
    completion_date = models.DateField("Дата завершения", null=True, blank=True)
    SERVICE_EMPLOYEE_CHOICES = [
        ('', 'Не выбрано'),
        ('Сервис динамики', 'Сервис динамики'),
        ('Головин Д.О.', 'Головин Д.О.'),
        ('Гуськов В.Г.', 'Гуськов В.Г.'),
        ('Колтырин В.С.', 'Колтырин В.С.'),
        ('Быковский П.В.', 'Быковский П.В.'),
        ('(Студент 1)', '(Студент 1)'),
        ('(Студент 2)', '(Студент 2)'),
    ]

    service_employee = models.CharField(
        "Сотрудник сервиса",
        max_length=200,
        choices=SERVICE_EMPLOYEE_CHOICES,
        blank=True
    )
    # service_employee = models.CharField("Сотрудник сервиса", max_length=200, blank=True)

    CONCLUSION_CHOICES = [
        ('', 'Не выбрано'),
        ('factory_defect', 'Заводской брак'),
        ('no_issue', 'Неисправность не выявлена'),
        ('client_damage', 'Испорчен клиентом'),
        ('warranty_expired', 'Истечение срока гарантии'),
    ]

    conclusion = models.CharField(
        "Заключение",
        max_length=50,
        choices=CONCLUSION_CHOICES,
        blank=True
    )

    DECISION_CHOICES = [
        ('', 'Не выбрано'),
        ('warranty_repair', 'Гарантийный ремонт'),
        ('exchange', 'Обмен на новый'),
        ('return', 'Возврат клиенту без ремонта'),
        ('paid_repair', 'Ремонт за счет клиента'),
        ('hydra_repair', 'Ремонт за счет клиента HYDRA'),
        ('demo_repair', 'Ремонт по договору Demo car'),
    ]

    decision = models.CharField(
        "Принятое решение",
        max_length=50,
        choices=DECISION_CHOICES,
        blank=True
    )

    malfunction_formulation = models.TextField("Формулировка неисправности", blank=True)

    PRICE_TYPE_CHOICES = [
        ('', 'Не выбрано'),
        ('retail', 'Розничная'),
        ('dealer', 'Дилерская'),
    ]

    price_type = models.CharField(
        "Тип цен",
        max_length=20,
        choices=PRICE_TYPE_CHOICES,
        blank=True
    )

    ACT_STATUS_CHOICES = [
        ('in_work', 'В работе'),
        ('waiting_payment', 'Ожидает оплаты'),
        ('completed', 'Завершено'),
    ]

    act_status = models.CharField(
        "Статус акта",
        max_length=50,
        choices=ACT_STATUS_CHOICES,
        blank=True
    )

    REFUSAL_REASON_CHOICES = [
        ('', 'Не выбрано'),
        ('client_refused', 'От платного ремонта отказался'),
        ('no_spare_parts', 'Платный ремонт невозможен в связи с отсутствием запасных частей'),
    ]

    refusal_reason = models.CharField(
        "Причина отказа от ремонта",
        max_length=100,
        choices=REFUSAL_REASON_CHOICES,
        blank=True
    )

    detected_problem = models.TextField("Выявленная неисправность", blank=True)
    repair_date = models.DateField("Дата ремонта", null=True, blank=True)

    REPAIR_TYPE_CHOICES = [
        ('', 'Не выбрано'),
        ('acoustics', 'Акустика'),
        ('amplifier', 'Усилитель'),
    ]

    repair_type = models.CharField(
        "Вид ремонта",
        max_length=50,
        choices=REPAIR_TYPE_CHOICES,
        blank=True
    )

    acoustics_repair_subtype = models.CharField(
        "Тип ремонта акустики",
        max_length=200,
        blank=True,
        choices=[
            ('', 'Не выбрано'),
            ('Замена ВЧ динамика', 'Замена ВЧ динамика'),
            ('Замена динамика', 'Замена динамика'),
            ('Замена динамиков', 'Замена динамиков'),
            ('Замена звуковой катушки', 'Замена звуковой катушки'),
            ('Замена корзины', 'Замена корзины'),
            ('Замена корзины и подвижной части динамика', 'Замена корзины и подвижной части динамика'),
            ('Замена подвижной части динамика', 'Замена подвижной части динамика'),
            ('Замена подвижных частей динамиков', 'Замена подвижных частей динамиков'),
            ('Замена пылезащитного колпака', 'Замена пылезащитного колпака'),
            ('Замена терминала', 'Замена терминала'),
            ('Проклеивание', 'Проклеивание'),
            ('Проклеивание пакета центрирующих шайб', 'Проклеивание пакета центрирующих шайб'),
            ('Проклеивание подвеса', 'Проклеивание подвеса'),
            ('Проклеивание пылезащитного колпака', 'Проклеивание пылезащитного колпака'),
            ('Пропайка контактов', 'Пропайка контактов'),
            ('Устранение дефекта без замены подвижной части', 'Устранение дефекта без замены подвижной части'),
            ('Устранение обрыва звуковой катушки', 'Устранение обрыва звуковой катушки'),
            ('Центровка подвижной части', 'Центровка подвижной части'),
            ('Чистка зазора магнитной системы динамика', 'Чистка зазора магнитной системы динамика'),
        ]
    )

    amplifier_repair_subtype = models.CharField(
        "Тип ремонта усилителя",
        max_length=200,
        blank=True,
        choices=[
            ('', 'Не выбрано'),
            ('Замена вентилятора', 'Замена вентилятора'),
            ('Замена переключателей', 'Замена переключателей'),
            ('Замена регулятора громкости', 'Замена регулятора громкости'),
            ('Замена толкателя кнопки', 'Замена толкателя кнопки'),
            ('Замена тюльпанов ГСА', 'Замена тюльпанов ГСА'),
            ('Компонентный ремонт', 'Компонентный ремонт'),
            ('Питание ОУ', 'Питание ОУ'),
            ('Пропайка ГСА', 'Пропайка ГСА'),
            ('Ремонт выходного каскада', 'Ремонт выходного каскада'),
            ('Ремонт БП', 'Ремонт БП'),
            ('Ремонт БП выходного каскада', 'Ремонт БП выходного каскада'),
            ('Ремонт ОУ', 'Ремонт ОУ'),
            ('Ремонт ПУ', 'Ремонт ПУ'),
            ('Фильтр выходного каскада', 'Фильтр выходного каскада'),
            ('Фильтр питания вентилятора', 'Фильтр питания вентилятора'),
        ]
    )

    # acoustics_repair_subtype = models.CharField("Тип ремонта акустики", max_length=200, blank=True)
    # amplifier_repair_subtype = models.CharField("Тип ремонта усилителя", max_length=200, blank=True)
    repair_performed = models.TextField("Произведенный ремонт", blank=True)
    additional_info = models.TextField("Доп информация", blank=True)
    internal_comment = models.TextField("Внутренний комментарий", blank=True)

    # Поля оплаты
    payment_link = models.URLField("Ссылка на оплату", blank=True)
    labor_cost = models.DecimalField("Стоимость работ", max_digits=10, decimal_places=2, null=True, blank=True)
    parts_cost = models.DecimalField("Запчасти", max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField("Общая стоимость", max_digits=10, decimal_places=2, null=True, blank=True)
    parts_discount = models.IntegerField("% скидки на запчасти", null=True, blank=True)
    paid_by_client = models.DecimalField("Оплачено клиентом", max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField("Дата оплаты", null=True, blank=True)

    # ========== КОНЕЦ: ДОБАВЛЕННЫЕ ПОЛЯ ДЛЯ ДИАГНОСТИКИ ==========

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