# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import UserProfile


# === Ресурс для экспорта профилей ===
class UserProfileResource(resources.ModelResource):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user__username',
            'user__email',
            'user__first_name',
            'user__last_name',
            'role',
            'specialization',
            'rating',
            'portfolio',
            'created_at',
            'updated_at'
        )
        export_order = fields


# === Inline для отображения в User ===
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = "Профиль пользователя"
    verbose_name_plural = "Профили пользователей"


# === Кастомный UserAdmin (без изменений) ===
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = UserAdmin.list_display + ('get_role', 'get_specialization', 'get_portfolio')

    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile:
            return profile.get_role_display()
        return '-'
    get_role.short_description = 'Роль'

    def get_specialization(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.specialization if profile else '-'
    get_specialization.short_description = 'Специализация'

    def get_portfolio(self, obj):
        profile = getattr(obj, 'profile', None)
        return (profile.portfolio[:50] if profile and profile.portfolio else '-') if profile else '-'
    get_portfolio.short_description = 'Портфолио'


# === Регистрация ===
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

from import_export.admin import ExportActionMixin
# Дополнительно регистрируем UserProfile отдельно — для экспорта!
@admin.register(UserProfile)
class UserProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_class = UserProfileResource
    list_display = ('user', 'role', 'specialization', 'rating')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')