# Live Validation: `rju4K7`

Date: `2026-05-19`

## Device

- model name: `Smart Bulb Light`
- PID: `rju4K7`
- live device tested: redacted for public repository publication
- live IP during test: redacted for public repository publication

## Catalog Declaration

`model.json` declares these DPIDs for `rju4K7`:

- `1`
- `2`
- `3`
- `4`
- `5`
- `6`
- `7`
- `8`
- `9`
- `13`
- `14`
- `15`
- `44`

## Initial Observed State

- `1`: `1`
- `2`: `0`
- `3`: `65535`
- `4`: `1000`
- `5`: `7`
- `6`: `1000`

## Verified Live Behaviors

- direct TCP info response succeeded
- direct TCP query response succeeded
- on/off control succeeded
- brightness control succeeded
- color-temperature control succeeded
- HS color control succeeded
- `sleep` effect payload succeeded
- `warm` effect payload succeeded
- `study` effect payload succeeded
- `chrismas` effect payload succeeded
- brightness transition succeeded after transition-path repair
- color-temperature transition succeeded after transition-path repair
- HS transition succeeded after transition-path repair
- original device state was restored and confirmed by query

## Observed Effect-Related Query Surface

During `chrismas`, the device query surface exposed:

- `2`: `1`
- `7`: hex scene payload
- `8`: `500`

This is the first live confirmation in this repository that DPID `7` and `8` are active in at least one light effect path for this PID.

## Remaining Parity Gaps

The following catalog-declared DPIDs were not observed in live query responses during the full validation pass:

- `9`
- `13`
- `14`
- `15`
- `44`

Current repository status for those DPIDs:

- they are catalog-declared for `rju4K7`,
- they are not mapped to a first-class Home Assistant light capability in the current code,
- their runtime semantics remain unverified in this repository.

## Integration-Specific Note

The `natural` effect is integration-specific rather than a pure device capability:

- without a loaded Circadian Lighting runtime, it degrades to a plain `turn_on` path,
- no distinct device-side state mutation was confirmed for `natural` in this validation pass.
