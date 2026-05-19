# Documentation Harness Plan

Status: Active

## Objective

Turn inherited analysis into a durable documentation system that separates:
- current verified behavior,
- desired end state,
- active technical debt,
- execution plans.

The harness must also make future implementation sessions intelligible from the maintained docs alone, without requiring a fresh repository archaeology pass.

## Deliverables

- rewritten top-level docs,
- architecture doc,
- design-doc index and principle docs,
- product-spec index and core specs,
- reliability and security posture docs,
- active debt tracker,
- explicit evidence bar for promoting device classes into supported status.
- explicit catalog provenance and CI policy for upstream snapshot drift.

## Exit Criteria

- a new reader can understand the repository without relying on stale README claims,
- the repo clearly distinguishes verified facts from targets,
- future refactors can point at explicit desired outcomes,
- archaeology outputs are clearly treated as dated evidence rather than permanent root-level canon,
- a future agent given a light prompt can identify the canonical docs, the current support policy, and the next safe implementation seam.
