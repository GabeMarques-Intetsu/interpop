<!-- MINIMAL TEMPLATE — copy to PM-NN-<slug>.md. This skill owns the TRACEABILITY + the home, not the
     authoring craft. For the blameless write-up (timeline, 5-whys, root cause, action items) use the
     documentation-engineer agent / the `postmortem-writing` skill. Keep the ↑/←/↓ links below filled. -->

# PM-NN — <incident title> (<DD/MM/YYYY>)

> **Type**: Postmortem (production-incident record — NOT a backlog item)
> **Severity**: 🔴 SEV1 | 🟠 SEV2 | 🟡 SEV3
> **Status**: 🚧 Draft | ✅ Reviewed | 📦 Closed (all actions tracked)
> **Date / duration**: DD/MM/YYYY · <downtime / blast radius>

---

## Summary (blameless)

<2–3 lines: what happened, who/what was affected, business impact. Full write-up → `postmortem-writing` skill.>

## Traceability ↑ (which requirement failed in production)

| Failed                                             | ID       | Where                                                                     |
| -------------------------------------------------- | -------- | ------------------------------------------------------------------------- |
| Dependability `RNF` (avail/reliability/resilience) | `RNF-NN` | [RNF](../requirements/RNF/RNF-....md) — e.g. `AVAIL`/`RTO`/`RPO` breached |
| Acceptance Criterion (if a `CA` was violated)      | `CANN`   | [F-NN](../backlog/features/F-NN-....md)                                   |

## Origin ← (how it surfaced)

- Triaged from: [`ISS-NN`](../backlog/support-quality-investigation/issues/ISS-NN-....md) _(an incident is a triage outcome of the issues inbox)_ — or a monitoring alert (state which).

## Corrective actions ↓ (the loop back to the backlog)

| Action                         | Becomes      | Where                                                                   |
| ------------------------------ | ------------ | ----------------------------------------------------------------------- |
| Fix the defect                 | `BUG-NN`     | [bugs/](../backlog/bugs/)                                               |
| Technical / infra hardening    | `TX-NN`      | [support/](../backlog/support-quality-investigation/support/)           |
| Capture the recovery procedure | `RB-NN`      | [runbooks/](../runbooks/)                                               |
| Tighten the requirement        | RNF revision | the **requirements document first** (`SKILL.md §2.1`), then the backlog |

> **The loop**: an incident that changes a requirement flows through the requirements document **first** (rule zero) — never straight into the backlog. Each action item has a `BUG/TX/RB` id so it is tracked to closure.
