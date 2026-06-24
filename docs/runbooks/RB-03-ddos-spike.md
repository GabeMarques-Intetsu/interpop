# RB-03 — DDoS / traffic spike

> **Tipo**: Runbook (procedimento operacional — NÃO é item de backlog)
> **Gatilho**: spike de tráfego suspeito (possível DDoS / scraping abusivo)
> **Status**: 🚧 Stub — preencher conforme incidentes reais (não inventar antes de sintomas observados)

---

## Operacionaliza ↑ (qual requisito este procedimento entrega)

| Operacionaliza                       | ID                                                            | Onde                                                                                                                  |
| ------------------------------------ | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Disponibilidade sob carga / spike    | [`RNF-availability`](../requirements/RNF/RNF-availability.md) | `RB-03-ddos-spike.md` já catalogado como runbook operacional (degradação graciosa)                                    |
| Segurança — abuso por usuário válido | [`RNF-security`](../requirements/RNF/RNF-security.md)         | rate limit / Cloudflare Turnstile ([ADR-007](../planning/adrs/ADR-007-cloudflare-turnstile.md)) contra scraping/abuso |

## Sintoma

_STUB: o que o operador vê (RPS anômalo, p95 disparando, 429/503, alertas Cloudflare/Sentry)._

## Diagnóstico

_STUB: comandos para confirmar (origem do tráfego, padrão de requisições), dashboards a abrir._

## Ações

_STUB: procedimento de mitigação, em ordem, com comandos exatos. Autoria: agent `documentation-engineer` / skill `incident-runbook-templates`._

## Escalation

_STUB: quando escalar + para quem._

## Postmortems relacionados

_Nenhum ainda — linkar o `PM-NN` correspondente após o primeiro incidente real registrado em `docs/postmortems/`._
