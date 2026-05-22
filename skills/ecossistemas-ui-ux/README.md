# ecossistemas-ui-ux

A Claude Code skill that loads a five-category reference ecosystem (galleries, design systems, audits, communities, technical analysis) for any UI/UX decision in projects where visual quality, accessibility, and performance must be measurable — not subjective.

## When it triggers

Any UI/UX task: design, redesign, audit, component selection, palette/typography choice, WCAG validation, Core Web Vitals review, or comparison against industry leaders.

## What it provides

- Curated list of references per category — Awwwards, Apple HIG, Lighthouse, Mobbin, CSS Stats, and 10+ more.
- Mandatory application order: inspire → study → watch → validate → monitor.
- Guiding principle: "observe how leaders solve problems; do not copy aesthetics."
- Hard rule: never ship a visual choice that fails Lighthouse or WAVE.

## Origin

Derived from `docs/references/ecossistema_ui_ux_revisado.pdf` of the Interpop editorial project, which curates the same five-category map used by editorial newsrooms and design systems teams.

## Installation

Source lives in this project at `skills/ecossistemas-ui-ux/`. The path `~/.claude/skills/ecossistemas-ui-ux/` is a **symlink** to here — single source of truth as documented in [`skills/README.md`](../README.md). Edit only the in-project version.

## Usage

Inside Claude Code, the skill is auto-discovered by the orchestration protocol whenever a UI/UX task is detected. To force invocation, reference the skill name explicitly in the prompt (e.g., "apply `ecossistemas-ui-ux`") or invoke via the Skill tool.

## Related

- Companion standard for dashboards: `referencias_dashboards` (in the project's `AGENTS.md`).
- Complementary plugins: `frontend-design@claude-plugins-official` (component patterns), `superpowers@claude-plugins-official` (process: TDD, debugging, review).
