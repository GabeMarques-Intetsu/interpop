<!-- MINIMAL TEMPLATE — copy to RB-NN-<slug>.md. This skill owns the TRACEABILITY + the home; the step
     authoring (commands, verification, rollback) belongs to documentation-engineer / incident-runbook-templates. -->

# RB-NN — <runbook title>

> **Type**: Runbook (operational procedure — NOT a backlog item)
> **Trigger**: <when to run — alert, deploy, recovery, key rotation, scaling…>
> **Status**: 🚧 Draft | ✅ Validated (dry-run passed)

---

## Purpose

<one line: the operational outcome this procedure achieves.>

## Traceability ↑ (which requirement it operationalizes)

| Operationalizes                 | ID       | Where                                                                   |
| ------------------------------- | -------- | ----------------------------------------------------------------------- |
| Resilience / availability `RNF` | `RNF-NN` | [RNF](../requirements/RNF/RNF-....md) — e.g. `RTO` 15 min / `RPO` 5 min |
| Feature / spec it serves        | `F-NN`   | [F-NN](../backlog/features/F-NN-....md)                                 |

## Procedure

> Steps + verification + rollback → author with the `documentation-engineer` agent / `incident-runbook-templates` skill.

1. <step> → **verify**: <how you know it worked>

## Related

- Postmortems that exercised / updated this runbook: `PM-NN`.
