"""
Testes do módulo apps.users.services — JWT token issue/rotate/blacklist
e cookie lifecycle.

**Por que estes testes existem (especialmente test_rotate_refresh_token_*)**:
o C1 (Improvement-system.md §11.1) foi um bug **HISTÓRICO** que sobreviveu
porque ninguém testou rotate_refresh_token: a função fazia
`refresh.access_token.user` (atributo inexistente no AccessToken do
SimpleJWT) → AttributeError → `except: pass` silencioso → return False.
Sintoma: toda sessão expirava em 15min reais em vez de 7 dias.

Estes testes garantem que o fix não regrida. Em produção, regression aqui
significa "todos os usuários deslogados a cada 15min" — pior UX possível
para produto editorial de leitura longa.
"""
from __future__ import annotations

from django.test import RequestFactory
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services import (
    issue_tokens_for_user,
    logout_user,
    rotate_refresh_token,
)

REFRESH_COOKIE_NAME = 'refresh_token'
ACCESS_COOKIE_NAME  = 'access_token'


# ── issue_tokens_for_user ─────────────────────────────────────────────────────

def test_issue_tokens_sets_both_cookies(reader_user):
    response = Response()
    issue_tokens_for_user(reader_user, response)

    assert ACCESS_COOKIE_NAME in response.cookies
    assert REFRESH_COOKIE_NAME in response.cookies
    # Cookies httpOnly + secure (defesa em profundidade contra XSS hijack)
    assert response.cookies[ACCESS_COOKIE_NAME]['httponly']
    assert response.cookies[REFRESH_COOKIE_NAME]['httponly']
    # Refresh cookie restrito ao endpoint /api/v1/auth/refresh/
    assert response.cookies[REFRESH_COOKIE_NAME]['path'] == '/api/v1/auth/refresh/'


# ── rotate_refresh_token (C1 regression) ──────────────────────────────────────

def test_rotate_refresh_token_returns_true_for_valid_cookie(reader_user):
    """C1 regression: antes do fix, ESTA assertion falhava em 100% dos casos
    porque `refresh.access_token.user` lançava AttributeError silencioso.

    Cenário: usuário tem cookie de refresh válido → rotação deve emitir
    novo par e retornar True."""
    # Setup: emite tokens reais
    refresh = RefreshToken.for_user(reader_user)
    raw_refresh = str(refresh)

    # Simula request com o cookie
    factory = RequestFactory()
    request = factory.post('/api/v1/auth/refresh/')
    request.COOKIES[REFRESH_COOKIE_NAME] = raw_refresh

    response = Response()
    result = rotate_refresh_token(request, response)

    assert result is True, (
        'C1 REGRESSION: rotate_refresh_token retornou False para refresh '
        'token válido. Verificar apps/users/services.py:90-96 — claim '
        '`user_id` deve ser lido via `refresh["user_id"]`, NÃO via '
        '`refresh.access_token.user` (atributo inexistente).'
    )
    # Novos cookies emitidos
    assert ACCESS_COOKIE_NAME in response.cookies
    assert REFRESH_COOKIE_NAME in response.cookies


def test_rotate_refresh_token_blacklists_old_token(reader_user):
    """Após rotação, o refresh antigo deve estar na blacklist —
    senão atacante com token roubado pode rotacionar infinitamente."""
    refresh = RefreshToken.for_user(reader_user)
    raw_refresh = str(refresh)

    factory = RequestFactory()
    request = factory.post('/api/v1/auth/refresh/')
    request.COOKIES[REFRESH_COOKIE_NAME] = raw_refresh

    rotate_refresh_token(request, Response())

    # O jti do refresh original deve estar na blacklist
    jti = refresh['jti']
    assert BlacklistedToken.objects.filter(token__jti=jti).exists()


def test_rotate_refresh_token_returns_false_for_missing_cookie():
    factory = RequestFactory()
    request = factory.post('/api/v1/auth/refresh/')
    assert rotate_refresh_token(request, Response()) is False


def test_rotate_refresh_token_returns_false_for_garbage_cookie():
    factory = RequestFactory()
    request = factory.post('/api/v1/auth/refresh/')
    request.COOKIES[REFRESH_COOKIE_NAME] = 'not.a.jwt.at.all'
    assert rotate_refresh_token(request, Response()) is False


def test_rotate_refresh_token_returns_false_when_user_deleted(reader_user):
    """Edge case: token válido mas usuário foi deletado entre emit e rotate.
    Não pode levantar 500 — retorna False (frontend redireciona pra login)."""
    refresh = RefreshToken.for_user(reader_user)
    raw_refresh = str(refresh)
    user_id = reader_user.id
    reader_user.delete()

    factory = RequestFactory()
    request = factory.post('/api/v1/auth/refresh/')
    request.COOKIES[REFRESH_COOKIE_NAME] = raw_refresh

    assert rotate_refresh_token(request, Response()) is False
    # E o user permanece deletado
    from apps.users.models import User
    assert not User.objects.filter(id=user_id).exists()


# ── logout_user ───────────────────────────────────────────────────────────────

def test_logout_user_blacklists_token_and_clears_cookies(reader_user):
    refresh = RefreshToken.for_user(reader_user)
    raw_refresh = str(refresh)

    factory = RequestFactory()
    request = factory.post('/api/v1/auth/logout/')
    request.COOKIES[REFRESH_COOKIE_NAME] = raw_refresh

    response = Response()
    logout_user(request, response)

    assert BlacklistedToken.objects.filter(token__jti=refresh['jti']).exists()
    # delete_cookie seta cookie com max_age=0 (browser apaga)
    assert response.cookies[ACCESS_COOKIE_NAME]['max-age'] == 0
    assert response.cookies[REFRESH_COOKIE_NAME]['max-age'] == 0


def test_logout_user_silent_on_invalid_token():
    """Double-logout cenário: 2ª chamada com token já blacklistado não pode
    levantar 500 — cleared cookies anyway."""
    factory = RequestFactory()
    request = factory.post('/api/v1/auth/logout/')
    request.COOKIES[REFRESH_COOKIE_NAME] = 'invalid.token.data'

    response = Response()
    logout_user(request, response)  # NÃO deve levantar

    # Cookies foram limpos mesmo assim
    assert response.cookies[ACCESS_COOKIE_NAME]['max-age'] == 0
