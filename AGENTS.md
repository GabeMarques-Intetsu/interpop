# Agent Instructions — Interpop

## Package Manager
Use **npm**: `npm install`, `npm run dev`, `npm run build`, `npm run lint`

## File-Scoped Commands
| Task | Command |
|------|---------|
| Typecheck | `npx tsc --noEmit` |
| Lint | `npx eslint src/path/to/file.tsx` |
| Build | `npm run build` |
| Dev server | `npm run dev` |

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

## Padrão `ecossistemas_ui_ux`

Fonte: `ecossistema_ui_ux_revisado.pdf`. Antes de decidir qualquer questão de UI/UX, **combinar fontes** das 5 categorias — nenhuma cobre tudo.

### 1. Galerias de referência (inspiração visual)
| Fonte | Uso |
|-------|-----|
| **Awwwards** (`awwwards.com`) | Sites avaliados por especialistas — usabilidade, criatividade, conteúdo. Filtros por categoria e prêmios diários. |
| **Godly** (`godly.website`) | Curadoria nichada, design minimalista e tipografia forte. Tendências editoriais. |
| **Siteinspire** (`siteinspire.com`) | Clássico, com filtros por estilo, tipo de projeto e paleta de cores. |

### 2. Sistemas de design (padrões de big tech)
| Sistema | Uso |
|---------|-----|
| **Material Design** (Google) | Componentes, acessibilidade, espaçamento e responsividade. Base Android. |
| **Apple HIG** | Padrão iOS/macOS. Interações por gesto, voz e teclado + acessibilidade nativa. |
| **Carbon (IBM) / Fluent (Microsoft)** | Tokens de design, componentes com variantes de acessibilidade, código aberto. |

### 3. Auditorias e acessibilidade (validação técnica)
| Ferramenta | Uso |
|------------|-----|
| **Google Lighthouse** | Chrome DevTools. Performance, acessibilidade, SEO, boas práticas (0–100). |
| **WebAIM / WAVE** | Conformidade WCAG. Erros de contraste, estrutura e semântica. |
| **PageSpeed Insights** | Lighthouse online + Core Web Vitals reais de usuários. |

### 4. Comunidades de design (inspiração diária)
| Comunidade | Uso |
|------------|-----|
| **Mobbin** (`mobbin.design`) | UI mobile/web de apps reais (Airbnb, Notion, Figma). Padrões em contexto real. |
| **Muzli** | Extensão Chrome — feed diário dos melhores designs. |
| **Dribbble / Behance** | Tendências visuais e estilos emergentes (estética > usabilidade). |

### 5. Análise técnica (stack + código)
| Ferramenta | Uso |
|------------|-----|
| **CSS Stats** (`cssstats.com`) | Complexidade, seletores, cores e fontes de qualquer site. |
| **a11y Project** | Checklist de acessibilidade baseado em WCAG 2.1 e 2.2. |
| **BuiltWith / Wappalyzer** | Tecnologias, frameworks e bibliotecas de qualquer site. |

### Fluxo de aplicação (ordem obrigatória)
1. **Buscar inspiração** — Awwwards/Godly para tendências alinhadas ao projeto.
2. **Estudar padrões** — Material/Apple HIG para entender os princípios, não só a estética.
3. **Observar apps reais** — Mobbin para ver como líderes resolvem UX em contexto real (não em mockups).
4. **Validar com métricas** — Lighthouse + WAVE em referências e no próprio produto.
5. **Monitorar tecnicamente** — CSS Stats + Wappalyzer para entender stack e padrões de implementação.

### Princípio-guia
> Observar como líderes resolvem problemas, não copiar estética. Bom design é **funcional, acessível e rápido** — auditoria torna isso mensurável, não subjetivo.

## Padrão `referencias_dashboards`

Fonte: `docs/guia_referencias_dashboards.pdf`. Antes de projetar ou refatorar qualquer dashboard, **cruzar fontes** das 3 categorias — cada uma resolve um problema diferente (estética, lógica de negócio, densidade de dados).

### 1. Design de interface e componentização (UI/UX)
Para estrutura visual, comportamento responsivo, paletas (light/dark) e componentes reutilizáveis.

| Fonte | Uso |
|-------|-----|
| **Figma Community** | Pesquisar `"CRM Dashboard"`, `"SaaS Analytics"`. Medir espaçamentos exatos, exportar SVGs, extrair tipografia e paletas prontas para código. |
| **Tailwind UI / componentes da comunidade** | HTML limpo, grids modernos, sidebars colapsáveis, tabelas com paginação. Acelera dev full-stack mantendo responsividade. |
| **Dribbble / Behance** | Tendências de vanguarda (micro-interações, glassmorphism, cartões flutuantes). Quebrar monotonia de layouts admin. |

### 2. Métricas de negócio e KPIs setoriais
Para decidir **quais dados exibir**, como resumir operações em cartões primários/secundários, e qual gráfico usar.

| Fonte | Uso |
|-------|-----|
| **Klipfolio (Dashboard Examples Gallery)** | Painéis por setor (Vendas, Executivo, Marketing, Finanças). Cruzamento de dados (conversão, MoM, CAC). Prioriza agregados monetários/percentuais no topo, detalhamento gráfico abaixo. |
| **Geckoboard Examples** | Monitorização em tempo real, ecrãs partilhados. Filosofia minimalista — foca no que exige ação imediata, evita sobrecarga. |

### 3. Business Intelligence e análise densa
Para grande volume de dados, filtros avançados, segmentações dinâmicas e relatórios corporativos densos.

| Fonte | Uso |
|-------|-----|
| **Power BI Data Stories Gallery** | Relatórios de analistas seniores: cadeias de suprimentos, demografia regional, consolidações fiscais. |
| **Looker Studio Template Gallery** | Integração web/APIs de anúncios: funis de conversão, comportamento de cliques, performance de campanhas. |

### Boas práticas de implementação (regras técnicas obrigatórias)
- **Paleta**: máximo 3 cores principais para evitar ruído visual.
- **Cartões de resumo**: agrupados com `border-radius` suave (cantos ligeiramente arredondados).
- **Filtros principais**: sempre acessíveis no topo da página ou na sidebar estática (nunca escondidos em modais).
- **Hierarquia vertical**: agregados monetários/percentuais no topo, detalhamentos gráficos abaixo (regra Klipfolio).
- **Densidade**: minimalismo Geckoboard para painéis operacionais; densidade Power BI/Looker apenas quando há filtros que permitam drill-down.

### Fluxo de aplicação (ordem obrigatória)
1. **Definir o tipo de dashboard** — operacional (Geckoboard), de negócio (Klipfolio) ou analítico (Power BI/Looker)?
2. **Mapear KPIs** — listar métricas primárias (topo) e secundárias (abaixo) antes de desenhar.
3. **Buscar inspiração visual** — Figma Community + Tailwind UI para layout e componentização do tipo escolhido.
4. **Refinar estética** — Dribbble/Behance apenas para micro-interações e detalhes finais.
5. **Validar contra `ecossistemas_ui_ux`** — Lighthouse + WAVE + Mobbin (todo dashboard é UI/UX antes de ser dashboard).

### Princípio-guia
> Dashboard ruim mostra tudo; dashboard bom mostra o que importa **na ordem que importa**. Hierarquia vertical, paleta restrita e filtros sempre visíveis são inegociáveis.

## Key Conventions
- Stack: React 19 + TypeScript + Vite + React Router 7
- Backend separado em `backend/`
- Antes de propor qualquer mudança de UI/UX, aplicar o padrão `ecossistemas_ui_ux` acima
- Antes de projetar ou refatorar qualquer dashboard, aplicar o padrão `referencias_dashboards` acima
- Validar acessibilidade (WCAG 2.2) e Core Web Vitals em toda entrega de frontend
