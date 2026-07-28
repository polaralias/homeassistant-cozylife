---
type: "Delivery Plan"
title: "Documentation Harness Plan"
description: "Documents Documentation Harness Plan for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - delivery-plan
navigation:
  role: supporting
  order: 100
---
# Documentation Harness Plan

Status: Active

## Objective

Turn inherited analysis into a durable documentation system that separates:
- current verified behaviour,
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
- explicit catalogue provenance and CI policy for upstream snapshot drift.

## Exit Criteria

- a new reader can understand the repository without relying on stale README claims,
- the repo clearly distinguishes verified facts from targets,
- future refactors can point at explicit desired outcomes,
- archaeology outputs are clearly treated as dated evidence rather than permanent root-level canon,
- a future agent given a light prompt can identify the canonical docs, the current support policy, and the next safe implementation seam.

## Repository knowledge

- [Documentation map](../../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
