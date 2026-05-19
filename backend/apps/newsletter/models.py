import uuid
from django.db import models


class NewsletterSubscriber(models.Model):
    email              = models.EmailField(unique=True, db_index=True)
    subscribed_at      = models.DateTimeField(auto_now_add=True)
    is_active          = models.BooleanField(default=True, db_index=True)
    unsubscribe_token  = models.UUIDField(unique=True, default=uuid.uuid4, db_index=True)

    class Meta:
        db_table = 'newsletter_subscribers'
        ordering = ['-subscribed_at']
        indexes  = [models.Index(fields=['email', 'is_active'])]

    def __str__(self):
        return self.email
