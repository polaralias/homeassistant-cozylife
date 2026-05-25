# Contributing

Use [AGENTS.md](AGENTS.md) as the repo-specific operating guide. This file defines the shared Git and release workflow expected across Polaralias repositories.

## Branch Workflow

- branch from `main`
- do not commit directly to `main`
- use short-lived branches named `feat/...`, `fix/...`, `docs/...`, `chore/...`, `refactor/...`, or `test/...`
- keep one logical change per branch and pull request
- rebase or merge `main` into your branch before merge if it has drifted

## Pull Requests

- open a pull request for every merge into `main`, including solo work
- use draft pull requests for partial work and mark them ready only when the branch is reviewable
- summarize the behavior change, validation performed, and docs touched
- prefer squash merge unless preserving multiple commits has durable review value
- delete the merged or closed feature branch after the work is finished; never delete `main`

## Releases

- use tags in `vX.Y.Z` format for releases
- pushes to `main` update the draft release notes
- pushing a `vX.Y.Z` tag publishes or refreshes the corresponding GitHub Release
- do not move or reuse published release tags

## Licensing

- by contributing, you agree your changes are licensed under `Apache-2.0`
- preserve copyright and license notices in forks and redistributions

## Verification

- run the smallest relevant local test, lint, or build path before opening a pull request
- when behavior changes, update tests and documentation in the same branch
- never commit secrets, machine-local credentials, or unredacted personal data
