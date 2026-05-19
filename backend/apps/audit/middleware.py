"""
AuditLogMiddleware — asynchronously-safe, non-blocking audit recorder.
Records every state-changing HTTP request after the response is sent.
Never raises: a logging failure must never break a user request.
"""
import logging
from .models import AuditLog

logger = logging.getLogger(__name__)

_WRITE_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})
_SKIP_PATHS    = frozenset({'/api/auth/refresh/', '/admin/'})


def _get_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method in _WRITE_METHODS
            and not any(request.path.startswith(p) for p in _SKIP_PATHS)
        ):
            self._record(request, response)

        return response

    def _record(self, request, response) -> None:
        try:
            user = request.user if request.user.is_authenticated else None
            AuditLog.objects.create(
                actor=user,
                action=f'{request.method} {request.path}',
                request_path=request.path,
                request_method=request.method,
                response_status=response.status_code,
                ip_address=_get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        except Exception:
            logger.exception('AuditLog write failed — request processing unaffected.')
