"""
Fixtures globais do pytest-django.

Os fixtures aqui ficam disponíveis pra qualquer test_*.py em qualquer app
sem precisar importar — pytest descobre automaticamente.

Convenção: 1 fixture = 1 user com role específico. Factories detalhadas
(com username, email parametrizáveis) vivem em apps/<app>/tests/factories.py.
"""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# ── User fixtures por role ─────────────────────────────────────────────────────

@pytest.fixture
def reader_user(db) -> 'User':
    """Leitor comum — role 'user'. Pode comentar e curtir, nada mais."""
    return User.objects.create_user(
        username='leitor.teste',
        email='leitor@interpop.test',
        password='SenhaForte!2026',
        first_name='Leitor',
        last_name='Teste',
        role=User.Role.USER,
    )


@pytest.fixture
def editor_user(db) -> 'User':
    """Redator/editor — role 'editor'. Pode publicar artigos e solicitar
    banimento (mas não banir diretamente)."""
    return User.objects.create_user(
        username='redator.teste',
        email='redator@interpop.test',
        password='SenhaForte!2026',
        first_name='Redator',
        last_name='Teste',
        role=User.Role.EDITOR,
    )


@pytest.fixture
def admin_user(db) -> 'User':
    """Administrador — role 'admin'. Pode tudo do editor + banir + acessar
    /admin. Imune a banimento por design."""
    return User.objects.create_user(
        username='admin.teste',
        email='admin@interpop.test',
        password='SenhaForte!2026',
        first_name='Admin',
        last_name='Teste',
        role=User.Role.ADMIN,
    )


@pytest.fixture
def dev_user(db) -> 'User':
    """Dev — dono/criador da plataforma. Role 'dev' = admin++ (mesmos
    privilégios + imune a ban absoluto). Único role que pode gerenciar
    outros admins (B6 backlog)."""
    return User.objects.create_user(
        username='dev.teste',
        email='dev@interpop.test',
        password='SenhaForte!2026',
        first_name='Dev',
        last_name='Teste',
        role=User.Role.DEV,
    )


# ── API client autenticado ─────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """REST framework APIClient sem autenticação. Useful pra hits anon."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authed_client_factory(api_client):
    """Factory que retorna um APIClient logado como o user passado.
    Usa force_authenticate (não passa pelo flow de cookie — adequado pra
    testes de view que não estão testando o login flow em si)."""
    def _make(user):
        api_client.force_authenticate(user=user)
        return api_client
    return _make
