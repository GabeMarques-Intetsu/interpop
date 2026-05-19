"""
Business logic for authentication.
Views stay thin; all token/cookie manipulation lives here.
"""
from datetime import timedelta

from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


def _jwt_settings():
    return getattr(settings, 'SIMPLE_JWT', {})


def _set_auth_cookies(response: Response, refresh: RefreshToken) -> None:
    s   = _jwt_settings()
    access_str  = str(refresh.access_token)
    refresh_str = str(refresh)

    access_max_age: int = int(
        s.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=15)).total_seconds()
    )
    refresh_max_age: int = int(
        s.get('REFRESH_TOKEN_LIFETIME', timedelta(days=7)).total_seconds()
    )

    cookie_kwargs = dict(
        httponly=s.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=s.get('AUTH_COOKIE_SECURE', True),
        samesite=s.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        path='/',
    )

    response.set_cookie(
        key=s.get('AUTH_COOKIE', 'access_token'),
        value=access_str,
        max_age=access_max_age,
        **cookie_kwargs,
    )
    # Restrict refresh cookie to only the refresh endpoint
    refresh_kwargs = {**cookie_kwargs, 'path': '/api/auth/refresh/'}
    response.set_cookie(
        key=s.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
        value=refresh_str,
        max_age=refresh_max_age,
        **refresh_kwargs,
    )


def _clear_auth_cookies(response: Response) -> None:
    s = _jwt_settings()
    response.delete_cookie(s.get('AUTH_COOKIE', 'access_token'))
    response.delete_cookie(
        s.get('AUTH_COOKIE_REFRESH', 'refresh_token'),
        path='/api/auth/refresh/',
    )


def issue_tokens_for_user(user, response: Response) -> None:
    """Create a fresh token pair and attach them as httpOnly cookies."""
    refresh = RefreshToken.for_user(user)
    _set_auth_cookies(response, refresh)


def rotate_refresh_token(request, response: Response) -> bool:
    """
    Read the refresh cookie, rotate it, set new cookies.
    Returns False if the cookie is missing or invalid.
    """
    s           = _jwt_settings()
    cookie_name = s.get('AUTH_COOKIE_REFRESH', 'refresh_token')
    raw_token   = request.COOKIES.get(cookie_name)
    if not raw_token:
        return False
    try:
        refresh = RefreshToken(raw_token)
        refresh.blacklist()
        new_refresh = RefreshToken.for_user(refresh.access_token.user)
        _set_auth_cookies(response, new_refresh)
        return True
    except Exception:
        return False


def logout_user(request, response: Response) -> None:
    """Blacklist the refresh token and clear both cookies."""
    s           = _jwt_settings()
    cookie_name = s.get('AUTH_COOKIE_REFRESH', 'refresh_token')
    raw_token   = request.COOKIES.get(cookie_name)
    if raw_token:
        try:
            RefreshToken(raw_token).blacklist()
        except Exception:
            pass
    _clear_auth_cookies(response)
