# Codex Handoff: CozyLife TCP Reliability Fix

Date: 2026-10-05

## Mission

Finish and validate the focused CozyLife local-TCP reliability fix, then prepare the change for upstream review. The Home Assistant installation is production, so do not make changes to the live HA system until the code has passed local tests and the operator explicitly approves a controlled deployment step.

## Repository and branch

- Working repository: `~/code/homeassistant-cozylife`
- Fork: `ddean6232/homeassistant-cozylife`
- Upstream: `polaralias/homeassistant-cozylife`
- Working branch: `fix/stateless-cozylife-tcp`
- Draft upstream PR: `polaralias/homeassistant-cozylife#19`
- Initial implementation commit: `cad840d`

## User constraints

- Scope only the CozyLife integration.
- Do not change indicator-mode behavior; it is explicitly deferred.
- Do not modify other Home Assistant integrations, networking, router settings, DNS, or unrelated automations.
- Treat Home Assistant as production.
- Do not install the branch into production without a backup and explicit approval for that deployment step.
- Prefer a small, reviewable upstream PR over a broad rewrite.

## Problem being fixed

CozyLife devices can silently close idle local TCP connections after roughly 30–60 seconds. The current upstream client retains a socket between operations, so later Home Assistant polls can use a stale connection and mark a device unavailable even while the CozyLife app continues to control it successfully.

Archived PR #7 and commit `651b967` identified the same failure mode and used connect/send/receive/disconnect with retries. Do not copy that change blindly: the current upstream client has better framing, sequence-number correlation, and command acknowledgement handling that must be preserved.

## Current code change

`custom_components/cozylife/tcp_client.py` currently:

- adds bounded retry constants;
- returns success/failure from `_initSocket()`;
- closes the socket after each `_exchange()`;
- retries failed exchanges on a fresh connection;
- preserves the current `_FRAME_TERMINATOR` framing;
- preserves top-level sequence-number matching;
- preserves `CMD_SET` acknowledgement validation through `res == 0`.

`tests/test_tcp_client_contract.py` adds coverage for:

- cleanup after successful and failed exchanges;
- retrying after stale connections, failed sends, and failed responses;
- closing sockets created by failed connection attempts;
- fragmented response framing and unrelated sequence-number filtering;
- negative command acknowledgements;
- device-info discovery through the stateless exchange path.

## Local validation

Completed on 2026-10-04 without modifying the production Home Assistant system:

1. The repository test command with the CI dependency versions:

   ```bash
   uv run --prerelease=allow \
     --with 'homeassistant==2025.1.4' \
     --with 'pytest==8.3.4' \
     --with 'pytest-asyncio==0.24.0' \
     python -m pytest -q
   ```

   Result: `34 passed, 7 warnings in 2.77s`. The warnings are upstream
   dependency deprecations from `josepy`, `acme`, and Home Assistant's HTTP
   component.

2. `git diff --check` completed successfully.
3. The final diff was reviewed manually against archived PR #7 / commit
   `651b967`. The current implementation keeps the newer framing,
   sequence-correlation, and acknowledgement behavior that the archived change
   did not preserve.

## Remaining work

1. Keep PR #19 as a draft until live hardware validation is complete.
2. Do not deploy to HA without explicit operator approval. Use a reversible
   production-test plan:
   - identify the installed CozyLife integration files/version;
   - back up only `custom_components/cozylife`;
   - install only the tested CozyLife files;
   - restart HA only with approval;
   - monitor both switches through polling and an idle period;
   - roll back the CozyLife backup if required.

Local unit tests establish the client contract but do not prove the production
switch-unavailability symptom is fixed.

## Definition of done for this handoff

- The integration-only change is tested locally.
- No indicator-mode code is changed.
- No production Home Assistant files have been changed without explicit approval.
- The branch is clean except for deliberate committed work.
- PR #19 contains an accurate summary, test evidence, and clearly labels live validation status.

## Important evidence

The upstream repository currently treats switches as potentially supported and has not validated switch reliability on real hardware. The app working normally does not disprove this bug because the app and the Home Assistant integration can use different connection/session paths.
