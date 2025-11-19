# filters.py (создайте новый файл)
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta


class PackageStatusFilter(admin.SimpleListFilter):
    title = 'Статус пакета'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('sent', 'Отправленные'),
            ('accepted', 'Принятые'),
            ('returned', 'Возвращенные'),
            ('processing', 'В обработке'),
            ('today', 'Созданные сегодня'),
            ('week', 'Созданные за неделю'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(created_at__date=timezone.now().date())
        elif self.value() == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        elif self.value() in ['sent', 'accepted', 'returned', 'processing']:
            return queryset.filter(status=self.value())
        return queryset


class HasRequestsFilter(admin.SimpleListFilter):
    title = 'Наличие заявок'
    parameter_name = 'has_requests'

    def lookups(self, request, model_admin):
        return (
            ('with_requests', 'С заявками'),
            ('without_requests', 'Без заявок'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'with_requests':
            return queryset.filter(requests__isnull=False).distinct()
        elif self.value() == 'without_requests':
            return queryset.filter(requests__isnull=True)
        return queryset