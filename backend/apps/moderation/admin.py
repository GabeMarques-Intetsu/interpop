from django.contrib import admin
from .models import Ban

@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display  = ('user', 'banned_by', 'is_active', 'created_at', 'expires_at')
    list_filter   = ('is_active',)
    search_fields = ('user__email', 'reason')
    readonly_fields = ('created_at', 'unbanned_at')
