---
ticket: EOA-20193
status: pending
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

- **Checkpoint on 2026-11-12** (T21): list the tasks done and green and the tasks not started or unfinished.
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

- **A1 — Jenkins job location:** there is no Jenkinsfile in this repository. T6 delivers a script and documentation only; wiring it into the Jenkins job is outside the repository.
- **A2 — Report exit code (T6):** the script exits 1 only when `pnpm audit --prod` has unresolved high or critical findings, so Jenkins can mark the build unstable. Confirm.
- **A3 — Jenkins Node version (T2):** jsdom 30, Chromatic CLI 18 and the utilities need Node 22.22.2 or later. The repository pin is 22.23.3, which meets it. Only the agents' version is unknown.
- **A4 — TypeScript 7 side by side:** excluded from T8; it is optional in the draft and waits for TypeScript 7.1.
- **A5 — React wrapper tests (T7):** Part B is dropped if the user decides React is not worth the new tooling.
- **A6 — Node move and pnpm 12:** not in this plan; they remain drafts R2 and R3.

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
| `scripts-boreal/bin/deps-report.js`, `scripts-boreal/lib/deps-report.js`, `scripts-boreal/lib/__tests__/deps-report.spec.js` | New — dependency report (T6) |
| `packages/boreal-web-components/stencil.config.ts`, `vitest.config.ts`, spec files | Modify / New — test runner migration (T15 to T17) |
| `pnpm-lock.yaml` | Modify — every dependency task |
| `ai-docs/templates/dependency-maintenance-ticket.md` | Modify — hold register seed list (T20) |
| `.claude/pr-description.md` | Modify — PR descriptions (T20, T21) |

---

## Progress

| Task | Status |
| --- | --- |
| T1 Create the working branch and record the gate baseline | pending |
| T2 Confirm the Jenkins Node version and record the Node target | pending |
| T3 Update prettier to 3.9 and reformat the flagged files | pending |
| T4 Upgrade ESLint to 10 with its companions | pending |
| T5 Investigate the Stencil 4.45.2 boolean-attribute change and remove the 4.45.1 pin | pending |
| T6 Add the dependency report script | pending |
| T7 Add automated wrapper tests for Vue and React | pending |
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
| T20 Housekeeping: holds, template, PR descriptions, index | pending |
| T21 Deadline checkpoint and merge readiness | pending |

---

## Wave 0: prerequisites

### Task 1: Create the working branch and record the gate baseline

**Status:** pending
**Executor:** main thread (no executor)
**Files:** none (no code change)

**Acceptance criteria:**

- `chore/EOA-20193_dependency-upgrades-followup_DG` is cut from the tip of the PR 1 branch and pushed with upstream tracking.
- PR 1 (#208) is confirmed to be still open and its branch has no commits that are not on the working branch.
- The standard gates are run once on the working branch and the numbers are recorded in this task's status line as the baseline.
- The user is told the branch is ready to open PR 2 (target: the PR 1 branch); the pull request itself is opened by the user.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with `git log --oneline -3` on both branches and the standard gates.

- [ ] Given the working branch, when compared with the PR 1 branch, then they point to the same commit. Pass: `git rev-parse` outputs match.
- [ ] Given the standard gates, when run, then all pass. Pass: baseline recorded.

**Commit:** none.

### Task 2: Confirm the Jenkins Node version and record the Node target

**Status:** pending
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

- [ ] Given the recorded answer, when compared with the floors above, then T10, T18 and T19 are marked "can proceed" or "blocked". Pass: each has a marking.

**Commit:** none.

---

## Wave 1: independent, low risk

### Task 3: Update prettier to 3.9 and reformat the flagged files

**Status:** pending
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
- Standard gates are green.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate with each package's `format:check` script and the standard gates.

- [ ] Given the bumped pins, when `format:check` runs in each workspace, then it passes after the reformat commit. Pass: exit code 0 everywhere that passed before.
- [ ] Given the reformat commit, when `git show --stat` is read, then it contains only the flagged files. Pass: no other file.

**Commit (two commits, each confirmed by the user):**

```bash
git commit -m "build(deps): EOA-20193 update prettier to 3.9"
git commit -m "style: EOA-20193 reformat files with prettier 3.9"
```

### Task 4: Upgrade ESLint to 10 with its companions

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `apps/boreal-docs/package.json`, `packages/boreal-web-components/package.json`, `examples/react-testapp/package.json`, `examples/vue-testapp/package.json` (modify)
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

- [ ] Given ESLint 10, when `pnpm lint` runs, then error counts are 0 and warning counts equal the baseline. Pass: 9 / 50 / 0 / 0.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 upgrade eslint to 10"
```

### Task 5: Investigate the Stencil 4.45.2 boolean-attribute change and remove the 4.45.1 pin

**Status:** pending
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

- [ ] Given `<bds-file-picker multiple="false">` in a `<form>`, when the page loads, then `multiple` is `false` and form validity matches the 4.45.1 behavior. Pass: no difference, or the difference is the documented decision.
- [ ] Given the same markup in the React and Vue wrapper apps, when rendered, then behavior matches the raw web component. Pass: no divergence.

**Commit:**

```bash
git commit -m "build(deps): EOA-20193 update @stencil/core to a caret range"
```

### Task 6: Add the dependency report script

**Status:** pending
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

**Status:** pending
**Executor:** @testing-subagent (tests), @qa-subagent (one browser smoke pass on the packed artifacts)
**Files:**

- `examples/vue-testapp/` spec files and `vitest.config.ts` (create / modify)
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

- A data-driven test reads `custom-elements.json` and fails when a component with a model prop and model event has no `componentModels` entry. Adding a component needs no test edit.
- A class-merging test mounts a wrapped component that sets its own host class, toggles a consumer `:class` and the component state, and asserts both sets of classes survive each re-render and removed consumer classes disappear.
- A `v-model` smoke test on a representative component asserts the bound ref updates when the model event fires.

Part B — React (dropped if the user decides, assumption A5):

- A test asserts every custom event in `custom-elements.json` is exposed as an `on<Event>` prop on the matching wrapper.
- A `className` test asserts consumer classes and the component's own host classes both survive re-renders.
- An event smoke test on a representative component asserts the handler fires with the event detail.

Both parts: the root `pnpm test` runs the new tests and they pass. Standard gates are green.

**Unit tests to cover:** the behaviors listed above; coverage-phase only.

**Manual test _(required — not waiveable)_:**

- [ ] Given the Vue test app, when `pnpm test` runs from the root, then the new specs run and pass. Pass: exit code 0.
- [ ] Given a deliberately removed `componentModels` entry in a scratch change, when the tests run, then the invariant test fails. Pass: failure names the component. Revert the scratch change.
- [ ] Given the packed artifacts, when @qa-subagent repeats one class-merging and one `v-model` scenario in a browser, then the result matches the tests. Pass: no divergence.

**Commit:**

```bash
git commit -m "test(examples): EOA-20193 add automated wrapper tests"
```

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

### Task 20: Housekeeping: holds, template, PR descriptions, index

**Status:** pending
**Executor:** main thread (no executor)
**Files:**

- `ai-docs/templates/dependency-maintenance-ticket.md` (modify — seed list)
- `.claude/pr-description.md` (modify — PR 1 and PR 2 descriptions)
- `ai-work/plans/INDEX.md` (modify)
- The two draft files under `ai-work/tickets/` (modify — mark items done)

**Acceptance criteria:**

- Each hold lifted by a task is removed from the template's seed list; holds that remain keep their rows.
- The Confluence template page (SENG `2469101953`) is brought in line with the local template only after the user agrees, since it is an outward-facing change.
- The PR descriptions list the tasks included, the consumer-visible changes and the breaking changes, with the merge order (PR 2 into PR 1, then PR 1 into `release/current`).
- The draft items are marked done in the draft files and this plan's index row is updated.

**Manual test _(required — not waiveable)_:**

Non-visual task. Validate by reading the files.

- [ ] Given the template, when its seed list is read, then it names only the holds still in place. Pass: no lifted hold appears.

**Commit:** none (all files are outside git except the PR description draft, which is also local).

### Task 21: Deadline checkpoint and merge readiness

**Status:** pending
**Executor:** main thread (no executor)
**Files:** none

**Acceptance criteria:**

- On 2026-11-12 the status of every task is listed for the user: done and green, not started, or unfinished.
- Unfinished tasks are confirmed as excluded from the working branch (no partial commits).
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
