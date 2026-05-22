"""
Tests para permission classes (apps.users.permissions).

Foco principal: IsNotBanned no DEFAULT_PERMISSION_CLASSES (S8 §11.6) —
precisa passar anon (porque endpoints AllowAny ainda devem aceitar
requests não-autenticadas) e bloquear authenticated banned.
"""
from __future__ import annotations

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from apps.articles.models import Article
from apps.users.permissions import IsNotBanned


@pytest.fixture
def published_article(editor_user):
    """Article publicado mínimo — necessário pros testes de endpoint de comments."""
    return Article.objects.create(
        title='Test article',
        slug='test-article-perm',
        excerpt='excerpt',
        body='body de teste com tamanho razoável pra passar validação futura.',
        author=editor_user,
        status='published',
        published_at=timezone.now(),
    )


@pytest.fixture
def factory():
    return APIRequestFactory()


# ── IsNotBanned ──────────────────────────────────────────────────────────────


def test_is_not_banned_allows_anonymous_user(factory):
    """Anon não tem `is_banned` semanticamente — deve passar.
    Garante que IsNotBanned no DEFAULT_PERMISSION_CLASSES não quebra
    endpoints públicos (AllowAny)."""
    request = factory.get('/api/v1/articles/')
    request.user = type('Anon', (), {'is_authenticated': False, 'is_banned': False})()
    assert IsNotBanned().has_permission(request, view=None) is True


def test_is_not_banned_allows_authenticated_non_banned(reader_user, factory):
    """Reader normal autenticado passa (caminho feliz mais comum)."""
    request = factory.get('/api/v1/auth/me/')
    request.user = reader_user
    assert IsNotBanned().has_permission(request, view=None) is True


@pytest.mark.django_db
def test_is_not_banned_blocks_authenticated_banned(reader_user, factory):
    """Banned authenticated é cortado. Regressão para S8."""
    reader_user.is_banned = True
    reader_user.save(update_fields=['is_banned'])

    request = factory.get('/api/v1/auth/me/')
    request.user = reader_user
    assert IsNotBanned().has_permission(request, view=None) is False


def test_is_not_banned_has_humane_error_message():
    """Mensagem de erro é humana — vai pro frontend, leitor entende."""
    assert 'suspensa' in IsNotBanned.message.lower()


# ── IsNotBanned via API real (integração com endpoints que já usam) ────────
#
# Nota arquitetural: views que declaram `permission_classes = [...]`
# SOBRESCREVEM o DEFAULT_PERMISSION_CLASSES. IsNotBanned no DEFAULT funciona
# como safety-net para endpoints futuros que esqueçam de declarar. Comments
# e moderation já listam IsNotBanned explicitamente — testes abaixo
# confirmam que o fix S8 (tornar IsNotBanned anon-friendly) não quebrou
# esse padrão.


@pytest.mark.django_db
def test_is_not_banned_via_comments_endpoint_blocks_banned(
    reader_user, published_article, authed_client_factory,
):
    """`/api/v1/articles/<slug>/comments/` exige IsAuthenticated + IsNotBanned
    (comments/views.py:31). Banned reader recebe 403 ao tentar comentar."""
    reader_user.is_banned = True
    reader_user.save(update_fields=['is_banned'])

    client = authed_client_factory(reader_user)
    resp = client.post(
        f'/api/v1/articles/{published_article.slug}/comments/',
        {'content': 'tentativa de banido'},
        format='json',
    )
    assert resp.status_code == 403, (
        f'Banned reader deveria receber 403 ao tentar comentar; '
        f'recebido {resp.status_code}. Body: {resp.content[:200]}'
    )


@pytest.mark.django_db
def test_is_not_banned_via_comments_endpoint_allows_non_banned(
    reader_user, published_article, authed_client_factory,
):
    """Garantia de não-regression: reader não-banido pode listar comments
    (GET é AllowAny via override, mas confirma que IsNotBanned no DEFAULT
    não vaza pra endpoints públicos)."""
    client = authed_client_factory(reader_user)
    resp = client.get(f'/api/v1/articles/{published_article.slug}/comments/')
    assert resp.status_code == 200, (
        f'Reader normal deveria conseguir listar comments; '
        f'recebido {resp.status_code}.'
    )
