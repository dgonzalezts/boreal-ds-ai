# Dependency maintenance ticket — monthly template

## How to use (do not paste this section)

- Open a ticket from this template at the start of each monthly window defined by the policy in Confluence, "ADR-0016 - Dependency Maintenance Policy" (local copy: `ai-docs/decisions/0019-dependency-maintenance-policy.md`).
- Copy everything below the `--- paste below ---` line into a new Jira ticket (Task, project EOA), replace each `{placeholder}`, delete the guidance in parentheses, and create sub-tasks only for the steps that apply this month. The pasted text deliberately contains no local file paths.
- The structure mirrors the baseline ticket EOA-19635. The `create-ticket` command can turn the filled copy into a Jira-ready description.
- Quarterly (January, April, July, October) also run the runtime review step; skip it in the other months.
- **Seed the hold register from here the first time** (state at the end of the baseline, 2026-10-30): `@stencil/core` pinned to 4.45.1 (4.45.2 parses a string `"false"` as `true` on form-associated components); `@stencil/react-output-target` pinned to 1.4.2 (from 1.5.0 the generated wrapper imports types from a `/components` path the package does not export); `typescript-eslint` capped at `~8.58.2` (8.59 adds 38 type-assertion errors); `@tanstack/virtual-core` capped below 3.19.6 (3.19.6 fails 24 `bds-search-bar` tests); `@vitest/eslint-plugin` held at 1.6.27 (1.6.28 needs TypeScript 6 or later); `prettier` held at 3.8.x (3.9 reformats 16 files). After the first window, copy the register from the previous ticket instead.
- When Phase 2 or Phase 3 of the policy arrives (scheduled Jenkins job, Renovate), replace the snapshot and update steps with the automated output and keep the rest.

--- paste below ---

**Summary:** Dependency maintenance — {Month YYYY}

**Type:** Task · **Project:** EOA · **Labels:** `dependencies`, `security`, `maintenance`, `tooling`, `technical-debt`
**Parent:** {PI feature or epic} · **Assignee:** {name} · **Window:** {start date} to {end date}

## Goal

Keep the Boreal DS dependencies maintained under the policy in [ADR-0016 - Dependency Maintenance Policy](https://telesign.atlassian.net/wiki/spaces/SENG/pages/2412085321): fix production vulnerabilities, refresh the browser data, apply the pending patch and minor updates in one PR, and keep the backlog of major updates visible.

## Snapshot at the start of the window

| Measure | How to read it | Last window | This window |
| --- | --- | --- | --- |
| Outdated entries (major / minor / patch) | `pnpm outdated -r` | {M / m / p} | {fill} |
| Production audit (critical / high / moderate / low) | `pnpm audit --prod` | {c / h / m / l} | {fill} |
| `caniuse-lite` version | lockfile | {version} | {fill} |
| Node pin and newest patch of that line | `.node-version`, nodejs.org | {pin / patch} | {fill} |
| pnpm pin and newest patch of the 11 line | `packageManager` | {pin / patch} | {fill} |
| Packages on hold (hold register) | previous ticket | {n} | {fill} |

## Scope

- Production audit triage and fixes.
- Browser data refresh.
- Patch and minor updates, including re-testing each hold.
- Check of the major-update backlog.
- Runtime review (quarterly only).

## Out of scope

- Executing major updates: each family has its own ticket and plan.
- Dev-only audit findings, unless they block a gate.

## Sub-tasks

### 1- Triage the production audit findings

- Run `pnpm audit --prod` and list every finding with package, dependency path, severity and fix version, high and critical first.
- Fix a finding in this order: raise the direct dependency, re-resolve the transitive package inside its existing range, then add an override. Never force a major through a patch PR; log it as a new task.
- High and critical findings are fixed within 2 weeks of discovery, outside the monthly schedule if needed.

Acceptance criteria:
- High and critical findings are fixed, overridden, or documented as accepted with a reason.
- Moderate and low findings have a recorded decision.
- `pnpm audit --prod` is re-run and the output is attached.

### 2- Refresh the browser data

- Run `pnpm update -r --lockfile-only --depth 9999 caniuse-lite baseline-browser-mapping`. `npx update-browserslist-db@latest` changes nothing under pnpm 11.
- `minimumReleaseAge` (1 day) can hold back the newest release; take the newest one older than a day.

Acceptance criteria:
- The lockfile change is committed on its own.
- The `web-components` build prints no `Browserslist:` line. If it still does, the data is bundled in `@stencil/core`: check whether a newer Stencil clears it.

### 3- Apply the pending patch and minor updates

- List candidates with `pnpm outdated -r --format json` and classify each by current to latest. Skip releases younger than a day.
- Update the lockfile one package name at a time (or `xargs pnpm update -r --lockfile-only < names.txt`); do not pass the names as one unsplit variable. `pnpm update` also rewrites manifest ranges: restore the ones that do not need a bump, then run `pnpm install --lockfile-only` and format the lockfile with the `web-components` Prettier (`pnpm --filter @pxglobal/boreal-web-components exec prettier --write ../../pnpm-lock.yaml`).
- Re-test each package in the hold register against its latest version before updating anything else.
- Treat pre-1.0 packages (0.x minors can break) and packages that generate published output (Stencil, the React and Vue output targets) separately, with a changelog review.
- Run `pnpm peers check` after each batch.
- When a gate fails, bisect: update the single package to explicit versions to find the first failing release, then hold it with an explicit range cap (a hold kept only in the lockfile does not survive re-resolution) and add it to the register.
- For a risky bump, trial it in a disposable worktree: `git worktree add --detach <dir> HEAD`, `HUSKY=0 pnpm install --frozen-lockfile`, `pnpm build` to generate the files type-aware lint needs, apply the bump, run the gates, then `git worktree remove --force <dir>`.

Acceptance criteria:
- One PR covers the updates; no major version changes.
- Product-critical packages (Stencil, Storybook, TypeScript, Node, pnpm, release-it) have a reviewed changelog recorded in the PR description.
- All gates below pass.

### 4- Review the hold register

For every held package: re-test the latest version, then either lift the hold or keep it with the reason updated.

| Package | Held at | Latest | Reason | How to test | Next review |
| --- | --- | --- | --- | --- | --- |
| {package} | {version or cap} | {version} | {reason} | {command or check} | {window} |

Acceptance criteria:
- Every row is re-tested or has a dated reason for skipping; lifted holds are removed.

### 5- Check the major-update backlog

- Re-run `pnpm outdated -r` and compare the majors with the planned families (test tooling, lint, Vite and Storybook, TypeScript, Chromatic, utilities, runtimes).
- Add each new major to its family ticket, or open a ticket if it fits none. Note any family whose prerequisite is now met.

Acceptance criteria:
- Every major has a family ticket; the count is recorded in the snapshot.

### 6- Runtime review (quarterly)

- Node: check the release schedule at nodejs.org, the end-of-life date of the pinned line, and the minimum Node of the tools in use. Update `.node-version` and `.nvmrc` to the newest patch of the pinned line when a newer one exists.
- pnpm: take the newest patch of the 11 line; track the 12 upgrade in its own ticket.

Acceptance criteria:
- The pinned versions and the next decision date are recorded.

### 7- Close out

- Attach the audit output, the PR link and the updated hold register; create the tickets for new majors; open next month's ticket from this template.

## Gates before merge

- `pnpm lint` passes with no errors.
- Unit tests pass with at least 80% coverage (`pnpm --filter @pxglobal/boreal-web-components test:coverage`).
- `pnpm build` passes, including the Storybook build, and `pnpm peers check` is clean.
- Commit the dependency changes **before** `pnpm validate:all`: `validate:pack` restores the wrapper and test-app `package.json` files and the lockfile with `git checkout HEAD --` on exit and discards uncommitted edits to them. If the run is killed, restore those files with `git checkout`.
- `git status` is clean after the build and after `validate:all`.
- Majors of published dependencies also need a release-it dry run.
- A change to a wrapper runtime library (`@stencil/vue-output-target`, `@stencil/react-output-target`) gets a browser smoke test of the wrapper before the next release.
- A Chromatic CLI or addon upgrade gets one real `pnpm deploy:docs` run by the token holder.

## Definition of Done

- All sub-tasks closed.
- `pnpm audit --prod` has no unresolved high or critical findings.
- Pending patch and minor updates are merged and all gates are green.
- The hold register is updated; new majors are ticketed.
- Next month's ticket exists.

## Risks

- A patch or minor release can change behavior: stricter lint rules, a tightened peer range, a different parsing rule. Bisect and hold instead of forcing it through.
- Production fixes may need major bumps of transitive packages: use an override or accept the finding with a recorded reason.
- Newly published releases may be skipped by `minimumReleaseAge`, so a fix can be unavailable for a day.
