from django import forms
from .models import RepairRequest, RepairRequestPhoto
from django.core.exceptions import ValidationError


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        # fields = [
        #     "serial_number", "model_name", "purchase_date", "warranty_status",
        #     "problem_description", "customer_name", "customer_phone",
        #     "customer_email", "dealer_name", "dealer_city", "additional_notes"
        # ]
        fields = '__all__'
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "problem_description": forms.Textarea(attrs={"class": "form-textarea"}),
            "additional_notes": forms.Textarea(attrs={"class": "form-textarea"}),
            "serial_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "SN123456789"}),
            "model_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Apocalypse AP-M81SE"}),
            "customer_name": forms.TextInput(attrs={"class": "form-input"}),
            "customer_phone": forms.TextInput(attrs={"class": "form-input", "type": "tel", "placeholder": "+7 (999) 123-45-67"}),
            "customer_email": forms.EmailInput(attrs={"class": "form-input"}),
            "dealer_name": forms.TextInput(attrs={"class": "form-input"}),
            "dealer_city": forms.TextInput(attrs={"class": "form-input"}),
            "warranty_status": forms.Select(attrs={"class": "form-select"}),
        }
    # additional_notes = forms.CharField(
    #     label="Дополнительные примечания",
    #     widget=forms.Textarea(attrs={"class": "form-textarea", "placeholder": "Любая дополнительная информация..."}),
    # )

    # Явно указываем обязательность поля в самой форме
    # customer_name = forms.CharField(required=False)  # Обязательное для формы
    # customer_phone = forms.CharField(required=False)  # Обязательное для формы
    # dealer_name = forms.CharField(required=False)  # Обязательное для формы
    # dealer_city = forms.CharField(required=False)  # Обязательное для формы
    def save(self, commit=True):
        instance = super().save(commit=commit)

        # Сохраняем фотографии после сохранения основной модели
        if commit and self.cleaned_data.get('photos'):
            for photo in self.cleaned_data['photos']:
                RepairRequestPhoto.objects.create(
                    repair_request=instance,
                    photo=photo
                )
        return instance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Выводим все методы родительского класса через super()
        print("Методы и атрибуты родительского класса:")
        print(dir(super(RepairRequestForm, self)))

        # Проверяем, есть ли объект заявки (редактирование)
        if not self.instance.pk:  # Если объекта нет (новая заявка)
            self.fields['customer_name'].required = True
            self.fields['customer_phone'].required = True
            # self.fields['dealer_name'].required = True
            # self.fields['dealer_city'].required = True
            for field in ['status', 'dealer_company', 'package', 'created_by', 'sent_at']:
                self.fields.pop(field, None)
        else:  # Если объект существует (редактирование)
            self.fields['customer_name'].required = False
            self.fields['customer_phone'].required = False
            # self.fields['dealer_name'].required = False
            # self.fields['dealer_city'].required = False


class RepairRequestEditForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        # Список полей, которые можно редактировать
        fields = [
            "serial_number",
            "model_name",
            "purchase_date",
            "warranty_status",
            "status",
            "problem_description",
            "additional_notes"
        ]
        widgets = {
            "serial_number": forms.TextInput(attrs={"class": "form-input"}),
            "model_name": forms.TextInput(attrs={"class": "form-input"}),
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "warranty_status": forms.Select(attrs={"class": "form-select"}),
            "problem_description": forms.Textarea(attrs={"class": "form-textarea"}),
            "additional_notes": forms.Textarea(attrs={"class": "form-textarea"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Все поля уже обязательны по умолчанию; при желании можно настроить required
        self.fields['problem_description'].required = False
        self.fields['additional_notes'].required = False
