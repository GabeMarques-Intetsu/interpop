# Postmortems — Interpop

> Postmortems são **blameless** — foco em causas sistêmicas, não em pessoas.
> Cada incidente SEV-1 ou SEV-2 deve gerar um postmortem dentro de 7 dias.
> SEV-3 fica a critério.

## Convenção de nome de arquivo + id

`YYYY-MM-DD-slug-curto.md` (mantido — referenciado por ADRs/specs/BUG). Cada postmortem carrega um **id `PM-NN`** no próprio H1 + os links de rastreabilidade (alinhamento à skill _engenharia-de-requisitos_ v1.28): o id vive no documento, não no filename.

## Rastreabilidade (v1.28)

Todo postmortem liga **↑** ao `RNF`/`CA` de dependability que **falhou em produção**, **←** à origem (incidente/triagem), e **↓** às ações corretivas (`BUG`/`TX` + eventual aperto de `RNF`, pelo documento de requisitos primeiro). É um **documento** que se liga à espinha (como ADR) — não é item de backlog.

## Template

[`_TEMPLATE.md`](./_TEMPLATE.md) — copiar + preencher (esqueleto de rastreabilidade; o relato blameless completo segue a prática deste README).

## Catálogo

| Id      | Data       | Severidade | Título                                                                    | Status                            |
| ------- | ---------- | ---------- | ------------------------------------------------------------------------- | --------------------------------- |
| `PM-01` | 2026-05-19 | SEV-2      | [Rotação de JWT silenciosamente quebrada](./PM-01-jwt-rotation-broken.md) | Resolvido — postmortem retroativo |

---

_A39 do reorganization-proposal. Estrutura criada 2026-05-22._
