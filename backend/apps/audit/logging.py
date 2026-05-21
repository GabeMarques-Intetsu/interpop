"""
Logging structurado com contexto de request.

Como funciona:
- `RequestIDMiddleware` (em middleware.py) gera UUID curto por request e
  popula 2 contextvars: `request_id_var` e `user_id_var`.
- `RequestContextFilter` injeta esses valores em todo LogRecord — não
  importa de qual logger vem (Django, DRF, app code, libs).
- Formatters (configurados em settings.LOGGING) usam essas chaves no
  output.

Resultado: cada linha de log carrega `request_id` único + `user_id` (ou
`-` para anon). Investigação pós-bug = `grep request_id=<id>` agrega
TODAS as linhas daquele request, mesmo cruzando módulos diferentes.

Sem isso, journald guarda strings opacas e a única forma de correlacionar
eventos é por timestamp aproximado — frágil sob concorrência.
"""
from __future__ import annotations

import logging
from contextvars import ContextVar

# Defaults: '-' (não '' nem None) facilita filtros em logs JSON e
# diferencia "sem contexto" de "valor vazio".
request_id_var: ContextVar[str] = ContextVar('request_id', default='-')
user_id_var:    ContextVar[str] = ContextVar('user_id',    default='-')


class RequestContextFilter(logging.Filter):
    """Anexa `request_id` e `user_id` a todo LogRecord.

    Filter (não Formatter) porque o Django LOGGING aplica filters antes
    do formatter consumir os atributos. Configurado em
    `settings.LOGGING['handlers']['console']['filters']`.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id    = user_id_var.get()
        return True
