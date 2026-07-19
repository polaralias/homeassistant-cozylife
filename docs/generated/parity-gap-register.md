# Parity Gap Register

This register tracks live support truth versus catalogue-declared capability.

Primary tracking unit:
- concrete model/PID

Support labels:
- supported
- partially supported
- potentially supported

## Entry Format

For each model/PID, record:
- model name
- PID
- device class
- support label
- live evidence date
- discovery status
- query status
- control status
- catalogue-declared capabilities
- live-validated capabilities
- parity gaps
- notes

## Entries

### Smart Bulb Light (`rju4K7`)

- model name: `Smart Bulb Light`
- PID: `rju4K7`
- device class: `light`
- support label: `supported`
- live evidence date: `2026-05-19`
- discovery status: `verified`
- query status: `verified`
- control status: `verified for the repository's live light surface, including on/off, brightness, color temperature, HS color, named effect payloads, and transition paths`

Catalogue-declared capabilities from `model.json`:
- on/off
- brightness
- colour temperature
- HS colour
- effect-related datapoints

Live-validated capabilities:
- discovery
- device info
- state query
- real-world control via Home Assistant on a previous repository revision
- on/off control
- brightness control
- colour-temperature control
- HS colour control
- `sleep`, `warm`, `study`, and `chrismas` effect payloads
- brightness, colour-temperature, and HS transition paths
- explicit state restore after the full live pass

Parity gaps:
- DPID `7` and `8` are now observed live through the `chrismas` effect path, but DPID `9`, `13`, `14`, `15`, and `44` remain catalogue-declared and unverified
- bounded live probing on `2026-05-19` showed that `13` and `44` accept writes of `0` and `1`, while `9`, `14`, and `15` reject those bounded writes
- broader live probing on `2026-05-19` showed that `13 = 1` reproducibly causes delayed power-off on this bulb, while `44` accepts a broad numeric range without observable query-surface deltas and rejects `65535`

Notes:
- this PID is the first concrete truth unit used to seed the register
- the repository treats this light class as first-class supported based on real-world Home Assistant control history plus current explicit discovery/query/control verification
- full live validation on `2026-05-19` exercised the repo-defined light feature surface against a real bulb and confirmed restore to the original state
- see `docs/generated/rju4k7-live-validation-2026-05-19.md` for the concrete live matrix
- see `docs/generated/rju4k7-unknown-dpid-probe-2026-05-19.md` for the bounded experimental probe of unknown catalogue DPIDs
- see `docs/generated/tested-but-not-confirmed-capabilities.md` for ambiguous live findings that are deliberately not exposed as product behaviour
- the unknown-DPID probe now gives the repo one concrete semantic lead: DPID `13` may represent delayed off or a closely related timer behaviour for `rju4K7`
- automated tests now enforce that active Home Assistant `color_mode` is derived from queried live state rather than constructor-time capability hints
