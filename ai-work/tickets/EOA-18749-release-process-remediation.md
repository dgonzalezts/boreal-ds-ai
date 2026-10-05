# EOA-18749 — release-process-remediation

**Ticket:** [EOA-18749](https://telesign.atlassian.net/browse/EOA-18749) — SPIKE - Release pipeline hardening — wrapper-generation validation & release automation (parent epic [EOA-18400](https://telesign.atlassian.net/browse/EOA-18400), PI9)
**Goal:** Make the alpha release process trustworthy and shareable with the team: correct versions, accurate per-package changelogs, no releases without changes, wrappers always pinned to the current web-components version, and publishing under the new `@pxglobal` npm scope.

## Scope

**In:**

- Upgrade Node (22.23.3) and release tooling (`release-it` 21, `@release-it/conventional-changelog` 12) first — enables native skipping of non-releasable changes
- Fix the five release-process defects from the 2026-08-12 audit by patching `release-it` in place (ADR 0013, Option A — accepted 2026-10-01)
- Skip any package with no changes since its last release; never publish an empty release
- Release orchestration: `release:styles` (independent) and `release:wc-stack` (web-components → `validate:all` → React → Vue)
- A token change in style-guidelines also releases web-components and both wrappers (decision (a))
- Backfill changelog entries lost to unparseable squash-merge titles
- Two maintained changelogs — web-components (also covers tokens and React/Vue) and style-guidelines; React/Vue changelogs become pointers
- Retroactive CHANGELOG cleanup: link rewrite (required), trim each maintained changelog to its own entries (recommended)
- Squash and merge as the required merge method (documented in CONTRIBUTING.md)
- Folder rename `packages/boreal-styleguidelines` → `packages/boreal-style-guidelines`
- npm scope rename `@telesign/*` → `@pxglobal/*` starting at `0.14.0` with no prerelease suffix (alpha stated in docs), `git.tagMatch`/anchor tags, a changelog "moved" notice, and `latest` tracking the newest version
- Workspace-root `CONTRIBUTING.md` and an updated `ai-docs/guidelines/release-process.md`
- Final documentation sync after the first `@pxglobal` release: internal guidelines, diagrams, agent/skill docs, and Boreal-owned Confluence pages (Publishing & Deployment Guide, ADR-0011 amendment, ADR 0013 publication); owners of consumer pages notified

**Out:**

- Any real publish, tag push, or npm deprecation — performed later, by the single admin npm user, during the end-to-end test (EOA-18866)
- Migration to `changesets` (ADR 0013 Option B — revisit triggers recorded in the ADR)
- Automated PR-title enforcement (no server-side hook access)
- CI wrapper-generation gate and drift smoke test — deferred until the DevOps meeting (EOA-18870) confirms pipeline access
- Graduation to `1.0.0` / stable package strategy (EOA-18867)
- Editorial noise cleanup of historical changelogs (A7 tier 3) — open decision
- Creating the `@pxglobal` npm org and users (EOA-18864, external)

## Acceptance Criteria

- [ ] While below 1.0 (`preMajor`): a breaking change produces a `preminor` bump; `feat`/`fix`/`perf`/`revert` produce `prepatch` (e.g. `0.1.0-alpha.12` → `0.1.1-alpha.0`); no commit moves the library to `1.0.0` on its own
- [ ] The first `@pxglobal` release publishes all four packages at `0.14.0` (plain `0.x`, alpha status stated in READMEs, Storybook, and CONTRIBUTING.md); `@telesign` history stays in the CHANGELOGs, git tags, and deprecation messages
- [ ] Each package's version bump only reflects commits touching its own folder (web-components also counts style-guidelines)
- [ ] Only web-components and style-guidelines write a changelog; web-components' changelog includes token and wrapper-only changes
- [ ] A package with no releasable commits (`feat`, `fix`, `perf`, `revert`, breaking) since its last tag is skipped without failing the release chain; `docs`/`test`/`chore`-only changes never publish
- [ ] Every web-components release is followed by React and Vue releases that pin the new web-components version
- [ ] A PR title of the form `Pull request #N: feat(scope): …` is parsed into the changelog
- [ ] Generated and historical commit/compare links resolve on Bitbucket Server (`/projects/DEV/repos/boreal-ds/...`)
- [ ] Squash-merged PRs missing from published changelogs are backfilled
- [ ] All four packages build, validate, and dry-run under `@pxglobal/*`
- [ ] `CONTRIBUTING.md` documents branching, commits, PR rules, and the release/versioning policy (including minor vs. patch in alpha)
- [ ] Every change is validated with `release-it --dry-run`; nothing is published or tagged remotely

## Dependencies

- EOA-18864 — `@pxglobal` npm org and publishing user (prerequisite for the end-to-end test, not for implementation)
- EOA-18866 — end-to-end release test, run after the teammate returns from PTO
- EOA-18870 — DevOps meeting; may unblock CI gates and a non-personal publish token
- Only one admin npm user can publish; credentials cannot be shared

## Open Questions

- A7 tier 3 (editorial noise cleanup, ~3,100 changelog lines): invest or skip?
- Who runs `npm deprecate` on the four `@telesign` packages, and when (after the first `@pxglobal` publish)?
- Single-publisher risk: raise a CI/automation publish token with DevOps (EOA-18870)?
- Confirm with the epic owner that "remains in alpha this PI" (EOA-18400) means stated status, not a `-alpha` version suffix — before Task 10
- Restrict the repository's merge methods to squash-only in Bitbucket (admin setting, EOA-18870)?
