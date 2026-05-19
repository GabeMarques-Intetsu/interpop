from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('created_at', 'actor', 'action', 'response_status', 'ip_address')
    list_filter   = ('request_method', 'response_status')
    search_fields = ('actor__email', 'action', 'request_path', 'ip_address')
    readonly_fields = [f.name for f in AuditLog._meta.get_fields()]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
