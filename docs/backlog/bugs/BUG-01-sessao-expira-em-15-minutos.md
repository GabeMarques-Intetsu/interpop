# BUG-01 — Sessão do leitor expira sozinha a cada 15 minutos

> **Type**: Bug (defect) · _orig. C1 (Improvement-system §11.1) / postmortem 2026-05-19_
> **Severity**: 🔴 Critical
> **Layer**: Backend
> **Status**: ✅ Verified
> **Sprint**: 1 · **Reported**: 18/05/2026

---

## Defect (observed × expected)

- **Observed**: o leitor autenticado era deslogado a cada ~15 minutos (vida do access token), forçando re-login constante. A rotação do refresh token nunca acontecia.
- **Expected**: enquanto o refresh token for válido, a sessão se renova de forma transparente e o leitor permanece logado — leitura longa sem interrupção.

## Steps to reproduce

1. Logar na plataforma em pré-produção.
2. Ler um artigo por mais de 15 minutos (ou aguardar o access token expirar).
3. Próxima ação autenticada retorna como deslogado — sessão caiu em vez de rotacionar.

## Causa raiz (curto)

`rotate_refresh_token` lia `refresh.access_token.user` — atributo inexistente no SimpleJWT. O `except Exception: pass` defensivo engolia o `AttributeError` e devolvia `False` sempre, mesmo com cookie válido. Cobertura zero no happy path desse módulo escondeu o defeito. Detalhe completo no postmortem retroativo.

## Traceability ↑ (what this defect VIOLATES)

| Violates | ID                                           | Where                                                        |
| -------- | -------------------------------------------- | ------------------------------------------------------------ |
| Feature  | `F-01` — Autenticação JWT em cookie httpOnly | [F-01](../features/F-01-autenticacao-jwt-cookie-httponly.md) |
| Epic     | `EP-01` — Fundação da plataforma             | [EP-01](../epics/EP-01-fundacao-plataforma.md)               |

## Origin ← (where it came from)

- Direct report — relato de re-login frequente em pré-prod; bug localizado por inspeção linha-a-linha durante refactor da estratégia de sessão (orig. **C1**).

## Resolution ↓ (traceability of the fix)

| Artifact        | Reference                                                                                                                                                                        |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fix Task        | `[back]`                                                                                                                                                                         |
| Commit / PR     | `633d032` — Fix: rotate_refresh_token quebrado — sessão expirava em 15min reais (C1)                                                                                             |
| Regression test | `backend/apps/users/tests/test_services.py` — 5 testes (cookie válido, blacklist do antigo, cookie ausente, cookie corrompido, user deletado) — **vermelho antes, verde depois** |
| Postmortem      | [`docs/postmortems/PM-01-jwt-rotation-broken.md`](../../postmortems/PM-01-jwt-rotation-broken.md)                                                                                |

> Lição sistêmica (STATE.md §Evitar): `except Exception: pass` em path crítico esconde bug real; cobertura funcional > cobertura de linha.
