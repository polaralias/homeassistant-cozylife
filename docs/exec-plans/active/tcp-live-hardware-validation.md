---
type: "Delivery Plan"
title: "CozyLife TCP Live Hardware Validation"
description: "Draft production-safe plan for validating stateless CozyLife TCP exchanges on real switches."
timestamp: 2026-10-04T00:00:00-06:00
authority: canonical
verification: untested
owner: ddean6232
tags:
  - homeassistant-cozylife
  - delivery-plan
  - live-validation
navigation:
  role: supporting
  order: 100
---
# CozyLife TCP Live Hardware Validation

Status: **Live validation inconclusive — rollback completed**

Plan content was approved by the operator on `2026-10-04`. That approval alone
did not authorise SSH access, backup creation, deployment, restart, device
control, or any other production action.

Gate 1 was authorised by the operator on `2026-10-04` for a 90-minute
maintenance window from approximately 22:05 to 23:35 local time. Gate 1 permitted
operator-executed read-only SSH preflight and creation of the documented
rollback backup only. It did not authorise candidate staging, deployment,
restart, or device control.

The preflight completed and the backup was verified. Gate 1 paused before
candidate staging because the installed `tcp_client.py` hash did not match the
current repository history. Read-only comparison subsequently confirmed that
the installed file exactly matches archived commit `651b967`. The candidate
retains every TCP-client interface used by the installed integration, and the
copied production tree compiled successfully with the candidate substituted.
That pre-deployment hold was cleared before the later gates were authorised.

Gate 2 candidate staging and Gate 3 deployment were subsequently authorised by
the operator on `2026-10-04`. The candidate was hash-verified, installed as the
only changed production file, and loaded by one controlled Core restart.

The MVP could not reach its first control checkpoint. The two target entities
remained in their pre-test `unavailable` condition because TCP connections to
their stored device addresses were refused or timed out. No successful
protocol exchange occurred, and no switch control was attempted. The original
file was restored atomically from the verified backup, its hash was confirmed,
and Core restarted successfully. Live hardware validation therefore remains
pending; this execution is not evidence that the production symptom is fixed.

No further production execution is authorised. Any future attempt requires a
new maintenance window, renewed gate approvals, and confirmation that the
target devices accept TCP connections from Home Assistant before deployment.

## Objective

Validate on two known CozyLife switches that commit `e4aa6b1`:

- keeps the entities available after the devices' observed 30–60 second idle
  TCP disconnect window;
- still queries state and controls each switch correctly;
- restores each tested switch to its pre-test state;
- introduces no new CozyLife-specific setup, polling, or protocol errors.

This is evidence for the focused TCP reliability change. It is not evidence
that every switch model or the full switch feature surface is supported.

## Non-goals and safety boundary

- Do not change indicator-mode behaviour.
- Do not change integration configuration, entity definitions, automations,
  networking, DNS, router settings, or other integrations.
- Do not update Home Assistant, HACS, Python packages, or the operating system.
- Do not test switches attached to safety-critical, security-critical,
  refrigeration, medical, heating, pumping, or otherwise hazardous loads.
- Do not expose IP addresses, device IDs, credentials, tokens, or private log
  content in repository evidence or the pull request.
- Do not retrieve credentials until execution is approved. Vaultwarden is the
  only authorised credential source.

## MVP scope

- Target: one production Home Assistant instance.
- Devices: exactly two known, non-critical CozyLife switches affected by the
  stale-connection symptom.
- Production code deployed: only
  `custom_components/cozylife/tcp_client.py` from commit `e4aa6b1`.
- Restarts: one controlled restart for deployment; one additional restart only
  if rollback is required.
- Maintenance-window estimate: 30 minutes, including restart and rollback
  buffer.
- Core readiness timeout: five minutes after either restart.
- Observation: immediate verification, a 90-second idle boundary check, and a
  10-minute Home Assistant polling observation.
- Mutations: one reversible off/on cycle per switch at each control checkpoint,
  always ending in the recorded original state.

## Details required before approval

The plan is not executable while any item is `TBD`.

| Item | Required value |
|---|---|
| Home Assistant installation type | Home Assistant OS `18.3` |
| Home Assistant version | `2026.9.4` |
| Non-secret target/endpoint | Supplied privately; redact from repository evidence |
| Approved API access method | Confirmed: long-lived access token via Vaultwarden |
| Approved filesystem access method | Operator-executed SSH as `darren_dean` through the operator's existing Tailscale access |
| Configuration root | `/config` |
| CozyLife integration path | `/config/custom_components/cozylife` |
| Restart method | Operator-run `ha core restart` over SSH |
| Backup destination outside `custom_components` | `/config/.cozylife-validation/rollback-pre-e4aa6b1` |
| Switch A entity and physical load | Entity confirmed privately; safe to toggle |
| Switch B entity and physical load | Entity confirmed privately; safe to toggle |
| Maintenance window | `2026-10-04`, approximately 22:05–23:35 local time |
| Operator available to observe physical state | Required throughout the approved window |

If the access method requires a secret, agree the canonical Vaultwarden item
name before execution, for example `Home Assistant — SSH credential` or
`Home Assistant — API token`. If the item is absent, stop and ask the operator
to enter it with `vaultwarden-secret put`; never search local files for it.

Unauthenticated reachability was checked with operator approval on 2026-10-04.
The endpoint served the normal Home Assistant authentication page. During that
unauthenticated check, no login, API request, configuration inspection, service
call, or mutation was made.

Subsequent operator-approved, authenticated read-only API checks confirmed:

- Home Assistant `2026.9.4` is running outside safe mode;
- the instance is Supervisor-managed and exposes `/config`;
- the CozyLife integration owns six light entities and two switch entities;
- both target switch entities were `unavailable` before deployment;
- SSH port 22 is reachable for a possible out-of-band rollback path.

Operator-executed preflight additionally confirmed:

- Home Assistant OS `18.3`, Core `2026.9.4`, Supervisor `2026.09.3`;
- Core was running and the system reported ready;
- Supervisor reported the pre-existing system flag `supported: false`;
- installed `tcp_client.py` ownership/mode was `root:root` / `0644`;
- installed `tcp_client.py` SHA-256 was
  `9655edb8494ce36c6e511abec0faceef74260ea0d129870fdca8a6353c4f0f0a`;
- the rollback directory was `908.0K` and contained 30 hashed files;
- `diff -qr` produced no differences between the installed directory and the
  backup;
- the backup manifest SHA-256 was
  `5b4651c268da42f2fb22b3ad921df98a63c22d313bb4904ba8fb00f73e7281b2`.

The pre-existing `supported: false` flag is recorded as an external risk and
will not be investigated or changed as part of this focused integration test.

The installed-file hash is now explained as an exact match for archived commit
`651b967`; it is not an unknown local edit. The production manifest version is
`2026.03.14.1904`, so the surrounding integration is older than the current
repository. Local compatibility review found that the installed call sites use
only client members retained by the candidate, and the copied production tree
compiled successfully after substituting the candidate client. Only
`tcp_client.py` remains approved for deployment.

Exact entity IDs, friendly names, the private endpoint, and access metadata are
intentionally omitted from this public repository plan.

The operator authenticates SSH through Tailscale as `darren_dean` and will run
the reviewed SSH commands at each gate. The agent will not use the operator's
Tailscale authentication state or provision another production credential.

## Approved candidate artifact

- implementation commit: `e4aa6b13770cfd2a5da10e67f3ca77f665829316`
- production file: `custom_components/cozylife/tcp_client.py`
- SHA-256: `5a55fd4f4befb07ef6c987b878e7a0b66a51af7beb2189dfe1d9b42b24c4748b`

Any code change or hash change invalidates this plan and requires a fresh test
run, diff review, artifact hash, and operator approval.

## Evidence record

Create a private working record during execution containing only:

- date and local time;
- Home Assistant version and installation type;
- branch commit and SHA-256 of the candidate `tcp_client.py`;
- installed CozyLife manifest version and pre-change file hash;
- redacted switch labels, model names, and PIDs;
- original state and result of each checkpoint;
- CozyLife-specific warnings or errors;
- deployment, restart, rollback, and recovery timestamps.

Public repository evidence must redact IP addresses, device IDs, hostnames,
credentials, and private log context.

### Execution result — 2026-10-04

The approved maintenance-window attempt produced the following redacted
evidence:

- the staged candidate was owned by `root:root`, mode `0600`, and matched the
  approved SHA-256 before deployment;
- the live replacement was atomic, left `tcp_client.py` owned by `root:root`
  with mode `0644`, and matched the approved candidate SHA-256;
- the first non-interactive `ha core restart` attempt was rejected because that
  SSH session did not have a valid Supervisor API token; Core remained running,
  and the operator then restarted it successfully from the authenticated
  interactive Home Assistant CLI;
- Core returned as `RUNNING`, outside safe mode, and the CozyLife integration
  loaded;
- both target entities remained in the same `unavailable` condition recorded
  before deployment;
- a temporary runtime-only `INFO` level for
  `custom_components.cozylife.tcp_client` captured connection refusal for two
  stored device addresses and connection/receive timeouts for another address;
- the temporary logger level was restored to `WARNING` after one polling
  interval;
- recurring `NoEntitySpecifiedError` exceptions were also observed in the
  unchanged `light.py` polling path for duplicate switch-as-light objects; that
  separate issue was not investigated or modified in this focused test;
- no response framing, sequence correlation, acknowledgement, idle-boundary,
  or control behaviour reached live execution, and neither switch was toggled;
- the rollback trigger fired because the switches remained unavailable for
  more than two polling intervals and the MVP could not proceed;
- the original file was restored atomically with SHA-256
  `9655edb8494ce36c6e511abec0faceef74260ea0d129870fdca8a6353c4f0f0a`,
  ownership `root:root`, and mode `0644`;
- the rollback restart completed successfully; the initial post-rollback API
  check reported Core `RUNNING`, safe mode disabled, CozyLife loaded, and both
  target entities still in their original `unavailable` condition;
- later read-only preflight under the restored original client produced three
  successful TCP/5555 handshakes for each target, followed by two successful
  checks after separate 90-second idle intervals; these probes opened and
  closed TCP connections without sending CozyLife protocol payloads;
- a subsequent API check showed both target entities available, `off`, and
  reporting current timestamps under the restored original client;
- after rollback, the operator separately ran two identical Home Assistant API
  sequences against both targets: toggle three times with short pauses, then
  request `off`. The patio entity finished `off`; the yard entity became
  `unavailable` during both sequences. The operator physically confirmed that
  both loads finished off. These controls ran entirely under the restored
  original client and are baseline evidence, not validation of the candidate.

The verified backup and inert staged candidate were retained under
`/config/.cozylife-validation/`. No second deployment is authorised in this
maintenance window. The late recovery shows that the earlier refusal/timeouts
were transient, but it does not validate the candidate or explain their cause.
A later baseline control attempt also showed that TCP-port reachability alone
does not guarantee stable entity availability under the original client.
A future live attempt requires a new window and must repeat the scoped
reachability and entity-availability baseline immediately before deployment.

## Approval gates

### Gate 0 — plan content approval

Completed on `2026-10-04`. This gate approves the documented MVP scope and
rollback design only. It does not authorise execution.

### Gate 1 — preflight approval

Completed on `2026-10-04` before SSH preflight and backup creation. Required
conditions were:

- every `TBD` is resolved;
- both loads are confirmed safe to toggle;
- the maintenance window and expected brief outage are accepted;
- the private SSH target has been substituted and the exact commands have been
  shown to the operator;
- exact backup, deploy, restart, and restore commands are written into this
  plan for the identified installation type;
- operator-executed SSH remains available for deployment and rollback;
- the operator explicitly authorises read-only preflight and backup creation.

### Gate 2 — preflight and backup approval

Completed on `2026-10-04` after presenting the baseline, compatibility review,
and verified backup evidence. This authorised inert candidate staging only.

### Gate 3 — deployment approval

Completed on `2026-10-04` immediately before the operator replaced
`tcp_client.py` and restarted Home Assistant. The candidate hash, target path,
backup path, rollback triggers, and exact rollback commands were shown
together. The subsequent validation was inconclusive and the rollback was
completed in the same window.

## Phase 1 — read-only preflight

1. Confirm the current branch is `fix/stateless-cozylife-tcp`, implementation
   commit `e4aa6b1` is present, the working tree is clean, and local tests still
   pass.
2. Compute and record the candidate `tcp_client.py` SHA-256.
3. Confirm the target is the approved Home Assistant instance and record its
   installation type and version without inspecting unrelated configuration.
4. Confirm the CozyLife integration path and record:
   - `manifest.json` version;
   - installed `tcp_client.py` SHA-256;
   - directory ownership and permissions needed for exact restoration.
5. Compare the installed CozyLife files with the expected upstream baseline.
   Stop if there are unexplained local modifications or an unexpected version;
   do not overwrite them.
6. Record the availability and original on/off state of Switch A and Switch B.
7. Confirm physically that both attached loads are safe to toggle and that the
   operator can observe them for the whole mutation window.
8. Review only CozyLife-specific recent log entries and record the existing
   stale-connection symptom. Do not inspect unrelated integrations.

Preflight stop conditions:

- wrong host, installation type, path, version, or branch;
- unexplained installed-file drift;
- either device or load cannot be identified confidently;
- either load is not safe to toggle;
- Home Assistant is already degraded for an unrelated reason;
- a required credential is missing from Vaultwarden.

## Phase 2 — backup and rollback verification

1. Create a timestamped backup of the complete installed
   `custom_components/cozylife` directory outside `custom_components`.
2. Preserve file contents, permissions, and timestamps.
3. Generate a recursive file inventory and SHA-256 manifest for the backup.
4. Compare the backup to the installed directory and require an exact match.
5. Confirm sufficient storage and read access to the backup.
6. Write the exact restore commands for this installation type and perform a
   dry review only. Do not restore over the live files during verification.
7. Present the backup path, comparison result, original `tcp_client.py` hash,
   candidate hash, deployment command, restart command, and restore commands at
   Gate 2.

A backup that has not been compared successfully is not a rollback plan.

## Phase 3 — minimal deployment

Only after Gate 3:

1. Copy the candidate `tcp_client.py` to a temporary file in the target
   directory with the installed file's ownership and permissions.
2. Verify the temporary file's SHA-256 matches the approved candidate hash.
3. Atomically replace only the installed `tcp_client.py`.
4. Verify the installed hash matches the candidate hash.
5. Restart Home Assistant once using the approved installation-specific method.
6. Wait for Home Assistant core to become ready, then inspect only CozyLife
   integration setup status and CozyLife-specific logs.

Do not copy tests, documentation, repository metadata, the whole branch, or any
other integration file into production.

## Phase 4 — MVP validation sequence

At every control checkpoint, record the pre-check state, issue the inverse
state once, confirm both Home Assistant state and the physical load, then return
the switch to its recorded original state and confirm restoration. The operator
performs control actions in the Home Assistant UI; the agent uses the API only
for read-only state and availability verification.

1. **Startup check**
   - Both switch entities become available within two normal polling intervals.
   - No new CozyLife setup or protocol error appears.
2. **Immediate control check**
   - Run one reversible control cycle on Switch A, then Switch B.
   - Confirm the device response is reflected in Home Assistant and physically.
3. **Idle boundary check**
   - Make no CozyLife control calls for 90 seconds.
   - Confirm both entities remain available and their states can be queried.
   - Run and restore one reversible control cycle on each switch.
4. **Polling observation**
   - Leave both switches in their original states for 10 minutes while normal
     Home Assistant polling continues.
   - Do not use the CozyLife app during this interval; it would add a second
     control path and weaken attribution.
   - Record availability at the start, midpoint, and end.
5. **Final control check**
   - Run and restore one final reversible control cycle on each switch.
   - Confirm both entities are available and in their original states.
   - Review only CozyLife-specific log entries produced during the test.

## Pass criteria

The MVP passes only if all conditions hold:

- Home Assistant restarts normally and the CozyLife integration loads;
- both switches remain available throughout all checkpoints;
- every query/control checkpoint succeeds on the first Home Assistant action;
- Home Assistant state and physical state agree after every action;
- both switches finish in their recorded original states;
- no new CozyLife connection, framing, correlation, acknowledgement, or setup
  error is recorded;
- no rollback trigger occurs.

A pass validates this focused fix on the two tested devices and environment. It
does not by itself promote all CozyLife switches to `supported`.

## Rollback triggers

Rollback immediately if any of these occurs after deployment:

- Home Assistant fails to become ready within five minutes;
- the CozyLife integration fails to load;
- either tested switch is missing or remains unavailable for two polling
  intervals;
- a command reports success but physical state does not match;
- a switch cannot be restored to its original state;
- new repeated CozyLife protocol or socket errors appear;
- an unexpected file, integration, entity, or automation is affected;
- the operator requests rollback for any reason.

## Rollback procedure

The installation-specific commands must be filled in before Gate 1. The
procedure is:

1. Stop further test actions and record the trigger and current switch states.
2. Restore the original `tcp_client.py` from the verified directory backup
   using a temporary file and atomic replacement.
3. Restore its original ownership and permissions.
4. Verify its SHA-256 matches the recorded pre-change hash.
5. Restart Home Assistant once using the approved method.
6. Confirm Home Assistant and the CozyLife integration load.
7. Confirm both switch entities recover and restore them to their original
   states if safe and necessary.
8. Verify source and configuration files against the backup inventory,
   excluding runtime cache files such as `__pycache__`.
9. Preserve the failure evidence, keep PR #19 in draft, and do not attempt a
   second deployment in the same window.

If Home Assistant cannot restart after file restoration, stop and use the
installation's native recovery console or supervisor rollback path agreed in
the completed installation-specific section. Do not improvise changes to other
configuration or integrations.

## Post-test evidence and decision

After a pass:

1. Leave the tested switches in their original states.
2. Record a redacted evidence file under `docs/generated/` with the tested
   models/PIDs, checkpoints, duration, and result.
3. Update `docs/RELIABILITY.md` and PR #19 with the dated, limited evidence.
4. Keep claims scoped to the tested devices and Home Assistant environment.
5. Decide explicitly whether to:
   - keep PR #19 in draft for a longer soak;
   - run an optional 24-hour availability soak without additional mutations;
   - mark the PR ready for upstream review.

After a failure or rollback, document the observed behaviour without claiming
the production problem is fixed.

## Installation-specific commands

The private Tailscale SSH target is substituted immediately before execution
and shown to the operator. No command containing a placeholder may be run.
Commands that use `<private-ssh-target>` below are therefore review templates,
not executable commands.

### Read-only operator preflight

Run over the operator's normal SSH session:

```bash
id
ha info
ha core info
test -d /config/custom_components/cozylife
test -f /config/custom_components/cozylife/tcp_client.py
test -w /config/custom_components/cozylife
stat -c '%u:%g %a %n' /config/custom_components/cozylife/tcp_client.py
sha256sum /config/custom_components/cozylife/tcp_client.py
test ! -e /config/.cozylife-validation/rollback-pre-e4aa6b1
```

Stop if any command fails. Record the exact installation type, Core version,
file ownership/mode, and original hash before proceeding.

### Verified directory backup

Run only after Gate 1 approval and a successful read-only preflight:

```bash
mkdir -p /config/.cozylife-validation
mkdir /config/.cozylife-validation/rollback-pre-e4aa6b1
cp -a /config/custom_components/cozylife /config/.cozylife-validation/rollback-pre-e4aa6b1/cozylife
diff -qr /config/custom_components/cozylife /config/.cozylife-validation/rollback-pre-e4aa6b1/cozylife
find /config/.cozylife-validation/rollback-pre-e4aa6b1/cozylife -type f -exec sha256sum '{}' ';' > /config/.cozylife-validation/rollback-pre-e4aa6b1.sha256
```

`diff -qr` must produce no output and exit successfully. The operator then
presents the backup path, original hash, ownership/mode, and directory listing
at Gate 2.

### Candidate staging

The SSH service does not expose an SCP/SFTP subsystem. Non-interactive SSH runs
as the unprivileged operator account, so the approved staging path requires the
account's verified passwordless `sudo`. From the repository root on the
development machine, stage through the normal operator-authenticated SSH
stream after replacing the private target placeholder locally:

```bash
ssh darren_dean@<private-ssh-target> 'set -eu; test ! -e /config/.cozylife-validation/tcp_client.e4aa6b1.py; test ! -e /config/.cozylife-validation/tcp_client.e4aa6b1.py.part; sudo -n dd of=/config/.cozylife-validation/tcp_client.e4aa6b1.py.part bs=4096; sudo -n chmod 600 /config/.cozylife-validation/tcp_client.e4aa6b1.py.part; sudo -n sha256sum /config/.cozylife-validation/tcp_client.e4aa6b1.py.part' < custom_components/cozylife/tcp_client.py
ssh darren_dean@<private-ssh-target> 'set -eu; sudo -n mv /config/.cozylife-validation/tcp_client.e4aa6b1.py.part /config/.cozylife-validation/tcp_client.e4aa6b1.py; sudo -n stat -c "%u:%g %a %n" /config/.cozylife-validation/tcp_client.e4aa6b1.py; sudo -n sha256sum /config/.cozylife-validation/tcp_client.e4aa6b1.py'
```

Then verify remotely:

```bash
sha256sum /config/.cozylife-validation/tcp_client.e4aa6b1.py
```

The result must be exactly
`5a55fd4f4befb07ef6c987b878e7a0b66a51af7beb2189dfe1d9b42b24c4748b`.

### Atomic deployment and Core restart

Run only after Gate 3 approval from the authenticated interactive Home
Assistant root shell. A non-interactive `sudo ha core restart` does not inherit
the Supervisor API token and must not be used.

```bash
printf "%s  %s\n" "9655edb8494ce36c6e511abec0faceef74260ea0d129870fdca8a6353c4f0f0a" "/config/custom_components/cozylife/tcp_client.py" | sha256sum -c -
printf "%s  %s\n" "9655edb8494ce36c6e511abec0faceef74260ea0d129870fdca8a6353c4f0f0a" "/config/.cozylife-validation/rollback-pre-e4aa6b1/cozylife/tcp_client.py" | sha256sum -c -
printf "%s  %s\n" "5a55fd4f4befb07ef6c987b878e7a0b66a51af7beb2189dfe1d9b42b24c4748b" "/config/.cozylife-validation/tcp_client.e4aa6b1.py" | sha256sum -c -
test ! -e /config/custom_components/cozylife/.tcp_client.py.e4aa6b1.tmp
install -o root -g root -m 0644 /config/.cozylife-validation/tcp_client.e4aa6b1.py /config/custom_components/cozylife/.tcp_client.py.e4aa6b1.tmp
printf "%s  %s\n" "5a55fd4f4befb07ef6c987b878e7a0b66a51af7beb2189dfe1d9b42b24c4748b" "/config/custom_components/cozylife/.tcp_client.py.e4aa6b1.tmp" | sha256sum -c -
mv /config/custom_components/cozylife/.tcp_client.py.e4aa6b1.tmp /config/custom_components/cozylife/tcp_client.py
sha256sum /config/custom_components/cozylife/tcp_client.py
ha core restart
```

Both deployment hashes must match the approved candidate hash. After restart,
the operator runs `ha core info`; the agent verifies API readiness and only the
target CozyLife entity states. CozyLife-specific log review uses operator-run
`ha core logs` with output filtered to `cozylife`; unrelated log content is not
copied into the evidence record.

### Atomic rollback and Core restart

Run immediately when a rollback trigger occurs:

```bash
test ! -e /config/custom_components/cozylife/.tcp_client.py.rollback.tmp
install -o root -g root -m 0644 /config/.cozylife-validation/rollback-pre-e4aa6b1/cozylife/tcp_client.py /config/custom_components/cozylife/.tcp_client.py.rollback.tmp
printf "%s  %s\n" "9655edb8494ce36c6e511abec0faceef74260ea0d129870fdca8a6353c4f0f0a" "/config/custom_components/cozylife/.tcp_client.py.rollback.tmp" | sha256sum -c -
mv /config/custom_components/cozylife/.tcp_client.py.rollback.tmp /config/custom_components/cozylife/tcp_client.py
sha256sum /config/custom_components/cozylife/tcp_client.py
ha core restart
```

Both rollback hashes must match the recorded pre-change hash. After restart,
run `ha core info`, verify both target entities through the API, and compare the
installed directory to the backup. Do not redeploy during the same window.
If `ha core info` reports that Core is stopped after the original file is
restored, the operator may run `ha core start` once. If Core is not ready within
five minutes, stop and preserve the system for recovery rather than making
additional changes.

## Command source

The Home Assistant OS documentation identifies `/config` as the mapped
configuration directory available to SSH apps and documents `ha core info`,
`ha core logs`, and `ha core restart`:

- <https://www.home-assistant.io/common-tasks/os/>
