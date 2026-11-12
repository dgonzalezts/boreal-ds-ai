---
ticket: EOA-20193
status: in progress
created: 2026-10-30
---

# Dependency Upgrades Follow-up Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Apply the deferred major upgrades and follow-ups from the dependency maintenance baseline on a branch cut from the PR 1 branch, so PR 1 reaches `release/current` once with everything in it.

**Ticket brief:** [`ai-work/tickets/EOA-20193-dependency-upgrades-followup.md`](../tickets/EOA-20193-dependency-upgrades-followup.md)

**Architecture:** One working branch, `chore/EOA-20193_dependency-upgrades-followup_DG`, cut from the tip of `chore/EOA-19635_dependency-security-and-minor-updates_DG` (PR 1, #208). Each task is committed on it only when it is complete and green, then pushed. At the end PR 2 (working branch into the PR 1 branch) is merged first, and then PR 1 is merged into `release/current` once. Source material: the 14 upgrade drafts (U1 to U14) in `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`, draft R7 in `ai-work/tickets/EOA-18749-release-process-followup-tickets.md`, the three research files `ai-work/research/2026-10-27-EOA-19635-*`, and the findings of tasks 13 to 22 of `ai-work/plans/EOA-19635-dependency-maintenance-baseline.md`.

**Tech Stack:** pnpm 11 workspaces, Turborepo, Stencil 4.45.1, Storybook 10, Vite, Vitest, Jest (Stencil runner), ESLint, TypeScript, Chromatic, release-it.

---

## Working agreements

- **Branching:** the working branch is cut from the PR 1 branch and pushed with upstream tracking. There are no per-task branches and no per-task PRs. The user opens PR 2 (target: the PR 1 branch) and merges it before PR 1 merges to `release/current`.
- **Jira:** EOA-20193 is the only ticket. No other ticket is created and no sub-tasks. Jira is changed only on the user's instruction.
- **One commit per task**, with the message confirmed by the user before it is run. T3 (two commits) and T16 (one commit per batch) are the stated exceptions. No `Co-Authored-By` trailer. Never commit `src/index.html`.
- **A task is committed only when it is complete and green** on the standard gates. Partial work stays uncommitted or on a local scratch branch, so the working branch never holds a half-finished task.
- **Push after each confirmed task.** The pre-push hook runs the full unit suite, about one minute.
- **Start of each task:** `git fetch`. If `release/current` has new commits, tell the user before continuing; merging it into the PR 1 branch and then into the working branch is the user's decision.
- **Confirm after each task**, one task at a time, as the plan-execution rules require.
- **Code rules:** no inline comments, no `any`, JSDoc only on exported public API, no ticket IDs in test names.

## Standard gates

Run from the repository root after `fnm use`. A task is green when all pass:

1. `pnpm lint` exits 0 (warnings baseline: docs 9, web-components 50, test apps 0).
2. `pnpm --filter @pxglobal/boreal-web-components test:coverage` passes with the 80% thresholds (baseline 375 suites, 4,810 tests, coverage 93.2 / 85.6 / 92.7 / 94.8).
3. `pnpm build` passes for all workspaces and leaves `git status` clean.
4. `pnpm peers check` is clean.
5. After the task's commit: `pnpm validate:all` passes. It restores the wrapper and test-app manifests and the lockfile with `git checkout HEAD --`, so changes must be committed first. If it fails, fix and amend with the user's agreement before pushing.
6. `pnpm --filter scripts-boreal test:coverage` passes when `scripts-boreal` changed.

Lockfile edits are formatted with the web-components Prettier. New versions must be older than the 1-day `minimumReleaseAge`.

## Deadline safeguard: 2026-11-13

The production audit fixes (29 to 0 vulnerabilities) are already on the PR 1 branch and stay unreleased until it merges. The policy asks for high and critical findings within 2 weeks, counted from the 2026-10-16 snapshot. A revert of the single squash commit would also revert those fixes. So:

- **Checkpoint on 2026-11-12** (T22): list the tasks done and green and the tasks not started or unfinished.
- **On 2026-11-13** PR 2 is merged into PR 1 with the completed tasks only, and PR 1 is merged to `release/current`. Unfinished tasks are not committed on the branch.
- **Unfinished tasks** continue on the working branch after PR 1 merges and go in a third PR to `release/current`. The branch is rebased first: `git rebase --onto release/current <PR 1 branch tip before the squash>` drops the already squashed commits.
- The date moves only if the user decides so in writing in this plan.

## Risks

| Risk | Mitigation |
| --- | --- |
| The squash merge to `release/current` is one commit with one conventional type and one version bump | Put `!` in the PR 1 title when any task is breaking; below 1.0, mark doubtful ones breaking. Consumer-visible items (T12, T14, Node floors in T19) are listed in the PR description. |
| `pnpm-lock.yaml` conflicts when `release/current` moves | Check at the start of every task; user decides on the merge. |
| One failing major blocks the whole PR | A task is committed only when green; an unfinished task is excluded. |
| A revert after release takes the security fixes with it | The deadline safeguard; tasks are separate commits on PR 2 so a single one can be reverted before the final merge. |
| PR 2 reviewer load | The PR descriptions carry a per-task list; each task is one commit. |
| PR 1 is squash-merged before PR 2 | Accepted: the order is PR 2 into PR 1 first. The rebase recipe above covers the exception. |
| The November monthly window overlaps | Its patch and minor bumps land on the same branch as extra commits, after the tasks already planned. |
| Drafts have stale statements | Each task has an integration research pass; the live grounding check at execution is the safety net. One known case is in T10. |

## Open assumptions (confirm before dispatching the affected task)

- **A1 — Jenkins job location:** there is no Jenkinsfile in this repository. T6a delivers documentation only (the commands and the stage rules in the `scripts-boreal` README) and T6b, the script, is deferred; wiring the stage into the Jenkins job is outside the repository.
- **A2 — Report exit code (T6b):** confirmed by the user, then refined in the T6 review: three states, 0 clean, 1 high or critical production findings, 2 the check could not run or its output could not be parsed.
- **A3 — Jenkins Node version (T2):** jsdom 30, Chromatic CLI 18 and the utilities need Node 22.22.2 or later. The repository pin is 22.23.3, which meets it. Only the agents' version is unknown.
- **A4 — TypeScript 7 side by side:** excluded from T8; it is optional in the draft and waits for TypeScript 7.1.
- **A5 — React wrapper tests (T7):** Part B is dropped if the user decides React is not worth the new tooling.
- **A6 — Node move and pnpm 12:** the Node move is not in this plan and remains draft R3. The pnpm 11 to 12 upgrade was added as T20 on 2026-11-11 at the user's request (the baseline ticket had left it out of scope); it is late in the order and deferrable to the third PR.

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `package.json` (root) | Modify — lint-staged, engines, scripts (T3, T19, T6) |
| `apps/boreal-docs/package.json` | Modify — prettier, eslint, typescript, vitest, vite, chromatic (T3, T4, T8, T10, T11, T18) |
| `packages/boreal-web-components/package.json` | Modify — prettier, eslint, typescript-eslint, `@stencil/core` pin, virtual-core, colordx, jest removal, exports (T3 to T5, T9, T12 to T17) |
| `packages/boreal-react/package.json`, `packages/boreal-vue/package.json` | Modify — TypeScript, output-target versions (T8, T12) |
| `packages/boreal-style-guidelines/package.json`, `scripts-boreal/package.json` | Modify — TypeScript, vitest, chalk, execa (T8, T10, T19) |
| `examples/react-testapp/*`, `examples/vue-testapp/*` | Modify — plugins, vite config, vitest, wrapper tests (T4, T7, T10, T11, T19) |
| `tsconfig` files of the workspaces | Modify — TypeScript 6 settings (T8) |
| `scripts-boreal/README.md` | Modify — dependency check commands and stage rules (T6a) |
| `scripts-boreal/bin/deps-report.js`, `scripts-boreal/lib/deps-report.js`, `scripts-boreal/lib/__tests__/deps-report.spec.js` | New — dependency report (T6b, deferred) |
| `packages/boreal-web-components/stencil.config.ts`, `vitest.config.ts`, spec files | Modify / New — test runner migration (T15 to T17) |
| `pnpm-workspace.yaml` | Modify — the scoped peer rule (T4), its replacement by the `:peer` override (T20) |
| `README.md`, `ai-docs/guidelines/cicd-dependency-installation.md` | Modify — pnpm version prerequisite (T20) |
| `pnpm-lock.yaml` | Modify — every dependency task |
| `ai-docs/templates/dependency-maintenance-ticket.md` | Modify — hold register seed list (T21) |
| `.claude/pr-description.md` | Modify — PR descriptions (T21, T22) |

---

## Progress

| Task | Status |
| --- | --- |
| T1 Create the working branch and record the gate baseline | done 2026-11-11, confirmed by the user 2026-11-11 |
| T2 Confirm the Jenkins Node version and record the Node target | done 2026-11-11, confirmed by the user 2026-11-11 |
| T3 Update prettier to 3.9 and reformat the flagged files | done 2026-11-11, confirmed by the user (`38a69981`, `46206715`) |
| T4 Upgrade ESLint to 10 with its companions | done 2026-11-11, confirmed by the user (`9fc3dc40`) |
| T5 Investigate the Stencil 4.45.2 boolean-attribute change and remove the 4.45.1 pin | done 2026-11-11, confirmed by the user (`6e6530e2`) |
| T6a Document the dependency check commands and the stage rules | done 2026-11-11, confirmed by the user (`a8d5473e`) |
| T6b Add the dependency report script | deferred by the user's decision (not before the Jenkins stage is confirmed) |
| T7 Add automated wrapper tests for Vue (React half dropped) | done 2026-11-11, confirmed by the user (`0e4f072e`) |
| T7b Fix the `bds-toggle` v-model mapping in the Vue wrapper | done 2026-11-12, confirmed by the user (`3554eda5`) |
| T7c Document the Vue `v-model` contract | done 2026-11-12, awaiting confirmation (`992dcbf5`) |
| T8 Upgrade TypeScript to 6.0.3 | pending |
| T9 Clear the `typescript-eslint` 8.59+ type-assertion errors | pending |
| T10 Upgrade Vitest to 5 and jsdom to 30 | pending |
| T11 Upgrade Vite to 8 and its React plugin | pending |
| T12 Add the `./components` export and lift the `@stencil/react-output-target` hold | pending |
| T13 Resolve the `@tanstack/virtual-core` 3.19.6+ failures | pending |
| T14 Upgrade `@colordx/core` 5 to 7 | pending |
| T15 Spike the migration to `@stencil/vitest` | pending |
| T16 Migrate the web-components specs in batches | pending |
| T17 Remove Jest and Puppeteer and update the test documentation | pending |
| T18 Upgrade the Chromatic CLI to 18 and the addon to 5 | pending |
| T19 Upgrade lint-staged, chalk, execa and npm-run-all2 | pending |
| T20 Upgrade pnpm 11 to 12 | pending |
| T21 Housekeeping: holds, template, PR descriptions, index | pending |
| T22 Deadline checkpoint and merge readiness | pending |

---

## Wave 0: prerequisites

### Task 1: Create the working branch and record the gate baseline

**Status:** done 2026-11-11, confirmed by the user 2026-11-11. Branch `chore/EOA-20193_dependency-upgrades-followup_DG` cut from `6495b48e` (the PR 1 branch tip, identical locally and on the remote; `release/current` had no new commits) and pushed with upstream tracking. PR 1 (#208) is still open and not merged. Baseline on the working branch: lint 0 errors (warnings docs 9, web-components 50, test apps 0); 375 suites and 4,810 tests; coverage 93.24 / 85.64 / 92.66 / 94.75; build 7/7 with a clean tree; `pnpm peers check` clean; `validate:all` passes (React and Vue) with a clean tree; `scripts-boreal` 45 tests, 98.27% statements. Remaining for the user: open PR 2 (source: the working branch, target: the PR 1 branch)
**Executor:** main thread (no executor)
**Files:** none (no code change)

**Acceptance criteria:**

- `chore/EOA-20193_dependency-upgrades-followup_DG` is cut from the tip of the PR 1 branch and pushed with upstream tracking.
- PR 1 (#208) is confirmed to be still open and its branch has no commits that are not on the working branch.
- The standard gates are run once on the working branch and the numbers are recorded in this task's status line as the baseline.
- The user is told the branch is ready to open PR 2 (target: the PR 1 branch); the pull request itself is opened by the user.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with `git log --oneline -3` on both branches and the standard gates.

- [x] Given the working branch, when compared with the PR 1 branch, then they point to the same commit. Pass: `git rev-parse` outputs match. _(both `6495b48e`)_
- [x] Given the standard gates, when run, then all pass. Pass: baseline recorded.

**Commit:** none.

### Task 2: Confirm the Jenkins Node version and record the Node target

**Status:** done 2026-11-11, confirmed by the user 2026-11-11. The Jenkins job has not been implemented yet, so there are no agents to check; it will be built on the chosen Node version. Decision: the Node target is **26, with 24 as the fallback** if a short check under 26 (lint, unit suite, builds, `validate:all`, a release dry run, run locally with `fnm`) fails. The published packages declare no `engines`, so the choice only affects contributors and CI. Consequence for the plan: T10 (jsdom 30), T18 and T19 can proceed (the repository pin 22.23.3 already meets their 22.22.2 floor). The Node move itself stays outside this plan (draft R3).
**Executor:** main thread (no executor)
**Files:** none (the answer is recorded in this plan)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Facts from the 2026-10-27 runtimes research: `.node-version` is 22.23.3 and root `engines.node` is `>=22`. Node 22 ends life 2027-04-30; Node 24 entered maintenance on 2026-10-20; Node 26 became Active LTS on 2026-10-28. `jsdom` 30 needs `^22.22.2 || ^24.15 || >=26`; Chromatic CLI 18 needs Node 22 or later; `npm-run-all2` 9 needs `^22.22.2 || ^24.15 || >=26`.
- [ ] Boundary case: if the Jenkins agents run a Node below 22.22.2, T10 (jsdom part), T18 and T19 cannot be committed as planned. They would be postponed past the deadline, and the user decides.
- [ ] Default state: the Node move itself is not planned here; this task only records the agents' version and the preferred target (24 or 26).

**Acceptance criteria:**

- The Jenkins agents' Node version is recorded with its source (the user or DevOps).
- The preferred Node target (24 or 26) is recorded.
- For T10, T18 and T19 the plan states whether they can proceed.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate by reading the recorded answer in this task's status line.

- [x] Given the recorded answer, when compared with the floors above, then T10, T18 and T19 are marked "can proceed" or "blocked". Pass: each has a marking. _(all three can proceed)_

**Commit:** none.

---

## Wave 1: independent, low risk

### Task 3: Update prettier to 3.9 and reformat the flagged files

**Status:** done 2026-11-11, committed and pushed, confirmed by the user 2026-11-11: `38a69981` `build(deps): EOA-20193 update prettier to 3.9` and `46206715` `style(multiple): EOA-20193 reformat files with prettier 3.9`. The second message needed the scope `multiple`: the repository's commit-msg hook has a custom `scope-required` rule that rejects an empty scope, which the earlier `style:` message would have hit. `pnpm validate:all` passes on the committed state (React and Vue) with a clean tree; the pre-push suite passed (375 suites, 4,810 tests). All four `prettier` pins moved to exactly `3.9.10`: it is the newest version older than the 1-day delay, because `3.10.0` was published on 2026-11-11 (age 0.4 days). The lockfile was refreshed and formatted with the new prettier (92-line diff). `format:check` flagged exactly the 14 + 2 files from the baseline finding (docs 14, web-components 2; the React test app keeps its 3 pre-existing flagged files, the Vue test app passes) and the reformat touched only those 16 files (276 insertions, 226 deletions). Gates before commit: `format:check` passes in docs and web-components, lint 0 errors (warnings 9 / 50 / 0), 375 suites and 4,810 tests, coverage 93.24 / 85.64 / 92.66 / 94.75, build 7/7, `pnpm peers check` clean. Remaining after the commits: `pnpm validate:all` and the push
**Executor:** main thread (no executor)
**Files:**

- `apps/boreal-docs/package.json`, `examples/vue-testapp/package.json`, `examples/react-testapp/package.json`, `packages/boreal-web-components/package.json` (modify)
- `pnpm-lock.yaml` (modify)
- The 16 files that `format:check` flags at 3.9 (modify, formatting only)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Current pins (checked 2026-10-30): docs, Vue test app and React test app at exact `3.8.1`; web-components at exact `3.8.0`.
- [ ] Finding from the baseline: `format:check` passes at 3.8.0 and 3.8.1 and flags 2 + 14 files at 3.9.10. The React test app has 3 flagged files at both versions (generated `.vite/deps/_metadata.json` and two config files), so it is not affected.
- [ ] Call sites: `lint-staged` runs the package `format` script on staged files, so unreformatted files would be rewritten inside unrelated commits.
- [ ] Reactivity: not applicable.

**Acceptance criteria:**

- All four `prettier` pins move to the same version, the newest one older than the 1-day delay, keeping the exact-pin style.
- The flagged files are reformatted in a second commit that contains formatting changes only.
- Every `format:check` script passes.
- Re-format step after `release/current` receives other merged PRs: those files were formatted with prettier 3.8 by their authors, so after `release/current` is merged into the branch, run `pnpm format:check` in `apps/boreal-docs` and `packages/boreal-web-components`. If anything is flagged, run `pnpm format` in both and commit the result as one more formatting-only commit. If a merge conflicts on the 16 files above, take the incoming version and re-run the formatter.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with each package's `format:check` script and the standard gates.

- [ ] Given the bumped pins, when `format:check` runs in each workspace, then it passes after the reformat commit. Pass: exit code 0 everywhere that passed before.
- [ ] Given the reformat commit, when `git show --stat` is read, then it contains only the flagged files. Pass: no other file.

**Commit (two commits, each confirmed by the user):**

```bash
git commit -m "build(deps): EOA-20193 update prettier to 3.9"
git commit -m "style(multiple): EOA-20193 reformat files with prettier 3.9"
```

### Task 4: Upgrade ESLint to 10 with its companions

**Status:** done 2026-11-11, committed `9fc3dc40` and pushed, confirmed by the user 2026-11-11. `pnpm validate:all` passes on the committed state (React and Vue) with a clean tree; the pre-push suite passed (375 suites, 4,810 tests). Tested while deciding the peer rule: the `overrides` entry with the `:peer` suffix fails on pnpm 11.28.2 and on the newest pnpm 11 (11.28.11) with `ERR_PNPM_INVALID_SELECTOR`, and works on pnpm 12.19.0, which also accepts the `peerDependencyRules` entry; T20 therefore swaps the rule for the override. Versions applied (registry checked 2026-11-11, all older than the 1-day delay): `eslint` `^10.14.0` in the four workspaces (the planning trial used 10.13.0), `@eslint/js` `^10.0.1` in docs, web-components and the React test app, `globals` `^17.14.0` in the React test app (docs already `^17.0.0`), `eslint-plugin-jsdoc` `^65.4.5` in web-components (Node `^22.22.2 || >=24.15.0`; the repository pin 22.23.3 meets it). `typescript-eslint` stays at `~8.58.2`: that exact version already declares ESLint 10 in its peer range, so T9 is unaffected. Every other ESLint plugin in the four workspaces declares ESLint 10 support (`@stencil/eslint-plugin` 1.4.0, `eslint-plugin-storybook`, `eslint-plugin-vue`, `@vue/eslint-config-typescript` 14.9.0, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `eslint-config-prettier`). Workaround for the one blocker: `eslint-plugin-react` `7.37.5` (exact) added as a devDependency of web-components, and `pnpm-workspace.yaml` gets `peerDependencyRules.allowedVersions` `"eslint-plugin-react>eslint": "10"`, so `pnpm peers check` is clean. The `overrides` entry with the `:peer` suffix that the pnpm docs recommend does not work on the repository's pnpm 11.28.2 (`ERR_PNPM_INVALID_SELECTOR`); `peerDependencyRules` is documented as deprecated but still supported. Remove both once `eslint-plugin-react` or `@stencil/eslint-plugin` declares ESLint 10 (candidate row for the hold register in T20). Gates before commit: lint 0 errors with warnings 9 / 50 / 0 / 0 (same as the baseline), 375 suites and 4,810 tests, coverage 93.24 / 85.64 / 92.66 / 94.75, build 7/7, `pnpm peers check` clean. Remaining after the commit: `pnpm validate:all` and the push
**Executor:** main thread (no executor)
**Files:**

- `apps/boreal-docs/package.json`, `packages/boreal-web-components/package.json`, `examples/react-testapp/package.json`, `examples/vue-testapp/package.json` (modify)
- `pnpm-workspace.yaml` (modify — the scoped peer rule)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Trial result from the planning (disposable worktree): identical lint results in all four workspaces (0 errors; 9, 50, 0 and 0 warnings) and 0 findings from the three rules added to the recommended set.
- [ ] Known blocker: `@stencil/eslint-plugin` 1.4.0 loads its optional peer `eslint-plugin-react` unconditionally and `eslint-plugin-react` 7.37.5 does not declare ESLint 10. Verified workaround: declare `eslint-plugin-react@7.37.5` as an explicit devDependency of web-components; decide whether to add a `peerDependencyRules` entry for the unmet-peer warning.
- [ ] Companions: `eslint` 10.13.0, `@eslint/js` 10.0.1, `globals` 17.13.0 in the React test app, and `eslint-plugin-jsdoc` 65.4.2 only if T2 confirms Node 22.22.2 or later.
- [ ] Boundary case: the `typescript-eslint` cap `~8.58.2` is unchanged here; whether it supports ESLint 10 must be checked at execution, not assumed.

**Acceptance criteria:**

- Lint passes in all four workspaces with the same error and warning counts.
- `pnpm peers check` is clean, or the exception is documented in this task's status line.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with lint in each workspace and the standard gates.

- [x] Given ESLint 10, when `pnpm lint` runs, then error counts are 0 and warning counts equal the baseline. Pass: 9 / 50 / 0 / 0.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade eslint to 10"
```

### Task 5: Investigate the Stencil 4.45.2 boolean-attribute change and remove the 4.45.1 pin

**Status:** done 2026-11-11, committed `6e6530e2` `build(deps): EOA-20193 update @stencil/core to ^4.45.2 and adapt tests and docs` and pushed, confirmed by the user 2026-11-11. `pnpm validate:all` passes on the committed state (React and Vue) with a clean tree; the pre-push suite passed (375 suites, 4,810 tests). Decision by the user 2026-11-11: **accept the new Stencil behavior** and adapt tests and docs; no consumer-facing migration note (the library has no real consumers yet), only this record and a line in the PR descriptions.
Findings. Cause: Stencil 4.45.2 changed `attributeChangedCallback` on form-associated components so that a present boolean attribute means `true` even for the string `"false"` (`newValue === null || newValue === "false" && !isFormAssociated ? false : true`); non-form-associated components still map `"false"` to `false`. It is deliberate (upstream PR stenciljs/core#6908, issue #6905, release v4.45.2): the browser treats a present attribute as set, so `<x disabled="false">` was natively disabled while the prop said `false`. 4.45.3 keeps the rule, so it is permanent and there is nothing to report upstream. It matches the HTML standard's boolean attribute rule (the values "true" and "false" are not allowed; a false value is expressed by omitting the attribute). Stencil's own Properties page still says the string `"false"` gives `false` and its form-associated page does not mention the change.
Live check (Chromium, Stencil 4.45.2, raw components and the packed React and Vue wrappers): `bds-file-picker multiple="false"` gives `multiple=true`; `error="false"` adds the error class; `bds-text-field disabled="false"` is `:disabled` and excluded from `FormData`; `bds-checkbox checked="false"` is checked and submitted; non-form-associated components (`bds-dropdown`, `bds-radio-button`) still give `false`; JS properties, React `={false}` and Vue `:prop="false"` still give `false`; the string form through the wrappers (a Vue static attribute, a React string prop) gives `true`.
Inventory: 14 form-associated components with 66 boolean props, all defaulting to `false`; no source file, test app or wrapper passes `"false"` as an attribute. Applied: `@stencil/core` exact `4.45.1` replaced by `^4.45.2` (resolves 4.45.2; 4.45.3 was 0.1 days old and excluded by the release-age rule) and the lockfile refreshed; five `bds-file-picker` specs rewritten to omit the attribute, or to use `removeAttribute`, instead of the string `"false"` (three failed, two had lost their intent); the date-picker story `with-time=${args.withTime}` changed to `?with-time=${args.withTime}`; `hide="false"` removed from the file-uploader MDX snippet (no new text added). The testing agent also removed four existing inline comments inside two of the edited tests, in line with the no-inline-comments rule. One test remains weak: 'handle alternating between single and multiple modes' only goes from single to multiple (not changed, out of scope).
Gates before commit: format checks pass (web-components, docs), lint 0 errors with warnings 9 / 50 / 0 / 0, 375 suites and 4,810 tests, coverage 93.24 / 85.64 / 92.66 / 94.75, build 7/7, `pnpm peers check` clean (a single `@stencil/core` 4.45.2 resolution; the inert copy in `boreal-vue` is the same version). Remaining after the commit: `pnpm validate:all` and the push
**Executor:** @frontend-subagent (investigation and source), @testing-subagent (specs), @qa-subagent (live-browser check)
**Files:**

- `packages/boreal-web-components/package.json` (modify — the exact `@stencil/core` pin)
- Component sources and specs only if the investigation decides on a fix
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding: with 4.45.2, three `bds-file-picker` tests fail because a string attribute `multiple="false"` or `error="false"` on this form-associated component is parsed as `true`; 4.45.0 and 4.45.1 pass all 178 tests. In Chromium on 4.45.1 the attribute `"false"` gives `false`.
- [ ] Boundary case: decide in a real browser what 4.45.2 and the newest release do, using packed artifacts, since the unit tests run on Stencil's mock DOM.
- [ ] Call sites: list every component that uses `formAssociatedMixin` and has boolean props; check which tests pass `"false"` as an attribute.
- [ ] Reference: team memory on form-associated children: their behavior is invisible to unit tests, so use a live `<form>` check.
- [ ] Inert copy: `packages/boreal-vue` resolves `@stencil/core@4.45.2` as an auto-installed peer of `@stencil/vue-output-target`; confirm when the pin is removed.

**Acceptance criteria:**

- The behavior difference is understood and recorded in this task's status line, and either fixed in the components, accepted with a migration note, or reported upstream. The user decides between the three.
- The exact pin becomes a caret range and the full unit suite, build and `pnpm validate:all` pass.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Run the check on the pack-based pipeline (`pnpm dev:pack:react` / `dev:pack:vue`), not the live dev server, via @qa-subagent:

- [x] Given `<bds-file-picker multiple="false">` in a `<form>`, when the page loads, then `multiple` is `false` and form validity matches the 4.45.1 behavior. Pass: no difference, or the difference is the documented decision. _(the difference is the documented decision: `multiple` is `true`)_
- [x] Given the same markup in the React and Vue wrapper apps, when rendered, then behavior matches the raw web component. Pass: no divergence. _(typed values match; the string form matches the raw component, as `true`)_

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 update @stencil/core to ^4.45.2 and adapt tests and docs"
```

### Task 6a: Document the dependency check commands and the stage rules

**Status:** done 2026-11-11, committed `a8d5473e` `docs(scripts): EOA-20193 document dependency check commands` and pushed, confirmed by the user 2026-11-11. `pnpm validate:all` passes on the committed state with a clean tree. Chosen by the user (Option A) after a review with two independent agents, an advocate and a critic. Agreement of both: the exit code needs three states (ok, findings, tool error) and a plain 0/1 reads a failed check as "no findings"; `pnpm audit --prod --audit-level high` already gives the high and critical threshold natively; the trigger for a script is not met because the Jenkins job does not exist. They differed on whether to build a parser (advocate: yes, amended, low priority; critic: no, write the contract). Outcome: write the contract now (this task), build the script later (T6b). Added to `scripts-boreal/README.md`, section "Dependency checks": the three commands, what each exit code means, and four rules for a stage (exit 1 from `pnpm outdated` is expected; moderate and low findings do not fail the stage; an audit exit code of 1 also means the registry could not be reached, told apart by `audit.json` holding `metadata.vulnerabilities` or an `error` object; production dependencies only for the audit). Verified before writing: `pnpm audit --prod --audit-level high` exits 0 with the current single moderate finding while plain `pnpm audit --prod` exits 1; `pnpm outdated -r --format json` exits 1 and returns an object keyed by package name (51 entries; fields `current`, `dependencyType`, `dependentPackages`, `isDeprecated`, `latest`, `wanted`); with an unreachable registry `pnpm audit` retries for over a minute, prints `[ERROR] fetch failed`, exits 1, and its JSON output is `{"error": {"code": "pnpm", "message": "fetch failed"}}` with no `metadata`. Not re-observed today: the exit code 0 of an audit with zero findings (the repository has one moderate finding now).
**Executor:** main thread (no executor)
**Files:**

- `scripts-boreal/README.md` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: the README is read by contributors and by whoever owns the Jenkins job; the monthly ticket template (`ai-docs/templates/dependency-maintenance-ticket.md`) already lists the same commands for a human. No other file changes.
- [x] Boundary case: a failed check must not read as a clean one; the README states how to tell them apart.
- [x] Default state: with no high or critical finding the stage passes whatever the moderate and low counts are.

**Acceptance criteria:**

- The README lists the three commands with their exit codes and the four rules above.
- Every statement in the section matches the observed output of the commands (checked on 2026-11-11).
- No ticket IDs, plan references or version history in the README text.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate by running the documented commands and comparing with the README.

- [x] Given the repository, when the three commands run, then their exit codes and JSON shapes match the table. Pass: exit 0 for `--audit-level high`, exit 1 for the other two, `metadata.vulnerabilities` present, 51 outdated entries keyed by package name.

**Commit (on the user's confirmation of the message):**

```bash
git commit -m "docs(scripts): EOA-20193 document dependency check commands"
```

---

### Task 6b: Add the dependency report script (deferred)

**Status:** deferred 2026-11-11 by the user's decision (Option A of the T6 review). Not built now: the Jenkins job does not exist, has no owner and no DevOps agreement, and the deadline is 2026-11-13. It is built only when DevOps confirms that a scheduled stage will call it, in the third PR or later. Until then this task is left out of the deadline scope.
**Executor:** @release-subagent
**Files:**

- `scripts-boreal/bin/deps-report.js` (create)
- `scripts-boreal/lib/deps-report.js` (create)
- `scripts-boreal/lib/__tests__/deps-report.spec.js` (create)
- `package.json` (modify — root script `deps:report`)
- `scripts-boreal/README.md` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Utility discovery: searched `scripts-boreal/lib/` for command execution and logging. Candidates: `Cmd.run` (`lib/cmd.js`) and `Logger` (`lib/logger.js`). Fit to be verified at execution; reuse them, and extend `Cmd` first if it cannot capture output. No parallel implementation.
- [ ] Boundary case: `pnpm outdated -r` exits non-zero when anything is outdated, and `pnpm audit` exits non-zero when it finds vulnerabilities; both must be treated as data, not as script failure.
- [ ] Default state: with no outdated packages and no findings the report prints zero counts and exits 0.
- [ ] Assumptions A1 and A2 apply: the job wiring is outside the repository, and the exit code is 1 only for unresolved high or critical production findings.

**Amendments agreed in the review (advocate and critic both asked for them):**

- Three exit states: 0 clean, 1 high or critical production findings, 2 the check could not run or its output could not be parsed (registry unreachable, empty output, unexpected shape). A plain 0/1 would read a failed check as "no findings".
- Read counts from `metadata.vulnerabilities` of `pnpm audit --prod --json`; a result without that block is state 2. Real captured pnpm 11 output is used as fixtures, and one test pins the shape so that the pnpm upgrade in T20 fails loudly instead of reporting zero.
- `Cmd.run` uses `stdio: 'inherit'` and rethrows on a non-zero exit, so `Cmd` is extended first with a capture method that returns stdout and the exit code without rejecting.
- Report production and dev outdated entries separately (`pnpm outdated -r --format json` is an object keyed by package name, so workspace duplicates are already merged); count only production findings for the audit.
- Keep it to the smallest size that satisfies the 80% coverage gate on `lib/**`.

**Acceptance criteria:**

- `pnpm deps:report` prints the outdated counts (major, minor, patch) from `pnpm outdated -r --format json` and the production audit counts (critical, high, moderate, low) from `pnpm audit --prod --json`.
- Parsing lives in `lib/deps-report.js` as pure functions, covered by unit tests with fixture JSON and no network.
- The README describes the command and the steps DevOps needs to run it monthly from Jenkins.
- Standard gates are green, including gate 6.

**Unit tests to cover:**

- Classification of outdated entries into major, minor and patch from current and latest versions.
- Audit counting by severity, and the exit-code rule for unresolved high or critical findings.
- Empty input and malformed JSON.
- Coverage-phase only (80%); mutation testing is not planned for scripts.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with the unit tests and one real run.

- [ ] Given the repository, when `pnpm deps:report` runs, then the printed counts equal `pnpm outdated -r` and `pnpm audit --prod`. Pass: numbers match.

**Commit:**

```bash
git commit -m "feat(scripts): EOA-20193 add dependency report script"
```

---

## Wave 2: the toolchain chain (order matters)

### Task 7: Add automated wrapper tests for Vue and React

**Status:** done 2026-11-11, committed `0e4f072e` `test(examples): EOA-20193 add automated vue wrapper tests` and pushed, confirmed by the user 2026-11-12. `pnpm validate:all` passes on the committed state (React and Vue) with a clean tree; the pre-push suite passed (375 suites, 4,810 tests). Decisions by the user 2026-11-11: Part B (React) is dropped under assumption A5 and T7b follows right after T7. Feasibility spike by @testing-subagent (feasible; stubs and data sources recorded below), then the real suite by @testing-subagent: 3 spec files and 12 tests in `examples/vue-testapp/src/__tests__/` plus `setup.ts` (the jsdom stubs) and `settle.ts` (shared wait helper); `vitest.config.ts` gets `test.setupFiles`; `package.json` gets the script `"test": "vitest run"` so turbo's `test` task and the root `pnpm test` run the tests. `component-models.spec.ts` (4 tests) is the data-driven invariant: every tag that declares `valueChange` in `custom-elements.json` must have a wrapper with `modelValue` and `update:modelValue`, and every wrapper with a model must map to a tag that declares `valueChange` or to the one-entry map (`bds-table` to `selectedRowsChange`); adding a component needs no edit. `class-merging.spec.ts` (4 tests) covers the full class sequence on `BdsTextField` (consumer classes, a reactive `:class`, `--disabled`, `--readonly`, `--error`, `hydrated`). `v-model.spec.ts` (4 tests) covers `BdsTextField` (real `input` event, programmatic change flowing back) and `BdsCheckbox` (click true, click false). No toggle assertion exists until T7b. Mutation check: removing `bds-select` from the target's model list and rebuilding made the invariant fail with `BdsSelect (bds-select) declares valueChange but its wrapper has no modelValue prop and update:modelValue emit`; the file was restored and rebuilt. Not proven: the reverse direction (an extra model on a wrapper with no matching event) has no mutation evidence. Verified by me: the new files have no inline comments, ticket IDs, version numbers or `any`; `pnpm test` from the root runs `vue-testapp:test` (3 files) and passes; lint 0 errors (warnings 9 / 50 / 0), `pnpm peers check` clean, build 7/7 (the app's `vue-tsc --build` type-checks the specs); three repeat runs took 1.6 to 1.8 seconds with no flakiness. Open caveat, not verified: turbo's `test` task lists only `src/**` files as inputs, so whether a change that only affects the generated wrapper re-runs the Vue tests depends on the hash of the `build` task it depends on; check this when T7b changes the target list. Remaining after the commit: `pnpm validate:all` and the push
Spike result: feasible. The real `@pxglobal/boreal-vue` wrappers register, upgrade and render in jsdom 28 with Vitest 4.1; the components are light DOM (no shadow root) and carry Stencil's `hydrated` class. A setup file is needed (registered through `test.setupFiles`; Vitest 4.1's CLI has no `--setupFiles` flag) with these stubs, each needed only by the listed components: `ElementInternals.prototype.setFormValue` (`BdsCheckbox`, `BdsCheckboxButton`, `BdsCheckboxCard`, `BdsCheckboxGroup`), `ElementInternals.prototype.setValidity` (`BdsToggle` on click), `ResizeObserver` (`BdsPagination`, `BdsStepper`, `BdsTable`), `HTMLElement.prototype.showPopover` and `hidePopover` (`BdsToastContainer`). jsdom 28 has no `IntersectionObserver`, `matchMedia`, `CSS`, `DragEvent`, `DataTransfer` or `scrollIntoView`, but no wrapper needed them at mount. All 81 `Bds*` wrappers mount in about 2.2 seconds; an 11-test spike takes about 2.4 seconds with no flakiness over three runs. Mount with `attachTo: document.body`, wait about 50 ms plus `flushPromises()`, clean up with `document.body.innerHTML = ''`; use `defineComponent` with `h()` for parents (the `template` option needs the Vue compiler). Events: setting `input.value` and dispatching a real `input` event gave `update:modelValue [['hello']]` on `BdsTextField`; a click on `BdsCheckbox` gave `[[true]]`. Class merging: on `BdsTextField` the consumer classes, a reactive `:class` and the component's own `--disabled` host class all survived each re-render and a removed consumer class disappeared (`BdsTextField` is the good probe; `BdsToggle` keeps its state classes on an inner element). Data sources for the invariant test: (A) runtime introspection of each wrapper (`'modelValue' in Wrapper.props` and `update:modelValue` in `Wrapper.emits`; 18 wrappers have a model) and (B) `packages/boreal-web-components/custom-elements.json` (tracked in git; the 17 tags that declare `valueChange` equal exactly the 17 `valueChange` entries of `componentModels`; `bds-table` uses `selectedRowsChange`). The generated `packages/boreal-vue/lib/components.ts` is gitignored and needs text parsing; `componentModels` itself is a non-exported literal in `targets/vue-output-target.ts`. Gap found: `vue-testapp` has `test:unit` but no `test` script, so turbo's `test` task and the root `pnpm test` do not run its tests; T7 adds a `test` script.
Scratch files from the spike, untracked: `examples/vue-testapp/src/__tests__/spike.spec.ts` and `spike.setup.ts` (the basis for the real tests).
**Executor:** @testing-subagent (tests), @qa-subagent (one browser smoke pass on the packed artifacts)
**Files:**

- `examples/vue-testapp/` spec files, a setup file for the jsdom stubs, `vitest.config.ts` (`test.setupFiles`) and `package.json` (a `test` script, so the root `pnpm test` runs them) (create / modify)
- `examples/react-testapp/` spec files and test configuration (create — Part B)
- Root test wiring (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding: the wrapper packages have placeholder `test` scripts. `vue-testapp` already has `vitest`, `jsdom`, `@vue/test-utils` and a jsdom `vitest.config.ts`, with no test files. `react-testapp` has no test tooling.
- [ ] Spike first: confirm that the real Stencil components render and emit events inside jsdom. If they do not, fall back to a stub custom element that sets its own host class, which covers the runtime contract but not the real host classes.
- [ ] Vue risk: `componentModels` in `packages/boreal-web-components/targets/vue-output-target.ts` is a manual list; a forgotten entry or a mistyped event name fails silently. React has no equivalent list.
- [ ] Runtime delta that motivated this: `@stencil/vue-output-target` 0.13.1 to 0.14.7 rewrote the class-merging code (`syncElementClasses`) and left the `v-model` path untouched.
- [ ] Constraints: no inline comments in specs, no ticket IDs in `describe` or `it` names, and the test apps resolve the wrappers through the workspace build, so the root build order must build `boreal-vue` and `boreal-react` first.

**Acceptance criteria:**

Part A — Vue:

- A data-driven test compares two sources and fails on any difference, so adding a component needs no test edit: the wrappers that expose a `modelValue` prop and an `update:modelValue` emit (runtime introspection) must equal the tags that declare a `valueChange` event in `custom-elements.json`, plus the other model events in the target list (`bds-table`).
- A class-merging test mounts a wrapped component that sets its own host class, toggles a consumer `:class` and the component state, and asserts both sets of classes survive each re-render and removed consumer classes disappear.
- A `v-model` smoke test on a representative component asserts the bound ref updates when the model event fires.

Part B — React (DROPPED by the user's decision 2026-11-11; kept here for the record):

- A test asserts every custom event in `custom-elements.json` is exposed as an `on<Event>` prop on the matching wrapper.
- A `className` test asserts consumer classes and the component's own host classes both survive re-renders.
- An event smoke test on a representative component asserts the handler fires with the event detail.

Both parts: the root `pnpm test` runs the new tests and they pass. Standard gates are green.

**Unit tests to cover:** the behaviors listed above; coverage-phase only.

**Manual test _(required — not waiveable)_:**

- [x] Given the Vue test app, when `pnpm test` runs from the root, then the new specs run and pass. Pass: exit code 0.
- [x] Given a deliberately removed `componentModels` entry in a scratch change, when the tests run, then the invariant test fails. Pass: failure names the component. Revert the scratch change.
- [ ] Given the packed artifacts, when @qa-subagent repeats one class-merging and one `v-model` scenario in a browser, then the result matches the tests. Pass: no divergence. _(not run: the browser behavior of the same scenarios was already observed on the packed artifacts during T5, and the suite runs the real components in jsdom; it can be repeated in the T7b browser check, which exercises `v-model` through the pack-based pipeline)_

**Commit:**

```bash
git commit -m "test(examples): EOA-20193 add automated wrapper tests"
```

### Task 7b: Fix the `bds-toggle` v-model mapping in the Vue wrapper

**Status:** done 2026-11-12, committed `3554eda5` `fix(vue): EOA-20193 map bds-toggle v-model to checked` (the target file and the spec; `examples/vue-testapp/src/App.vue`, the playground, is deliberately NOT committed and stays a local modification by the user's decision) and pushed, confirmed by the user 2026-11-12. `pnpm validate:all` passes on the committed state (React and Vue); the pre-push suite passed (375 suites, 4,810 tests). Why the toggle's `value` is now always `"on"` (question by the user, answered from the source): `value` is documented as the value submitted with the form data when checked, like the `value` attribute of a native checkbox; the component submits `this.isChecked ? this.value : null` through `setFormValue`, restores the checked state in `formStateRestoreCallback` by comparing the saved state with `value`, and puts it in the `bdsChange` payload, while the on or off state lives in `checked`. The old mapping wrote the model into `value`, so a checked toggle would have submitted `"true"` or `"false"` instead of `"on"` and the form restore comparison was confused (the restore path was not exercised in a browser; it follows from the code). A consumer who wants another submitted value sets `value` explicitly and the model no longer overwrites it. Test-driven: two toggle cases were added to `v-model.spec.ts` and failed on the unfixed build (`expected 'false' to be true`; `expected false to be true`), then the fix was applied and all 14 Vue tests pass. Fix: in `packages/boreal-web-components/targets/vue-output-target.ts`, `bds-toggle` leaves the `value` group and gets its own entry `{ elements: ['bds-toggle'], event: 'valueChange', targetAttr: 'checked', eventAttr: 'detail' }`. Verified in the runtime of `@stencil/vue-output-target` 0.14.7 (an incoming `modelValue` is written to the model property; the outgoing value is a dot path on the event, `eventAttr` or `target.<targetAttr>`), and by a cross-check of every `valueChange` payload type against its mapped property: `bds-toggle` was the only mismatch. The generated wrapper is now typed `JSX.BdsToggle["checked"]` (boolean), so `vue-tsc` accepts a boolean binding; the typed wrapper also requires `name` (declared required in the component), which the old `string` model type had been hiding, so the spec's mount helper and the playground pass `name`. Browser evidence on the packed artifacts (Chromium, `dev:pack:vue`, by @qa-subagent, scenarios W0 to W5, both sections on one page): BEFORE, the real wrapper behaved exactly like the hand-wired reproduction: a click changed only the visual switch while the toggle's `checked` stayed `false`, the bound model became the string `"false"` and never changed again, and setting the model to `true` from code left the toggle off (also after a reload); AFTER, in the real wrapper section the model is always a boolean and agrees with the host `checked` and the visual state at every step (click: `true`, click again: `false`, set to `true` from code: checked and blue, also after a reload), `valueChange` still carries a boolean `detail`, 0 console errors or warnings; the hand-wired section still shows the old behavior. Observed side effects: the host `value` is now `"on"` in every state (it no longer echoes the model); the wrapper host still carries a `modelvalue` attribute that follows the model (`"false"` at load, `"true"` when checked), which comes from the generic wrapper runtime, not from this mapping, and is not changed here. Gates: build 7/7 with `vue-tsc` clean, root `pnpm test` runs `vue-testapp:test` (14 tests), lint 0 errors (warnings 9 / 50 / 0), `pnpm peers check` clean, format checks pass. Turbo cache caveat from T7, now checked: changing only the target file changes the hash of `vue-testapp#test` (`8f1c3ad9d8516b75` with the fix, `01399a741490111b` with the old mapping, the first hash again after restoring), so a wrapper-only change does re-run the Vue tests. Release check: the release configs of `boreal-vue` and `boreal-react` include `../boreal-web-components` in their commit paths, so a `fix` touching the target file is releasable for the wrappers. The playground `examples/vue-testapp/src/App.vue` (the user asked for a before-and-after example) is modified and formatted but not part of the commit unless the user decides otherwise. Remaining after the commit: `pnpm validate:all` and the push
**Executor:** @release-subagent (output target), @testing-subagent (the test), @qa-subagent (browser check on the packed artifacts)
**Files:**

- `packages/boreal-web-components/targets/vue-output-target.ts` (modify — the `componentModels` entry for `bds-toggle`)
- `examples/vue-testapp/` spec files from T7 (modify — add the toggle case)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Finding (verified in the source 2026-11-11): `bds-toggle` keeps its state in the readonly prop `checked` (default `false`); `value` is a string (default `'on'`); the `valueChange` event emits the boolean state. The target list maps `bds-toggle` with `event: 'valueChange'` and `targetAttr: 'value'`, so on a click the wrapper reads `target.value` and emits `"on"` instead of `true`; and a bound `modelValue: true` is written to `value`, leaving `checked` at `false`. The spike observed both ends broken.
- [x] The Vue target supports an `eventAttr` option (`modelUpdateEventAttribute`, default `target.<targetAttr>`); the likely fix is `targetAttr: 'checked'` with `eventAttr: 'detail'`. Confirm against the runtime of `@stencil/vue-output-target` 0.14.7 before editing.
- [x] Call sites: `bds-checkbox`, `bds-checkbox-button` and `bds-checkbox-card` use `targetAttr: 'checked'` because their `checked` is mutable; confirm no other element has a readonly state prop with the same problem (check each entry of `componentModels` against its `valueChange` payload in `custom-elements.json`).
- [x] Consumer effect: the fix changes what `v-model` yields on `BdsToggle` (from a string to a boolean, and a bound `true` now checks the toggle); recorded as an item of the housekeeping task for the PR descriptions.

**Acceptance criteria:**

- `v-model` on `BdsToggle` yields a boolean on click and a bound `true` sets the checked state, verified in the T7 test and in a browser on the packed artifacts.
- No other `componentModels` entry has the same mismatch, or each one found is listed.
- Standard gates are green, including `pnpm validate:all`.

**Manual test _(required — not waiveable)_:**

- [x] Given a `BdsToggle` bound with `v-model` in the Vue test app (pack-based pipeline), when it is clicked, then the bound ref becomes `true` and clicking again makes it `false`. Pass: booleans, no `"on"`.
- [x] Given the ref set to `true` from code, when the page updates, then the toggle shows checked. Pass: the host reflects `checked`.

**Commit (on the user's confirmation of the message):**

```bash
git commit -m "fix(vue): EOA-20193 map bds-toggle v-model to checked"
```

---

### Task 7c: Document the Vue `v-model` contract

**Status:** done 2026-11-12, committed `992dcbf5` `docs(web-components): EOA-20193 document the vue v-model contract` (the README and the spec messages; `App.vue` stays an uncommitted local change) and pushed, awaiting the user's confirmation. `pnpm validate:all` passes on the committed state (React and Vue); the pre-push suite passed (375 suites, 4,810 tests). Texts approved by the user on 2026-11-12 (E, B, G1, G2, G3 as described; G5 and the optional guideline sentence in `ai-docs/guidelines/stencil-best-practices.md` were NOT applied by the user's decision). Applied: (E) the three failure messages of `examples/vue-testapp/src/__tests__/component-models.spec.ts` now name the file to edit (`packages/boreal-web-components/targets/vue-output-target.ts`), the rebuild command and, for the other-event case, `OTHER_MODEL_EVENTS`; mutation check re-run on rebuilt output in BOTH directions: removing `bds-select` from the list fails the first invariant with `BdsSelect (bds-select) declares valueChange but its wrapper has no modelValue prop and update:modelValue emit. Add 'bds-select' to componentModels in packages/boreal-web-components/targets/vue-output-target.ts with the property that holds its state as targetAttr, then rebuild with pnpm --filter @pxglobal/boreal-web-components build.`, and adding `bds-radio` (it has a `value` property and declares no `valueChange`) fails the second with `BdsRadio (bds-radio) exposes a v-model but the component declares neither valueChange nor a listed model event. If it uses another model event, add it to OTHER_MODEL_EVENTS in this spec; otherwise remove it from componentModels in packages/boreal-web-components/targets/vue-output-target.ts.`; this closes the T7 gap (the reverse direction had no mutation evidence). A first attempt with `bds-button` was invalid because the wrapper build failed (no `value` property), so it is not counted. The target was restored with `git checkout --` and both packages rebuilt; the suite is 14 of 14 again. (B) the subsection "Adding `v-model` to a component (Vue)" in the "Framework Wrappers" section of `packages/boreal-web-components/README.md`: every file, name and command it references was checked against the repository (the target file, both specs, `custom-elements.json`, the git-ignored `packages/boreal-vue/lib/components.ts`, `OTHER_MODEL_EVENTS`, `eventAttr`, the build script and the root `test` script) and the file is Prettier-clean; no versions, tickets or history in the text and no diagram. (G, local only, excluded from git) `vue-vmodel-reads-property-not-event-detail.md` rewritten (default path `target.<targetAttr>`, `eventAttr` reads a path on the event such as `detail`, the earlier "never `event.detail`" was wrong; mapping now 12 on `valueChange`/`value` plus the toggle on `checked` with `eventAttr: 'detail'`; the toggle case; a payload-type audit rule; pointer to the invariant test and the README), `vue-componentmodels-regeneration.md` runtime-contract sentence corrected, `vue-vmodel-modelvalue-attribute-leak.md` corrected (the shim was prototyped, verified and reverted in EOA-19597 T27, is in no git ref, the leak is live and present in 0.14.7 and 0.15.0; design kept for reference), the two index rows updated and a changelog row added. Follow-up by the user's decision on 2026-11-12 (done, local only): the older claim "never `event.detail`" in the per-subagent notes under `.claude/agent-memory/` (`frontend-subagent/vue-model-reads-prop-silent-commits-break.md`, `frontend-subagent/MEMORY.md`, `qa-subagent/bds-search-bar-vue-vmodel-does-not-track-typing.md`) was corrected to "by default the element property, and `eventAttr` can point it at the event", with a pointer to the team note; no copy of the old wording remains there. The user also decided that the playground `examples/vue-testapp/src/App.vue` example stays a local, uncommitted change. Gates: build 7/7, root `pnpm test` runs `vue-testapp:test` (14 tests), lint 0 errors (warnings 9 / 50 / 0), `pnpm peers check` clean, format checks pass. The playground `App.vue` stays an uncommitted local change. Remaining after the commit: `pnpm validate:all` and the push
**Executor:** @testing-subagent (the failure messages), @documentation-subagent (the README section), @knowledge-keeper (the team memory entry)
**Files:**

- `examples/vue-testapp/src/__tests__/component-models.spec.ts` (modify — option E)
- `packages/boreal-web-components/README.md` (modify — option B, section "Framework Wrappers")
- `.agents/memory/` (a new entry and its index line — option G; excluded from git)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Facts to state, each verified against the code at the time of writing: the Vue wrapper turns `v-model` into "set the component's state property and listen to its model event"; the pairing is a hand-written list, `componentModels` in `packages/boreal-web-components/targets/vue-output-target.ts`, because the generator cannot guess it; a component missing from the list simply has no `v-model` in Vue; the invariant test compares the tags that declare `valueChange` in `custom-elements.json` with the wrappers that expose `modelValue` and fails naming the component; the one explicit exception is the map for `bds-table` (`selectedRowsChange`), so a component with another model event name must be added there; a component whose state is not in `value` (`checked`, `files`, `selectedRows`) needs a short `v-model` behavior test, because the invariant checks presence, not the mapped property; the React wrapper has no hand-written list. For components with a boolean state, the README text also says what the two properties are for: `checked` holds the on or off state and is what `v-model` binds, while `value` is the string submitted with the form data when checked (default `"on"`), like a native checkbox, so it stays constant and the model must never be mapped onto it.
- [ ] Call sites: the README section "Framework Wrappers" of `packages/boreal-web-components/README.md` (line 109 at planning time); the failure messages built in `component-models.spec.ts`; the team memory index.
- [ ] Boundary case: documentation must not name versions, tickets or project history in consumer-facing text; the README is read by contributors, so it states rules, not history. The toggle lesson is written as a rule ("check the mapped property, not only that the component is listed"), not as a story.

**Acceptance criteria:**

- The invariant test's failure messages tell the reader exactly what to do, including the path `packages/boreal-web-components/targets/vue-output-target.ts` and, for the other-event case, where the exception map is; the test still fails in both directions as before (re-run the mutation check).
- The README section has the three steps, the exception cases and the behavior-test rule, verified against the code, and renders correctly.
- The team memory entry records the non-obvious facts and links to related entries; the index line is added.
- The user has approved the texts before they were applied. (Approved 2026-11-12.)

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate by reading and by re-running the mutation check.

- [x] Given the invariant test with one model element removed from the list, when it runs, then the failure message names the component and the file to edit. Pass: both are present.
- [x] Given the README section, when a contributor follows its steps for a hypothetical new component, then each referenced file and command exists. Pass: every path and command resolves.

**Commit (on the user's confirmation of the message):**

```bash
git commit -m "docs(web-components): EOA-20193 document the vue v-model contract"
```

---

### Task 8: Upgrade TypeScript to 6.0.3

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `package.json` of all seven workspaces that declare `typescript` (modify) and `pnpm-lock.yaml`
- `packages/boreal-react/tsconfig*.json`, `packages/boreal-vue/tsconfig*.json` (modify — `rootDir`)
- `packages/boreal-web-components/tsconfig.json`, `apps/boreal-docs/tsconfig*.json` (modify — remove `baseUrl`)
- `packages/boreal-web-components/src/components/actions/bds-tree-menu/bds-tree-menu-item/bds-tree-menu-item.tsx` (modify — two assertions)
- `examples/vue-testapp/package.json` (modify — lift the `@vitest/eslint-plugin` hold)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Trial result (disposable worktree): `rootDir: "./lib"` in the `boreal-react` and `boreal-vue` tsconfigs (error TS5011 otherwise); remove `baseUrl` from the web-components and docs tsconfigs and change the web-components alias to `"@/*": ["./src/*"]`; set `strict: false` explicitly in web-components (TypeScript 6 and 7 turn strict on by default; without it there are 151 errors and different lint results); remove two unnecessary type assertions in `bds-tree-menu-item.tsx`.
- [ ] Call sites: the web-components alias is used across `src`; confirm the build resolves it after `baseUrl` is removed.
- [ ] Hold: `@vitest/eslint-plugin` 1.6.28 requires TypeScript `>=6.0.0`; once TypeScript 6 is in, the 1.6.27 hold in `examples/vue-testapp` is lifted.
- [ ] Reactivity: not applicable. Assumption A4: TypeScript 7 side by side is not part of this task.

**Acceptance criteria:**

- Build, lint (no errors), `pnpm peers check`, unit tests and `pnpm validate:all` pass on TypeScript 6.0.3.
- The published `dist` of `boreal-react` and `boreal-vue` is unchanged: a file-by-file comparison of the build output before and after is recorded.
- The docs and web-components tsconfigs no longer use `baseUrl`.
- `@vitest/eslint-plugin` resolves to its newest version and the hold row is marked lifted.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with the standard gates and the dist comparison.

- [ ] Given the build before and after, when the wrapper `dist` folders are diffed, then there is no difference. Pass: empty diff.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade typescript to 6.0.3"
```

### Task 9: Clear the `typescript-eslint` 8.59+ type-assertion errors

**Status:** pending
**Executor:** @frontend-subagent (source edits), @testing-subagent (spec check)
**Files:**

- `packages/boreal-web-components/package.json` and the other two workspaces holding the `~8.58.2` cap (modify)
- The files that the rule flags, 17 in the baseline count (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding: `typescript-eslint` 8.59.0 is the first version that raises 38 `@typescript-eslint/no-unnecessary-type-assertion` errors in 17 web-components files; 8.58.2 lints clean. Re-run the bisect at execution time, since T8 (TypeScript 6) may change the count and ESLint 10 (T4) may change which versions are allowed.
- [ ] Call sites: each flagged assertion, for example `(this.el as HTMLElement)` in `bds-text-field.tsx`, may still be needed for another TypeScript version or for Stencil's JSX typing; check each before removing it.
- [ ] Default state: if T8 removes the errors by itself, this task only lifts the caps.

**Acceptance criteria:**

- Every flagged assertion is removed or justified, with no behavior change.
- The three `~8.58.2` caps become caret ranges, resolving to the newest version older than the 1-day delay.
- `pnpm lint` exits 0 and the web-components unit suite passes.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with lint and the unit suite.

- [ ] Given the new `typescript-eslint`, when `pnpm lint` runs, then no assertion errors appear. Pass: 0 errors.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 update typescript-eslint and clear assertion errors"
```

### Task 10: Upgrade Vitest to 5 and jsdom to 30

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `package.json` in `apps/boreal-docs`, `packages/boreal-style-guidelines`, `scripts-boreal` and `examples/vue-testapp` (modify)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Packages that move together: `vitest`, `@vitest/browser-playwright`, `@vitest/coverage-v8`, `@vitest/ui` (Vitest 5 pins them to the same version, 5.0.5), then `jsdom` 28.1.0 to 30.1.3 and `@types/jsdom` 28 to 30 in `vue-testapp`.
- [ ] **Stale statement in the draft:** it says no `vi.fn`, `vi.mock` or `vi.spyOn` is used. That is not true for `scripts-boreal`: `lib/__tests__/logger.spec.js` uses `vi.spyOn` and `lib/__tests__/signals.spec.js` uses `vi.fn`. Vitest 5 turns `clearMocks` on by default, so re-run these specs and re-check every spec that holds a mock across tests.
- [ ] Other breaking changes: `test.workspace` to `test.projects`, `browser.api` to a top-level `api`; confirm none appears in the four `vitest.config` files.
- [ ] Compatibility: the Storybook vitest addon 10.6.5 accepts Vitest 4 or 5; Vitest 5 accepts Vite 6.4 to 8, so this task does not wait for T11.
- [ ] Boundary case: jsdom 30 is applied only if T2 marked the Node floor as met.

**Acceptance criteria:**

- All four `vitest` packages resolve to the same 5.x version in every workspace.
- Lint, the spec files of `boreal-style-guidelines`, `scripts-boreal` and `vue-testapp`, the Storybook build, the Storybook vitest addon run and `pnpm validate:all` pass.
- Standard gates are green, including gate 6.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with each workspace's test command and the Storybook vitest addon run.

- [ ] Given Vitest 5, when each workspace's tests run, then the pass counts equal the baseline (scripts-boreal: 45). Pass: no new failures.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade vitest to 5 and jsdom to 30"
```

### Task 11: Upgrade Vite to 8 and its React plugin

**Status:** pending
**Executor:** main thread (no executor), @qa-subagent (dev-server smoke test)
**Files:**

- `apps/boreal-docs/package.json`, `examples/react-testapp/package.json`, `examples/vue-testapp/package.json` (modify)
- `examples/react-testapp/vite.config.*` (modify — the Babel option)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Versions: `vite` 7.3.1 to 8.3.5; `@vitejs/plugin-react` 5.1.4 to 6.1.2. The trial built Storybook and both test apps on Vite 8; the Storybook output grew about 1%.
- [ ] Order: after T10, because `@vitest/mocker` 4.0.18 does not accept Vite 8.
- [ ] Breaking change: `@vitejs/plugin-react` 6 removes the `babel` option. In the React test app, replace it with `react()` plus `babel({ presets: [reactCompilerPreset()] })` from the new devDependency `@rolldown/plugin-babel@^0.2.4` (0.3.0 is not accepted by plugin-react 6.1.2; the package is pre-1.0).
- [ ] Expect dev-only peer warnings in `vue-testapp` from `vite-plugin-vue-devtools`' older helper packages until it updates.

**Acceptance criteria:**

- The Storybook build, both test-app builds and `pnpm validate:all` pass; the Storybook vitest addon run passes.
- The React Compiler is still applied in the React test app.
- `pnpm peers check` is clean except for the documented Vue helper warnings.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

- [ ] Given the React test app dev server, when opened, then it renders with no console errors and the React Compiler marker is present. Pass: compiled output shows the compiler.
- [ ] Given the Vue test app dev server and the Storybook dev server, when opened, then both render. Pass: no console errors.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade vite to 8 and the react plugin to 6"
```

---

## Wave 3: published surface (each task starts with a decision from the user)

### Task 12: Add the `./components` export and lift the `@stencil/react-output-target` hold

**Status:** pending
**Executor:** @release-subagent (package exports and pack validation), @qa-subagent (wrapper parity)
**Files:**

- `packages/boreal-web-components/package.json` (modify — `exports`)
- `packages/boreal-react/package.json` (modify — output-target version)
- `packages/boreal-web-components/targets/react-output-target.ts` (modify if needed)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] **Decision first:** this changes what consumers can import. The user confirms adding the bare `./components` export before any edit.
- [ ] Finding: `@stencil/react-output-target` 1.5.0 and later generate `import type { Components }` (or `{ JSX }` in 1.5.1) from `@pxglobal/boreal-web-components/components`. The `exports` map has `./components/*.js` but no bare `./components`, so `tsc` in `boreal-react` fails with TS2307. The package is held at exactly 1.4.2.
- [ ] Call sites: `targets/react-output-target.ts` (`customElementsDir: 'components'`, `outDir: '../boreal-react/lib/components'`). Check the Vue output target as well, since it may add the same requirement.
- [ ] Boundary case: `components-build/index.d.ts` exists after a build and is the likely type target; confirm it is part of the published `files` and resolves from a consumer install, using the pack-based pipeline.
- [ ] Release effect: a new export is consumer-visible; the PR description records it.
- [ ] Observation from 2026-11-11: `pnpm audit --prod` reports 1 moderate finding, `minimatch` (advisory GHSA-g3hv-75wg-m249, patched in `>=11.0.1`), reached through `packages__boreal-react>@stencil/react-output-target>ts-morph>@ts-morph/common>minimatch`. After the output-target bump in this task, re-run `pnpm audit --prod` and record whether the finding is gone; if it remains, the housekeeping task records an accept-or-override decision.

**Acceptance criteria:**

- `exports["./components"]` resolves its types from a packed tarball in the React and Vue test apps.
- `@stencil/react-output-target` moves to the newest version past the 1-day delay, as a range.
- `pnpm validate:all` passes. Standard gates are green.

**Manual test _(required — not waiveable)_:**

- [ ] Given the packed artifacts, when the React and Vue test apps import from `@pxglobal/boreal-web-components/components`, then types resolve and the apps build. Pass: no TS2307.
- [ ] Given the React wrapper, when a component with an event is rendered in the pack-based app, then the handler fires. Pass: matches the raw component.

**Commit:**

```bash
git commit -m "feat(web-components): EOA-20193 export ./components types"
```

### Task 13: Resolve the `@tanstack/virtual-core` 3.19.6+ failures

**Status:** pending
**Executor:** @frontend-subagent (investigation and source), @testing-subagent (specs), @qa-subagent (live-browser check)
**Files:**

- `packages/boreal-web-components/package.json` (modify — the range)
- `packages/boreal-web-components/src/utils/dom/virtualWindow/virtual-window.ts` and `src/components/forms/bds-search-bar/` (modify only if a fix is decided)
- `packages/boreal-web-components/src/utils/testing/mocks/layout.ts` (modify only if the mock is the cause)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (bisect over every stable release 3.17.1 to 3.19.8): 3.19.5 passes all 305 `bds-search-bar` tests; 3.19.6 fails 24, all in items mode (windowed suggestions). The range is capped at `>=3.17.1 <3.19.6`.
- [ ] Call sites: `virtual-window.ts` and `bds-table.tsx` both use `@tanstack/virtual-core`; run the `bds-table` specs against 3.19.6 and later too.
- [ ] **Decision:** `virtual-core` is a published runtime `dependency` declared as `^3.17.1`, so consumers resolve the newest 3.x whatever this repository does. The user decides whether to keep the cap or widen it after the investigation.
- [ ] Boundary case: decide whether the failure is real in a browser or only in the mock DOM (the specs use `utils/testing/mocks/layout.ts`).

**Acceptance criteria:**

- The cause of the 3.19.6 failures is documented in this task's status line.
- The published range is either kept capped with the reason recorded, or widened after a source or test fix.
- `bds-search-bar` and `bds-table` specs pass at the newest allowed version, and a live-browser check of the items-mode list passes.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

- [ ] Given a search bar in items mode with a long list on the pack-based pipeline, when scrolling and keyboard navigating, then windowing and focus behave as on 3.19.5. Pass: no missing or duplicated rows.

**Commit:**

```bash
git commit -m "fix(web-components): EOA-20193 resolve virtual-core range for search bar"
```

### Task 14: Upgrade `@colordx/core` 5 to 7

**Status:** pending
**Executor:** @frontend-subagent (source), @testing-subagent (specs)
**Files:**

- `packages/boreal-web-components/package.json` (modify)
- `bds-color-picker` sources and specs under `packages/boreal-web-components/src/components/forms/bds-color-picker/` (modify as the changelogs require)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Versions: 5.6.0 to 7.3.0, two majors. It is a runtime `dependency`, so it ships to consumers; a change in color parsing, formatting or alpha handling is consumer-visible.
- [ ] First step: read both changelogs and list the breaking changes before any edit.
- [ ] Call sites: list every import of `@colordx/core` in `src`, starting with `bds-color-picker`, with `grep` over the source.
- [ ] Boundary case: values that parse differently between 5 and 7 (alpha, hex shorthand, named colors) get tests before the upgrade.

**Acceptance criteria:**

- Breaking changes and the affected components are listed in this task's status line.
- Color conversion behavior is covered by unit tests that pass before and after the upgrade.
- Standard gates are green, including `pnpm validate:all`.

**Unit tests to cover:** conversion, formatting and alpha handling for the values above; coverage-phase only.

**Manual test _(required — not waiveable)_:**

- [ ] Given the color picker in the playground (`pnpm dev:components`), when a color is typed, picked and an alpha is set, then the emitted value matches the pre-upgrade value. Pass: identical output.

**Commit:**

```bash
git commit -m "fix(web-components): EOA-20193 upgrade @colordx/core to 7"
```

---

## Wave 4: large or last

### Task 15: Spike the migration to `@stencil/vitest`

**Status:** pending
**Executor:** @testing-subagent
**Files:**

- `packages/boreal-web-components/vitest.config.ts` (create)
- `packages/boreal-web-components/package.json` (modify — add `@stencil/vitest`)
- A small sample of spec files (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Scale: 374 spec files; 337 use `newSpecPage` (2,756 call sites); 335 import from `@stencil/core/testing`; 197 use Jest APIs (1,286 uses).
- [ ] Context: Stencil's built-in runner is deprecated since 4.43 and removed in Stencil 5; it does not support Jest 30 on Stencil 4, so `jest`, `jest-cli`, `@types/jest` and `puppeteer` cannot be upgraded in place. `@stencil/vitest` 1.16.1 accepts `@stencil/core ^4 || ^5` and `vitest ^2` to `^5`.
- [ ] Stencil's guide maps `newSpecPage` to `render`, moves `testing` options to a `vitest.config.ts`, and lets spec tests keep the mock DOM or use jsdom or happy-dom.
- [ ] Evaluate a codemod before starting. Check how the per-component Stryker setup depends on the Jest preset (team memory: the setup drops `testRegex` from Stencil's Jest preset and adds a `moduleNameMapper`).
- [ ] Order: after T10, because both use the same Vitest version.

**Acceptance criteria:**

- A decision is recorded: codemod or manual migration, the batch size, and the environment (mock DOM, jsdom or happy-dom).
- At least three representative spec families (one simple, one form-associated, one with many `newSpecPage` calls) pass on `@stencil/vitest` with equal or better coverage.
- A written estimate of the remaining batches is recorded in T16's status line.
- Standard gates are green; the Jest runner still works for the unmigrated specs.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with both runners.

- [ ] Given the sample specs, when run on `@stencil/vitest` and on Jest, then results and coverage match. Pass: same pass count, coverage not lower.

**Commit:**

```bash
git commit -m "test(web-components): EOA-20193 add @stencil/vitest and migrate sample specs"
```

### Task 16: Migrate the web-components specs in batches

**Status:** pending
**Executor:** @testing-subagent
**Files:** spec files under `packages/boreal-web-components/src/` (modify, grouped by directory)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] The batch order and size come from T15's decision.
- [ ] Boundary case: shared test utilities (for example the search-bar and date-picker test-utils) are used by many specs; migrate each utility with its first consumer.
- [ ] Constraints: zero inline comments, no ticket IDs in test names, and coverage must stay at or above the baseline.

**Acceptance criteria:**

- Every spec file passes on `@stencil/vitest`; after the last batch the full suite equals the baseline (375 suites, 4,810 tests) or the difference is explained.
- Each batch is a separate commit and is green on its own.
- Coverage is equal or better at every batch.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate after each batch.

- [ ] Given a batch, when the suite runs on both runners, then both pass for the migrated and unmigrated specs. Pass: no failures.

**Commit (one per batch, each confirmed by the user):**

```bash
git commit -m "test(web-components): EOA-20193 migrate <directory> specs to @stencil/vitest"
```

### Task 17: Remove Jest and Puppeteer and update the test documentation

**Status:** pending
**Executor:** @testing-subagent (verification), main thread (documentation)
**Files:**

- `packages/boreal-web-components/package.json` (modify — remove `jest`, `jest-cli`, `@types/jest`, `puppeteer`)
- `packages/boreal-web-components/stencil.config.ts` (modify — the `testing` section)
- The per-component Stryker config files (modify as needed)
- `CONTRIBUTING.md` and the standards documents that name the test commands (modify)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding: `puppeteer` is used only by `stencil test --e2e` and the package has no e2e specs; removing it removes its Chrome download.
- [ ] Call sites: search the repository (scripts, `turbo.json`, Husky hooks, docs, the agent and skill files) for `stencil test`, `jest` and `puppeteer`; update each.
- [ ] Boundary case: re-verify the 80% coverage thresholds and the per-component mutation setup on the new runner by running one mutation config on a sample component.

**Acceptance criteria:**

- `jest`, `jest-cli`, `@types/jest` and `puppeteer` are removed and nothing references them.
- `pnpm validate:all` passes and the mutation score of a sample component is unchanged.
- The standards documents and `CONTRIBUTING.md` describe the new test commands.
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with a clean install and the full gates.

- [ ] Given a clean `pnpm install --frozen-lockfile`, when the suite runs, then it passes without Jest or Puppeteer installed. Pass: exit code 0.
- [ ] Given one component's mutation config, when run, then the score equals the previous score. Pass: unchanged.

**Commit:**

```bash
git commit -m "build(web-components): EOA-20193 remove jest and puppeteer"
```

### Task 18: Upgrade the Chromatic CLI to 18 and the addon to 5

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `apps/boreal-docs/package.json` (modify — `chromatic` 15.2.0 to 18.13.6, `@chromatic-com/storybook` 4.1.3 to 5.6.0)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Trial result: both installed cleanly; Storybook built with the new addon (same addons registered, same single warning); the two CLI flags in use (`--storybook-build-dir`, `--exit-zero-on-changes`) and `CHROMATIC_PROJECT_TOKEN` still exist.
- [ ] CLI 16 and 17 drop Node 18 and 20; CLI 18 needs Node 22 or later and renders progress with a new terminal UI. Addon 5 requires Storybook 10.1 or later (10.6.5 installed).
- [ ] Not verified: a real upload. The token holder runs `pnpm deploy:docs` once and checks the build in Chromatic, including that `--exit-zero-on-changes` still exits 0 when visual changes are detected.
- [ ] Boundary case: proceeds only if T2 marked the Jenkins Node floor as met.

**Acceptance criteria:**

- Storybook builds with the new addon and `pnpm peers check` is clean.
- One real `pnpm deploy:docs` publishes a build to Chromatic and exits as before (run by the token holder; the result is recorded).
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

- [ ] Given the upgraded packages, when `pnpm --filter boreal-docs build` runs, then Storybook builds. Pass: exit code 0.
- [ ] Given the token holder's run of `pnpm deploy:docs`, when it finishes, then the build appears in Chromatic and the exit code is as before. Pass: recorded by the user.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade chromatic to 18 and the storybook addon to 5"
```

### Task 19: Upgrade lint-staged, chalk, execa and npm-run-all2

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `package.json` (root — `lint-staged` 16.2.7 to 17.6.0, `engines.node`)
- `scripts-boreal/package.json` (modify — `chalk` 5.6.2 to 6.0.1, `execa` 9.6.1 to 10.2.1)
- `examples/vue-testapp/package.json` (modify — `npm-run-all2` 8.0.4 to 9.0.4)
- `README.md` (modify — the Node prerequisite)
- `pnpm-lock.yaml` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Trial result: all four installed cleanly and passed the full build, the Vue app lint, the `scripts-boreal` specs, `pnpm validate:all` and a real `lint-staged` run. None of the breaking changes touches the two `execa` calls, the colour chains or the two `npm-run-all2` scripts.
- [ ] Node floor: the highest is `npm-run-all2` 9 at `^22.22.2 || ^24.15 || >=26`. The hook runs on every contributor's machine, so `engines.node` (now `>=22`) and the README prerequisite (now "22+") change in the same commit. Proceeds only if T2 marked the Jenkins floor as met.
- [ ] Boundary case: `npm-run-all2` 9 succeeds silently when a glob matches no script; keep `lint:*` matching real scripts.
- [ ] Call sites: `scripts-boreal` now has more `chalk` and `execa` users than the baseline trial (the dependency report script from T6 uses the shared `Cmd` and `Logger`); re-check them.

**Acceptance criteria:**

- `lint-staged` runs successfully on a real staged change.
- `pnpm validate:all`, the `scripts-boreal` specs, the Vue app `build` and `lint`, and `pnpm peers check` pass.
- `engines.node` and the README prerequisite state the new floor.
- Standard gates are green, including gate 6.

**Manual test _(required — not waiveable)_:**

- [ ] Given a trivial staged change, when `git commit` runs the hook, then `lint-staged` runs and passes. Pass: hook output shows the tasks completing.
- [ ] Given `scripts-boreal`, when its specs run, then all pass. Pass: baseline count.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade lint-staged, chalk, execa and npm-run-all2"
```

---

## Close-out

### Task 20: Upgrade pnpm 11 to 12

**Status:** pending
**Executor:** @release-subagent (pin, lockfile, pack validation), main thread (documentation)
**Files:**

- `package.json` (root — `packageManager`, `engines.pnpm` if it needs to change)
- `pnpm-workspace.yaml` (modify — replace the `peerDependencyRules` entry with the `:peer` override)
- `pnpm-lock.yaml` (modify — one-time rewrite, own commit)
- `README.md` and `ai-docs/guidelines/cicd-dependency-installation.md` (modify)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Placement: late and deferrable. It changes the lockfile and install behavior for every other task, so it runs after Wave 4's dependency tasks; if the deadline arrives first it goes in the third PR. Added 2026-11-11 at the user's request; the baseline ticket had left it out of scope.
- [ ] Current state (checked 2026-11-11): `packageManager` is `pnpm@11.28.2+sha512…`; the newest pnpm 11 is 11.28.11 and the newest pnpm 12 is 12.19.0 (1.9 days old on that date; re-check the 1-day delay at execution).
- [ ] pnpm 12.0.0 changes against this repository (from the 2026-10-27 research): git dependencies on known hosts resolve to HTTPS (no git dependencies here); unrecognized settings in `pnpm-workspace.yaml` fail with `ERR_PNPM_UNRECOGNIZED_WORKSPACE_SETTINGS` (the file has `packages`, `allowBuilds` and, after T4, `peerDependencyRules`; a scratch install on 12.19.0 accepted `allowBuilds` and `peerDependencyRules`); dependency cycles are broken in a fixed order during peer resolution (expect a one-time lockfile rewrite, committed separately); `packageImportMethod: auto` tries hardlinks first on Linux (Jenkins only); `engineStrict` now fails on incompatible optional subtrees (not set here); `--frozen-lockfile false` is unsupported (no occurrence in the repository scripts; the Jenkins job does not exist yet).
- [ ] Open question: the committed lockfile has an environment section `packageManagerDependencies.pnpm` pinned to 12.4.2 while `packageManager` says 11.28.2. Find out what writes it before the upgrade and record the answer.
- [ ] Verified while implementing T4: the override `"eslint-plugin-react>eslint:peer"` is rejected by pnpm 11.28.2 and 11.28.11 and accepted by 12.19.0, where `pnpm peers check` is clean.
- [ ] Call sites: search the repository for the pnpm version (`README.md`, `CONTRIBUTING.md`, `RELEASING.md`, the documents under `ai-docs/guidelines/`, scripts that call `pnpm` with flags) and update each.
- [ ] Boundary case: Windows. `RELEASING.md` says release commands run on macOS or Linux only, so the Windows check covers the contributor commands (`pnpm install`, `dev:pack:*`, `validate:pack:*`). It cannot be run in this environment; the user or a teammate confirms it.

**Acceptance criteria:**

- `packageManager` is pinned to the newest pnpm 12.x older than the 1-day delay, with its integrity hash.
- The lockfile rewrite is its own commit, formatted with the web-components Prettier, and the diff reason is recorded in this task's status line.
- The `peerDependencyRules` entry is replaced by the `:peer` override and `pnpm peers check` is clean.
- The origin of the `packageManagerDependencies` section is explained in this task's status line.
- Standard gates are green, `pnpm validate:all` passes, and a release dry run passes (`pnpm release:all --dry-run`).
- The README and `cicd-dependency-installation.md` state the new version.
- The user confirms the Windows check.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with a clean install and the gates.

- [ ] Given a clean `pnpm install --frozen-lockfile` on pnpm 12, when the gates run, then they pass as on pnpm 11. Pass: same lint, test and coverage numbers.
- [ ] Given `pnpm release:all --dry-run`, when run, then it completes as before. Pass: no new errors.
- [ ] Given the Windows check by the user, when `pnpm install` and a pack validation run, then they succeed. Pass: confirmed by the user.

**Commit (two commits, each confirmed by the user):**

```bash
git commit -m "build(workspace): EOA-20193 upgrade pnpm to 12"
git commit -m "build(deps): EOA-20193 rewrite lockfile for pnpm 12"
```

---

### Task 21: Housekeeping: holds, template, PR descriptions, index

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `ai-docs/templates/dependency-maintenance-ticket.md` (modify — seed list)
- `.claude/pr-description.md` (modify — PR 1 and PR 2 descriptions)
- `ai-work/plans/INDEX.md` (modify)
- The two draft files under `ai-work/tickets/` (modify — mark items done)

**Acceptance criteria:**

- Each hold lifted by a task is removed from the template's seed list; holds that remain keep their rows. If T20 is not done, the `eslint-plugin-react` workaround from T4 (explicit devDependency plus the `peerDependencyRules` entry) is added as a row, with the removal condition.
- The Confluence template page (SENG `2469101953`) is brought in line with the local template only after the user agrees, since it is an outward-facing change.
- The PR descriptions list the tasks included, the consumer-visible changes and the breaking changes, with the merge order (PR 2 into PR 1, then PR 1 into `release/current`).
- The PR descriptions record the `BdsToggle` `v-model` fix from T7b: the bound value is now a boolean (it was a string), a bound `true` now checks the toggle, the toggle's `value` property is no longer overwritten by the model (this also fixes a form side effect: a checked toggle submitted the model string, `"true"` or `"false"`, instead of its `value`, `"on"` by default), and the generated model type changes from `string` to `boolean`.
- The PR descriptions record the Stencil 4.45.2 behavior change from T5: on form-associated components the string `"false"` in an attribute now resolves to `true` (typed values and properties are unaffected), with `disabled="false"` now disabling the control and excluding it from form data.
- The moderate `minimatch` production finding (see T12) has a recorded decision: fixed by the T12 bump, overridden, or accepted with a reason. `pnpm audit --prod --audit-level high` still exits 0.
- The draft items are marked done in the draft files and this plan's index row is updated.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate by reading the files.

- [ ] Given the template, when its seed list is read, then it names only the holds still in place. Pass: no lifted hold appears.

**Commit:** none (all files are outside git except the PR description draft, which is also local).

### Task 22: Deadline checkpoint and merge readiness

**Status:** pending
**Executor:** main thread (no executor)
**Files:** none

**Acceptance criteria:**

- On 2026-11-12 the status of every task is listed for the user: done and green, not started, or unfinished.
- Unfinished tasks are confirmed as excluded from the working branch (no partial commits).
- The re-format step from T3 is repeated on the final branch state: `pnpm format:check` in docs and web-components passes, or a formatting-only commit is added.
- The PR 2 title is confirmed, with `!` if any task is breaking, and the PR descriptions are final.
- The user merges PR 2 into the PR 1 branch and then PR 1 into `release/current`; after the merge, the user decides on closing EOA-20016 and EOA-20193.
- If tasks remain, the rebase recipe from the deadline section is run and the user decides on a third PR.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with the branch state.

- [ ] Given the working branch, when `git log` is read against PR 2's description, then each listed task has exactly one commit (T3: two, T16: one per batch). Pass: counts match.
- [ ] Given PR 1 after the merge of PR 2, when the standard gates run on it, then they pass. Pass: all green.

**Commit:** none.

---

## Definition of Done (from ticket EOA-20193)

- Every task is done, or explicitly left out by the user before 2026-11-13.
- PR 2 is merged into the PR 1 branch and PR 1 is merged into `release/current`.
- The hold register and the template seed list match the holds still in place.
- No Jira ticket exists apart from EOA-20193.
