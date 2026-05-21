"""
Testes E2E do flow de auth via APIClient — bate nos endpoints reais
(login, me, refresh, logout, register, change-password).

Diferença vs test_services.py: aqui exercitamos o ciclo HTTP completo —
DRF view + serializer + service + cookie setter + middleware (axes,
CSRF, etc.). Pega regressions de wiring que testes unitários de service
não pegariam (ex.: view não passa context, permission errada, cookie
path divergente).

Convenção: cada teste usa client.cookies como request COOKIES (cookie
jar do APIClient persiste entre requests, simulando o browser).
"""
from __future__ import annotations

from rest_framework.test import APIClient

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

REFRESH_COOKIE = 'refresh_token'
ACCESS_COOKIE  = 'access_token'

LOGIN_URL    = '/api/v1/auth/login/'
LOGOUT_URL   = '/api/v1/auth/logout/'
ME_URL       = '/api/v1/auth/me/'
REFRESH_URL  = '/api/v1/auth/refresh/'
REGISTER_URL = '/api/v1/auth/register/'


# ── Login ─────────────────────────────────────────────────────────────────────

def test_login_success_sets_both_cookies(reader_user, client):
    resp = client.post(LOGIN_URL, data={
        'email': 'leitor@interpop.test',
        'password': 'SenhaForte!2026',
    }, content_type='application/json')

    assert resp.status_code == 200
    assert resp.cookies.get(ACCESS_COOKIE) is not None
    assert resp.cookies.get(REFRESH_COOKIE) is not None
    # Body contém payload do user serializado (UserPublicSerializer não
    # inclui email — defensive privacy. Usar username que é safe-public).
    data = resp.json()
    assert data['username'] == 'leitor.teste'
    assert data['role'] == 'user'


def test_login_wrong_password_returns_400_no_cookies(reader_user, client):
    resp = client.post(LOGIN_URL, data={
        'email': 'leitor@interpop.test',
        'password': 'SenhaErrada123!',
    }, content_type='application/json')

    assert resp.status_code == 400
    assert resp.cookies.get(ACCESS_COOKIE) is None
    assert resp.cookies.get(REFRESH_COOKIE) is None


def test_login_banned_user_blocked(reader_user, admin_user, client):
    """User banido não consegue logar mesmo com senha correta. Defesa
    em profundidade: além de IsNotBanned futuro (S8), o LoginSerializer
    já bloqueia."""
    from apps.moderation.services import ban_user
    ban_user(target=reader_user, admin=admin_user, reason='test')

    resp = client.post(LOGIN_URL, data={
        'email': 'leitor@interpop.test',
        'password': 'SenhaForte!2026',
    }, content_type='application/json')

    assert resp.status_code == 400


# ── /me/ ──────────────────────────────────────────────────────────────────────

def test_me_returns_current_user_with_access_cookie(reader_user, client):
    # Login → preserva cookies no jar do client → me usa
    client.post(LOGIN_URL, data={
        'email': 'leitor@interpop.test',
        'password': 'SenhaForte!2026',
    }, content_type='application/json')

    resp = client.get(ME_URL)
    assert resp.status_code == 200
    assert resp.json()['username'] == 'leitor.teste'


def test_me_without_cookie_returns_401(client):
    resp = client.get(ME_URL)
    assert resp.status_code == 401


# ── Refresh (C1 regression via HTTP) ──────────────────────────────────────────

def test_refresh_with_valid_cookie_rotates_and_returns_200(reader_user, client):
    """C1 regression E2E: bate no endpoint real /api/auth/refresh/.
    Antes do fix (633d032), TODO POST aqui retornava 401 silenciosamente
    porque rotate_refresh_token lançava AttributeError mascarado por
    except: pass. Aqui simulamos o cenário exato do interceptor axios."""
    refresh = RefreshToken.for_user(reader_user)
    client = APIClient()
    client.cookies[REFRESH_COOKIE] = str(refresh)

    resp = client.post(REFRESH_URL)
    assert resp.status_code == 200, (
        'C1 REGRESSION via HTTP: POST /api/auth/refresh/ deveria retornar '
        '200 com cookie de refresh válido. Status 401 indica que '
        'rotate_refresh_token voltou a retornar False — verificar fix '
        'em apps/users/services.py.'
    )
    # Novo par de cookies emitido
    assert resp.cookies.get(ACCESS_COOKIE) is not None
    assert resp.cookies.get(REFRESH_COOKIE) is not None


def test_refresh_without_cookie_returns_401(client):
    resp = client.post(REFRESH_URL)
    assert resp.status_code == 401


def test_refresh_with_garbage_cookie_returns_401():
    client = APIClient()
    client.cookies[REFRESH_COOKIE] = 'not.a.valid.jwt'
    resp = client.post(REFRESH_URL)
    assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

def test_logout_blacklists_refresh_and_clears_cookies(reader_user):
    refresh = RefreshToken.for_user(reader_user)
    refresh_jti = refresh['jti']
    client = APIClient()
    client.cookies[REFRESH_COOKIE] = str(refresh)
    client.cookies[ACCESS_COOKIE]  = str(refresh.access_token)

    resp = client.post(LOGOUT_URL)
    assert resp.status_code == 200
    # Refresh foi pra blacklist (anti-replay)
    assert BlacklistedToken.objects.filter(token__jti=refresh_jti).exists()
    # Cookies foram limpos (max_age=0 = delete)
    assert resp.cookies.get(ACCESS_COOKIE).get('max-age') == 0
    assert resp.cookies.get(REFRESH_COOKIE).get('max-age') == 0


# ── Register ──────────────────────────────────────────────────────────────────

def test_register_creates_user_with_role_user(db, client):
    """Register público SEMPRE cria como role='user'. Nunca como editor/
    admin/dev — privilege escalation por payload tem que ser impossível."""
    resp = client.post(REGISTER_URL, data={
        'email': 'novo@interpop.test',
        'username': 'novo_usuario',
        'first_name': 'Novo',
        'last_name': 'Usuário',
        'password': 'SenhaForte!2026',
        'password2': 'SenhaForte!2026',
        # tentativa maliciosa de escalation:
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    }, content_type='application/json')

    assert resp.status_code == 201

    from apps.users.models import User
    u = User.objects.get(email='novo@interpop.test')
    # Apesar do payload tentar promover, role ficou USER
    assert u.role == User.Role.USER
    assert u.is_staff is False
    assert u.is_superuser is False
