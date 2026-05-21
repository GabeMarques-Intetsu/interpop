"""
Business logic for authentication.
Views stay thin; all token/cookie manipulation lives here.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


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
    refresh_kwargs = {**cookie_kwargs, 'path': '/api/v1/auth/refresh/'}
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
        path='/api/v1/auth/refresh/',
    )


def issue_tokens_for_user(user, response: Response) -> None:
    """Create a fresh token pair and attach them as httpOnly cookies."""
    refresh = RefreshToken.for_user(user)
    _set_auth_cookies(response, refresh)


def rotate_refresh_token(request, response: Response) -> bool:
    """
    Read the refresh cookie, rotate it, set new cookies.
    Returns False if the cookie is missing or invalid.

    Implementação: o claim `user_id` é lido do JWT (RefreshToken['user_id']),
    o token atual vai pra blacklist, e um novo par é emitido para o User
    correspondente. A versão anterior acessava `refresh.access_token.user`
    — atributo que **não existe** em AccessToken do SimpleJWT (só `.payload`)
    — e o `except Exception: pass` mascarava o AttributeError, fazendo TODO
    refresh retornar False silenciosamente. Sintoma: sessão expirava em
    15min reais (TTL do access) em vez de 7 dias. Bug histórico, identificado
    na auditoria de segurança 2026-05-20 (C1 do Improvement-system.md §11.1).
    """
    s           = _jwt_settings()
    cookie_name = s.get('AUTH_COOKIE_REFRESH', 'refresh_token')
    raw_token   = request.COOKIES.get(cookie_name)
    if not raw_token:
        return False
    try:
        refresh     = RefreshToken(raw_token)
        user_id     = refresh['user_id']
        refresh.blacklist()
        user        = get_user_model().objects.get(pk=user_id)
        new_refresh = RefreshToken.for_user(user)
        _set_auth_cookies(response, new_refresh)
        return True
    except Exception:
        # Logger expõe o motivo real (refresh inválido, expirado, blacklisted,
        # user deletado). Antes era `pass` silencioso — não fazer isso de novo.
        logger.warning('rotate_refresh_token failed', exc_info=True)
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
            # Expected on already-blacklisted/expired tokens — logamos como
            # info (não warning) porque é caminho normal de duplo-logout.
            logger.info('logout_user: token already invalid', exc_info=True)
    _clear_auth_cookies(response)
