from rest_framework import serializers
from apps.users.serializers import UserPublicSerializer
from apps.users.models import User
from .models import Ban


class BanSerializer(serializers.ModelSerializer):
    user      = UserPublicSerializer(read_only=True)
    user_id   = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='user', is_banned=False),
        write_only=True,
        source='user',
    )
    banned_by   = UserPublicSerializer(read_only=True)
    unbanned_by = UserPublicSerializer(read_only=True)

    class Meta:
        model  = Ban
        fields = [
            'id', 'user', 'user_id', 'banned_by', 'unbanned_by',
            'reason', 'trigger_message',
            'created_at', 'expires_at', 'is_active',
            'unbanned_at',
        ]
        read_only_fields = ['id', 'banned_by', 'unbanned_by', 'created_at', 'is_active', 'unbanned_at']

    def validate_user_id(self, user):
        if Ban.objects.filter(user=user, is_active=True).exists():
            raise serializers.ValidationError('Usuário já está banido.')
        return user
