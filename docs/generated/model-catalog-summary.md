# Model Catalog Summary

This file is derived from `custom_components/cozylife/model.json`.

It is a lightweight inventory reference, not a support claim.

Generated from repository state observed on `2026-05-17`.

Upstream source for the checked-in catalog snapshot:
- [api-us.doiting.com/api/device_product/model?lang=en](https://api-us.doiting.com/api/device_product/model?lang=en)

## Top-Level Summary

- top-level device type groups: `11`

## Groups

| Device Type Code | Model Count | Example Model |
| --- | ---: | --- |
| `01` | 492 | Color temperature lamp |
| `00` | 290 | Smart Switch |
| `02` | 7 | Curtain |
| `05` | 14 | Tea bar machine |
| `06` | 16 | energy storage battery |
| `19` | 5 | Car lights |
| `08` | 1 | Mesh gateway |
| `07` | 4 | DIY |
| `03` | 21 | multi-sensor |
| `11` | 42 | Video intercom |
| `22` | 26 | AI Conversation |

## Interpretation

- The local catalog is much broader than the active Home Assistant entity surface.
- Presence in `model.json` should not be read as proof of repository support.
- Presence in `model.json` may indicate a potentially supported surface, but not a verified or maintained one.
- Current runtime support is narrower and should be documented separately in architecture and product-spec docs.
