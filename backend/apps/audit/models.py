from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Immutable record of every state-changing request."""
    actor         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action        = models.CharField(max_length=120, db_index=True)
    target_repr   = models.CharField(max_length=300, blank=True)
    request_path  = models.CharField(max_length=500)
    request_method = models.CharField(max_length=10)
    response_status = models.PositiveSmallIntegerField()
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user_agent    = models.TextField(blank=True)
    metadata      = models.JSONField(default=dict, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['actor', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['response_status', '-created_at']),
        ]

    def __str__(self):
        return f'[{self.created_at:%Y-%m-%d %H:%M}] {self.action} by {self.actor_id}'
