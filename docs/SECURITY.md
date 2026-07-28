---
type: "Security Boundary"
title: "Security"
description: "Documents Security for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - security-boundary
navigation:
  role: foundational
  order: 20
---
# Security

This document records the current security posture and the desired end state.

## Desired End State

The integration should be explicit about:
- its trust model,
- the LAN assumptions it relies on,
- any known plaintext or unauthenticated device communication,
- the boundaries between local control and cloud dependence.

## Current Observations

- device communication is local TCP-based,
- the repository assumes access to devices on the local network,
- the protocol client does not implement transport encryption,
- historical notes suggest CozyLife cloud/device communication may also be weakly protected or plaintext, but that has not been re-verified in this repository.

## Security Principles

- Never overstate confidentiality or authenticity guarantees.
- Treat the local network as partially trusted, not fully trusted.
- Document protocol weaknesses even if they are device-vendor constraints.
- Prefer local-only operation over cloud dependency where possible.

## Current Unknowns

- whether device commands are authenticated beyond LAN reachability,
- whether unsolicited packets can spoof state transitions,
- whether the protocol has any replay or pairing assumptions,
- whether sensor-class devices expose different security characteristics.

## Security Follow-Up

- capture protocol exchanges and inspect any `res` semantics,
- document the actual trust model once more live traffic is observed,
- convert historical notes into verified statements or remove them.

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
