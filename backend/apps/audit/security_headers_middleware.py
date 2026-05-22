"""
SecurityHeadersMiddleware — adiciona headers de segurança não cobertos
nativamente pelo Django SecurityMiddleware.

Hoje cobre:
- Permissions-Policy: desabilita APIs sensíveis (camera, microfone,
  geolocalização, pagamento, USB, sensores). Bloqueia uso por origens
  embutidas via iframe ou scripts third-party.

Django 4.2+ já injeta nativamente (via setting):
- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Cross-Origin-Opener-Policy

Não cobertos aqui (vão no nginx em produção):
- Content-Security-Policy (S3 — depende de auditoria report-only primeiro)
- Cross-Origin-Resource-Policy (caso-a-caso por endpoint)

S9 do Improvement-system §11.6.
"""
from __future__ import annotations


_PERMISSIONS_POLICY = (
    'camera=(), microphone=(), geolocation=(), '
    'payment=(), usb=(), accelerometer=(), '
    'gyroscope=(), magnetometer=(), '
    'autoplay=(), encrypted-media=(), '
    'picture-in-picture=(), fullscreen=(self)'
)


class SecurityHeadersMiddleware:
    """Adiciona Permissions-Policy em todo response.

    Roda no fim da chain de middleware — depois que view + outros
    middlewares já escreveram headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Permissions-Policy', _PERMISSIONS_POLICY)
        return response
