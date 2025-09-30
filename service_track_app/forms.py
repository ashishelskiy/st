from django import forms
from .models import RepairRequest


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = [
            "serial_number", "model_name", "purchase_date", "warranty_status",
            "problem_description", "customer_name", "customer_phone",
            "customer_email", "dealer_name", "dealer_city", "additional_notes"
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "problem_description": forms.Textarea(attrs={"class": "form-textarea"}),
            "additional_notes": forms.Textarea(attrs={"class": "form-textarea"}),
            "serial_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "SN123456789"}),
            "model_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Apocalypse AP-M81SE"}),
            "customer_name": forms.TextInput(attrs={"class": "form-input"}),
            "customer_phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+7 (999) 123-45-67"}),
            "customer_email": forms.EmailInput(attrs={"class": "form-input"}),
            "dealer_name": forms.TextInput(attrs={"class": "form-input"}),
            "dealer_city": forms.TextInput(attrs={"class": "form-input"}),
            "warranty_status": forms.Select(attrs={"class": "form-select"}),
        }

    # Явно указываем обязательность поля в самой форме
    # customer_name = forms.CharField(required=False)  # Обязательное для формы
    # customer_phone = forms.CharField(required=False)  # Обязательное для формы
    # dealer_name = forms.CharField(required=False)  # Обязательное для формы
    # dealer_city = forms.CharField(required=False)  # Обязательное для формы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Выводим все методы родительского класса через super()
        print("Методы и атрибуты родительского класса:")
        print(dir(super(RepairRequestForm, self)))

        # Проверяем, есть ли объект заявки (редактирование)
        if not self.instance.pk:  # Если объекта нет (новая заявка)
            self.fields['customer_name'].required = True
            self.fields['customer_phone'].required = True
            self.fields['dealer_name'].required = True
            self.fields['dealer_city'].required = True
        else:  # Если объект существует (редактирование)
            self.fields['customer_name'].required = False
            self.fields['customer_phone'].required = False
            self.fields['dealer_name'].required = False
            self.fields['dealer_city'].required = False
