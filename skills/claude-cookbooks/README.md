# claude-cookbooks

A Claude Code skill that points to the official Anthropic Cookbook notebooks living locally at `/home/gabriel/Documentos/Projetos/claude-cookbooks-main/`, so any Claude API / Anthropic SDK feature in the Interpop project starts from a proven reference pattern instead of being implemented from scratch.

## When it triggers

Any task involving Claude API or Anthropic SDK: prompt caching, tool use, extended thinking, vision/multimodal, RAG, agent SDK, evals, sub-agents, moderation, JSON mode, classification.

## What it provides

- Catalog of 84+ notebooks organized by 9 categories.
- For each category: the notebooks that matter and what each covers.
- Hard rule: read the matching notebook **before** writing the code.
- Prompt caching default reminder (always consult `misc/prompt_caching.ipynb` for stable-system-prompt calls).

## Origin

Derived from the official Anthropic Cookbook repository, cloned locally at `/home/gabriel/Documentos/Projetos/claude-cookbooks-main/`.

## Installation

Source lives at `skills/claude-cookbooks/` in the Interpop repository. The Claude Code global directory `~/.claude/skills/claude-cookbooks/` symlinks here (single source of truth — same pattern as `ecossistemas-ui-ux` and `referencias-dashboards`).

## Usage

Auto-discovered by Claude Code when the conversation touches Claude API features. To force invocation, reference the skill explicitly in the prompt.

## Related

- `claude-api` (plugin) — live SDK guidance, current model IDs, prompt-caching defaults. Use **together** with this skill: `claude-cookbooks` for reference patterns, `claude-api` for current syntax.
- `superpowers@claude-plugins-official` — process discipline (TDD, debug, review) for the implementation work.
