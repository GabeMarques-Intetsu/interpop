# RB-01 — Celery worker stuck

> **Tipo**: Runbook (procedimento operacional — NÃO é item de backlog)
> **Gatilho**: worker Celery travado (tarefas async paradas — newsletter/email não saem)
> **Status**: 🚧 Stub — preencher conforme incidentes reais (não inventar antes de sintomas observados)

---

## Operacionaliza ↑ (qual requisito este procedimento entrega)

| Operacionaliza                        | ID                                                            | Onde                                                                                      |
| ------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Disponibilidade / degradação graciosa | [`RNF-availability`](../requirements/RNF/RNF-availability.md) | falha de processamento assíncrono (Celery) não derruba o serviço síncrono (MTTR < 30 min) |

## Sintoma

_STUB: o que o operador vê (alerta Sentry / fila Redis crescendo / tarefas não completam)._

## Diagnóstico

_STUB: comandos para confirmar hipótese (inspecionar fila, status do worker), dashboards a abrir._

## Ações

_STUB: procedimento de mitigação, em ordem, com comandos exatos. Autoria: agent `documentation-engineer` / skill `incident-runbook-templates`._

## Escalation

_STUB: quando escalar + para quem._

## Postmortems relacionados

_Nenhum ainda — linkar o `PM-NN` correspondente após o primeiro incidente real registrado em `docs/postmortems/`._
