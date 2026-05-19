# CI

This document records the desired CI posture for the repository.

## Current State

- the repository now has an observational GitHub Actions workflow for upstream catalog drift,
- the repository contains a local `model.json` catalog snapshot whose upstream source is known.

## Catalog Snapshot Requirement

`custom_components/cozylife/model.json` is a checked-in snapshot of the upstream Doiting model catalog:

- [api-us.doiting.com/api/device_product/model?lang=en](https://api-us.doiting.com/api/device_product/model?lang=en)

Desired CI behavior:
- fetch the upstream catalog snapshot on a scheduled and/or manual basis,
- diff the upstream response against the checked-in `model.json`,
- surface the diff clearly for maintainers,
- avoid silently rewriting the checked-in file on merge.

## Policy

- upstream catalog drift should be visible,
- upstream catalog drift should not automatically become a support claim,
- CI may report or propose catalog updates,
- catalog updates should remain deliberate repository changes.

## Why This Matters

- the integration uses `model.json` for classification and capability inference,
- upstream catalog changes can affect potentially supported surfaces,
- the repository should track upstream drift without pretending that upstream breadth equals maintained support.

## Future Work

- keep the catalog-drift workflow observational unless repository policy changes,
- decide whether CI should fail on drift or only report it,
- document any review process for accepting catalog snapshot updates.
