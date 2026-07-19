# Design

This repository should evolve towards a design that is boring in the right places and explicit in the uncertain places.

## Design Goals

- Make the supported product surface obvious.
- Make verification status visible.
- Avoid hidden compatibility rules.
- Prefer one clear path for onboarding, discovery, and runtime state.
- Expose hardware quirks as documented constraints instead of folklore.

## Current Design Tension

The repository currently combines:
- a compact integration structure,
- useful real-world protocol knowledge,
- legacy compatibility paths,
- uneven entity modelling,
- limited verification evidence.

That combination is acceptable for an internal project, but not yet sufficient for a public portfolio-quality integration.

## Desired Design Outcome

The intended design should make it easy to answer these questions:
- What devices are supported?
- How are they discovered?
- What Home Assistant entities do they create?
- What protocol assumptions are verified?
- What reliability guarantees are intended?
- What is known debt versus accidental behaviour?

## Design Standard

Every major behaviour should eventually have one home:
- architecture belongs in `ARCHITECTURE.md`,
- principles belong in `docs/design-docs/`,
- user-facing behaviour belongs in `docs/product-specs/`,
- active execution work belongs in `docs/exec-plans/`.
