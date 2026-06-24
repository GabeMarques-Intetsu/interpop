# ADR-016: Postgres local no VPS confirmado — Supabase cenário (B) "DB managed" rejeitado

- **Date**: 2026-06-20
- **Status**: Accepted (reafirma e reforça [ADR-015](ADR-015-supabase-evaluation-deferred.md); **não** a supersede)
- **Deciders**: Gabriel Marques (DPO/owner), com análise de 4 especialistas (`database-architect`, `backend-architect`, `cyber-security-architect`, hosting/custo/escala)
- **Tags**: database, hosting, scalability, security, lgpd, cost

## Context and Problem Statement

Em 2026-06-20 foi levantada a proposta de **mover o banco de dados para Supabase** e manter o app **hospedado na Hostinger**. Isso reabre o **cenário (B) "DB managed"** que a [ADR-015](ADR-015-supabase-evaluation-deferred.md) havia explicitamente adiado (a ADR-015 só autorizava o cenário (A) — Storage/pgvector como suplemento — mediante gatilho de produto).

Por se tratar de reabertura de decisão arquivada e cross-cutting (afeta todo o read-path), o cenário (B) foi reavaliado formalmente por **4 lentes independentes e isoladas**. As quatro convergiram, sem se comunicarem, na mesma recomendação: **manter Postgres local no VPS**.

A premissa que muda tudo: o Interpop é um produto **editorial read-heavy** cuja moeda é tráfego orgânico (SEO/Core Web Vitals), e o **Django já é dono de auth (JWT httpOnly + django-axes + roles), API (DRF) e admin** — ou seja, ~70% da plataforma Supabase (GoTrue, PostgREST, Realtime, Studio) seria peso morto.

### Topologias avaliadas

| Opção                                        | Descrição                                                                                | Veredito                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------- |
| **(A) Supabase Cloud + Django na Hostinger** | DB gerenciado, app conecta pela internet                                                 | ❌ latência WAN por query |
| **(B) Auto-hospedar Supabase no KVM 1**      | stack Supabase (~12 contêineres) via Docker no próprio VPS                               | ❌ inviável em 4GB/1vCPU  |
| **(C) Postgres local no VPS**                | plano original ([ADR-005](ADR-005-hostinger-kvm1.md)); já configurado em `production.py` | ✅ **escolhido**          |

## Decision Drivers

- **Latência do read-path** — Django/ORM dispara 10–30 queries/request; cada round-trip WAN (mesmo intra-SP) custa 1–5ms vs ~0,05–0,3ms em socket local → **+30 a 150ms/página** que vão direto no TTFB → degrada LCP/SEO.
- **Reaproveitamento da stack** — Django já cobre auth/API/admin; Supabase entregaria essencialmente só "Postgres gerenciado".
- **LGPD / residência de dados** — dado de cidadão BR; minimizar subprocessadores e transferência internacional.
- **Custo previsível** — VPS já pago (custo marginal $0) vs Supabase Pro $25+/mês com egress opaco.
- **Reversibilidade** — a decisão não pode criar lock-in.

## Considered Options

- **(A)** Supabase Cloud (managed) + Django na Hostinger
- **(B)** Auto-hospedar Supabase no KVM 1
- **(C)** Postgres local no VPS (status quo do `production.py`)

## Decision Outcome

Escolhido: **(C) Postgres local no VPS**, porque vence nos quatro eixos avaliados (latência, integração backend, segurança/LGPD, custo/escala) e **já é o estado atual** de `backend/config/settings/production.py` (`HOST=localhost` via env, `CONN_MAX_AGE=60`, `sslmode=require`). O cenário (B) "DB managed" fica **formalmente rejeitado**. O cenário (A) "suplemento" (Storage/pgvector) permanece adiado sob os gatilhos da ADR-015.

### Positive Consequences

- Read-path em socket local — sem penalidade de WAN, p95/TTFB preservados (proteção direta de SEO/CWV).
- Um único vendor, uma superfície de ataque; Postgres não exposto à internet (`listen_addresses=localhost`).
- LGPD de menor atrito — dado fica no VPS Hostinger (Brasil), zero subprocessador novo, direito de eliminação sob controle direto.
- Custo marginal $0; nenhuma migração necessária (config já presente).

### Negative Consequences

- Backups/PITR continuam **DIY** (`pg_dump`/`pgBackRest` + WAL para storage externo cifrado) — não gerenciados. Mantém-se a linha da ADR-032 da busca.
- App e DB compartilham o mesmo box (KVM 1) — saturação de recursos é risco a monitorar (runbook `RB-04-RB-04-disk-full.md`); blast radius do host cobre o DB.
- Sem managed Realtime/Storage — aceitável (produto editorial não é chat; capas resolvidas via CDN, abaixo).

### Trade-offs aceitos

- RLS do Supabase **não** é adotado: seria redundante (authz já vive no Django) e criaria dupla fonte de verdade de autorização.
- Escala futura via cache + vertical scaling, não via DB gerenciado (ver caminho abaixo).

## Caminho de escalabilidade (até ~100k MAU)

1. **Cache na frente** (maior alavanca read-heavy): Cloudflare CDN ([ADR-003](ADR-003-cloudflare-pos-dominio.md)) + Redis local (page/fragment cache, sessões).
2. **PgBouncer local** (pooling) quando workers/conexões crescerem.
3. **Tuning Postgres**: `shared_buffers≈1GB`, `effective_cache_size≈3GB`, índices por hot query, `pg_stat_statements`, matar N+1 com `select_related`/`prefetch_related`.
4. **Scaling vertical do KVM** (KVM 2/4 — resize in-place, sem migração).
5. **Só então** DB em box dedicado + **read replica**. Gatilho: cache hit ratio caindo **E** CPU de DB sustentada >70%.

## Gatilhos para reabrir Supabase (herda + estende ADR-015)

Reavaliar **Supabase Cloud em `sa-east-1` (São Paulo)** — nunca cenário (B) abrupto — apenas se, **com evidência medida**:

1. Qualquer gatilho da ADR-015 disparar (disco KVM ≥70%, demanda concreta de semantic search/pgvector, real-time, janela de spike).
2. Scaling vertical do KVM esgotado **E** necessidade comprovada de read-replica/PITR gerenciados.

**Pré-condições inegociáveis** se algum dia entrar: região `sa-east-1` + **DPA assinado** + AWS mapeada no RoPA + co-localização app↔DB (não prender o app na Hostinger pagando WAN).

## Follow-up desacoplado (não-Supabase)

- **Capas de artigo → Cloudflare CDN** (ou bucket S3-compatível), tirando a entrega de imagem do gunicorn. É o único valor real que o Supabase Storage teria, resolvido sem adotar a plataforma. Encaminhar como item próprio (alinha com ADR-003).

## Links / Cross-ref

- Reafirma: [ADR-015 — Avaliação de Supabase adiada](ADR-015-supabase-evaluation-deferred.md) (cenário B agora fechado; cenário A segue adiado sob gatilho)
- Premissa: [ADR-005 — Hostinger KVM 1](ADR-005-hostinger-kvm1.md)
- Premissa de cache/CDN: [ADR-003 — Cloudflare](ADR-003-cloudflare-pos-dominio.md)
- Baseline implementado: `backend/config/settings/production.py` (DATABASES default)
- Incompatibilidades do cenário B com a busca: ADR-018 / ADR-019 / ADR-021b (em `docs/specs/busca-editorial/adrs/`)

## Histórico

| Data       | Evento                                                                                                                                                                                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-06-20 | Reabertura do cenário (B) proposta pelo owner. Reavaliação formal por 4 especialistas isolados → convergência unânime em (C). Cenário (B) rejeitado; (C) confirmado (já era o estado de `production.py`). Anti-sycophancy aplicada. |
