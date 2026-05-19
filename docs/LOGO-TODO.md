# Logo — pendências

## Estado atual (2026-05-17)

**SVG em produção**: [src/assets/interpop-logo.svg](../src/assets/interpop-logo.svg) (+ [public/interpop-logo.svg](../public/interpop-logo.svg)).
**Fonte original**: `docs/Logos/sugestão #01 base_*.svg` (auto-trace do PNG original).

**Em uso em:**
- [src/components/layout/Navbar.tsx](../src/components/layout/Navbar.tsx) (header, fundo claro — sem filter)
- [src/components/layout/Footer.tsx](../src/components/layout/Footer.tsx) (rodapé navy — `filter: brightness(0) invert(1)`)
- [src/components/layout/AuthLayout.tsx](../src/components/layout/AuthLayout.tsx) (painel navy — invertido)
- [src/pages/Admin/index.tsx](../src/pages/Admin/index.tsx) (sidebar navy escuro — invertido)
- [src/pages/Home.tsx](../src/pages/Home.tsx) (hero visual panel — invertido)
- [public/favicon.svg](../public/favicon.svg) (favicon redesenhado em SVG navy com mark "i")

**Otimizações já feitas:**
- Background rects brancos removidos do SVG (eram opacos e inviabilizavam `filter: invert`)
- `viewBox` cortado de `0 0 1500 1500` (canvas com padding) para `150 560 1200 350` (só wordmark)
- Atributos `width`/`height` fixos removidos do `<svg>` raiz pra honrar CSS

## Pendências (nice-to-have)

1. **Variante branca explícita** — `interpop-logo-white.svg`
   - Elimina o hack `filter: brightness(0) invert(1)` no footer/auth/admin/hero
   - Permite tipografia mais precisa (filter degrada bordas em densidades baixas)
   - Custo: trocar `fill="#19144c"` por `fill="#ffffff"` no SVG e salvar separado

2. **Mark compacto** — `interpop-mark.svg`
   - Só o globo "pop" como ícone autônomo
   - Substitui o favicon atual (que é uma adaptação genérica com "i")
   - Útil pra OG image, badges, app icon

3. **Open Graph / metadados sociais**
   - Gerar `public/og-image.png` 1200×630 com logo + tagline editorial
   - Adicionar `<meta property="og:image">` no [index.html](../../index.html)
   - Melhora preview em WhatsApp, Twitter, LinkedIn quando compartilhado

4. **PNG legado** — pode deletar quando confirmar tudo OK visualmente em produção
   - [src/assets/interpop-logo.png](../src/assets/interpop-logo.png) (95 KB)
   - [public/interpop-logo.png](../public/interpop-logo.png) (95 KB)

## Decisões registradas

- **2026-05-17**: Migração PNG → SVG completa. Background rects removidos via Python regex. viewBox cortado manualmente após inspeção empírica das coordenadas dos paths.
- **2026-05-17**: Tamanhos calibrados pós-crop do viewBox: navbar 38px, footer 40px, auth 48px, admin sidebar 36px, home hero `clamp(220px, 65%, 380px)`.
