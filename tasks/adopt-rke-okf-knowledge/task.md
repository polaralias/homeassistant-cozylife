---
type: Task
task: adopt-rke-okf-knowledge
title: Adopt RKE OKF knowledge format
description: Represent durable repository knowledge and migration evidence in the
  full RKE OKF format.
status: done
created: '2026-07-28T21:56:59Z'
timestamp: '2026-07-28T23:10:48Z'
owner: polaralias
time:
- id: 20260728t215701z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T21:57:01Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Adjusted allocation from one shared cross-repository migration and validation
    session; prevents duplicate portfolio effort.
  basis: 'Wall-clock session was 19 minutes. Active effort was adjusted to 3 minutes:
    Adjusted allocation from one shared cross-repository migration and validation
    session; prevents duplicate portfolio effort.'
  finished: '2026-07-28T22:16:22Z'
  elapsed_minutes: 19
  effort_minutes: 3
- id: 20260728t223500z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T22:35:00Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Adjusted allocation from one shared branch-rename, duplicate-removal, and
    exhaustive Markdown census session.
  basis: 'Wall-clock session was 4 minutes. Active effort was adjusted to 1 minutes:
    Adjusted allocation from one shared branch-rename, duplicate-removal, and exhaustive
    Markdown census session.'
  finished: '2026-07-28T22:39:00Z'
  elapsed_minutes: 4
  effort_minutes: 1
- id: 20260728t225556z-codex-tracked
  status: closed
  actor: codex
  started: '2026-07-28T22:55:56Z'
  method: tracked-adjusted
  activity: knowledge-maintenance
  summary: Generated, integrated, and validated repository-wide HTML and Mermaid OKF
    visualizations.
  basis: 'Wall-clock session was 15 minutes. Active effort was adjusted to 1 minutes:
    Generated, integrated, and validated repository-wide HTML and Mermaid OKF visualizations.'
  finished: '2026-07-28T23:10:45Z'
  elapsed_minutes: 15
  effort_minutes: 1
started: '2026-07-28T21:57:01Z'
effort_minutes: 5
completion_history:
- finished: '2026-07-28T22:17:32Z'
  reopened: '2026-07-28T22:34:59Z'
- finished: '2026-07-28T22:39:25Z'
  reopened: '2026-07-28T22:55:56Z'
finished: '2026-07-28T23:10:47Z'
---

# Adopt RKE OKF knowledge format

## Outcome

Durable repository knowledge is represented with portable, plaintext OKF metadata, connected through an RKE-managed relationship graph, and kept distinct from operational Task state and specialised producer-owned schemas.

## Scope

- In scope: type and connect 29 durable knowledge documents; create and validate the bounded `docs/knowledge/` bundle; record this migration as an OKF Task; generate repository-wide HTML and Mermaid views.
- In scope: preserve canonical, evidence, derived, generated, instruction, handoff, fixture, and task boundaries.
- Out of scope: change product behaviour, upgrade support claims, rewrite historical evidence, publish externally, or alter generated/vendor content outside its owning workflow.

## Acceptance

- [x] Classify durable documents and deliberate schema exclusions.
- [x] Add required and recommended plaintext RKE OKF metadata.
- [x] Connect governed knowledge and execution concepts through repository-relative links.
- [x] Preserve reserved indexes and specialised document schemas.
- [x] Classify all 44 in-scope repository Markdown files with zero omissions.
- [x] Remove the redundant repository overview and confirm zero exact duplicate governed knowledge bodies.
- [x] Build and validate the `docs/knowledge/` bundle.
- [x] Validate the OKF Tasks bundle in strict mode.
- [x] Generate repository-wide standalone HTML and scalable Mermaid visualizations with persisted exclusions.
## Dependencies and risks

- The installed `okf-tasks 0.1.0` package is missing its task-body asset; the feature-identical bundled reference CLI is used instead.
- Metadata migration does not upgrade the evidential strength of existing repository claims.
- Existing manual indexes, generated documents, handoffs, fixtures, and skill packages retain their owning formats.

## Related knowledge

- [Documentation map](../../docs/knowledge/documentation-map.md)
- [Repository visualization](../../docs/knowledge/repository-visualization.md)

## Workstreams

- No separately owned workstreams are required.

## Evidence

- RKE bundle validation: conformant (3 concepts, 1 generated index).
- OKF Tasks strict validation: valid (1 task, 0 workstreams, 0 warnings).
- Visualization freshness: standalone HTML and Mermaid outputs match the repository records and persisted exclusion policy.
- Complete Markdown census: 44 in-scope files, 0 unclassified, 0 exact duplicate governed knowledge bodies.
