"""
Custom JWT authentication that reads tokens from httpOnly cookies.
Falls back to the Authorization header for API clients / testing.
"""
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
        cookie_name  = jwt_settings.get('AUTH_COOKIE', 'access_token')
        raw_token    = request.COOKIES.get(cookie_name)

        if raw_token is None:
            # Fall back to standard Authorization header
            return super().authenticate(request)

        try:
            validated = self.get_validated_token(raw_token)
        except InvalidToken:
            return None

        return self.get_user(validated), validated
