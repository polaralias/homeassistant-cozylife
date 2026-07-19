# Tested But Not Confirmed

This document tracks capability findings that have been exercised on real hardware but are not yet confirmed strongly enough to expose as product behaviour or Home Assistant entities.

Use this category when all of the following are true:

- the repository has real-hardware evidence,
- the behaviour is not yet semantically stable enough to claim publicly,
- the current integration does not expose it as a first-class surface,
- more protocol or product interpretation work is still required.

This is intentionally different from:

- `supported`
- `partially supported`
- `potentially supported`

Those are product-support labels. This document is an evidence register for ambiguous live findings.

## Current Entries

### `rju4K7` unknown catalogue DPIDs

Source artefacts:

- `docs/generated/rju4k7-live-validation-2026-05-19.md`
- `docs/generated/rju4k7-unknown-dpid-probe-2026-05-19.md`
- `docs/generated/parity-gap-register.md`

#### DPID `13`

Status:
- tested on real hardware
- not confirmed as an exposed repository capability

Current evidence:
- bounded writes were accepted
- broader probing showed that `13 = 1` reproducibly causes delayed power-off on the tested bulb
- other tested values did not yield a stable query-surface effect

Current interpretation:
- likely related to delayed off, timer behaviour, or a closely related shutdown control
- not yet semantically confirmed enough to expose in product docs or Home Assistant

Why not exposed:
- the broader contract is still unknown
- the behaviour has only been verified on one PID and one inferred semantic path
- the repository has not yet chosen a user-facing representation for it

#### DPID `44`

Status:
- tested on real hardware
- not confirmed as an exposed repository capability

Current evidence:
- accepts a broad numeric range in direct protocol writes
- rejects `65535`
- no accepted value produced an immediate or delayed observable query-surface effect in the probe window

Current interpretation:
- writable but semantically opaque
- could be write-only, mode-specific, delayed, or otherwise not visible through the current query model

Why not exposed:
- no stable user-visible meaning is known
- no clear Home Assistant mapping exists

#### DPID `9`, `14`, `15`

Status:
- probed on real hardware
- not confirmed as writable or exposed capabilities

Current evidence:
- bounded integer writes tested in this repository were rejected

Current interpretation:
- still unknown
- may require different value domains, stronger mode gating, or may not be directly writable

Why not exposed:
- no successful or semantically meaningful live behaviour has been established

## Repository Rule

Do not expose a tested-but-not-confirmed capability in product docs or Home Assistant unless:

- the semantic meaning is stable enough to describe clearly,
- the behaviour is reproducible,
- the repository can explain how it should appear to users,
- the support and parity docs are updated in the same session.
