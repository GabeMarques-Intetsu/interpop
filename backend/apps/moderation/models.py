import uuid
from django.conf import settings
from django.db import models


class Ban(models.Model):
    """
    One active ban per user.
    - reason:          admin's textual explanation (always required).
    - trigger_message: copy of the specific content (comment/post) that led to
                       the ban — optional, shown highlighted in the admin UI.
    """
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user     = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ban',
    )
    banned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bans_issued',
    )

    reason          = models.TextField(help_text='Motivo formal do banimento.')
    trigger_message = models.TextField(
        blank=True,
        help_text='Mensagem/conteúdo específico que originou o banimento (exibido em destaque).',
    )

    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField(null=True, blank=True, help_text='Null = permanente.')
    is_active   = models.BooleanField(default=True, db_index=True)

    unbanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bans_reversed',
    )
    unbanned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bans'
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['is_active', '-created_at'])]

    def __str__(self):
        return f'Ban({self.user_id})'
