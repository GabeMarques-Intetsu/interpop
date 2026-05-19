from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'username', 'full_name', 'role', 'is_banned', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_banned', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Dados',        {'fields': ('username', 'first_name', 'last_name', 'bio', 'avatar')}),
        ('Permissões',   {'fields': ('role', 'is_active', 'is_banned', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas',        {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    readonly_fields = ('date_joined', 'last_login')
