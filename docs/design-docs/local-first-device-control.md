---
type: "Design Concept"
title: "Local-First Device Control"
description: "Documents Local-First Device Control for the homeassistant-cozylife repository."
timestamp: 2026-07-28T21:55:36Z
authority: canonical
verification: untested
owner: polaralias
tags:
  - homeassistant-cozylife
  - design-concept
navigation:
  role: supporting
  order: 100
---
# Local-First Device Control

## Principle

The integration should work as a local-network product first and only.

## Desired Outcome

A user should be able to:
- add the integration in Home Assistant,
- discover verified supported devices on the LAN,
- control them without relying on CozyLife cloud services,
- keep them working even if the device IP changes.

## Current Evidence

- the repository uses TCP and UDP LAN discovery paths,
- a real bulb was discovered and queried locally on `2026-05-16`,
- the live bulb was reachable through the repo client without using a cloud API.

## Implications

- local discovery and reconnect behaviour are tier-one engineering concerns,
- cloud behaviour should only appear in docs as contextual caution unless verified.

## Repository knowledge

- [Documentation map](../knowledge/documentation-map.md) — RKE-managed reading order and relationship hub.
