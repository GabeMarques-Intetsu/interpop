# Hospedagem & Deploy — Interpop

> Documento de decisão e roadmap. Atualizado em 2026-05-17.
> Decisões aqui afetam OAuth (Google/Facebook precisam de HTTPS público
> de callback), entrega de imagens (uploads de capa), envio de e-mail e
> performance do signal `post_save` que dispara newsletter.

## Stack recomendada (free tier honesto, 2026)

| Camada | Provider | Free tier | Por quê |
|---|---|---|---|
| **Frontend (Vite build)** | **Vercel** | 100 GB bandwidth/mês, builds ilimitados, custom domain HTTPS | Deploy automático do GitHub, zero config pra Vite, instant rollback, padrão da indústria pra React |
| **Backend Django** | **Fly.io** (1ª escolha) ou **Render** | Fly: $5 credit/mo (~3 VMs sempre on); Render: 750h/mês mas **spin-down 15min idle** (cold start ~30s) | Fly **não dorme** — crítico pro signal síncrono de email no `post_save`. Render dormindo = timeout. Ambos dão HTTPS automático |
| **Postgres** | **Neon** | 3 GB grátis, serverless (escala a zero), branching tipo git | Setup em 30s. Supabase (500MB) é menor. Render/Railway Postgres custam $7/mês após teste |
| **Media (capas)** | **Cloudflare R2** | 10 GB grátis, **zero egress fees** | S3-compatible. AWS S3 cobra egress. **Sem isso, `runserver` perde uploads a cada deploy** |
| **SMTP** | **Gmail** (já configurado) → **Resend** quando crescer | Gmail: 500/dia; Resend: 3.000/mês free | Gmail está OK por enquanto. Resend dev-friendly quando passar |

**Custo total enquanto pequeno: R$ 0/mês**
**Quando crescer (~1k leitores/dia): ~$50/mês** (Vercel Pro $20 + Fly ~$10 + Neon $19 + R2 < $5 + SMTP grátis)

## Pré-requisitos antes do primeiro deploy

Ajustes obrigatórios no backend Django:

1. **`SECRET_KEY`** — via env var, nunca commitado
2. **`DEBUG=False`** em produção
3. **`ALLOWED_HOSTS`** — domínio Fly/Render + custom domain
4. **`CORS_ALLOWED_ORIGINS`** — URL do Vercel + custom domain
5. **`CSRF_TRUSTED_ORIGINS`** — idem
6. **WhiteNoise** instalado e configurado pra servir static do Django admin
7. **`django-storages` + `boto3`** pra apontar `MEDIA_ROOT` para R2 (S3-compatible)
8. **`DATABASE_URL`** env var via `dj-database-url`
9. **Cookies `SameSite=None; Secure`** em produção (front/back em domínios diferentes)
10. **Build pipeline**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`

## Por que isso bloqueia OAuth (Google/Facebook)

OAuth requer **HTTPS público** para callback URL. Google permite `localhost` apenas em modo dev, Facebook bloqueia totalmente. Sem hospedar:
- Não consegue cadastrar OAuth app com callback `https://interpop.app/api/auth/google/callback/`
- Em dev funciona com tunelamento (ngrok/cloudflared) mas é frágil
- Produção quebra sem domínio próprio

## Caminho mais curto até OAuth funcionar

```
Dia 1: Vercel (front) + Fly (back) + Neon (db) + R2 (media)
       → site rodando em HTTPS público
Dia 2: Cadastrar OAuth apps Google Cloud Console + Facebook Developers
       → obter CLIENT_ID + CLIENT_SECRET pra ambos
Dia 3: Implementar django-allauth + wire dos botões de login social
       → fluxo completo: clique → redirect → callback → cookie JWT
```

## Status atual (2026-05-17)

- **Backend pronto pra deploy**: ❌ Falta ajustar settings/production.py (DEBUG, ALLOWED_HOSTS, CSRF, cookies), instalar django-storages + WhiteNoise
- **Frontend pronto pra deploy**: ⚠️ Provavelmente OK (Vite + React). Falta `VITE_API_URL` env apontando pro backend prod
- **OAuth**: ❌ Botões existem mas são placeholders sem onClick — implementação completa pendente até ter URLs públicas
- **Contas de provider**: ❌ Nenhuma criada ainda

## Decisão pendente

Qual provider de backend? **Fly.io** (recomendado por não-dormir) ou **Render** (mais simples mas dorme em free tier).

## Próximos passos (quando for hora)

1. Decidir Fly vs Render
2. Pedir pra preparar config files: `requirements.txt` + `settings/production.py` + `fly.toml`/`render.yaml` + `vercel.json` + `.env.production.example`
3. Criar contas Vercel + Fly/Render + Neon + Cloudflare (R2)
4. Deploy inicial
5. Configurar custom domain (opcional mas recomendado)
6. Cadastrar OAuth apps Google + Facebook usando as URLs reais
7. Implementar django-allauth no backend e wirear os botões no Login.tsx
