---
ticket: EOA-19635
status: done
created: 2026-10-27
updated: 2026-10-30
---

# Dependency Maintenance Baseline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Bring Boreal DS to a known, maintained dependency state: triage and fix production audit findings, refresh Browserslist data, apply patch and minor updates, plan the 30 major updates by family, publish the dependency maintenance policy, and evaluate Renovate on Bitbucket Server.

**Ticket brief:** [`ai-work/tickets/EOA-19635-dependency-maintenance-baseline.md`](../tickets/EOA-19635-dependency-maintenance-baseline.md)

**Architecture:** No component code changes. Work is dependency and tooling maintenance in the pnpm 11 workspace (`packages/*`, `apps/*`, `examples/*`, `scripts-boreal`) plus documentation. Each task maps one-to-one to a Jira sub-task (task number N = `1-` to `11-` prefixed sub-task, EOA-20013+N). Major-version upgrades are planned here and executed only in follow-up tickets. Gates for every code-touching task are `pnpm validate:all`, lint, unit tests (≥ 80% coverage), and the Storybook build.

**Tech Stack:** pnpm 11.28.2 (`packageManager`), Node 22.23.3 (`.node-version`), Turborepo, Stencil (`boreal-web-components`), Storybook, Vitest/Jest, release-it, Bitbucket Server (Renovate evaluation only).

**Related:** ADR `ai-docs/decisions/0019-dependency-maintenance-policy.md` (status: Proposed) · Confluence page [ADR-0016 - Dependency Maintenance Policy](https://telesign.atlassian.net/wiki/spaces/SENG/pages/2412085321/ADR-0016+-+Dependency+Maintenance+Policy) (exists, v1, status Proposed) · plan `EOA-18749` (T24 pnpm 12, T26 Node 24: planned here in Task 4, executed under their own tickets) · plan `EOA-18870` (references this ticket as a follow-up).

---

## Files to create / modify

| File | Notes |
| --- | --- |
| `pnpm-lock.yaml` | Modify — audit fixes (T1), Browserslist data (T2), patch/minor (T3) |
| `package.json` (root, per workspace package `package.json`) | Modify — `overrides` / `pnpm.overrides` only where T1 decides an override is needed; version bumps in T3 |
| `pnpm-workspace.yaml` | Modify only if T1 finds `minimumReleaseAge` / `allowBuilds` need changes; verify first (see Open assumptions) |
| `packages/boreal-web-components/browserslist` or `package.json` `browserslist` key | Create only if T2 decides a config is needed |
| `ai-work/research/2026-10-27-EOA-19635-audit-triage.md` | New — T1 audit triage table |
| `ai-work/research/2026-10-27-EOA-19635-major-updates.md` | New — T4 creates; T5–T9 append one family section each |
| `ai-docs/decisions/0019-dependency-maintenance-policy.md` | Modify — status `Proposed` → accepted (T10) |
| Confluence page SENG `2412085321` | Modify (external) — T10 status update and ADR numbering fix, after user confirmation |
| `ai-work/research/2026-10-27-EOA-19635-renovate-bitbucket-evaluation.md` | New — T11 evaluation and recommendation |
| `ai-work/plans/INDEX.md` | Modify — add this plan row |
| `scripts-boreal/bin/publish.js`, `scripts-boreal/README.md` | Modify — T12 only (deferred follow-up) |

---

## Progress

| Task | Jira | Status |
| --- | --- | --- |
| T1 Triage the 27 production audit findings | EOA-20014 | done 2026-10-29 (`d0fbfe4b`) |
| T2 Update caniuse-lite and fix the Browserslist warning | EOA-20015 | done 2026-10-29 (`5d984553`); warning check moved to T3 |
| T3 Apply pending patch and minor updates | EOA-20016 | done 2026-10-29 (`23eab5da`) |
| T4 Plan major updates: test tooling | EOA-20017 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T5 Plan major updates: lint | EOA-20018 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T6 Plan major updates: Vite / Storybook | EOA-20019 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T7 Plan major updates: TypeScript | EOA-20020 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T8 Plan major updates: Chromatic | EOA-20021 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T9 Plan major updates: utilities | EOA-20022 | done 2026-10-30, confirmed by the user 2026-10-30 |
| T10 Publish the dependency maintenance policy | EOA-20023 | done 2026-10-30 |
| T11 Evaluate Renovate on Bitbucket Server with DevOps | EOA-20024 | re-scoped 2026-10-30; sub-task closed |
| T12 Make `validate:pack` exit non-zero on SIGINT/SIGTERM (re-scoped from the restore redesign) | draft item 1 | done 2026-10-30, committed 6495b48e |
| T13 Clear the `typescript-eslint` 8.59+ type-assertion errors and remove the `~8.58.2` cap (follow-up from T3) | draft item 13 | re-scoped 2026-10-30 |
| T14 Investigate the Stencil 4.45.2 boolean-attribute change on form-associated components and remove the `4.45.1` pin (follow-up from T3) | draft item 10 | re-scoped 2026-10-30 |
| T15 Revisit the `@vitest/eslint-plugin` hold at 1.6.27 (follow-up from T3) | draft item 6 | re-scoped 2026-10-30 |
| T16 Resolve the `@tanstack/virtual-core` 3.19.6+ failures in `bds-search-bar` items mode and decide the published range (follow-up from T3) | draft item 11 | re-scoped 2026-10-30 |
| T17 Exclude the generated flags file from coverage so the Functions gate passes on `release/current` (found while validating the merge) | none | done (`939f3c46`) |
| T18 Add a `./components` export to `boreal-web-components` and lift the `@stencil/react-output-target` 1.4.2 hold (follow-up from T3) | draft item 12 | re-scoped 2026-10-30 |
| T19 Update prettier to 3.9.x and reformat the 16 files it changes (follow-up from T3) | draft item 14 | re-scoped 2026-10-30 |
| T20 Add automated wrapper tests for Vue and React in the test apps (follow-up from T3) | draft item 9 | re-scoped 2026-10-30 |
| T21 Plan the move off Stencil's deprecated integrated testing options (follow-up from T3) | draft item 2 | re-scoped 2026-10-30 |
| T22 Plan the `@colordx/core` 5 → 7 upgrade (unassigned major found by T4) | draft item 3 | re-scoped 2026-10-30 |

---

## Open assumptions (confirm before dispatching the affected task)

- **A1 — `minimumReleaseAge`:** the ADR and the Confluence page describe it as the pnpm 11 default (1440 minutes, 1 day). It is not set explicitly in `pnpm-workspace.yaml` or the root `package.json`, which is consistent with a default. T1 confirms with `pnpm config get minimumReleaseAge` and records the result.
- **A2 — `validate:pack`:** there is no root `validate:pack` script. The root scripts are `validate:pack:react`, `validate:pack:vue`, `validate:pack:angular` and `validate:all` (react + vue). This plan uses `pnpm validate:all` as the wrapper gate and runs `pnpm validate:pack:angular` only if T3 touches Angular-consumed packages.
- **A3 — Browserslist config:** the ticket marks this "To be confirmed". T2 records the decision; the default proposal is no config (the repo has no browserslist config today and the warning is resolved by refreshing data).
- **A4 — Major-update count:** the ticket's families cover the majors it names. The full list of 30 must be reconciled against `pnpm outdated -r` in T4.
- **A5 — Confluence page (resolved):** the page already exists at SENG `2412085321` (created 2026-10-16, v1, status Proposed) with a body matching ADR 0019. No `ai-work/confluence/adr-dependency-maintenance-policy.md` source file is needed; T10 updates the existing page instead.
- **A7 — Runtimes scope:** the ticket lists Node 24 and pnpm 12 as out of scope (tracked as T26 and T24 in the EOA-18749 plan). This plan plans them in Task 4 (research only) and leaves execution to their own tickets. Confirm with the user whether the ticket's out-of-scope line should be reworded.
- **A6 — ADR numbering mismatch:** the Confluence page is titled "ADR-0016" and lists "ADR-0015: Patch release-it in Place" as related, while the local file is ADR 0019 and links ADR 0013. T10 asks the user which numbering is canonical before editing either side.

---

### Task 1: Triage the 27 production audit findings

**Status:** done 2026-10-29 — committed `d0fbfe4b` (manual tests run and passed). Audit went from 29 findings (4 low, 7 moderate, 17 high, 1 critical; the ticket snapshot said 27) to 0. Changes: `dompurify` range `^3.4.8` → `^3.4.17` in `packages/boreal-web-components/package.json`, plus a lockfile re-resolution within existing ranges; no overrides, no major bumps. Full web-components unit suite passes (368 suites, 4,544 tests). Details in `ai-work/research/2026-10-27-EOA-19635-audit-triage.md`.
**Jira:** EOA-20014
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-audit-triage.md` (create)
- `pnpm-lock.yaml` (modify, only for fixes applied)
- `package.json` files (modify, only for overrides required by fixes)

**Integration research pass (complete before writing acceptance criteria):**

Read the actual current `package.json` of `packages/boreal-web-components` and the root before choosing an override strategy.

- [ ] Call sites: `dompurify` (`^3.4.8` in `packages/boreal-web-components/package.json`) is consumed by the Stencil build output — confirm whether a bump changes runtime sanitisation behaviour of any `bds-*` component that renders untrusted HTML.
- [ ] Boundary case: a high finding whose fix version is a major bump of a transitive package — decide override vs. accepted-with-reason, do not force a major through a patch PR.
- [ ] Default/empty state: a finding with no fix version is recorded as "no fix available" with a re-check date, not silently accepted.
- [ ] Config: confirm `minimumReleaseAge` status (Open assumption A1) and record it in the triage document.

**Acceptance criteria:**

- Every `pnpm audit --prod` finding is listed in `ai-work/research/2026-10-27-EOA-19635-audit-triage.md` with package, dependency path, severity, and fix version (one row per advisory; 27 on the 2026-10-16 snapshot, 29 on 2026-10-28).
- The `dompurify` finding under `packages/boreal-web-components` is listed and resolved or decided.
- Every high and critical finding is fixed, overridden, or documented as accepted with a reason in the triage document.
- Every moderate and low finding has a recorded decision (fix, override, accept, or defer with a date).
- `pnpm audit --prod` is re-run after fixes and the output is saved to the triage document.
- No fix is applied through a major version bump in this task; any major needed is logged as a new follow-up task in the triage document.

**Manual test _(required — not waiveable)_:**

Run from the repository root:

1. `eval "$(fnm env --shell bash)" && fnm use` (Node 22.23.3).
2. `pnpm audit --prod` — capture the summary line.
3. Compare against the baseline: 27 findings (3 low, 7 moderate, 17 high) before fixes.

Checklist:

- [x] Given the triage document, when counting its audit rows, then the row count equals the `pnpm audit --prod` total on the day of the run (29 on 2026-10-28). Pass: counts match. _(29 rows, 29 advisories)_
- [x] Given the post-fix `pnpm audit --prod`, when read, then zero unresolved high or critical findings remain, or each remaining one is listed as accepted with a reason. Pass: no unexplained high or critical. _(`No known vulnerabilities found`)_
- [x] Given the modified lockfile, when `pnpm install --frozen-lockfile` runs, then it succeeds. Pass: exit code 0. _(exit 0)_

**Commit (on user confirmation of the message):**

```bash
git commit -m "fix(deps): EOA-20014 resolve production audit findings"
```

---

### Task 2: Update caniuse-lite and fix the Browserslist warning

**Status:** done 2026-10-29 — committed `5d984553`; the "no Browserslist warning" criterion moved to Task 3 (user decision 2026-10-29). Findings: (1) the repo's `caniuse-lite` moved 1.0.30001769 → 1.0.30001819 (newest version past the 1-day `minimumReleaseAge`; 1.0.30001820 was 8 hours old) and `baseline-browser-mapping` 2.9.19 → 2.11.34, but the web-components build still prints the warning (21 lines before and after). (2) The warning comes from the browser data bundled inside `@stencil/core@4.42.1` (`sys/node/autoprefixer.js`), not from the repo's `caniuse-lite`. A probe of `@stencil/core@4.45.2` (registry latest, in the declared `^4.27.1` range) prints no warning. (3) `npx update-browserslist-db@latest` reported success but left the lockfile unchanged: it runs `pnpm up --no-save`, which does nothing under pnpm 11. The working command is `pnpm update -r --lockfile-only --depth 9999 caniuse-lite baseline-browser-mapping`. (4) A browserslist config cannot affect this warning (it is about data age), so assumption A3 resolves to "no config". Decision needed: clear the warning through the Stencil minor update in Task 3, or pull that update into this task.
**Jira:** EOA-20015
**Executor:** main thread (no executor)

**Files:**

- `pnpm-lock.yaml` (modify — caniuse-lite and browserslist data)
- `packages/boreal-web-components/browserslist` (create — only if the decision in step 3 is "config needed")

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: the web-components build (`packages/boreal-web-components`) is the only place that prints the warning per the ticket — confirm by running the build before and after and comparing output.
- [ ] Default/empty state: with no browserslist config, the build falls back to the library default target list. Decide and record whether that default is acceptable for Stencil output (Open assumption A3).
- [ ] Reactivity: not applicable (build tooling).

**Acceptance criteria:**

- The browser data is refreshed with `pnpm update -r --lockfile-only --depth 9999 caniuse-lite baseline-browser-mapping` (the command `npx update-browserslist-db@latest` runs `pnpm up --no-save`, which changes nothing under pnpm 11), and the lockfile change is isolated in its own commit.
- The `caniuse-lite` version in `pnpm-lock.yaml` moves from `1.0.30001769` to the newest version older than the 1-day `minimumReleaseAge` (`1.0.30001819` on 2026-10-29).
- The "build no longer prints the Browserslist warning" criterion moved to Task 3: the warning comes from browser data bundled inside `@stencil/core`, so only the Stencil minor update clears it.
- The decision on a browserslist config (A3) is recorded: no config, because a config cannot affect a warning about data age.

**Manual test _(required — not waiveable)_:**

Run from the repository root:

1. `eval "$(fnm env --shell bash)" && fnm use`
2. `pnpm --filter boreal-web-components build` — or the workspace package name confirmed from its `package.json` — before the change, and note any Browserslist warning.
3. Apply the lockfile update, then run the same build again.

Checklist:

- [ ] Given the build before the change, when run, then the Browserslist outdated warning appears. Pass: warning present (baseline).
- [x] Given the build after the change, when run, then the build exits 0. Pass: exit code 0. _(exit 0; the Browserslist warning is still printed by the data bundled in `@stencil/core@4.42.1` and is checked in Task 3)_

**Commit (on user confirmation of the message):**

```bash
git commit -m "chore(deps): EOA-20015 update caniuse-lite and browserslist data"
```

---

### Task 3: Apply pending patch and minor updates

**Status:** done 2026-10-29, re-validated 2026-10-30 after merging the release commits and the `prebuild` removal from `release/current` (`32c952b5`; lint, 375 suites and 4,810 tests with coverage 92.7% functions, workspace build with a clean tree afterwards, `validate:all` all pass) — committed as `6fdc76ec`, `ffef82e4`, `f339bc7c`, `a1abae44` and `23eab5da` (plus the coverage exclusion `939f3c46` and the `release/current` merge `104e844f`); `validate:all` passed on the last commit. All 53 minor and patch entries were applied except 6 deliberate holds (8 `pnpm outdated -r` rows, because two packages appear twice), each tracked as a deferred task: `@stencil/core` pinned to 4.45.1 (Task 14), `typescript-eslint` capped at `~8.58.2` (Task 13), `@vitest/eslint-plugin` held at 1.6.27 (Task 15), `@tanstack/virtual-core` capped below 3.19.6 (Task 16), `@stencil/react-output-target` pinned to 1.4.2 (Task 18) and `prettier` held at 3.8.x (Task 19). The changelog review is in `ai-work/research/2026-10-27-EOA-19635-changelog-review.md`. Final gates: lint 0 errors, 375 suites and 4,810 tests pass with coverage 93.2% statements / 85.6% branches / 92.7% functions / 94.8% lines, web-components and Storybook builds succeed, Browserslist lines 21 → 0, `pnpm peers check` clean, `git status` clean after `validate:all`. Live-browser smoke pass of the Vue wrapper run 2026-10-29 by the QA subagent on the packed artifacts (Chromium, `dev:pack:vue`; the browser bundle contained the new `syncElementClasses`): host class merging held through 25 toggles of a consumer `:class` and the component's own `error` state with no stale, duplicated or resurrected classes, `v-model` worked in both directions on `bds-text-field` and `bds-checkbox`, and the console had 0 errors (6 warnings, all the expected missing `slot="trigger"` child warning; 2 other console messages were not inspected). Automated coverage is still proposed in Task 20.
**Jira:** EOA-20016
**Executor:** @release-subagent (validation pipeline) — main thread performs the update and changelog review

**Files:**

- `pnpm-lock.yaml` (modify)
- `package.json` files (modify — version ranges for the 42 minor and 11 patch entries from `pnpm outdated -r`)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: the 42 minor and 11 patch entries are read from `pnpm outdated -r` at execution time (not from this plan's snapshot of 2026-10-16). Record the list in the PR description.
- [ ] Boundary case: a minor bump in a product-critical package (Stencil, Storybook, TypeScript, release-it) can change generated output — each gets a changelog review before merge.
- [ ] Default/empty state: a package with no changelog is recorded as "no changelog, reviewed diff" rather than skipped.
- [ ] Dependency on T2: this task's lockfile change must be rebased on top of T2's caniuse-lite commit to keep the diff reviewable.
- [ ] Call sites: `pnpm validate:pack:*` (`scripts-boreal/bin/publish.js`) rewrites the wrapper `package.json`, the test app `package.json` and `pnpm-lock.yaml`, then runs `git checkout HEAD --` on them at exit, which discards any uncommitted edit to those files. The dependency changes must therefore be committed before `validate:all` runs.

**Acceptance criteria:**

- One PR covers all 42 minor and 11 patch entries from `pnpm outdated -r`; no major version is changed.
- Product-critical packages (Stencil, Storybook, TypeScript, release-it) each have a reviewed changelog recorded in the PR description.
- The web-components build no longer prints the Browserslist "outdated" warning (moved from Task 2). It is printed by browser data bundled inside `@stencil/core`, so the Stencil minor update (4.42.1 → the newest version in `^4.27.1` older than the 1-day delay; 4.45.2 probed on 2026-10-29) is what clears it.
- `pnpm lint` passes.
- Unit tests pass with at least 80% coverage.
- `pnpm validate:all` passes (Open assumption A2).
- The Storybook build passes.
- `pnpm validate:pack:angular` is run only if an Angular-consumed package changed (A2).
- The dependency changes are committed (message confirmed by the user) before `pnpm validate:all` runs, and `git status` is clean afterwards, confirming `validate:pack` neither discarded nor left behind edits to the wrapper and test app `package.json` files or `pnpm-lock.yaml`.

**Manual test _(required — not waiveable)_:**

Run from the repository root:

1. `pnpm outdated -r` — confirm only major entries remain.
2. `pnpm lint`
3. `pnpm test`
4. Commit the dependency changes first (message confirmed by the user), then run `pnpm validate:all`, then `git status`.
5. `pnpm --filter <storybook package> build` — confirm the exact Storybook package filter from its `package.json` before running.

Checklist:

- [x] Given the updated repo, when `pnpm outdated -r` runs, then no minor or patch entries remain and only the major entries are listed. Pass: no minor/patch rows. _(30 major rows plus 8 minor/patch rows, all deliberate holds with a tracked task each)_
- [x] Given the updated repo, when `pnpm lint` runs, then it exits 0. Pass: exit code 0.
- [x] Given the updated repo, when `pnpm test` runs, then all tests pass and coverage is at least 80%. Pass: green run, coverage ≥ 80%.
- [x] Given the committed updates, when `pnpm validate:all` runs, then it exits 0 and `git status` is clean afterwards. Pass: exit code 0, no modified files.
- [x] Given the updated repo, when the Storybook build runs, then it completes without errors. Pass: exit code 0.
- [x] Given the updated repo, when the web-components build runs, then no Browserslist "outdated" warning is printed. Pass: zero `Browserslist:` lines in the build output (21 before Task 2).

**Commit (on user confirmation of the message):**

```bash
git commit -m "chore(deps): EOA-20016 apply patch and minor dependency updates"
```

---

### Task 4: Plan major updates: test tooling

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 before Task 5 — `ai-work/research/2026-10-27-EOA-19635-major-updates.md` holds the 30-row reconciliation, the test tooling plan and the Runtimes section; follow-up ticket drafts are queued in `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results: the vitest stack (vitest 5.0.5, jsdom 30) is a small independent upgrade with no breaking-change exposure here; `jest`, `jest-cli`, `@types/jest` and `puppeteer` must not be upgraded in place because Jest 30 is unsupported by Stencil 4's built-in runner, which is deprecated and removed in Stencil 5 (migration to `@stencil/vitest`, Task 21, large); `puppeteer` has no e2e specs to serve; Node 26 became an Active LTS on 2026-10-28 and Node 24 is already in maintenance, so the Node target is a 24 versus 26 decision (an item-3 premise in the release-process drafts is out of date); one major (`@colordx/core`) fits no family and becomes Task 22. No commit applies: `ai-work/` is excluded from git.
**Jira:** EOA-20017
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (create — this task creates the file with its header and the reconciliation table; T5–T9 append their family sections)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: the test tooling family (vitest, `@vitest/*`, jest, jest-cli, `@types/jest`, jsdom, puppeteer) is used by `packages/boreal-web-components` (Stencil spec tests) and by any other package with a `test` script. Enumerate every package that declares each dependency.
- [ ] Boundary case: jest and vitest may coexist — record which package uses which runner, since a migration changes both.
- [ ] Reconciliation (A4): run `pnpm outdated -r --format json`, list all 30 majors, and record any major not in the six families. Each such major becomes a new follow-up task in the research file, not an inline note.
- [ ] Runtimes (A7): `pnpm` (`packageManager` field) and Node (`.node-version`, `.nvmrc`, `engines.node`) do not appear in `pnpm outdated -r`, so they are added to the reconciliation table by hand as a "Runtimes" row. Planning only, no version change.

**Acceptance criteria:**

- The research file contains the reconciliation table of all 30 major entries with current and latest versions, and the family each belongs to (or "unassigned" with a new task).
- For the test tooling family: exact current and target versions are listed, with breaking changes and compatibility notes (Stencil spec compatibility included).
- A "Runtimes (Node, pnpm)" section lists current and target versions for pnpm 11 → 12 and Node 22 → 24, with compatibility to check (Stencil, Storybook, Chromatic, puppeteer, Playwright, example apps, Jenkins agents' Node and Corepack support), the order, gates, and the Node 22 end-of-life date verified at nodejs.org/en/about/previous-releases. The upgrades themselves stay in their own tickets, drafted in `ai-work/tickets/EOA-18749-release-process-followup-tickets.md` (items 2 and 3).
- An order, effort estimate, and gates are defined for the family.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. `pnpm outdated -r` — count major entries.
2. Open `ai-work/research/2026-10-27-EOA-19635-major-updates.md`.

Checklist:

- [x] Given the reconciliation table, when its rows are counted against `pnpm outdated -r` majors, then the counts match. Pass: 30 rows, or the discrepancy is recorded as a new task. _(30 rows: 11 + 5 + 2 + 1 + 2 + 4 + 4 + 1 unassigned, which became Task 22)_
- [x] Given the test-tooling section, when read, then every package in the family has current version, target version, breaking change summary, and gate. Pass: all rows complete.

**Commit:** not applicable — `ai-work/` is excluded from git (`.git/info/exclude`).

---

### Task 5: Plan major updates: lint

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 before Task 6 — section 5 of `ai-work/research/2026-10-27-EOA-19635-major-updates.md`; ticket draft queued as item 4 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results, measured in a disposable worktree: ESLint 10.13.0 plus `@eslint/js` 10.0.1 gives identical lint results in all four workspaces and 0 findings from the three rules added to `eslint:recommended`; every plugin accepts ESLint 10 except one chain — `@stencil/eslint-plugin` loads its optional peer `eslint-plugin-react` unconditionally and `eslint-plugin-react` (latest 7.37.5) does not support ESLint 10, so `boreal-web-components` crashes unless that package is declared explicitly (workaround verified); `eslint-plugin-jsdoc` 65 and `globals` 17 are independent and have no visible impact; effort small. Cross-family note for Task 7: `@stencil/eslint-plugin` peers `typescript ^4.9.4 || ^5 || ^6`, which excludes TypeScript 7. No commit applies: `ai-work/` is excluded from git.
**Jira:** EOA-20018
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append the lint family section)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: `eslint` and `@eslint/js` configuration files across the workspace — list every flat config file that imports them. _(four flat configs, listed in the research file)_
- [x] Boundary case: any ESLint plugin peer-dependency that caps the ESLint major must be recorded as a blocker. _(one chain: `@stencil/eslint-plugin` → optional peer `eslint-plugin-react`, which caps at ESLint 9.7; workaround verified)_
- [x] Default/empty state: a plugin with no ESLint 9+ support is recorded as a blocker with a replacement candidate. _(adapted to ESLint 10: `eslint-plugin-react` has no 10 support and no replacement; explicit devDependency declared as the workaround)_

**Acceptance criteria:**

- Lint family section lists `eslint` and `@eslint/js` current and target versions, breaking changes, and plugin peer-dependency compatibility.
- Order, effort estimate, and gates are defined.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. Open the research file and confirm the lint section is present.
2. Run `pnpm lint` on the current tree to confirm the baseline passes before the plan's gate is defined.

Checklist:

- [x] Given the research file, when the lint section is read, then all rows (eslint, @eslint/js, plugins) are complete. Pass: no empty cells.
- [ ] Given the current tree, when `pnpm lint` runs, then it exits 0 (baseline for the gate). Pass: exit code 0.

**Commit:** not applicable — `ai-work/` is excluded from git.

---

### Task 6: Plan major updates: Vite / Storybook

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 before Task 7 — section 6 of `ai-work/research/2026-10-27-EOA-19635-major-updates.md`; ticket draft queued as item 5 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results, measured in a disposable worktree: Vite 8.3.5 builds Storybook and both test apps (Storybook assets +0.8%); Storybook's builder and the Vue plugins already accept Vite 8; Stencil and the Chromatic packages have no Vite dependency; `@vitejs/plugin-react` 6 (which requires Vite 8) removes the `babel` option, so the React Compiler setup in `react-testapp` needs `@rolldown/plugin-babel@^0.2.4` (plugin-react 6.1.2 rejects 0.3.0); vitest must be 4.1 or later first (`@vitest/mocker` 4.0.18 rejects Vite 8), which Task 4's vitest 5 covers; dev-only peer warnings remain in `vue-testapp` until `vite-plugin-vue-devtools` updates; effort small to medium. No commit applies: `ai-work/` is excluded from git.
**Jira:** EOA-20019
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append the Vite / Storybook family section)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: every `vite.config` and Storybook `main` config that imports Vite plugins — list them. _(five config files, listed in the research file)_
- [x] Boundary case: Storybook's own Vite version pin and the Chromatic addon's compatibility with the target Vite major. _(Storybook builder 10.6.5 accepts Vite ^5 to ^8; the Chromatic packages have no Vite dependency or peer)_
- [x] Reactivity/risk: the ticket names Vite as a risk to the Stencil and Storybook toolchain; the plan records the rollback path (lockfile revert) for the follow-up ticket. _(Stencil does not use Vite; rollback is the lockfile plus the `react-testapp` config)_

**Acceptance criteria:**

- Section lists `vite` current and target versions, with breaking changes and the Storybook and Stencil compatibility matrix.
- Order, effort estimate, and gates are defined, including a Storybook build gate and `pnpm validate:all`.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. Open the research file and confirm the Vite section is present.
2. Run the current Storybook build to confirm the baseline.

Checklist:

- [x] Given the research file, when the Vite section is read, then current, target, compatibility matrix, and gates are all present. Pass: all present.
- [x] Given the current tree, when the Storybook build runs, then it exits 0 (baseline). Pass: exit code 0. _(exit 0)_

**Commit:** not applicable — `ai-work/` is excluded from git.

---

### Task 7: Plan major updates: TypeScript

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 before Task 8 — section 7 of `ai-work/research/2026-10-27-EOA-19635-major-updates.md`; ticket draft queued as item 6 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results, measured in a disposable worktree: TypeScript 7.0.2 is a native compiler with no JavaScript API (7.1 is expected to add one), so tools must keep a TypeScript 6 API through the documented `@typescript/typescript6` alias, and `typescript-eslint` and `@stencil/eslint-plugin` reject TypeScript 7 outright; TypeScript 6.0.3 builds everything once `boreal-react` and `boreal-vue` set `rootDir`; both TypeScript 6 and 7 turn `strict` on by default, which changes lint results and gives 151 errors in `boreal-web-components` unless `strict: false` is set (then no new errors: the 21 existing spec-file errors are unchanged); `baseUrl` is a hard error in TypeScript 7 (web-components and docs tsconfigs); the published wrapper `dist` is byte-identical between TypeScript 5.9.3 and 7.0.2; Stencil bundles its own TypeScript 5.8.3. Recommendation: adopt TypeScript 6.0.3 first (about one day) and treat TypeScript 7 side by side as optional until 7.1. No commit applies: `ai-work/` is excluded from git.
**Jira:** EOA-20020
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append the TypeScript family section)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: every `tsconfig*.json` in the workspace that extends a shared base — list them. _(root base extended by boreal-react, boreal-vue and boreal-style-guidelines; web-components and docs are standalone; test apps use their own bases)_
- [x] Boundary case: Stencil's bundled TypeScript expectations versus the workspace `typescript` version (confirm which one the Stencil build uses). _(Stencil 4.45.1 bundles TypeScript 5.8.3 and the build is independent of the workspace version)_
- [x] Default/empty state: any new compiler default that changes strictness is recorded explicitly, not left for the upgrade ticket to discover. _(`strict` true by default in TypeScript 6 and 7; `types` defaults to `[]`; `rootDir` defaults to the config directory)_

**Acceptance criteria:**

- Section lists `typescript` current and target versions, with breaking changes and the Stencil/typescript-eslint compatibility notes.
- Order, effort estimate, and gates are defined, including `tsc` (or `rtk tsc`) across the workspace and the web-components build.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. Open the research file and confirm the TypeScript section is present.
2. Run the current type check across the workspace to confirm the baseline.

Checklist:

- [x] Given the research file, when the TypeScript section is read, then current, target, compatibility, and gates are all present. Pass: all present.
- [ ] Given the current tree, when the workspace type check runs, then it exits 0 (baseline). Pass: exit code 0.

**Commit:** not applicable — `ai-work/` is excluded from git.

---

### Task 8: Plan major updates: Chromatic

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 before Task 9 — section 8 of `ai-work/research/2026-10-27-EOA-19635-major-updates.md`; ticket draft queued as item 7 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results, measured in a disposable worktree without uploading anything: the CLI (15.2.0 to 18.13.6) and the addon (4.1.3 to 5.6.0) install cleanly, Storybook builds with the new addon with the same addons registered, and the two flags in use (`--storybook-build-dir`, `--exit-zero-on-changes`) plus `CHROMATIC_PROJECT_TOKEN` still exist; breaking changes are Node 22 or later for the CLI and Storybook 10.1 or later for the addon (both met) plus a new terminal UI; no ordering constraint with the other families; effort small. Not verified: a real upload, which needs the token holder to run `pnpm deploy:docs` once after the upgrade. No commit applies: `ai-work/` is excluded from git.
**Jira:** EOA-20021
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append the Chromatic family section)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: the Chromatic CI/deploy step and `@chromatic-com/storybook` addon registration in Storybook config — list them. _(addon in `.storybook/main.ts`; CLI in the `chromatic` script of `boreal-docs`, called by `deploy:docs` and `release:publish`; no CI file in the repository)_
- [x] Boundary case: Chromatic major bumps can change the CLI flags used by the deploy script; record every flag in use. _(`--exit-zero-on-changes` and `--storybook-build-dir=storybook-static`; both present in CLI 18.13.6 `--help`)_
- [x] Reference: `turborepo-cache-vs-chromatic-force-rebuild` (team memory) — Chromatic `--force-rebuild` does not bypass Turborepo cache; the plan must not rely on it. _(the plan does not use `--force-rebuild`; Turbo owns the build and Chromatic only uploads the existing directory)_

**Acceptance criteria:**

- Section lists `chromatic` and `@chromatic-com/storybook` current and target versions, with breaking changes and CLI flag changes.
- Order, effort estimate, and gates are defined.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. Open the research file and confirm the Chromatic section is present.
2. Confirm the current Chromatic CLI flags in use by listing them from the deploy script.

Checklist:

- [x] Given the research file, when the Chromatic section is read, then current, target, CLI-flag impact, and gates are all present. Pass: all present.
- [x] Given the deploy script, when read, then every Chromatic flag in use is recorded in the section. Pass: flag list matches the script.

**Commit:** not applicable — `ai-work/` is excluded from git.

---

### Task 9: Plan major updates: utilities

**Status:** done 2026-10-30, confirmed by the user 2026-10-30 — section 9 of `ai-work/research/2026-10-27-EOA-19635-major-updates.md`; ticket draft queued as item 8 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`. Key results, measured in a disposable worktree: all four bumps (`lint-staged` 17.6.0, `chalk` 6.0.1, `execa` 10.2.1, `npm-run-all2` 9.0.4) install cleanly and pass the full build, the Vue app lint, the 38 `scripts-boreal` specs, `pnpm validate:all` and a real `lint-staged` run; none of the breaking changes touches the two `execa` calls, the colour chains or the two `npm-run-all2` scripts; no CommonJS consumer exists (`scripts-boreal` is ESM and unpublished); the only real impact is the Node floor, which becomes 22.22.2 (set by `npm-run-all2`) while the root `engines.node` and README say `>=22` and the pre-commit hook runs on every contributor's machine; `npm-run-all2` 9 makes a glob that matches no script succeed silently; effort small. This completes the planning of all six families; no commit applies because `ai-work/` is excluded from git.
**Jira:** EOA-20022
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append the utilities family section)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Call sites: `lint-staged` configuration (root and per-package), `chalk` imports in scripts, `execa` imports in `scripts-boreal` and build scripts, `npm-run-all2` script usages — list every call site. _(`.lintstagedrc.js`; `scripts-boreal/lib/logger.js`; `scripts-boreal/lib/cmd.js`; two `vue-testapp` scripts)_
- [x] Boundary case: `chalk` and `execa` are ESM-only in recent majors — record any CommonJS consumer that would break (`package-dir-import-meta-resolve` team memory applies to ESM-only packages). _(none: `scripts-boreal` is `"type": "module"` and both are imported from ESM files; `npm-run-all2` 9 is ESM-only but used only through its CLI)_
- [x] Default/empty state: a script whose exit code depends on `npm-run-all2` behaviour is recorded with its expected exit semantics. _(`run-s lint:*` must fail when a lint script fails; in v9 a glob matching no script passes silently)_

**Acceptance criteria:**

- Section lists `lint-staged`, `chalk`, `execa`, `npm-run-all2` current and target versions, with breaking changes and the ESM/CJS impact.
- Order, effort estimate, and gates are defined.
- A follow-up upgrade ticket is created or its creation is queued for user confirmation.

**Manual test _(required — not waiveable)_:**

1. Open the research file and confirm the utilities section is present.
2. Stage a no-op change to a file already covered by `lint-staged` and run the pre-commit hook path (`pnpm exec lint-staged`) to confirm the baseline works.

Checklist:

- [x] Given the research file, when the utilities section is read, then all four packages have current, target, ESM/CJS impact, and gates. Pass: all rows complete.
- [x] Given a no-op staged change, when lint-staged runs, then it exits 0. Pass: exit code 0. _(a pure no-op is removed by Prettier and trips lint-staged's empty-commit safeguard in version 17; the baseline was run with a small staged change that survives formatting: lint-staged 16.2.7 exit 0, tree restored)_

**Commit:** not applicable — `ai-work/` is excluded from git.

---

### Task 10: Publish the dependency maintenance policy

**Status:** done 2026-10-30, confirmed by the user 2026-10-30. Decisions taken by the user on 2026-10-30: leave the ADR numbering as is (Confluence ADR-0016 / local 0019; recorded in the local ADR); set the status to Accepted ("Accepted on 2026-10-30"); correct item 7 to the pnpm 11 command with the 1-day delay and the Stencil-bundled-data note; reword item 8 to "the pnpm 12 and Node upgrades (24 or 26)"; mark the three completed follow-ups as done; **no Jira recurring ticket — a reusable monthly template instead**, saved at `ai-docs/templates/dependency-maintenance-ticket.md` (the scaffold's folder for reusable artifact templates; ticket briefs for single tickets stay in `ai-work/tickets/`; no mirror symlinks apply). Confluence page SENG `2412085321` is at version 4 (version 2 had flattened the numbered Decision list and version 3 restored it); its references to local files and plan task numbers were removed at the user's request; the local ADR 0019 carries the same text plus a local-only Related section with the page link and the template path. The template was also published in Confluence (SENG page `2469101953`, "Monthly Dependency Maintenance Ticket Template", in the "Jira Tickets" folder `2470543481` next to the Manual Release & Deployment template); the local file and the page must be kept in sync by hand. At the user's request the Jira tickets were edited: EOA-20023 acceptance criteria (ADR accepted, page linked, template replaces the recurring ticket) and EOA-19635 description (local plan references removed, Browserslist command, template link, Definition of Done).
**Jira:** EOA-20023
**Executor:** main thread (no executor)

**Files:**

- `ai-docs/decisions/0019-dependency-maintenance-policy.md` (modify — status `Proposed` → accepted, after review)
- Confluence page SENG `2412085321` (modify externally — status and numbering, after user confirmation; Open assumptions A5 and A6)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: other ADRs or docs that reference "no dependency automation" or the dependency policy — search `ai-docs/` and `ai-work/` for references to ADR 0019 and list them.
- [ ] Boundary case: the monthly recurring ticket is an external, outward-facing Jira action; it requires explicit user confirmation of title, project, and assignee before creation.
- [ ] Boundary case: Confluence title says ADR-0016 and cites ADR-0015, local file says ADR 0019 and cites ADR 0013 (A6) — the canonical numbering is decided with the user before either side is edited.
- [ ] Default/empty state: the local ADR is the source of truth; the Confluence page is brought in line with it, not the reverse.

**Acceptance criteria:**

- ADR 0019 is reviewed by the user and its status is updated from `Proposed` to the agreed status.
- The ADR numbering mismatch (A6) is resolved and recorded.
- ADR 0019 item 7 (Browserslist data) names the command that works under pnpm 11, `pnpm update -r --lockfile-only --depth 9999 caniuse-lite baseline-browser-mapping`, instead of `npx update-browserslist-db@latest`, and notes the 1-day `minimumReleaseAge` delay and that the web-components warning is cleared by Stencil updates.
- The existing Confluence page (SENG `2412085321`) is updated to match the reviewed ADR, including status and numbering, after user confirmation.
- ADR 0019 links to the Confluence page.
- ~~The recurring monthly ticket is created in Jira.~~ Replaced by the user's decision (2026-10-30): a reusable monthly ticket template is saved at `ai-docs/templates/dependency-maintenance-ticket.md`; no Jira ticket is created.

**Manual test _(required — not waiveable)_:**

1. Open `ai-docs/decisions/0019-dependency-maintenance-policy.md` and confirm the status line.
2. Open the Confluence page and compare it with the ADR.
3. After the update, open the Confluence link and the Jira monthly ticket.

Checklist:

- [x] Given the ADR file, when its status line is read, then it is no longer `Proposed`. Pass: status updated. _("Accepted on 2026-10-30")_
- [x] Given the Confluence page, when compared to the ADR, then status, numbering, decision and consequences match. Pass: no divergence. _(status, decision, consequences, risks and follow-ups match; the numbering differs by the user's decision; the local Related section adds local-only references)_
- [x] Given the Confluence page and the monthly ticket template, when opened, then both exist and the ADR links to the Confluence page. Pass: both resolve. _(page version 4 re-read after the update; template file exists; Jira ticket intentionally not created)_

**Commit:** not applicable — `ai-work/` and `ai-docs/` are excluded from git, and the Confluence edit is not a repository change.

---

### Task 11: Evaluate Renovate on Bitbucket Server with DevOps

**Status:** re-scoped 2026-10-30 with the user's confirmation — the research half is done (`ai-work/research/2026-10-27-EOA-19635-renovate-bitbucket-evaluation.md`: requirements, limitations, Mend comparison, open DevOps questions). The DevOps answers and the recommendation move to draft item 7 of `EOA-18749-release-process-followup-tickets.md` (Jenkins report, then Renovate). The Jira sub-task EOA-20024 was amended and closed on the user's instruction, without a pointer to the draft.
**Jira:** EOA-20024
**Executor:** main thread (no executor) — blocked on DevOps answers

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-renovate-bitbucket-evaluation.md` (create)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: none in the codebase; this is an external evaluation. Confirm no `renovate.json` exists in the repository root before starting.
- [ ] Boundary case: Renovate `platform=bitbucket-server` limitations (no assignees, labels, or issue creation; `automergeStrategy` not implemented) — record each limitation against the policy in T10.
- [ ] Dependency: DevOps must answer on bot account, token, and Jenkins hosting. Until then this task is blocked and must be reported as blocked, not completed.

**Acceptance criteria:**

- The evaluation document lists Renovate's self-hosted `platform=bitbucket-server` requirements and each limitation.
- A comparison with Mend for Bitbucket Data Center is recorded.
- DevOps has answered on bot account, token, and Jenkins hosting, and the answers are recorded in the document.
- A recommendation is recorded: proceed, defer, or reject.

**Manual test _(required — not waiveable)_:**

1. Confirm the DevOps answers are recorded in the document.
2. Confirm the recommendation line is present.

Checklist:

- [ ] Given the evaluation document, when read, then bot account, token, and Jenkins hosting each have a recorded DevOps answer. Pass: three answers present.
- [ ] Given the evaluation document, when read, then exactly one recommendation (proceed, defer, or reject) is recorded. Pass: one recommendation.

**Commit (on user confirmation of the message):**

```bash
git commit -m "docs(deps): EOA-20024 evaluate Renovate on Bitbucket Server"
```

---

### Task 12: Make `validate:pack` restore files safely (follow-up)

**Status:** done 2026-10-30 (re-scoped by the user's decision from the full restore redesign to the signal exit-code fix), committed as `6495b48e`. Change: new `scripts-boreal/lib/signals.js` (`registerSignalHandlers`, exit codes 130 for SIGINT and 143 for SIGTERM) used by `scripts-boreal/bin/publish.js` instead of `process.exit(0)`; new `scripts-boreal/lib/__tests__/signals.spec.js` (7 tests; suite 45 tests, `signals.js` 100% coverage). Manual test: the real `publish.js react --ci` was sent SIGTERM after 8 seconds; exit code 143, tarballs removed, tracked files restored, tree clean apart from the change. Not done, by decision: the backup-and-restore redesign for a dirty tree and SIGHUP / SIGKILL handling (documented as unrecoverable; the monthly template says to commit first). Done: the `kill -9` recovery step was added (`git checkout HEAD -- <wrapper package.json> <test-app package.json> pnpm-lock.yaml`) to `ai-docs/guidelines/publishing-and-deployment.md`.
**Executor:** @release-subagent

**Files:**

- `scripts-boreal/bin/publish.js` (modify)
- `scripts-boreal/README.md` (modify — troubleshooting for the dirty-file case)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Call sites: `validate:pack:react`, `validate:pack:vue` and `validate:pack:angular` in the root `package.json` all run through `scripts-boreal`; `validate:all` chains the first two. Confirm one change in `publish.js` covers all three.
- [ ] Boundary case: the three paths restored on exit (wrapper `package.json`, test app `package.json`, root `pnpm-lock.yaml`) already hold uncommitted edits when the script starts — define whether the script refuses to run or backs up and restores only what it changed.
- [ ] Signals: cleanup runs on exit, error, SIGINT and SIGTERM but not SIGHUP (terminal closed) or `kill -9`; decide which are handled and which are documented as unrecoverable.
- [ ] Observed 2026-10-29: `pnpm dev:pack:vue` was killed from outside (exit 137) during the QA smoke pass and left `examples/vue-testapp/package.json` and `packages/boreal-vue/package.json` pointing at `file:` tarballs and `pnpm-lock.yaml` rewritten (about 14.6k lines); it was restored with `git checkout` of those files. Normal `validate:all` runs in this task always left a clean tree, so the defect is the killed-process case this task already targets.

**Acceptance criteria:**

- The script restores only what it changed (backup and restore), or refuses to run when those files have uncommitted changes.
- A SIGHUP handler runs the same cleanup.
- `scripts-boreal/README.md` describes the dirty-file case and how to recover.
- Task 3's commit-before-`validate:all` guard is removed or reworded once this lands.

**Manual test _(required — not waiveable)_:**

1. Make an uncommitted edit to one of the three paths, run `pnpm validate:pack:react`, and check the edit is kept or the run is refused.
2. Start `pnpm validate:pack:react`, close the terminal window mid-run, reopen, and run `git status`.

Checklist:

- [ ] Given an uncommitted edit to a restored path, when `validate:pack:react` runs, then the edit is not discarded. Pass: the edit survives or the script refuses to run with a clear message.
- [ ] Given the terminal is closed mid-run, when `git status` is checked afterwards, then none of the three paths is left modified. Pass: clean tree.

**Commit (on user confirmation of the message):**

```bash
git commit -m "fix(scripts): make validate:pack restore files safely"
```

---

### Task 13: Clear the `typescript-eslint` 8.59+ type-assertion errors (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 13 of `EOA-19635-dependency-upgrade-followup-tickets.md`; the `~8.58.2` cap stays as a row of the monthly hold register (re-tested every window). If the TypeScript 6 upgrade (item 6) lands first, the count is redone. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** @frontend-subagent (source edits), @testing-subagent (spec check)

**Files:**

- `apps/boreal-docs/package.json`, `examples/react-testapp/package.json`, `packages/boreal-web-components/package.json` (modify — replace `~8.58.2` with a caret range)
- 17 files under `packages/boreal-web-components/src/components/` (modify — remove the flagged assertions; the list comes from running lint at 8.59.0 or later)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): `typescript-eslint` 8.59.0 is the first version that raises 38 `@typescript-eslint/no-unnecessary-type-assertion` errors in 17 web-components files; 8.58.2 lints clean. Re-run the bisect result at execution time, since later versions may change the rule again.
- [ ] Call sites: each flagged assertion, for example `(this.el as HTMLElement)` in `bds-text-field.tsx`, may still be needed for another TypeScript version or for Stencil's JSX typing — check each before removing it.

**Acceptance criteria:**

- Every flagged assertion is removed or justified, with no behavior change.
- The three `~8.58.2` caps become caret ranges and `typescript-eslint` resolves to the newest version older than the 1-day delay.
- `pnpm lint` exits 0 and the web-components unit suite still passes.

**Manual test _(required — not waiveable)_:**

1. `pnpm lint`, then `pnpm --filter @pxglobal/boreal-web-components test:coverage`.

Checklist:

- [ ] Given the updated `typescript-eslint`, when `pnpm lint` runs, then it exits 0. Pass: 0 errors.
- [ ] Given the source edits, when the unit suite runs, then all suites pass with coverage ≥ 80%. Pass: green.

**Commit (on user confirmation of the message):**

```bash
git commit -m "chore(deps): update typescript-eslint and remove unnecessary type assertions"
```

---

### Task 14: Investigate the Stencil 4.45.2 boolean-attribute change and remove the `4.45.1` pin (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 10; the exact `@stencil/core` 4.45.1 pin stays as a row of the monthly hold register. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** @frontend-subagent (investigation and source), @testing-subagent (specs), @qa-subagent (live-browser check)

**Files:**

- `packages/boreal-web-components/package.json` (modify — replace the exact `4.45.1` pin)
- `packages/boreal-web-components/src/components/forms/bds-file-uploader/bds-file-picker/__test__/bds-file-picker.methods.spec.ts` and `bds-file-picker.slots-watchers.spec.ts` (modify only if the investigation shows the tests encode wrong behavior)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): with `@stencil/core` 4.45.2, three `bds-file-picker` tests fail because the string attribute `multiple="false"` or `error="false"` on this form-associated component is parsed as `true`; 4.45.0 and 4.45.1 pass all 178 file-picker tests. The parsing function is identical in 4.42.1 and 4.45.2, but the attribute-to-property path differs.
- [ ] Boundary case: decide in a real browser whether `<bds-file-picker multiple="false">` was `false` or `true` at Stencil 4.45.1 and 4.42.1, since the unit tests run on Stencil's mock DOM and may not match production. _(Answered for 4.45.1 on 2026-10-29, Chromium, packed artifacts: `multiple="false"` and `error="false"` give `false`, `"true"` and `""` give `true`, absent gives `false`, all booleans, so the mock-DOM tests match production at 4.45.1. Still untested: 4.42.1 and 4.45.2 in a browser.)_
- [ ] Call sites: every other form-associated component (those using `formAssociatedMixin`) with boolean props could change the same way — list them and check which have tests that pass `"false"` as an attribute.
- [ ] Reference: team memory `face-composite-child-value-sync-on-non-string-branch.md` — behavior on form-associated components is invisible to unit tests, so use a live `<form>` check.
- [ ] Inert copy: `packages/boreal-vue` resolves `@stencil/core@4.45.2` as an auto-installed peer of `@stencil/vue-output-target`; only type declarations are used there. Confirm that when the pin is removed.

**Acceptance criteria:**

- The behavior difference is understood, documented in the plan, and either fixed in the components, accepted with a documented migration note, or reported upstream.
- The exact `4.45.1` pin becomes a caret range and the full unit suite, build and `validate:all` pass.

**Manual test _(required — not waiveable)_:**

1. `pnpm dev:components`, render `<bds-file-picker multiple="false">` and `<bds-file-picker error="false">` at the old and the new Stencil, and compare in the browser.

Checklist:

- [ ] Given Stencil 4.45.2, when the two attributes are set to `"false"`, then the behavior is the intended one. Pass: documented outcome, with no unexplained difference between mock DOM and browser.

**Commit (on user confirmation of the message):**

```bash
git commit -m "chore(deps): remove the @stencil/core 4.45.1 pin"
```

---

### Task 15: Revisit the `@vitest/eslint-plugin` hold at 1.6.27 (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped into draft item 6 (TypeScript 6.0.3), which lifts the `@vitest/eslint-plugin` hold; until then the 1.6.27 hold stays as a row of the monthly hold register. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** main thread (no executor)

**Files:**

- `pnpm-lock.yaml` (modify)
- `examples/vue-testapp/package.json` (modify only if a cap is needed)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): `@vitest/eslint-plugin` 1.6.28 raises its optional `typescript` peer from `>=5.0.0` to `>=6.0.0`; `pnpm peers check` flags it against TypeScript 5.9.3. The hold at 1.6.27 lives only in the lockfile, so any later re-resolution of `examples/vue-testapp` can move it to the newest 1.6.x again.
- [ ] Dependency: the TypeScript major update planned in Task 7. If the repository moves to TypeScript 6, the hold is no longer needed. _(Task 7 confirmed: `@vitest/eslint-plugin` 1.6.28 accepts `>=6.0.0`, so moving to TypeScript 6.0.3 lifts the hold.)_

**Acceptance criteria:**

- After the TypeScript decision from Task 7, the plugin is either at the newest version (TypeScript 6 in place) or capped explicitly in `examples/vue-testapp/package.json`.
- `pnpm peers check` reports no issues.

**Manual test _(required — not waiveable)_:**

1. `pnpm peers check`, then `pnpm --filter vue-testapp lint`.

Checklist:

- [ ] Given the final dependency set, when `pnpm peers check` runs, then it reports no issues. Pass: clean output.

**Commit (on user confirmation of the message):**

```bash
git commit -m "chore(deps): update @vitest/eslint-plugin"
```

---

### Task 16: Resolve the `@tanstack/virtual-core` 3.19.6+ failures in `bds-search-bar` items mode (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 11; the `>=3.17.1 <3.19.6` cap stays as a row of the monthly hold register. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** @frontend-subagent (investigation and source), @testing-subagent (specs)

**Files:**

- `packages/boreal-web-components/package.json` (modify — the `@tanstack/virtual-core` range)
- `packages/boreal-web-components/src/utils/dom/virtualWindow/virtual-window.ts` and the `bds-search-bar` specs (modify only if the investigation shows a real incompatibility)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29, bisect over every stable release from 3.17.1 to 3.19.8): 3.19.5 passes all 305 `bds-search-bar` tests, 3.19.6 fails 24 of them, all in items mode (windowed suggestions, EOA-19597). Task 3 caps the range at `>=3.17.1 <3.19.6` to keep the repository green.
- [ ] Call sites: `src/utils/dom/virtualWindow/virtual-window.ts` and `bds-table.tsx` both use `@tanstack/virtual-core`; check `bds-table` against 3.19.6+ too.
- [ ] Boundary case: `virtual-core` is a published runtime `dependency` declared as `^3.17.1`, so consumers resolve the newest 3.x regardless of this repository's lockfile. Decide whether the failure is real in a browser or only in the mock DOM (the tests use `utils/testing/mocks/layout.ts`).

**Acceptance criteria:**

- The cause of the 3.19.6 failures is identified and documented.
- The published range is either kept capped (with the reason in the plan) or widened after a source or test fix.
- `bds-search-bar` specs pass at the newest allowed version, and a live-browser check of the items-mode list passes.

**Manual test _(required — not waiveable)_:**

1. Run the `bds-search-bar` specs at 3.19.5 and at the newest version, then `pnpm dev:components` and scroll a 1,000-entry list in the browser.

Checklist:

- [ ] Given `virtual-core` at the newest allowed version, when the search-bar specs run, then all pass. Pass: 305 of 305.
- [ ] Given a 1,000-entry list in the browser, when scrolling and using Home, End and arrow keys, then only the visible window is mounted and focus behaves. Pass: no regression against 3.19.5.

**Commit (on user confirmation of the message):**

```bash
git commit -m "fix(web-components): EOA-19597 support the latest @tanstack/virtual-core"
```

---

### Task 17: Exclude the generated flags file from coverage (found while validating the merge)

**Status:** done 2026-10-29 for the coverage exclusion — committed `939f3c46` (`test:coverage` exits 0 with Functions 92.66%). The generated-file formatting side effect (each build rewrote `generatedFlags.ts` with quoted keys and left a 261-line diff) was resolved upstream on 2026-10-30 by commit `89d1919b` ("remove prebuild script"), merged here as `32c952b5`: a full workspace build now leaves the tree clean. The coverage exclusion is still needed because `generatedFlags.ts` stays tracked. `flagsManifest.ts` remains but nothing regenerates `generatedFlags.ts` automatically any more, so new flag SVGs need a manual refresh.
**Executor:** main thread (no executor)

**Files:**

- `packages/boreal-web-components/testing.config.ts` (modify — add an exclusion to `collectCoverageFrom`)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): `pnpm --filter @pxglobal/boreal-web-components test:coverage` exits 1 on the merged code with Functions 77.09% (threshold 80%), the same with and without Task 3 changes. `src/components/forms/bds-flag/helpers/generatedFlags.ts`, added by commit `32292f5f` (EOA-19436), has 542 functions of which 532 never run; without it Functions would be 92.67%.
- [x] Side effect: the `prebuild` script wrote that file with quoted keys, while the committed copy is Prettier-formatted, so every build left a 261-line formatting-only diff in the working tree. Resolved upstream by commit `89d1919b`, which removed the script.

**Acceptance criteria:**

- The generated file is excluded from coverage collection, and `test:coverage` exits 0 with Functions at or above 80%.
- A build leaves the working tree clean (done upstream by `89d1919b`).

**Manual test _(required — not waiveable)_:**

1. `pnpm --filter @pxglobal/boreal-web-components test:coverage`, then `pnpm --filter @pxglobal/boreal-web-components build` and `git status`.

Checklist:

- [ ] Given the exclusion, when coverage runs, then it exits 0. Pass: exit code 0, Functions ≥ 80%.
- [x] Given a build, when `git status` runs, then `generatedFlags.ts` is not modified. Pass: clean tree. _(verified 2026-10-30 after merging `32c952b5`)_

**Commit (on user confirmation of the message):**

```bash
git commit -m "test(web-components): exclude generated flags from coverage"
```

---

### Task 18: Add a `./components` export and lift the `@stencil/react-output-target` hold (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 12; the `@stencil/react-output-target` 1.4.2 pin stays as a row of the monthly hold register. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** @release-subagent (package exports and pack validation), @qa-subagent (wrapper parity)

**Files:**

- `packages/boreal-web-components/package.json` (modify — add a `./components` entry to `exports`, types from `./components-build/index.d.ts`)
- `packages/boreal-react/package.json` and `packages/boreal-web-components/package.json` (modify — replace the exact `1.4.2` pin of `@stencil/react-output-target`)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): `@stencil/react-output-target` 1.5.0 and later generate `import type { Components }` (or `{ JSX }` in 1.5.1) from `@pxglobal/boreal-web-components/components`; 1.4.1 and 1.4.2 do not. The `exports` map has `./components/*.js` but no bare `./components`, so `tsc` in `boreal-react` fails with TS2307. The merge commit (with 1.4.1) builds; Step 1 (1.6.5) did not.
- [ ] Call sites: `packages/boreal-web-components/targets/react-output-target.ts` (`customElementsDir: 'components'`, `outDir: '../boreal-react/lib/components'`); also check the Vue output target before Task 3 step 3 raises `@stencil/vue-output-target` to 0.14.x, since it may add the same requirement.
- [ ] Boundary case: `components-build/index.d.ts` exists after a build and is the likely type target; confirm it is included in the published `files` and resolves from a consumer install, using the pack-based pipeline.

**Acceptance criteria:**

- `exports["./components"]` resolves its types from a packed tarball in the React and Vue test apps.
- `@stencil/react-output-target` moves to the newest version past the 1-day delay, as a range.
- `pnpm validate:all` passes.

**Manual test _(required — not waiveable)_:**

1. `pnpm validate:all` after committing, then `git status`.

Checklist:

- [ ] Given the new export and the unpinned output target, when `pnpm validate:all` runs, then it exits 0. Pass: exit code 0, clean tree.

**Commit (on user confirmation of the message):**

```bash
git commit -m "feat(web-components): EOA-19635 export the components types entry"
```

---

### Task 19: Update prettier to 3.9.x and reformat the files it changes (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 14; the prettier 3.8.x hold stays as a row of the monthly hold register. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** main thread (no executor)

**Files:**

- `packages/boreal-web-components/package.json`, `apps/boreal-docs/package.json`, `examples/react-testapp/package.json`, `examples/vue-testapp/package.json` (modify — the exact `prettier` pins)
- The files `prettier --check` flags at 3.9.x: `bds-table.pin-offsets.spec.ts` and `ITable.ts` in `boreal-web-components`, and 14 files in `boreal-docs` (for example `FormDemo.ts` and several `*.stories.ts`); re-run the check at execution time for the current list.

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): the same `format:check` scripts pass at 3.8.0 and 3.8.1 and flag 2 + 14 files at 3.9.10. `react-testapp` has 3 flagged files at both versions (generated `.vite/deps/_metadata.json` and two config files), so it is not affected.
- [ ] Call sites: `lint-staged` runs the package `format` script on staged files, so these files would be reformatted the next time someone touches them; a single mechanical commit avoids that noise in unrelated PRs.

**Acceptance criteria:**

- All four `prettier` pins move to the same version older than the 1-day delay.
- The flagged files are reformatted in a commit that contains formatting changes only.
- Every `format:check` script passes.

**Manual test _(required — not waiveable)_:**

1. `pnpm --filter @pxglobal/boreal-web-components format:check` and `pnpm --filter @pxglobal/boreal-docs format:check`, then `pnpm lint`.

Checklist:

- [ ] Given prettier 3.9.x and the reformatted files, when the format checks run, then both exit 0. Pass: exit code 0.

**Commit (on user confirmation of the message):**

```bash
git commit -m "style: EOA-19635 format with prettier 3.9"
```

---

### Task 20: Add automated wrapper tests for Vue and React in the test apps (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 9. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** @testing-subagent (tests), @qa-subagent (one browser smoke pass on the packed artifacts)

**Files:**

- `examples/vue-testapp/src/__tests__/` (create — `wrapper-models.spec.ts`, `wrapper-classes.spec.ts`)
- `examples/vue-testapp/package.json` (modify — add a `test` script so the root `pnpm test` runs it)
- `examples/react-testapp/src/__tests__/` (create — `wrapper-events.spec.ts`, `wrapper-classes.spec.ts`; Part B)
- `examples/react-testapp/package.json`, `examples/react-testapp/vite.config.ts` (modify — Part B only: add `vitest`, `jsdom`, `@testing-library/react`, a jsdom test environment and a `test` script)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-29): the wrapper packages `boreal-vue` and `boreal-react` have placeholder `test` scripts, so every dependency bump to a wrapper runtime relies on manual checks. `vue-testapp` already has `vitest` 4.1, `jsdom` 28, `@vue/test-utils` 2.5 and a jsdom `vitest.config.ts`, with no test files. `react-testapp` has no test tooling at all.
- [ ] Spike first: confirm that the real Stencil components render and emit events inside jsdom. If they do not, fall back to a stub custom element that sets its own host class, which covers the runtime contract but not Boreal's real host classes.
- [ ] Vue risk: `componentModels` in `packages/boreal-web-components/targets/vue-output-target.ts` is a manual list; a forgotten entry or a mistyped event name fails silently. React has no equivalent list: its event props are generated from the component metadata.
- [ ] Runtime delta that motivated this (Task 3, `@stencil/vue-output-target` 0.13.1 → 0.14.7): the class-merging code (`syncElementClasses`) was rewritten, while the `v-model` path was untouched.
- [ ] Constraints: zero inline comments in the spec files, no ticket IDs in `describe` or `it` names, and the test apps resolve the wrappers through the workspace build, so the root build order must run `boreal-vue` and `boreal-react` first.

**Acceptance criteria:**

Part A — Vue:

- A data-driven invariant test reads `custom-elements.json` and fails when a component that emits a model event and has a model prop has no matching `componentModels` entry. Adding a component needs no test edit.
- A class-merging test mounts a wrapped component that sets its own host class, toggles a consumer `:class` and the component state, and asserts both sets of classes survive each re-render and removed consumer classes disappear.
- A `v-model` smoke test on a representative component asserts the bound ref updates when the model event fires.

Part B — React:

- An invariant test asserts every custom event in `custom-elements.json` is exposed as an `on<Event>` prop on the matching wrapper.
- A `className` test asserts consumer classes and the component's own host classes both survive re-renders.
- An event smoke test on a representative component asserts the handler fires with the event detail.
- Part B is dropped from this task if the user decides React is not worth the new tooling.

Both parts:

- The root `pnpm test` runs the new tests, and they pass.
- One QA subagent smoke pass on the packed artifacts (`dev:pack:vue`, `dev:pack:react`) confirms the same behavior in a real browser.

**Manual test _(required — not waiveable)_:**

1. `pnpm --filter vue-testapp test:unit --run` and, for Part B, the same for `react-testapp`; then `pnpm test` from the repository root.
2. Make the invariant fail on purpose by removing one entry from `componentModels`, confirm the test reports the missing component, then restore it.

Checklist:

- [ ] Given the new tests, when the root `pnpm test` runs, then the Vue (and React) tests run and pass. Pass: exit code 0.
- [ ] Given a `componentModels` entry removed on purpose, when the invariant test runs, then it fails naming the component. Pass: failure names the component.

**Commit (on user confirmation of the message):**

```bash
git commit -m "test(vue): EOA-19635 add wrapper tests"
```

---

### Task 21: Plan the move off Stencil's deprecated integrated testing options (follow-up from Task 3)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 2 (migration to `@stencil/vitest`), which already carries the core findings. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-29-EOA-19635-stencil-testing-deprecation.md` (create — findings and a recommended path; no source changes in this task)

**Integration research pass (complete before writing acceptance criteria):**

- [x] Answered by Task 4 (2026-10-30), see `ai-work/research/2026-10-27-EOA-19635-major-updates.md` section 2, Track B: Stencil's built-in runner is deprecated since 4.43 and removed in Stencil 5; Jest 30 is unsupported on Stencil 4; the replacement is `@stencil/vitest` 1.16.1 (accepts Stencil 4 and 5, vitest 2 to 5); the migration touches 374 spec files (337 with `newSpecPage`, 2,756 call sites; 197 with Jest APIs, 1,286 uses); `puppeteer` serves no e2e specs. Remaining here: the effort breakdown, the Stryker and coverage re-verification, and the start date.
- [ ] Finding (2026-10-29): Stencil 4.43.3 lists "testing: deprecate all integrated testing options" in its changelog. This repository runs `stencil test --spec` through `packages/boreal-web-components/testing.config.ts`, typed with `TestingConfig`, which the IDE already reports as deprecated (TS 6385). Nothing breaks on 4.45.1.
- [ ] Call sites: the `test`, `test:watch`, `test:coverage` and `test:scripts` scripts of `boreal-web-components`, the mutation-testing configs (Stryker, one per component), the CI gates that run the unit suite, and every spec that relies on `newSpecPage`.
- [ ] Boundary case: find which Stencil release removes the integrated options (the upstream changelog and migration notes), and what Stencil recommends instead, before estimating effort.

**Acceptance criteria:**

- The research file states the removal timeline, the recommended replacement, the files affected, an effort estimate and the gates, in the same shape as the major-update plans from Tasks 4 to 9.
- A follow-up ticket exists for the migration, or the user records that it is deferred with a date.

**Manual test _(required — not waiveable)_:**

1. Open the research file and check each section against the upstream changelog entry.

Checklist:

- [ ] Given the research file, when read, then every call site above is listed with its migration impact. Pass: no empty rows.

**Commit (on user confirmation of the message):**

```bash
git commit -m "docs(deps): EOA-19635 plan the Stencil testing migration"
```

---

### Task 22: Plan the `@colordx/core` 5 → 7 upgrade (unassigned major found by Task 4)

**Status:** re-scoped 2026-10-30 with the user's confirmation — Re-scoped to draft item 3. No Jira ticket yet, by the user's decision; create one from the draft when someone picks it up.
**Executor:** main thread (no executor)

**Files:**

- `ai-work/research/2026-10-27-EOA-19635-major-updates.md` (modify — append a `@colordx/core` section)

**Integration research pass (complete before writing acceptance criteria):**

- [ ] Finding (2026-10-30): `@colordx/core` 5.6.0 → 7.3.0 is a two-major jump in a runtime `dependency` of `boreal-web-components`, so it reaches consumers. It belongs to none of the six planned families.
- [ ] Call sites: every import of `@colordx/core` in `bds-color-picker`, `bds-color-box`, `bds-color-format`, `bds-alpha-slider`, `bds-hue-slider` and any shared color utility.
- [ ] Boundary case: color parsing and formatting edge cases (alpha, HSV, invalid input) must stay identical across the two majors.

**Acceptance criteria:**

- The section lists current and target versions, the breaking changes from both major changelogs, the affected components, an order, an effort estimate and the gates.
- A follow-up upgrade ticket exists, or the user confirms the draft in `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md` (item 3).

**Manual test _(required — not waiveable)_:**

1. Open the research section and check each affected component against the source.

Checklist:

- [ ] Given the section, when read, then every call site above is listed with its migration impact. Pass: no empty rows.

**Commit:** not applicable — `ai-work/` is excluded from git.

---

## Definition of Done (from ticket EOA-19635)

- All sub-tasks closed (T1–T11).
- `pnpm audit --prod` has no unresolved high or critical findings, or each remaining one is documented as accepted.
- Pending patch and minor updates merged; all gates green.
- Major updates planned and ticketed.
- Policy published and the monthly ticket exists.
