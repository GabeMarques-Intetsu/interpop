"""
SecurityHeadersMiddleware — adiciona headers de segurança não cobertos
nativamente pelo Django SecurityMiddleware.

Cobre:
- Permissions-Policy: desabilita APIs sensíveis (camera, microfone,
  geolocalização, pagamento, USB, sensores). Bloqueia uso por origens
  embutidas via iframe ou scripts third-party. (S9 §11.6)
- Content-Security-Policy: política de origens para script/style/img/etc.
  Modo Report-Only por default (baseline coleta violations sem bloquear);
  flip para enforce via setting CSP_ENFORCE=True. (S3 §11.6)

Django 4.2+ já injeta nativamente (via setting):
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Cross-Origin-Opener-Policy

Escopo: CSP aqui cobre TODA resposta Django (admin, DRF browsable, OG
crawler HTML, healthz). O SPA frontend é servido pelo nginx — sua CSP
vive no nginx (vai entrar no HOSTING-DEPLOY-PLAN.md como item separado).
"""
from __future__ import annotations

from django.conf import settings

_PERMISSIONS_POLICY = (
    'camera=(), microphone=(), geolocation=(), '
    'payment=(), usb=(), accelerometer=(), '
    'gyroscope=(), magnetometer=(), '
    'autoplay=(), encrypted-media=(), '
    'picture-in-picture=(), fullscreen=(self)'
)


def _build_csp(report_uri: str) -> str:
    """Constrói o header CSP a partir de diretivas baseline.

    'unsafe-inline' em script/style é COMPROMISSO consciente: Django admin
    usa <script> e <style> inline e não suporta nonce nativo. Sem unsafe-inline
    o admin quebra. Caminho futuro para enforce sem unsafe-inline: trocar
    /admin/ por interface custom (Sprint distante) OU adotar django-csp-nonces
    + fork de admin templates.

    img-src `https:` permite qualquer URL HTTPS — necessário para avatares e
    embeds. data: necessário para placeholders e PNG/SVG inline.

    frame-ancestors 'none' é redundante com X-Frame-Options DENY mas
    explícito (X-Frame está deprecated em favor de CSP).
    """
    parts = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
    ]
    if report_uri:
        parts.append(f'report-uri {report_uri}')
    return '; '.join(parts)


class SecurityHeadersMiddleware:
    """Adiciona Permissions-Policy + Content-Security-Policy em todo response.

    Roda no fim da chain de middleware — depois que view + outros
    middlewares já escreveram headers. Lê settings a cada request para
    permitir override em testes (`override_settings`).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Permissions-Policy', _PERMISSIONS_POLICY)

        report_uri = getattr(settings, 'CSP_REPORT_URI', '')
        enforce = getattr(settings, 'CSP_ENFORCE', False)
        header_name = (
            'Content-Security-Policy'
            if enforce
            else 'Content-Security-Policy-Report-Only'
        )
        response.setdefault(header_name, _build_csp(report_uri))
        return response
