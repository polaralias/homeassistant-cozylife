# Tech Debt Tracker

This file tracks debt that should be made explicit before major code cleanup.

## Active Debt

### Dual-modelled switches

Current state:
- switch-class devices now surface through `switch.py` only.
- the light platform no longer carries switch-specific entity naming in its class structure.

Desired state:
- one intentional entity-surface policy for switch devices, with light entities reserved for actual light-capable devices.

Status:
- resolved in code and automated tests.

### Non-authoritative command success

Current state:
- `tcp_client.control()` now waits for the matching top-level `sn` response and rejects explicit nonzero `res` acknowledgements in automated tests.

Desired state:
- command success backed by stronger protocol evidence.

Status:
- partially resolved; automated tests now cover framed reads, top-level `sn` correlation, and explicit acknowledgement handling, but live protocol evidence remains incomplete.

### Mixed config-entry shapes

Current state:
- the integration still supports both single-device and multi-device list entry structures,
- legacy bucketed full-scan storage is now migrated forward into canonical device rows,
- legacy options rescans no longer rewrite bucketed device dictionaries.

Desired state:
- one canonical persisted model plus explicit migrations.

Status:
- partially resolved; config-entry version `2` now activates migration for existing entries, migration canonicalises `location` to `area`, legacy bucketed full-scan entries now collapse into canonical `devices` rows with `scan_settings`, and legacy options rescans persist the same canonical row shape, but single-device and multi-device persisted shapes still both remain.

### Raw sensor semantics

Current state:
- sensors are mostly exposed as raw datapoints.

Desired state:
- documented support policy for sensor semantics and naming.

Status:
- documented, not resolved.

### Missing support-promotion evidence bar

Current state:
- the repository has a policy distinction between verified and potentially supported surfaces, but promotion evidence was previously implicit.

Desired state:
- contributors know exactly what evidence is required to promote a device class into verified supported status.

Status:
- resolved in docs, not yet exercised through contributor workflow.

### Missing partial-support matrix

Current state:
- the repository now distinguishes supported, partially supported, and potentially supported surfaces, but does not yet have a device-class matrix using those labels.

Desired state:
- support labels are applied consistently to concrete device classes and examples.

Status:
- documented, not resolved.

### Documentation drift

Current state:
- inherited docs overstated some behaviour.

Desired state:
- outcome-focussed docs with explicit verification boundaries.

Status:
- actively being resolved.

### Missing automated TDD harness

Current state:
- the repository has a checked-in pytest harness for behaviour-level changes,
- the initial test slices cover entity surfacing, command acknowledgement handling, and migration cleanup,
- future implementation sessions can extend the harness instead of starting from blind refactoring.

Desired state:
- the repository has the smallest useful automated harness needed for focussed TDD slices,
- tests exercise public behaviour such as onboarding, rediscovery, entry normalisation, and entity-surface outcomes,
- test names use repository support language and product language rather than implementation detail.

Status:
- resolved for the initial repair scope.

### Upstream catalogue drift visibility

Current state:
- `model.json` has a known upstream source, but the repository does not yet have CI that surfaces drift against that upstream snapshot.

Desired state:
- CI fetches and diffs the upstream catalogue without automatically rewriting repository metadata.

Status:
- documented, not resolved.

### Missing parity-gap register

Current state:
- the repository now distinguishes live support truth from catalogue-declared capability and has started a dedicated register, but the register is only seeded with one model entry.

Desired state:
- parity gaps between live behaviour and `model.json` are tracked explicitly per concrete model/PID, with class-level summaries only when useful.

Status:
- started, not resolved.
