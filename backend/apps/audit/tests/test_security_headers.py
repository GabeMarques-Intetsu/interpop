"""
Tests para SecurityHeadersMiddleware (apps.audit.security_headers_middleware).

S9 do Improvement-system §11.6 — confirma que Permissions-Policy entra
em TODO response, incluindo respostas de erro.
"""
from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_permissions_policy_header_present_on_healthz(client):
    """Endpoint mais simples — confirma que o middleware injeta o header
    em response 200 sem corpo significativo."""
    resp = client.get('/healthz/')
    assert resp.status_code == 200
    assert 'Permissions-Policy' in resp.headers
    assert 'camera=()' in resp.headers['Permissions-Policy']


@pytest.mark.django_db
def test_permissions_policy_header_present_on_404(client):
    """Header deve ir junto mesmo em response de erro — não deixa brecha
    para fingerprint via URL inválida."""
    resp = client.get('/url-que-nao-existe-em-lugar-nenhum/')
    assert resp.status_code == 404
    assert 'Permissions-Policy' in resp.headers


@pytest.mark.django_db
def test_permissions_policy_disables_sensitive_apis(client):
    """Header cobre as APIs mais críticas (camera, mic, geo, payment, usb)."""
    resp = client.get('/healthz/')
    policy = resp.headers['Permissions-Policy']

    for api in ('camera', 'microphone', 'geolocation', 'payment', 'usb'):
        assert f'{api}=()' in policy, (
            f'Permissions-Policy não bloqueia {api}: {policy}'
        )


@pytest.mark.django_db
def test_coop_header_present_on_response(client):
    """Cross-Origin-Opener-Policy injetado pelo Django SecurityMiddleware
    (setting SECURE_CROSS_ORIGIN_OPENER_POLICY)."""
    resp = client.get('/healthz/')
    assert resp.headers.get('Cross-Origin-Opener-Policy') == 'same-origin'


@pytest.mark.django_db
def test_security_middleware_chain_complete(client):
    """Checklist consolidado dos headers de segurança esperados — falha
    única caso algum vaze do setting."""
    resp = client.get('/healthz/')

    expected = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Cross-Origin-Opener-Policy': 'same-origin',
    }
    for header, value in expected.items():
        actual = resp.headers.get(header)
        assert actual == value, f'{header}: esperado {value!r}, recebido {actual!r}'

    # Permissions-Policy validado em test_permissions_policy_*
    assert 'Permissions-Policy' in resp.headers
