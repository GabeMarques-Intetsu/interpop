from rest_framework import serializers
from .models import NewsletterSubscriber


class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()

    def save(self):
        email = self.validated_data['email']
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])
        return subscriber, created


class UnsubscribeSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate_token(self, value):
        try:
            self._subscriber = NewsletterSubscriber.objects.get(unsubscribe_token=value, is_active=True)
        except NewsletterSubscriber.DoesNotExist:
            raise serializers.ValidationError('Token inválido ou já cancelado.')
        return value

    def save(self):
        self._subscriber.is_active = False
        self._subscriber.save(update_fields=['is_active'])
        return self._subscriber
