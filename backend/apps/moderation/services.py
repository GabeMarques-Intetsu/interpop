"""Ban / unban business logic, isolated from views."""
from django.utils import timezone
from apps.users.models import User
from .models import Ban


def ban_user(target: User, admin: User, reason: str, trigger_message: str = '') -> Ban:
    ban = Ban.objects.create(
        user=target,
        banned_by=admin,
        reason=reason,
        trigger_message=trigger_message,
    )
    User.objects.filter(pk=target.pk).update(is_banned=True)
    return ban


def unban_user(ban: Ban, admin: User) -> Ban:
    ban.is_active   = False
    ban.unbanned_by = admin
    ban.unbanned_at = timezone.now()
    ban.save(update_fields=['is_active', 'unbanned_by', 'unbanned_at'])
    User.objects.filter(pk=ban.user_id).update(is_banned=False)
    return ban
