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
- The pnpm 11 to 12 upgrade, late in the order and deferrable (added 2026-11-11; done as T20 on 2026-11-13).
- Housekeeping: hold register, monthly template seed list, PR descriptions, plan index.
- The 2026-11-13 deadline safeguard.

**Out:**
- Merging PR 1 (#208) and closing EOA-20016: done by the user (PR 1 merged on 2026-11-13).
- The Node move itself (kept as a draft in the release-process follow-up file).
- Renovate and any DevOps-dependent work.
- Any new Jira ticket other than EOA-20193 and its six sub-tasks.
- Dev-only audit findings unless they block a gate.

## Jira sub-tasks

Grouping of the plan tasks (`ai-work/plans/EOA-20193-dependency-upgrades-followup.md`) into six sub-tasks of EOA-20193, created 2026-11-11. The statuses below were updated locally on 2026-11-13; nothing was changed in Jira. T22 (merge readiness) and T23 (Confluence template page, deferred) are not part of any sub-task.

| Key | Title | Plan tasks | Status |
| --- | --- | --- | --- |
| [EOA-21184](https://telesign.atlassian.net/browse/EOA-21184) | Baseline and safe tooling updates | T1, T2, T3, T4, T19 | done (T1, T2, T3, T4, T19) |
| [EOA-21185](https://telesign.atlassian.net/browse/EOA-21185) | TypeScript 6, Vitest 5 and Vite 8 toolchain | T8, T9, T10, T11 | done |
| [EOA-21186](https://telesign.atlassian.net/browse/EOA-21186) | Stencil pin, wrapper tests and ./components export | T5, T7, T12 | done (T7 is Vue only, plus T7b and T7c) |
| [EOA-21187](https://telesign.atlassian.net/browse/EOA-21187) | Runtime dependencies: virtual-core and colordx | T13, T14 | done |
| [EOA-21188](https://telesign.atlassian.net/browse/EOA-21188) | Dependency report script and Chromatic upgrade | T6, T18 | partly: T6a and T18 done (the real `pnpm deploy:docs` was reported successful on 2026-11-13); T6b (dependency report script) deferred |
| [EOA-21189](https://telesign.atlassian.net/browse/EOA-21189) | Jest to @stencil/vitest migration and close-out | T15, T16, T17, T20, T21 | partly: T20 done; T15 (spike, done) and T16 and T17 (migration, removal of Jest) deferred to a follow-up; T21 in progress |

## Acceptance Criteria

- [ ] Every task in the plan is done, or explicitly left out by the user before 2026-11-13. (T6b, T15 to T17 and T23 are left out by the user's decisions; T21 items 11 and 12 and T22 are still open.)
- [x] Each task is committed on the working branch only when green on the standard gates (27 commits; T3, T12, T19 and T20 have two, and T12 and T19 needed a follow-up commit for a lockfile that was missing from the first).
- [x] Order changed by the user on 2026-11-13: PR 1 (#208) was squash-merged first (`ef73a750` on `release/current`) and this branch was rebased onto it (0 conflicts). [ ] The second PR from this branch to `release/current` is merged.
- [x] Lifted holds are removed from the local template seed list (all six lifted; the new register is in it). [ ] The Confluence template page is synced after the merges (deferred task T23).
- [x] The description of the second PR lists the tasks included and the breaking changes (drafted; the user pastes it). PR 1 merged with its own description.

## Dependencies

- PR 1 (#208) on `chore/EOA-19635_dependency-security-and-minor-updates_DG`: merged on 2026-11-13; EOA-20016 to be closed by the user.
- Jenkins agent Node version (needed for jsdom 30, Chromatic CLI 18 and the utilities, which require Node 22.22.2 or later).
- The Chromatic token holder, for one real `pnpm deploy:docs` after the Chromatic upgrade.
- Decisions from the user on the published surface: the `./components` export and the `virtual-core` range.

## Open Questions

- Does the Jenkins job definition live in a repository this team can edit? There is no Jenkinsfile in this repository. Still open; T6b stays deferred.
- Node 24 or 26 as the target; the Node move itself is outside this plan. Decided 2026-11-11: Node 26 with 24 as fallback.
- Is the React part of the wrapper tests worth the new tooling? Decided: no, the React half was dropped (T7).
