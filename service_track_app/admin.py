from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, RepairRequest, DealerCompany, RequestHistory, RepairRequestPhoto, RepairRequestVideo, Product


# admin.site.register(CustomUser, UserAdmin)
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Добавляем кастомные поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'dealer_company')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role', 'dealer_company')}),
    )

    # Чтобы поля отображались в списке пользователей
    list_display = ('username', 'email', 'role', 'dealer_company', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'dealer_company')

admin.site.register(RepairRequest)
admin.site.register(DealerCompany)
admin.site.register(RequestHistory)
admin.site.register(RepairRequestPhoto)
admin.site.register(RepairRequestVideo)
admin.site.register(Product)


