from django.contrib import admin

from .models import ModerationLog, Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active', 'theme')
    search_fields = ('name', 'owner__email', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['approve_shops', 'mark_rejected']

    @admin.action(description='Approve selected shops')
    def approve_shops(self, request, queryset):
        queryset.update(status='ACTIVE', is_active=True, rejection_reason='')

    @admin.action(description='Mark selected shops as rejected')
    def mark_rejected(self, request, queryset):
        queryset.update(status='REJECTED', is_active=False)


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'shop', 'action', 'actor')
    list_filter = ('action',)
    search_fields = ('shop__name', 'note')
    readonly_fields = ('created_at',)
