# Contribuindo com o Interpop

> Documento curto e operacional. Para visão geral do projeto, ver [`README.md`](./README.md). Para regras técnicas profundas, ver [`AGENTS.md`](./AGENTS.md) (idêntico a `CLAUDE.md` via symlink).

---

## Fluxo de branches

```
feature/*  ──┐
bugfix/*   ──┼──►  develop  ──►  main
hotfix/*   ──┘
```

**Regras duras (impostas por ruleset + CI):**

1. **Ninguém faz push direto em `main`.** Bloqueado por ruleset.
2. **PR para `main` só vem de `develop`.** Validado pelo workflow [`branch-gate.yml`](./.github/workflows/branch-gate.yml).
3. **Force push em `main` é bloqueado.** Ruleset.
4. **Deleção de `main` é bloqueada.** Ruleset.
5. **Histórico linear em `main`.** Sem merge commits — usar squash ou rebase.
6. **CI verde antes de merge.** Todos os 8 status checks precisam passar (7 do CI + security + 1 do branch gate).

**Por que esse fluxo:** `develop` é a integração contínua (acumula features). `main` é o que está (ou estará) em produção — só recebe estado "estável". Hotfix segue o mesmo caminho: aplica em `develop`, valida, sobe pra `main`. Sem atalhos.

---

## Como abrir um PR

### Feature/bugfix nova

```bash
git checkout develop
git pull
git checkout -b feature/<nome-curto>   # ou bugfix/<nome-curto>
# ... trabalha, commita ...
git push -u origin feature/<nome-curto>
gh pr create --base develop --fill
```

### Quando develop está pronto para subir pra main

```bash
git checkout develop
git pull
gh pr create --base main --head develop --title "release: <resumo>"
# após CI verde:
gh pr merge <NUM> --squash
```

> Só `develop` pode ser source de PR para `main`. Tentar de outra branch falha no `branch-gate.yml`.

> **Método de merge para `main`: SEMPRE `--squash`.** Não usar `--rebase`. O ruleset exige `signed commits` (Require signed commits) e o GitHub **não auto-assina rebase merges** — as assinaturas dos commits originais quebram quando os parents mudam no rebase. Squash gera 1 commit em main que o GitHub assina automaticamente com sua chave (`web-flow`, `verified=true`). Para `develop` e branches de feature/bugfix, `--rebase` continua OK.

### Tipos de commit (`.commitlintrc.json`)

Aceitos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `sec`, **`deps`**. O `deps` é usado pelo Dependabot (`deps(npm)`, `deps(py)`, `deps(actions)`) — não trocar para `chore` em reescritas offline, perderia o link com o PR original.

### Signed commits (obrigatório para PRs para `main`)

Ruleset `protect-main` exige assinatura criptográfica. Setup SSH signing (uma vez por máquina):

```bash
# 1. Cadastrar chave SSH como SIGNING KEY no GitHub:
gh auth refresh -h github.com -s admin:ssh_signing_key
gh ssh-key add ~/.ssh/id_rsa.pub --type signing --title "interpop-signing-$(hostname)"

# 2. Configurar git para assinar todo commit:
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_rsa.pub
git config --global commit.gpgsign true

# 3. (opcional, p/ verificação local de assinaturas)
echo "$(git config user.email) $(awk '{print $1, $2}' ~/.ssh/id_rsa.pub)" > ~/.ssh/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

Verificar: `git log --pretty=format:"%h %G? %s"` — `G` (good) é signed, `N` é unsigned. Server-side: `gh api /repos/.../commits/<sha> --jq '.commit.verification'`.

---

## Convenção de commits

Formato:

```
<tipo>: <descrição em minúsculas>

[corpo opcional explicando o "porquê"]

Co-Authored-By: ...   # quando aplicável
```

Tipos aceitos (alinhados com commits recentes do repo):

| Tipo       | Quando usar                                      |
| ---------- | ------------------------------------------------ |
| `feat`     | Nova feature                                     |
| `fix`      | Bugfix                                           |
| `refactor` | Mudança de código sem alteração de comportamento |
| `test`     | Adição/ajuste de teste                           |
| `docs`     | Documentação                                     |
| `chore`    | Tooling, deps, build, configs                    |
| `perf`     | Otimização                                       |
| `style`    | Formatação (prettier/eslint), sem mudança lógica |

**Commits de agentes AI** (Claude, Copilot, etc.) DEVEM terminar com:

```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Ajustar o nome do modelo conforme o agente real. Ver [`AGENTS.md` §1](./AGENTS.md).

---

## Testes — REGRA INEGOCIÁVEL

Antes de qualquer modificação em código testável: ler [`docs/tests/testing-standards.md`](./docs/tests/testing-standards.md) e [`AGENTS.md` §6](./AGENTS.md).

**Resumo operacional:**

- Lógica nova → teste primeiro (TDD).
- Bugfix → teste de regressão reproduzindo o bug, depois fix.
- Refactor de área crítica sem cobertura → backfill de testes antes.
- PR não merge se cobertura desce. CI bloqueia automaticamente (gate atual: 40% backend, 30% frontend).

Cada execução manual de teste gera report em `docs/tests/reports/AAAA-MM-DD_HH-MM-SS.md` (formato §6.2 do `AGENTS.md`).

---

## Antes de pedir merge

Checklist mental rápido:

- [ ] Branch é `feature/*`, `bugfix/*` ou `hotfix/*` (PR para `develop`) OU é `develop` (PR para `main`)?
- [ ] Testes novos cobrem a mudança?
- [ ] `npm run test:cov` e `cd backend && uv run pytest` passam localmente?
- [ ] `npx tsc --noEmit` sem erros?
- [ ] `npm run lint:check` e `npm run check-format` limpos?
- [ ] Se mudou UI: passa WCAG 2.2 AA e Core Web Vitals não regrediram? (ver `AGENTS.md` §4)
- [ ] PR tem descrição clara do "porquê", não só do "o quê"?

---

## Quando algo escapa da política

Se você precisa contornar uma regra (ex.: hotfix urgente que não pode esperar `develop`):

1. **Não force push, não merge sem PR, não desabilite check.**
2. Abra issue ou comente no PR explicando a urgência.
3. Discuta antes de mudar configuração de ruleset. Decisões assim viram ADR no [`Improvement-system.md`](./docs/Improvement-system.md).

Política existe para reduzir variância em produção. Quebrar política precisa ser **decisão consciente e registrada** — não atalho silencioso.
