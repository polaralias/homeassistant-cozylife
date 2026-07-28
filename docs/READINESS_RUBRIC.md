---
type: "Delivery Plan"
title: "Readiness Rubric"
description: "Documents Readiness Rubric for the homeassistant-cozylife repository."
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
# Readiness Rubric

This document replaces subjective quality scoring with explicit readiness conditions.

## Purpose

Use this rubric to decide whether the repository is ready for:
- public presentation,
- wider contributor use,
- support-claim expansion,
- deeper refactor work.

## Readiness Dimensions

### 1. Documentation Truth

Ready when:
- root docs no longer repeat invalidated claims,
- support policy has one canonical home,
- architecture, reliability, security, and support language agree,
- archaeology outputs are clearly marked as evidence artefacts rather than canon.

Current state:
- largely in place,
- still dependent on continued cleanup as evidence docs are folded into canon over time.

### 2. Support Policy Clarity

Ready when:
- support labels are explicit,
- evidence bar is explicit,
- contributor promotion path is explicit,
- unsupported but available code paths are clearly labelled.

Current state:
- in place through `docs/SUPPORT.md` and related docs.

### 3. Model/PID Truth Tracking

Ready when:
- parity tracking exists per concrete model/PID,
- support decisions are not made at vague class level alone,
- mismatches with `model.json` are recorded explicitly.

Current state:
- started with a seeded parity register,
- not yet mature.

### 4. Live Validation

Ready when:
- at least one first-class supported model has explicit discovery, query, and control evidence recorded against the current repository state,
- contributor guidance exists for validating additional models,
- unsupported classes are not overstated.

Current state:
- in place for the seeded light truth unit,
- lights are first-class supported by policy and prior real-world use,
- the seeded parity register entry now includes explicit current-state reversible brightness control evidence from `2026-05-17`.

### 5. Catalogue Governance

Ready when:
- upstream provenance for `model.json` is documented,
- CI policy for upstream diffing is documented,
- upstream breadth is not confused with maintained support.

Current state:
- documented,
- workflow not yet implemented.

### 6. Entity-Surface Coherence

Ready when:
- the repository has one intentional policy per device class,
- drift such as switch-as-light compatibility behaviour is either removed or explicitly justified,
- user-facing entity expectations are predictable.

Current state:
- policy is defined,
- implementation drift remains.

### 7. Refactor Safety

Ready when:
- canonical docs describe desired behaviour,
- major truth mismatches are named,
- parity gaps are tracked,
- support policy is stable enough that code changes can target explicit outcomes.

Current state:
- materially improved,
- ready for focussed implementation work, not yet for large blind refactors.

### 8. TDD Readiness

Ready when:
- a minimal automated test harness exists in-tree,
- new work can start from one public-behaviour test slice rather than a rediscovery pass,
- tests can target documented product behaviour without overfitting to helper internals.

Current state:
- documentation is ready enough to guide TDD,
- the automated harness itself is still missing.

## Practical Gate

The repository is ready for public-facing iteration when:
- documentation truth is stable,
- support policy is canonical,
- one supported model has explicit current-state evidence,
- unsupported classes are clearly labelled,
- upstream catalogue drift is visible or at least documented as managed debt.

## Practical Gate For Expanding Support

A new device class or model should not be promoted unless:
- it meets the support evidence bar in `docs/SUPPORT.md`,
- it has a parity register entry,
- its entity surface is documented,
- any gaps against `model.json` are recorded.

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
