from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('author', 'article', 'is_deleted', 'created_at')
    list_filter   = ('is_deleted',)
    search_fields = ('author__email', 'content')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
