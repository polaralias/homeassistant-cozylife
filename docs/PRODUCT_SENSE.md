---
type: "Repository Knowledge"
title: "Product Sense"
description: "Documents Product Sense for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - repository-knowledge
navigation:
  role: supporting
  order: 100
---
# Product Sense

This integration should be treated like a small product, not just a bag of protocol code.

## Product Outcome

The ideal user outcome is:
- install the integration,
- discover the device locally,
- understand what entities will appear,
- trust that the integration behaves consistently,
- recover from normal LAN drift without manual repair.

## Product Rules

- Do not claim support wider than verified support.
- Do not let legacy compatibility dominate the main user story.
- Do not hide reliability limits.
- Prefer fewer, clearer entity behaviours over more surprising ones.
- Do not promote a device class into supported status without contributor evidence from real hardware.
- State the evidence bar plainly when claiming a class is supported.
- Use partial support labels when a device works on real hardware but not all expected controls in the class are verified.

## Current Product Risks

- the current entity surface is not fully coherent,
- runtime behaviour has been partially verified on a live light but not on switches or sensors,
- the old README included claims that were stronger than current evidence.

## Repository knowledge

- [Documentation map](knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
