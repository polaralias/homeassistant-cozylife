# Repository Operating Guide

This file defines how humans and agents should work in this repository.

## Core Rules

- Keep HACS metadata updates manual.
- When preparing a release, bump `custom_components/cozylife/manifest.json` explicitly.
- If needed, adjust `hacs.json` explicitly in the same deliberate change.
- Do not introduce workflows or scripts that automatically commit or push version changes on merge.
- Prefer standard HACS versioning through manual releases and Git tags.

## Documentation Rules

- Treat existing prose as unverified until it is supported by code or live validation.
- Treat code as intent, not proof.
- When documentation states a desired end state, label it clearly as target-state guidance rather than current behavior.
- Prefer outcome-focused docs over historical narration.
- When behavior has been validated on real hardware or in a live Home Assistant runtime, record the evidence and date.

## Current Product Frame

This repository is a Home Assistant custom integration for CozyLife devices on the local network.

Current observed scope:
- config-flow onboarding,
- local discovery by TCP scan and UDP broadcast assistance,
- light entities,
- switch entities,
- sensor datapoint entities,
- periodic rediscovery to repair stale device IP addresses.

Current verified support:
- lights are verified on real hardware,
- switches and sensors are code-observed but not yet hardware-verified.

Do not use this summary as the primary architecture source. See `ARCHITECTURE.md` and `docs/` for maintained documentation.

## Preferred Documentation Sources

Use these files in this order:

1. `AGENTS.md`
2. `GLOSSARY.md`
3. `ARCHITECTURE.md`
4. `docs/PLANS.md`
5. `docs/exec-plans/active/implementation-readiness.md`
6. `docs/RELIABILITY.md`
7. `docs/SUPPORT.md`
8. `docs/SECURITY.md`
9. `docs/design-docs/`
10. `docs/product-specs/`
11. `docs/exec-plans/`

Treat `CODEBASE_MAP.md` and `VERIFICATION_AUDIT.md` as dated evidence artifacts, not as the final canonical documentation layer.

## Implementation Session Rules

- When a task asks for code changes with a light prompt, infer the intended behavior from the preferred documentation sources before asking broad clarifying questions.
- When a task says to use TDD, work in vertical slices against public behavior rather than implementation details.
- Prefer test seams around:
  - config-flow onboarding behavior,
  - discovery and rediscovery behavior,
  - config-entry normalization and migration behavior,
  - entity-surface classification and exposure,
  - protocol client query/control behavior where evidence exists.
- If the repository lacks a suitable automated harness for the slice you need to change, first add the smallest test harness required to exercise that public behavior.
- Do not let a missing test harness become an excuse for blind refactoring.

## Change Discipline

- Do not refactor code unless the task explicitly calls for code changes.
- When documenting bugs or ambiguity, describe the current observed behavior, the desired end state, and the verification status.
- Keep generated or machine-derived reference output isolated under `docs/generated/`.
- Keep active planning and debt tracking isolated under `docs/exec-plans/`.
