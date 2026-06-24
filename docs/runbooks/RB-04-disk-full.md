# RB-04 — Disk full

> **Tipo**: Runbook (procedimento operacional — NÃO é item de backlog)
> **Gatilho**: disco saturado no VPS (nginx 503 + alert; risco a writes do Postgres)
> **Status**: 🚧 Stub — preencher conforme incidentes reais (não inventar antes de sintomas observados)

---

## Operacionaliza ↑ (qual requisito este procedimento entrega)

| Operacionaliza                        | ID                                                            | Onde                                                               |
| ------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------ |
| Disponibilidade / degradação graciosa | [`RNF-availability`](../requirements/RNF/RNF-availability.md) | "Disco cheio → nginx 503 + alert; runbook instrui purge"; RTO ≤ 4h |

## Sintoma

_STUB: o que o operador vê (writes falhando, `No space left on device`, alert de disco, Sentry)._

## Diagnóstico

_STUB: comandos para confirmar (`df -h`, maiores diretórios, logs/backups acumulados), dashboards a abrir._

## Ações

_STUB: procedimento de mitigação (purge de logs/backups antigos), em ordem, com comandos exatos. Autoria: agent `documentation-engineer` / skill `incident-runbook-templates`._

## Escalation

_STUB: quando escalar + para quem._

## Postmortems relacionados

_Nenhum ainda — linkar o `PM-NN` correspondente após o primeiro incidente real registrado em `docs/postmortems/`._
