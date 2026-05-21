"""
Testes das role properties do User: is_dev, is_admin, is_editor, can_publish,
is_immune_to_ban.

Por que estes testes existem: a hierarquia de roles é a fundação de segurança
da aplicação. Bug aqui = privilege escalation OU ban acidental do dono.

Modelagem:
- DEV    = dono/criador (admin++ + imune a ban)
- ADMIN  = poder total + imune a ban
- EDITOR = publica + solicita ban (mas não bane)
- USER   = leitor (default do register público)
"""
from __future__ import annotations

import pytest


# ── Tabela canônica de role → properties esperadas ────────────────────────────
# (role_fixture_name, is_dev, is_admin, is_editor, can_publish, is_immune)
ROLE_MATRIX = [
    ('dev_user',     True,  True,  False, True,  True),
    ('admin_user',   False, True,  False, True,  True),
    ('editor_user',  False, False, True,  True,  False),
    ('reader_user',  False, False, False, False, False),
]


@pytest.mark.parametrize(
    'fixture_name, is_dev, is_admin, is_editor, can_publish, is_immune',
    ROLE_MATRIX,
)
def test_role_properties_match_matrix(
    request, fixture_name, is_dev, is_admin, is_editor, can_publish, is_immune,
):
    """Cobertura completa da matriz role × property em uma só rodada.

    Falha aqui significa: alguma property mudou comportamento sem que a
    intenção (DEV ⊆ admin, editor pode publicar, etc.) tenha sido revisada.
    Re-discutir hierarquia ANTES de relaxar o teste."""
    user = request.getfixturevalue(fixture_name)
    assert user.is_dev          is is_dev,         f'{user.role}.is_dev'
    assert user.is_admin        is is_admin,       f'{user.role}.is_admin'
    assert user.is_editor       is is_editor,      f'{user.role}.is_editor'
    assert user.can_publish     is can_publish,    f'{user.role}.can_publish'
    assert user.is_immune_to_ban is is_immune,     f'{user.role}.is_immune_to_ban'


def test_dev_is_subset_of_admin(dev_user):
    """ADR fundacional: 'dev é admin++'. Endpoints com IsAdminUser aceitam
    dev. Se este teste quebrar, revisar ADR e §11.2 do Improvement-system."""
    assert dev_user.is_dev and dev_user.is_admin


def test_admin_is_not_dev(admin_user):
    """Asymmetry: nem todo admin é dev. Importante pra B6 (dev pode promover/
    rebaixar admins, mas não o inverso)."""
    assert admin_user.is_admin and not admin_user.is_dev


def test_immune_set_equals_admin_set(dev_user, admin_user, editor_user, reader_user):
    """is_immune_to_ban e is_admin têm o MESMO conjunto: dev + admin.
    Se alguém alterar uma sem a outra (ex.: liberar ban de admin), este
    teste pega imediatamente."""
    for u in [dev_user, admin_user, editor_user, reader_user]:
        assert u.is_admin == u.is_immune_to_ban, (
            f'role={u.role}: is_admin={u.is_admin} != is_immune={u.is_immune_to_ban}'
        )


def test_avatar_initial_from_first_name(reader_user):
    assert reader_user.avatar_initial == 'L'  # Leitor


def test_full_name_concat(reader_user):
    assert reader_user.full_name == 'Leitor Teste'


def test_default_role_is_user(db):
    """Register público cria sempre como USER. Promoção pra editor/admin/dev
    é manual (Django admin OU futuro B6)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    u = User.objects.create_user(
        username='novo',
        email='novo@interpop.test',
        password='SenhaForte!2026',
        first_name='Novo',
        last_name='User',
    )
    assert u.role == User.Role.USER
