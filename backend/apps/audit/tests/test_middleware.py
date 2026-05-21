"""
Testes do RequestIDMiddleware e RequestContextFilter — observabilidade
(A27 do Improvement-system §11.2).
"""
from __future__ import annotations

import logging

import pytest

from apps.audit.logging import (
    RequestContextFilter,
    request_id_var,
    user_id_var,
)

# Os testes que batem em /api/v1/articles/ via Django test client precisam
# de DB porque a view consulta Article. Marca módulo inteiro pra evitar
# repetir o decorator em cada função.
pytestmark = pytest.mark.django_db


# ── RequestIDMiddleware via HTTP ──────────────────────────────────────────────

def test_response_carries_x_request_id_header(client):
    """Toda response deve carregar X-Request-ID — cliente pode logar
    em paralelo e usar pra reportar bug com correlação 1:1."""
    resp = client.get('/api/v1/articles/')
    assert resp.has_header('X-Request-ID')
    assert len(resp['X-Request-ID']) >= 8


def test_request_id_honors_client_provided_header(client):
    """Se cliente já gerou um ID (ex.: Sentry breadcrumb), middleware honra
    — facilita correlation cross-service."""
    custom = 'frontend-abc123'
    resp = client.get('/api/v1/articles/', HTTP_X_REQUEST_ID=custom)
    assert resp['X-Request-ID'] == custom


def test_request_id_truncated_to_64_chars(client):
    """Header malicioso com 10MB de lixo não passa adiante — cap em 64."""
    huge = 'x' * 10_000
    resp = client.get('/api/v1/articles/', HTTP_X_REQUEST_ID=huge)
    assert len(resp['X-Request-ID']) == 64


def test_distinct_requests_get_distinct_ids(client):
    r1 = client.get('/api/v1/articles/')
    r2 = client.get('/api/v1/articles/')
    assert r1['X-Request-ID'] != r2['X-Request-ID']


# ── Contextvars + RequestContextFilter ────────────────────────────────────────

def test_filter_injects_default_when_no_context():
    """Fora de request (script standalone, Celery task sem wrapper) o
    filter ainda deve funcionar com default '-' em vez de levantar."""
    f = RequestContextFilter()
    record = logging.LogRecord(
        name='test', level=logging.INFO, pathname='', lineno=0,
        msg='hi', args=None, exc_info=None,
    )
    assert f.filter(record) is True
    assert record.request_id == '-'
    assert record.user_id == '-'


def test_filter_picks_up_contextvar_values():
    """Quando RequestIDMiddleware popula os contextvars, o filter lê."""
    token_rid = request_id_var.set('abc123')
    token_uid = user_id_var.set('u42')
    try:
        f = RequestContextFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='hi', args=None, exc_info=None,
        )
        f.filter(record)
        assert record.request_id == 'abc123'
        assert record.user_id == 'u42'
    finally:
        request_id_var.reset(token_rid)
        user_id_var.reset(token_uid)
