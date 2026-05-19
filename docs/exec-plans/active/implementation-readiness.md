# Implementation Readiness

Status: Active

## Objective

Make future implementation sessions succeed from a light prompt such as "follow `AGENTS.md` and use TDD" without requiring a fresh archaeology pass.

This document is not a full implementation roadmap. It is the bridge between:
- canonical repository truth,
- dated evidence artifacts,
- the next safe unit of engineering work.

## Current Contract For Implementers

Before changing code, use this order:
1. `AGENTS.md`
2. `ARCHITECTURE.md`
3. `docs/PLANS.md`
4. `docs/SUPPORT.md`
5. `docs/RELIABILITY.md`
6. relevant design docs and product specs
7. `docs/exec-plans/tech-debt-tracker.md`
8. evidence artifacts only as needed

Implementation assumptions that are safe today:
- lights are the only verified supported surface,
- switches and sensors are available code paths and potentially supported surfaces,
- periodic rediscovery for stale IP recovery is part of the current intended runtime behavior,
- mixed config-entry shapes are a real compatibility surface,
- `model.json` is a catalog snapshot and parity target, not a support declaration.

## TDD Entry Guidance

When asked to use TDD, prefer behavior slices that can be named in repository language and exercised through a public interface.

Best current seams:
- config-flow onboarding behavior in `config_flow.py`
- config-entry normalization and migration behavior in `__init__.py`
- discovery and rediscovery behavior in `discovery.py` and `__init__.py`
- entity-surface classification behavior in `light.py`, `switch.py`, and `sensor.py`
- sensor datapoint exposure behavior in `sensor.py`

Higher-risk seam:
- command-success semantics in `tcp_client.py`

Why higher risk:
- the repository now has automated coverage for fragmented framed reads, top-level `sn` correlation, matching `set` acknowledgments, and explicit negative `res` handling,
- live protocol evidence is still incomplete for longer sessions and malformed/truncated responses,
- stronger changes in this area should continue to follow live protocol evidence or a clear simulated protocol contract.

## Immediate Readiness Gaps

### Automated test harness

Current state:
- the repository now has an in-tree `tests/` directory and checked-in pytest configuration,
- current automated coverage exercises entity-surface policy, light active-mode resolution, TCP framed-read/correlation/acknowledgment handling, config-entry migration cleanup, legacy options storage convergence, broadcast rediscovery IP repair, and IP-only import probing,
- the harness uses plain pytest async tests with local fakes so it runs reliably in the current Windows environment.

Desired state:
- the minimal automated harness continues to expand around focused TDD slices,
- tests name repository concepts such as onboarding, rediscovery, entity surface, and support-policy behavior,
- tests verify public behavior rather than internal helper calls.

Verification status:
- resolved for the initial repair slices; coverage breadth still needs expansion.

### Documented debt without implementation sequencing

Current state:
- the main debt items are named,
- but future implementation sessions still need a clear statement of which surfaces are safe to attack first.

Desired state:
- the first implementation sessions choose small documented seams,
- each session closes one explicit debt item, parity gap, or support-promotion slice,
- broad refactors are deferred until the harness exists and one or more slices have proven it out.

Verification status:
- resolved by this document and now exercised by multiple focused implementation sessions covering entity-surface policy, DIY support, TCP-client behavior, rediscovery behavior, and live light validation.

## Safe First-Slice Heuristics

- Prefer code paths already described by both `ARCHITECTURE.md` and a product spec.
- Prefer a slice where current behavior and desired behavior are both already named in docs.
- Prefer a slice that can be tested without live hardware first, then extended with live verification later.
- Avoid starting with broad protocol rewrites or sweeping entity refactors.
- If the chosen slice changes support claims, update `docs/SUPPORT.md` and the parity register in the same session.

## Success Condition

This repository is implementation-ready when a new agent can:
- read the canonical docs,
- identify one explicit debt item or parity gap,
- add or use a minimal automated test for that public behavior,
- make the smallest code change that satisfies the test and the documented contract,
- update the canonical docs only where the behavior contract changed or was newly verified.
