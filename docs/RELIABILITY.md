# Reliability

This document defines the desired reliability posture for the CozyLife integration.

## Desired End State

The integration should:
- find devices reliably on a typical home LAN,
- survive device IP drift,
- fail clearly when a device is offline,
- recover cleanly after reconnect,
- avoid reporting false command success.

## What Is Verified Today

Observed on `2026-05-16`:
- broadcast discovery successfully found a live bulb on the LAN,
- the integration connected to the bulb over TCP `5555`,
- the bulb responded to info and query requests,
- a stale supplied IP did not prevent rediscovery of the real address.

Observed on `2026-05-17`:
- the repository performed a reversible brightness control mutation against a verified light PID,
- queried state reflected the changed brightness,
- the original brightness was restored and confirmed by query.

Observed on `2026-05-19`:
- the repository exercised the full repo-defined verified light surface on real hardware,
- on/off, brightness, color temperature, HS color, `sleep`, `warm`, `study`, and `chrismas` all succeeded,
- brightness, color-temperature, and HS transition paths also succeeded after transition-path repair,
- the original state was restored and confirmed by query at the end of the full pass.

The repository's support policy is stricter than simple reachability:
- a class is only fully supported when relevant control behavior is also verified on real hardware.

The repository's parity policy is also explicit:
- live behavior determines support truth,
- catalog-declared capability sets the parity target,
- gaps between the two are reliability and/or product-surface findings.

Observed in code and protected by automated tests on `2026-05-30`:
- the light platform now resolves Home Assistant color-mode symbols through the modern `ColorMode` enum when older module-level `COLOR_MODE_*` constants are absent,
- this prevents import-time setup failure on newer Home Assistant light APIs,
- this is API-compatibility evidence, not fresh hardware validation.

## What Is Not Yet Reliable Enough

- live protocol evidence is still incomplete beyond the tested acknowledgment contract for `set` commands,
- the TCP client now has automated coverage for fragmented `\r\n`-terminated responses, but longer-session framing behavior is still not live-verified,
- response correlation is now tested against exact top-level `sn` matching, but longer-session protocol evidence is still incomplete,
- switch reliability has not been validated on real hardware,
- long-running reconnect behavior has not been measured.

## Reliability Principles

- Discovery should degrade gracefully.
- Offline devices should become unavailable, not silently stale.
- Reconnect logic should repair device access without manual entry surgery.
- Command success should be tied to protocol evidence rather than open sockets alone.

## Next Reliability Work

- capture live protocol transcripts for info, query, and control,
- verify behavior after device IP changes,
- verify behavior after temporary loss of power or Wi-Fi,
- verify polling behavior over longer sessions.
