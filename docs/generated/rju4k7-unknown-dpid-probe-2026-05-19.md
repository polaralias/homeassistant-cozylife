# Experimental DPID Probe: `rju4K7`

Date: `2026-05-19`

## Scope

This probe targeted the catalogue-declared but still-unmapped DPID set for `rju4K7`:

- `9`
- `13`
- `14`
- `15`
- `44`

The goal was not to claim support. The goal was to gather bounded live evidence without leaving the bulb in an altered state.

## Method

- captured a baseline query state
- tested each unknown DPID with bounded values `0` and `1`
- repeated the probes in:
  - normal mode
  - known working `chrismas` effect mode
- recorded:
  - command acknowledgement result
  - immediate query deltas
  - restore success
- restored the original device state at the end

## Initial Bounded Results

### DPID `9`

- write `0`: rejected
- write `1`: rejected
- no query-state change observed
- same result in normal mode and `chrismas` effect mode

### DPID `13`

- write `0`: accepted
- write `1`: accepted
- no query-state change observed
- same result in normal mode and `chrismas` effect mode

Interpretation:
- `13` appears writable at the protocol level,
- but its effect is not visible through the current query surface for this bulb under these probe values.

### DPID `14`

- write `0`: rejected
- write `1`: rejected
- no query-state change observed
- same result in normal mode and `chrismas` effect mode

### DPID `15`

- write `0`: rejected
- write `1`: rejected
- no query-state change observed
- same result in normal mode and `chrismas` effect mode

### DPID `44`

- write `0`: accepted
- write `1`: accepted
- no query-state change observed
- same result in normal mode and `chrismas` effect mode

Interpretation:
- `44` appears writable at the protocol level,
- but its effect is not visible through the current query surface for this bulb under these probe values.

## Advanced Sweep

After the bounded pass, the repository ran a broader integer sweep for `13` and `44` across:

- normal current mode
- `study`
- `warm`
- `sleep`
- `chrismas`

Test values:

- `0`
- `1`
- `2`
- `5`
- `10`
- `50`
- `100`
- `255`
- `500`
- `1000`
- `65535`

### DPID `13` advanced findings

- most tested values acknowledged successfully with no immediate query-surface delta
- `13 = 1` is the important repeatable exception:
  - in normal mode, it consistently left the light on immediately, then the queried power state became `0` after a short delay
  - in `chrismas` mode, it also consistently produced a delayed power-off while the effect-mode query fields remained present
- `13 = 2` did not reproduce that delayed power-off behaviour in the focussed rerun

Working interpretation:

- `13` is likely not a no-op
- `13 = 1` appears to map to some delayed shutdown or delayed off-like behaviour
- the current repository still does not know the broader semantic contract for `13`

### DPID `44` advanced findings

- `44` acknowledged writes for a broad range including:
  - `0`
  - `1`
  - `2`
  - `5`
  - `10`
  - `50`
  - `100`
  - `255`
  - `500`
  - `1000`
- `44 = 65535` was rejected consistently
- no accepted `44` value produced an immediate or delayed observable query-state delta in the probe window

Working interpretation:

- `44` is writable over a nontrivial numeric range
- its effect is either:
  - write-only,
  - mode-dependent in a way not surfaced by query,
  - delayed beyond the current probe window,
  - or not visible through the repo’s current capability model

## Strong Conclusions

- `9`, `14`, and `15` do not accept the bounded integer writes tested here.
- `13` and `44` do accept bounded integer writes.
- `13 = 1` reproducibly causes a delayed power-off on this bulb.
- `44` is writable over a broad range but still has no observed query-surface effect.
- all intermediate states were successfully restored.

## What This Does Not Prove

This probe does not prove the semantic meaning of these DPIDs.

Possible remaining explanations include:

- mode-specific behaviour not reached by this probe
- write-only behaviour
- delayed behaviour not visible in the immediate query window
- value domains other than `0` and `1`
- app-specific or cloud-assisted features

## Current Repository Position

These DPIDs remain:

- catalogue-declared for `rju4K7`
- unverified as user-facing Home Assistant capabilities
- not mapped to first-class light behaviour in the current integration

The strongest current inference is:

- `13` is now a concrete candidate for a delayed-off or timer-like control,
- `44` remains semantically opaque despite broad write acceptance,
- `9`, `14`, and `15` still look non-writable under the integer probe shapes tested here.
