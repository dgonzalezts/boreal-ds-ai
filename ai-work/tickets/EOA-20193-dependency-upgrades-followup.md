# EOA-20193 — dependency-upgrades-followup

**Ticket:** [EOA-20193](https://telesign.atlassian.net/browse/EOA-20193) (continues EOA-19635, closed)
**Goal:** Finish the dependency maintenance baseline by applying the deferred major upgrades and follow-ups on a branch cut from the PR 1 branch, so that PR 1 reaches `release/current` once with everything in it.

## Scope

**In:**
- Prerequisites: confirm the Node version on the Jenkins agents and record the Node target (24 or 26).
- Wave 1: prettier 3.9, ESLint 10, the Stencil 4.45.2 boolean-attribute investigation, a dependency report script for the Jenkins job (policy Phase 2).
- Wave 2: automated wrapper tests for Vue and React, TypeScript 6.0.3, the `typescript-eslint` 8.59+ errors, Vitest 5 with jsdom 30, Vite 8.
- Wave 3: the `./components` export with `@stencil/react-output-target`, the `@tanstack/virtual-core` range, `@colordx/core` 5 to 7.
- Wave 4: Stencil unit tests on `@stencil/vitest`, Chromatic CLI 18 with addon 5, lint-staged / chalk / execa / npm-run-all2.
- The pnpm 11 to 12 upgrade, late in the order and deferrable to the third PR (added 2026-11-11).
- Housekeeping: hold register, monthly template seed list, PR descriptions, plan index.
- The 2026-11-13 deadline safeguard.

**Out:**
- Merging PR 1 (#208) and closing EOA-20016: done by the user.
- The Node move itself (kept as a draft in the release-process follow-up file).
- Renovate and any DevOps-dependent work.
- Any new Jira ticket other than EOA-20193 and its six sub-tasks.
- Dev-only audit findings unless they block a gate.

## Jira sub-tasks

Grouping of the plan tasks (`ai-work/plans/EOA-20193-dependency-upgrades-followup.md`) into six sub-tasks of EOA-20193, created 2026-11-11.

| Key | Title | Plan tasks | Status |
| --- | --- | --- | --- |
| [EOA-21184](https://telesign.atlassian.net/browse/EOA-21184) | Baseline and safe tooling updates | T1, T2, T3, T4, T19 | in progress (T1, T2 done; T3 in progress) |
| [EOA-21185](https://telesign.atlassian.net/browse/EOA-21185) | TypeScript 6, Vitest 5 and Vite 8 toolchain | T8, T9, T10, T11 | pending |
| [EOA-21186](https://telesign.atlassian.net/browse/EOA-21186) | Stencil pin, wrapper tests and ./components export | T5, T7, T12 | pending |
| [EOA-21187](https://telesign.atlassian.net/browse/EOA-21187) | Runtime dependencies: virtual-core and colordx | T13, T14 | pending |
| [EOA-21188](https://telesign.atlassian.net/browse/EOA-21188) | Dependency report script and Chromatic upgrade | T6, T18 | pending |
| [EOA-21189](https://telesign.atlassian.net/browse/EOA-21189) | Jest to @stencil/vitest migration and close-out | T15, T16, T17, T20, T21 | pending |

## Acceptance Criteria

- [ ] Every task in the plan is done, or explicitly left out by the user before 2026-11-13.
- [ ] Each task is one commit on the working branch, green on the standard gates before it is committed.
- [ ] PR 2 (working branch into the PR 1 branch) is merged before PR 1 merges to `release/current`.
- [ ] Lifted holds are removed from the monthly hold register and from the template seed list.
- [ ] The PR 1 and PR 2 descriptions list the tasks included and any breaking change.

## Dependencies

- PR 1 (#208) open on `chore/EOA-19635_dependency-security-and-minor-updates_DG`, and EOA-20016 closed after its merge.
- Jenkins agent Node version (needed for jsdom 30, Chromatic CLI 18 and the utilities, which require Node 22.22.2 or later).
- The Chromatic token holder, for one real `pnpm deploy:docs` after the Chromatic upgrade.
- Decisions from the user on the published surface: the `./components` export and the `virtual-core` range.

## Open Questions

- Does the Jenkins job definition live in a repository this team can edit? There is no Jenkinsfile in this repository.
- Node 24 or 26 as the target; the Node move itself is outside this plan.
- Is the React part of the wrapper tests worth the new tooling?
