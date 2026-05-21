"""
Testes de defesa em profundidade dos serializers de moderation.

Por que estes testes existem: a hierarquia dev/admin imune a ban é
fundacional pra segurança. O modelo tem 3 camadas de defesa contra
banimento acidental de privilegiados:

  1. Queryset do PrimaryKeyRelatedField filtra `role__in=['user','editor']`
     — não permite nem sequer SELECIONAR um admin/dev.
  2. validate_user_id checa `user.is_immune_to_ban` explicitamente —
     mesmo se algum bug futuro relaxar o queryset, esta valida ainda
     bloqueia.
  3. ban_user service (em test_services.py) testa o caminho feliz.

Quebrar QUALQUER uma das camadas sem quebrar este teste = regression
silenciosa que só aparece quando alguém efetivamente banir um admin
por engano em produção. Indesejável.
"""
from __future__ import annotations

import pytest

from apps.moderation.serializers import BanRequestSerializer, BanSerializer
from apps.moderation.models import Ban


# ── Camada 1: queryset filtra dev/admin ──────────────────────────────────────

@pytest.mark.parametrize('fixture_name', ['dev_user', 'admin_user'])
def test_ban_serializer_queryset_excludes_immune_users(request, fixture_name):
    """PrimaryKeyRelatedField com queryset role__in=['user','editor']
    deveria rejeitar dev/admin já no parsing do payload."""
    target = request.getfixturevalue(fixture_name)
    serializer = BanSerializer(data={
        'user_id': str(target.id),
        'reason': 'test',
    })
    assert not serializer.is_valid()
    assert 'user_id' in serializer.errors


# ── Camada 2: validate_user_id explícito ─────────────────────────────────────

def test_validate_user_id_message_for_immune(reader_user, admin_user, mocker):
    """Mesmo se camada 1 falhasse (queryset relaxado), validate_user_id
    rejeitaria com mensagem clara. Simulamos relaxamento do queryset via
    mock e confirmamos que o validate explícito vence."""
    from apps.users.models import User
    serializer = BanSerializer(data={'user_id': str(admin_user.id), 'reason': 'x'})
    # Bypass camada 1 — substitui o queryset por TODOS os users
    serializer.fields['user_id'].queryset = User.objects.all()

    assert not serializer.is_valid()
    msg = str(serializer.errors['user_id'])
    assert 'Dev' in msg or 'Admin' in msg or 'imun' in msg.lower(), (
        'Mensagem deveria explicar que dev/admin são imunes. Recebido: '
        f'{msg}'
    )


# ── Casos felizes: editor e reader são alvos legítimos ───────────────────────

@pytest.mark.parametrize('fixture_name', ['editor_user', 'reader_user'])
def test_ban_serializer_accepts_editor_and_reader(request, fixture_name):
    target = request.getfixturevalue(fixture_name)
    serializer = BanSerializer(data={
        'user_id': str(target.id),
        'reason': 'spam de fato',
    })
    assert serializer.is_valid(), serializer.errors


# ── Caso defensivo: usuário já banido não pode ser banido duas vezes ─────────

def test_ban_serializer_rejects_already_banned_user(reader_user, admin_user):
    """Ban OneToOne já garante constraint, mas validate dá mensagem
    amigável antes de o constraint estourar."""
    from apps.moderation.services import ban_user
    ban_user(target=reader_user, admin=admin_user, reason='first')

    serializer = BanSerializer(data={
        'user_id': str(reader_user.id),
        'reason': 'second',
    })
    # Queryset filtra `is_banned=False` — então user banido nem aparece.
    # Camada 1 ataca primeiro.
    assert not serializer.is_valid()


# ── BanRequestSerializer (mesma lógica de imunidade) ─────────────────────────

@pytest.mark.parametrize('fixture_name', ['dev_user', 'admin_user'])
def test_ban_request_serializer_rejects_immune_target(request, fixture_name):
    target = request.getfixturevalue(fixture_name)
    serializer = BanRequestSerializer(data={
        'target_id': str(target.id),
        'reason': 'test',
    })
    assert not serializer.is_valid()
    assert 'target_id' in serializer.errors


def test_ban_request_serializer_rejects_duplicate_pending(
    reader_user, editor_user,
):
    """2 redatores não podem ter request pending pra mesmo alvo —
    serializer bloqueia antes do create."""
    from apps.moderation.models import BanRequest
    BanRequest.objects.create(
        target=reader_user, requested_by=editor_user, reason='spam',
    )

    serializer = BanRequestSerializer(data={
        'target_id': str(reader_user.id),
        'reason': 'spam 2',
    })
    assert not serializer.is_valid()
    msg = str(serializer.errors['target_id'])
    assert 'pendente' in msg.lower(), f'Mensagem inesperada: {msg}'
