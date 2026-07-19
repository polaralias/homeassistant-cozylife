# Plans

This file is the navigation entry point for active engineering and documentation work.

Canonical support policy lives in:
- `docs/SUPPORT.md`

## Current Priority Order

1. Make repository documentation truthful and outcome-focussed.
2. Build a repeatable verification harness around real device behaviour.
3. Define and enforce the evidence bar for promoting unverified code paths into verified supported surfaces.
4. Establish the smallest automated test harness that allows focussed TDD work against documented public behaviour.
5. Reduce ambiguity in runtime state and entity modelling.
6. Make upstream catalogue drift visible through CI without turning it into an automatic support claim.
7. Add automated validation only after the desired behaviour is explicit.

## Implementation Readiness

The repository is now expected to support focussed implementation sessions from the canonical docs without rediscovering the earlier analysis work.

Current execution stance:
- use `AGENTS.md`, `ARCHITECTURE.md`, `docs/SUPPORT.md`, and the active exec-plan docs as the contract for implementation work,
- treat `CODEBASE_MAP.md` and `VERIFICATION_AUDIT.md` as evidence inputs when a code path needs proof or historical context,
- prefer one debt item or parity gap at a time,
- when asked to use TDD, begin with the smallest behaviour-level slice that can be exercised through a real or simulated public interface.

## Active Plan References

- `docs/exec-plans/active/documentation-harness.md`
- `docs/exec-plans/active/implementation-readiness.md`
- `docs/exec-plans/active/diy-support.md`
- `docs/exec-plans/tech-debt-tracker.md`

## Completed Investigation References

- `CODEBASE_MAP.md`
- `VERIFICATION_AUDIT.md`
- `docs/generated/parity-gap-register.md`
- `docs/generated/tested-but-not-confirmed-capabilities.md`

These are dated evidence artefacts. They are useful inputs to the canonical docs, but they are not the long-term public documentation surface.
