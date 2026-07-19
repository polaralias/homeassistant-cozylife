# CI

This document records the desired CI posture for the repository.

## Current State

- the repository now has an observational GitHub Actions workflow for upstream catalogue drift,
- the repository contains a local `model.json` catalogue snapshot whose upstream source is known.

## Catalogue Snapshot Requirement

`custom_components/cozylife/model.json` is a checked-in snapshot of the upstream Doiting model catalogue:

- [api-us.doiting.com/api/device_product/model?lang=en](https://api-us.doiting.com/api/device_product/model?lang=en)

Desired CI behaviour:
- fetch the upstream catalogue snapshot on a scheduled and/or manual basis,
- diff the upstream response against the checked-in `model.json`,
- surface the diff clearly for maintainers,
- avoid silently rewriting the checked-in file on merge.

## Policy

- upstream catalogue drift should be visible,
- upstream catalogue drift should not automatically become a support claim,
- CI may report or propose catalogue updates,
- catalogue updates should remain deliberate repository changes.

## Why This Matters

- the integration uses `model.json` for classification and capability inference,
- upstream catalogue changes can affect potentially supported surfaces,
- the repository should track upstream drift without pretending that upstream breadth equals maintained support.

## Future Work

- keep the catalogue-drift workflow observational unless repository policy changes,
- decide whether CI should fail on drift or only report it,
- document any review process for accepting catalogue snapshot updates.
