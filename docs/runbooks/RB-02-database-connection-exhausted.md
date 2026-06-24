# RB-02 — Database connection exhausted

> **Tipo**: Runbook (procedimento operacional — NÃO é item de backlog)
> **Gatilho**: pool de conexões do Postgres esgotado (nginx retorna 503 + Retry-After)
> **Status**: 🚧 Stub — preencher conforme incidentes reais (não inventar antes de sintomas observados)

---

## Operacionaliza ↑ (qual requisito este procedimento entrega)

| Operacionaliza                        | ID                                                            | Onde                                                                                          |
| ------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Disponibilidade / degradação graciosa | [`RNF-availability`](../requirements/RNF/RNF-availability.md) | "DB connection exhausted → nginx 503 + Retry-After" (padrão de degradação graciosa); RTO ≤ 4h |

## Sintoma

_STUB: o que o operador vê (503 em massa, erros `too many connections` no log, Sentry)._

## Diagnóstico

_STUB: comandos para confirmar (contagem de conexões ativas, queries longas), dashboards a abrir._

## Ações

_STUB: procedimento de mitigação, em ordem, com comandos exatos. Autoria: agent `documentation-engineer` / skill `incident-runbook-templates`._

## Escalation

_STUB: quando escalar + para quem._

## Postmortems relacionados

_Nenhum ainda — linkar o `PM-NN` correspondente após o primeiro incidente real registrado em `docs/postmortems/`._
