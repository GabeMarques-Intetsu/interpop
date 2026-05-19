from django.contrib import admin, messages

from apps.newsletter.services import send_article_notification

from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = ('title', 'author', 'category', 'status', 'is_featured', 'view_count', 'published_at')
    list_filter    = ('status', 'is_featured', 'category')
    search_fields  = ('title', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    # Resend action kept as a manual fallback (e.g. SMTP outage at publish
    # time, edit of a recently published post). The default flow auto-notifies
    # via the post_save signal in apps/articles/signals.py.
    actions = ['resend_notification']

    @admin.action(description='Reenviar notificação aos assinantes (manual)')
    def resend_notification(self, request, queryset):
        total_sent = total_failed = skipped = 0
        for article in queryset:
            if article.status != Article.Status.PUBLISHED:
                skipped += 1
                continue
            sent, failed = send_article_notification(article)
            total_sent += sent
            total_failed += failed

        if total_sent:
            self.message_user(request, f'{total_sent} e-mail(s) reenviado(s).', level=messages.SUCCESS)
        if total_failed:
            self.message_user(request, f'{total_failed} falharam (verifique SMTP).', level=messages.WARNING)
        if skipped:
            self.message_user(request, f'{skipped} ignorado(s) (não publicados).', level=messages.INFO)
