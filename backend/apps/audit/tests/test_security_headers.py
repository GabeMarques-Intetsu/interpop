"""
Tests para SecurityHeadersMiddleware (apps.audit.security_headers_middleware).

S9 do Improvement-system §11.6 — confirma que Permissions-Policy entra
em TODO response, incluindo respostas de erro.

S3 do Improvement-system §11.6 — Content-Security-Policy em modo
Report-Only durante baseline (1 semana coletando violations antes do
flip para enforce via CSP_ENFORCE=True).
"""
from __future__ import annotations

import pytest
from django.test import override_settings


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


# ── S3: Content-Security-Policy ────────────────────────────────────────────


@pytest.mark.django_db
def test_csp_report_only_header_present_by_default(client):
    """Baseline: CSP entra em modo Report-Only — coleta violations
    sem quebrar nada por 1 semana antes do flip para enforce."""
    resp = client.get('/healthz/')
    assert 'Content-Security-Policy-Report-Only' in resp.headers
    # Enforce NÃO deve estar presente enquanto CSP_ENFORCE=False
    assert 'Content-Security-Policy' not in resp.headers


@pytest.mark.django_db
def test_csp_policy_includes_strict_defaults(client):
    """Política mínima: nega frame-ancestors, plugins (object), base-uri
    cross-origin, form action cross-origin. Defaults em 'self'."""
    resp = client.get('/healthz/')
    policy = resp.headers['Content-Security-Policy-Report-Only']

    expected_directives = [
        "default-src 'self'",
        "frame-ancestors 'none'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    for directive in expected_directives:
        assert directive in policy, (
            f'CSP não contém diretiva esperada {directive!r}: {policy}'
        )


@pytest.mark.django_db
def test_csp_allows_inline_for_django_admin_compatibility(client):
    """Django admin usa <script> e <style> inline — sem 'unsafe-inline'
    o admin quebraria. Compromisso documentado: admin nativo Django não
    suporta nonce. Workaround só viável com fork ou django-csp-nonces."""
    resp = client.get('/healthz/')
    policy = resp.headers['Content-Security-Policy-Report-Only']
    assert "'unsafe-inline'" in policy


@pytest.mark.django_db
@override_settings(CSP_ENFORCE=True)
def test_csp_enforce_when_setting_enabled(client):
    """Flip do toggle CSP_ENFORCE=True troca o header de Report-Only
    para enforce — browsers passam a BLOQUEAR violations, não só reportar."""
    resp = client.get('/healthz/')
    assert 'Content-Security-Policy' in resp.headers
    assert 'Content-Security-Policy-Report-Only' not in resp.headers


@pytest.mark.django_db
@override_settings(CSP_REPORT_URI='/api/v1/security/csp-report/')
def test_csp_includes_report_uri_when_configured(client):
    """Quando CSP_REPORT_URI está setado no .env, a diretiva report-uri
    entra na policy — browsers postam violation reports no endpoint."""
    resp = client.get('/healthz/')
    policy = resp.headers['Content-Security-Policy-Report-Only']
    assert 'report-uri /api/v1/security/csp-report/' in policy


@pytest.mark.django_db
def test_csp_header_present_on_404(client):
    """CSP deve cobrir respostas de erro também — defesa em profundidade
    mesmo em handler 404 do Django."""
    resp = client.get('/url-que-nao-existe-em-lugar-nenhum/')
    assert resp.status_code == 404
    assert 'Content-Security-Policy-Report-Only' in resp.headers
