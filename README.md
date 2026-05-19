# Interpop

> Projeto editorial independente que analisa criticamente o **Soft Power** e
> o papel da cultura pop na manutenção da hegemonia global.

A partir de música, moda, cinema, literatura e cultura digital, o Interpop
investiga como determinados atores exercem influência política de forma
indireta no sistema internacional.

---

## Stack

| Camada | Tecnologia |
|---|---|
| **Frontend** | React 19 + TypeScript + Vite + React Router 7 |
| **Backend** | Django 5 + Django REST Framework |
| **Banco** | SQLite (dev) · PostgreSQL recomendado (prod) |
| **Auth** | JWT em cookie httpOnly + django-axes (brute-force) |
| **Charts** | Recharts (dashboard de métricas admin) |
| **E-mail** | SMTP Gmail (welcome + notificações de artigo) |

## Rodar localmente

**Pré-requisitos:** Node ≥ 20.19 (Vite 8), Python ≥ 3.12.

```bash
# 1. Clonar
git clone git@github.com:GabeMarques-Intetsu/interpop.git
cd interpop

# 2. Backend (terminal 1)
cd backend
python -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env  # ajustar SECRET_KEY, EMAIL_*, etc
venv/bin/python manage.py migrate
venv/bin/python manage.py createsuperuser
venv/bin/python manage.py runserver  # http://127.0.0.1:8000

# 3. Frontend (terminal 2)
npm install
npm run dev  # http://localhost:5173
```

## Estrutura

```
interpop/
├── backend/                    # Django API
│   ├── apps/
│   │   ├── articles/           # Posts + categorias + signal de notify
│   │   ├── audit/              # Middleware + endpoint de métricas
│   │   ├── comments/           # Comentários + curtidas
│   │   ├── moderation/         # Banimentos
│   │   ├── newsletter/         # Inscrições + templates de e-mail
│   │   └── users/              # Auth (JWT), permissões
│   └── config/settings/        # base, development, production
├── src/                        # React app
│   ├── pages/                  # Home, Article, News, Admin, etc
│   ├── components/             # UI compartilhada (NewsCard, Modal, ...)
│   ├── services/               # Camada axios → Django
│   ├── router/                 # Rotas + ScrollToHashOrTop
│   └── utils/                  # Helpers puros (renderArticleBody, etc)
├── docs/                       # ecossistema_ui_ux, dashboards, deploy
│   └── Logos/                  # Variantes do logo (SVG + assinatura)
└── AGENTS.md                   # Regras de UI/UX e convenções
```

## Convenções

- **Lint/typecheck**: `npx tsc -b` deve sair com `exit 0` antes de qualquer push
- **Commits AI** incluem `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>`
- **Padrão UI/UX**: ver `AGENTS.md` (combina galerias, design systems, auditorias, Mobbin e CSS Stats)
- **Padrão dashboards**: ver `docs/guia_referencias_dashboards.pdf` referenciado em `AGENTS.md`

## Documentação adicional

- [AGENTS.md](AGENTS.md) — regras de UI/UX e convenções do projeto
- [docs/HOSTING-DEPLOY-PLAN.md](docs/HOSTING-DEPLOY-PLAN.md) — stack de hospedagem (Vercel + Fly.io + Neon + R2)
- [docs/LOGO-TODO.md](docs/LOGO-TODO.md) — estado e pendências da identidade visual
- [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) — documentação técnica geral

## Licença

A definir.
