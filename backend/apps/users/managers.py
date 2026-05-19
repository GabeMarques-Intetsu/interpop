from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def _create(self, email: str, password: str, **extra) -> 'User':  # type: ignore[name-defined]
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create(email, password, **extra)

    def create_superuser(self, email: str, password: str, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', 'admin')
        if extra['is_staff'] is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra['is_superuser'] is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        return self._create(email, password, **extra)
