# orders/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ExportActionMixin
from .models import Bid, Order


# === Ресурсы ===
class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = (
            'id',
            'title',
            'description',
            'customer__username',
            'customer__email',
            'assigned_executor__username',
            'status',
            'deadline',
            'budget',
            'created_at',
            'updated_at'
        )
        export_order = fields

class BidResource(resources.ModelResource):
    class Meta:
        model = Bid
        fields = (
            'id',
            'order__title',
            'executor__username',
            'executor__email',
            'message',
            'price_proposal',
            'created_at',
            'updated_at'
        )
        export_order = fields


# === Inlines ===
class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    verbose_name = 'Отклик'
    verbose_name_plural = 'Отклики'


# === Админки с поддержкой экспорта ===
@admin.register(Order)
class OrderAdmin(ExportActionMixin, admin.ModelAdmin):  # ← было admin.ModelAdmin
    resource_class = OrderResource
    list_display = ('title', 'customer', 'status', 'assigned_executor', 'created_at')
    list_filter = ('status', 'created_at', 'customer')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [BidInline]


@admin.register(Bid)
class BidAdmin(ExportActionMixin, admin.ModelAdmin):  # ← было admin.ModelAdmin
    resource_class = BidResource
    list_display = ('order', 'executor', 'price_proposal', 'created_at')
    list_filter = ('created_at', 'executor')
    raw_id_fields = ('order', 'executor')