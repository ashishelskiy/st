from django import forms
from .models import RepairRequest, RepairRequestPhoto, Product
from django.core.exceptions import ValidationError


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = [
            "serial_number",
            "product",
            "purchase_date",
            "warranty_status",
            "problem_description",
            "customer_name",
            "customer_phone",
            "customer_email",
            "additional_notes"
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "problem_description": forms.Textarea(attrs={"class": "form-textarea"}),
            "additional_notes": forms.Textarea(attrs={"class": "form-textarea"}),
            "serial_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "A123456789112345"}),
            "product": forms.Select(attrs={"class": "form-select select2-product"}),
            "customer_name": forms.TextInput(attrs={
                "class": "form-input customer-field hidden-field",
                "placeholder": "ФИО покупателя"
            }),
            "customer_phone": forms.TextInput(attrs={
                "class": "form-input customer-field hidden-field",
                "type": "tel",
                "placeholder": "+7 (999) 123-45-67"
            }),
            "customer_email": forms.EmailInput(attrs={
                "class": "form-input customer-field hidden-field",
                "placeholder": "email@example.com"
            }),
            "warranty_status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'product' in self.fields:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)
            self.fields['product'].label_from_instance = lambda obj: obj.display_name()

        if not self.instance.pk:  # Новая заявка
            for field in ['status', 'dealer_company', 'package', 'created_by', 'sent_at']:
                self.fields.pop(field, None)
        else:  # Редактирование
            self.fields['customer_name'].required = False
            self.fields['customer_phone'].required = False

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if commit and self.cleaned_data.get('photos'):
            for photo in self.cleaned_data['photos']:
                RepairRequestPhoto.objects.create(
                    repair_request=instance,
                    photo=photo
                )
        return instance


class RepairRequestEditForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        # ========== НАЧАЛО: ВСЕ ПОЛЯ ДЛЯ РЕДАКТИРОВАНИЯ ==========
        fields = [
            # Основные поля
            "serial_number", "product", "purchase_date", "warranty_status",
            "status", "problem_description", "additional_notes",

            # Поля диагностики
            "diagnosis_date", "completion_date", "service_employee",
            "conclusion", "decision", "malfunction_formulation",
            "price_type", "act_status",

            # Поля ремонта
            "refusal_reason", "detected_problem", "repair_date",
            "repair_type", "acoustics_repair_subtype", "amplifier_repair_subtype",
            "repair_performed", "additional_info", "internal_comment",

            # Поля оплаты
            "payment_link", "labor_cost", "parts_cost", "total_cost",
            "parts_discount", "paid_by_client", "payment_date",
        ]
        # ========== КОНЕЦ: ВСЕ ПОЛЯ ДЛЯ РЕДАКТИРОВАНИЯ ==========

        widgets = {
            # Основные поля
            "serial_number": forms.TextInput(attrs={"class": "form-input"}),
            "product": forms.Select(attrs={"class": "form-select select2-product"}),
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "warranty_status": forms.Select(attrs={"class": "form-select"}),
            "problem_description": forms.Textarea(attrs={"class": "form-textarea"}),
            "additional_notes": forms.Textarea(attrs={"class": "form-textarea"}),
            "status": forms.Select(attrs={"class": "form-select"}),

            # ========== НАЧАЛО: ВИДЖЕТЫ ДЛЯ НОВЫХ ПОЛЕЙ ==========
            # Диагностика
            "diagnosis_date": forms.DateInput(attrs={"type": "date", "class": "details-input"}),
            "completion_date": forms.DateInput(attrs={"type": "date", "class": "details-input"}),
            "service_employee": forms.TextInput(
                attrs={"class": "details-input", "placeholder": "Введите ФИО сотрудника"}),
            "conclusion": forms.Select(attrs={"class": "details-input"}),
            "decision": forms.Select(attrs={"class": "details-input"}),
            "malfunction_formulation": forms.Textarea(attrs={
                "class": "details-textarea",
                "rows": 3,
                "placeholder": "Подробное описание неисправности для клиента"
            }),
            "price_type": forms.Select(attrs={"class": "details-input"}),
            "act_status": forms.Select(attrs={"class": "details-input"}),

            # Ремонт
            "refusal_reason": forms.Select(attrs={"class": "details-input"}),
            "detected_problem": forms.Textarea(attrs={
                "class": "details-textarea",
                "rows": 3,
                "placeholder": "Опишите выявленную неисправность"
            }),
            "repair_date": forms.DateInput(attrs={"type": "date", "class": "details-input"}),
            "repair_type": forms.Select(attrs={"class": "details-input", "id": "repair_type"}),
            "acoustics_repair_subtype": forms.TextInput(attrs={
                "class": "details-input",
                "placeholder": "Начните вводить тип ремонта..."
            }),
            "amplifier_repair_subtype": forms.TextInput(attrs={
                "class": "details-input",
                "placeholder": "Начните вводить тип ремонта..."
            }),
            "repair_performed": forms.Textarea(attrs={
                "class": "details-textarea",
                "rows": 3,
                "placeholder": "Опишите произведенные работы"
            }),
            "additional_info": forms.Textarea(attrs={
                "class": "details-textarea",
                "rows": 2,
                "placeholder": "Дополнительная информация"
            }),
            "internal_comment": forms.Textarea(attrs={
                "class": "details-textarea",
                "rows": 2,
                "placeholder": "Внутренние комментарии для сотрудников"
            }),

            # Оплата
            "payment_link": forms.URLInput(attrs={
                "class": "details-input",
                "placeholder": "https://..."
            }),
            "labor_cost": forms.NumberInput(attrs={
                "class": "details-input",
                "placeholder": "0.00",
                "step": "0.01"
            }),
            "parts_cost": forms.NumberInput(attrs={
                "class": "details-input",
                "placeholder": "0.00",
                "step": "0.01"
            }),
            "total_cost": forms.NumberInput(attrs={
                "class": "details-input",
                "placeholder": "0.00",
                "step": "0.01",
                "readonly": True
            }),
            "parts_discount": forms.NumberInput(attrs={
                "class": "details-input",
                "placeholder": "0",
                "min": "0",
                "max": "100"
            }),
            "paid_by_client": forms.NumberInput(attrs={
                "class": "details-input",
                "placeholder": "0.00",
                "step": "0.01"
            }),
            "payment_date": forms.DateInput(attrs={"type": "date", "class": "details-input"}),
            # ========== КОНЕЦ: ВИДЖЕТЫ ДЛЯ НОВЫХ ПОЛЕЙ ==========
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['problem_description'].required = False
        self.fields['additional_notes'].required = False

        # Все новые поля необязательные
        for field_name, field in self.fields.items():
            if field_name not in ['serial_number', 'product', 'purchase_date', 'warranty_status', 'status']:
                field.required = False

        if 'product' in self.fields:
            self.fields['product'].queryset = Product.objects.filter(is_active=True)
            self.fields['product'].label_from_instance = lambda obj: obj.display_name()