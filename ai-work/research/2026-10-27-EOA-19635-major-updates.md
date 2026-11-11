# EOA-19635 — Major updates planning

Planning only: nothing in this document changes a version. Tasks 4 to 9 of the plan add one section per family; this file is created by Task 4 (test tooling and runtimes).

**Data date:** 2026-10-30. Versions come from `pnpm outdated -r` at that date and the registry's `latest` tags.

## 1. Reconciliation of the 30 major entries

`pnpm outdated -r --format json` lists 30 major rows (some packages appear in several rows because workspaces declare different versions). Every row is assigned below.

| Family | Rows | Packages (current → latest) |
| --- | --- | --- |
| d1 Test tooling (Task 4) | 11 | `vitest` 4.0.18 (docs, style-guidelines, scripts-boreal) and 4.1.0 (vue-testapp) → 5.0.5; `@vitest/browser-playwright` (docs), `@vitest/coverage-v8` (docs, style-guidelines, scripts-boreal), `@vitest/ui` (style-guidelines, scripts-boreal) 4.0.18 → 5.0.5; `jest` and `jest-cli` 29.7.0 → 30.5.2; `@types/jest` 29.5.14 → 30.0.0; `jsdom` 28.1.0 → 30.1.3; `@types/jsdom` 28.0.0 → 30.0.0; `puppeteer` 24.37.2 → 25.16.0 |
| d2 Lint (Task 5) | 5 | `eslint` 9.39.2 / 9.39.4 → 10.13.0 (two rows); `@eslint/js` 9.39.2 → 10.0.1; `eslint-plugin-jsdoc` 62.7.1 → 65.4.2; `globals` 16.5.0 → 17.13.0 (react-testapp) |
| d3 Vite / Storybook (Task 6) | 2 | `vite` 7.3.1 → 8.3.5; `@vitejs/plugin-react` 5.1.4 → 6.1.2 |
| d4 TypeScript (Task 7) | 1 | `typescript` 5.9.3 → 7.0.2 |
| d5 Chromatic (Task 8) | 2 | `chromatic` 15.2.0 → 18.13.6; `@chromatic-com/storybook` 4.1.3 → 5.6.0 |
| d6 Utilities (Task 9) | 4 | `lint-staged` 16.2.7 → 17.6.0; `chalk` 5.6.2 → 6.0.1; `execa` 9.6.1 → 10.2.1; `npm-run-all2` 8.0.4 → 9.0.4 |
| Runtimes (this task, section 3) | 4 | `@types/node` 22.19.11, 24.10.13, 24.12.0, 25.2.3 → 26.6.6 (four rows). They follow the Node decision, not the "latest" tag |
| Unassigned | 1 | `@colordx/core` 5.6.0 → 7.3.0 (runtime dependency of `boreal-web-components`) |

11 + 5 + 2 + 1 + 2 + 4 + 4 + 1 = 30. Classification choices that differ from the ticket's wording: `@types/jsdom` joins d1 (it types `jsdom`), `eslint-plugin-jsdoc` and `globals` join d2 (lint tooling), `@vitejs/plugin-react` joins d3 (it tracks Vite).

**New follow-up from the reconciliation:** `@colordx/core` jumps two majors in a package that ships to consumers (the color picker) and fits no family. It becomes plan Task 22 (deferred): read its changelog, check the `bds-color-picker` and `bds-color-box` usage, and plan the upgrade.

## 2. Family d1 — test tooling

### Where it is used

| Package | Declares | Tests that exist |
| --- | --- | --- |
| `boreal-web-components` | `jest` ^29.7.0, `jest-cli` ^29.7.0, `@types/jest` ^29.5.14, `puppeteer` ^24.3.0 | 374 spec files run by `stencil test --spec` (Stencil's built-in runner on Jest); 0 e2e files |
| `boreal-docs` | `vitest` ^4.0.16, `@vitest/browser-playwright` ^4.0.16 (and `@vitest/coverage-v8`) | none of its own; Storybook's vitest addon runs stories |
| `boreal-style-guidelines` | `vitest`, `@vitest/ui`, `@vitest/coverage-v8` ^4.0.18 | 1 spec file |
| `scripts-boreal` | `vitest`, `@vitest/ui`, `@vitest/coverage-v8` ^4.0.18 | 5 spec files |
| `vue-testapp` | `vitest` ^4.1.0, `jsdom` ^28.1.0, `@types/jsdom` ^28.0.0 | none yet (Task 20 proposes some) |

Two unrelated stacks share the heading "test tooling": the **Vitest stack** (4 workspaces) and **Stencil's Jest/Puppeteer stack** (1 workspace, the one with almost all the tests). They need different plans.

### Track A — Vitest stack: `vitest`, `@vitest/*`, `jsdom`, `@types/jsdom`

- **Current → target:** `vitest` 4.0.18 / 4.1.0 → 5.0.5; `@vitest/browser-playwright`, `@vitest/coverage-v8`, `@vitest/ui` 4.0.18 → 5.0.5 (vitest 5 pins these peers to the exact same version, so all four move together); `jsdom` 28.1.0 → 30.1.3; `@types/jsdom` 28.0.0 → 30.0.0.
- **Breaking changes (Vitest 5 migration guide):** `vi.clearAllMocks()` now runs before each test by default (`clearMocks`); `test.workspace` is replaced by `test.projects`; `browser.api` moves to the top-level `api` option.
- **Impact here:** none of the three applies. No package uses `vi.fn`, `vi.mock` or `vi.spyOn`; no config sets `workspace`; the docs config uses `browser.instances` without `browser.api`.
- **Compatibility checked:** `@storybook/addon-vitest` 10.6.5 accepts `vitest ^4 || ^5`; vitest 5 accepts Vite `^6.4 || ^7 || ^8`, so it does **not** wait for the Vite 8 upgrade (d3); vitest 5 needs Node `^22.12 || ^24 || >=26` (we run 22.23.3). `jsdom` 30 needs Node `^22.22.2 || ^24.15 || >=26`, which raises the floor from 22.12 / 22.13 (jsdom 28 / 29) to 22.22.2; the local pin satisfies it, and the Jenkins agents' Node version (DevOps question 17) must be confirmed first.
- **Order:** (1) vitest family together in one change; (2) `jsdom` and `@types/jsdom` afterwards, once the CI Node version is known. Independent of d2, d3 and d4.
- **Effort:** small (about half a day each step).
- **Gates:** lint; the 6 spec files in `boreal-style-guidelines` and `scripts-boreal`; the Storybook build; the Storybook vitest addon run in `boreal-docs`; `pnpm validate:all`.

### Track B — Stencil's Jest/Puppeteer stack: `jest`, `jest-cli`, `@types/jest`, `puppeteer`

- **Current → latest:** `jest` and `jest-cli` 29.7.0 → 30.5.2; `@types/jest` 29.5.14 → 30.0.0; `puppeteer` 24.37.2 → 25.16.0 (Node `>=22.12.0`).
- **Blocked, do not upgrade in place.** Stencil's support policy lists Jest 30 as unsupported for the built-in test runner on Stencil 4 (supported: Jest 24 to 29; Jest 30 only with a separate "Jest Stencil Runner"). The built-in runner is **deprecated since Stencil 4.43 and will be removed in Stencil 5**.
- **`puppeteer`** is used only by `stencil test --e2e`, and the package has **0 e2e spec files**; it still costs a Chrome download on every install and an `allowBuilds` entry. The `e2e` scripts and the standards document describe a workflow nobody uses yet.
- **Recommended path:** migrate the unit tests to `@stencil/vitest` (1.16.1; accepts `@stencil/core ^4 || ^5` and `vitest ^2` to `^5`; Node `^22.12 || ^24 || >=26`), which replaces `jest`, `jest-cli`, `@types/jest` and `puppeteer`. Browser-mode tests would use `@vitest/browser-playwright`, which `boreal-docs` already has.
- **Size of the migration:** 374 spec files; 337 use `newSpecPage` (2,756 call sites) and 335 import from `@stencil/core/testing`; 197 files use Jest APIs (`jest.fn`, `jest.spyOn`, timers; 1,286 uses). Stencil's guide maps `newSpecPage({ components, html })` to `render(<component />)` (HTML strings still supported), moves `testing` options from `stencil.config.ts` to a `vitest.config.ts`, and lets spec tests keep Stencil's mock DOM or use jsdom or happy-dom.
- **Effort:** large (multi-week, mostly mechanical; a codemod for `newSpecPage` and `jest.*` is worth evaluating). The coverage thresholds (80%) and the mutation-testing setup (Stryker, per component) need to be re-verified on the new runner.
- **Gates:** all 374 spec files green with the same coverage, `pnpm validate:all`, Stryker score unchanged on a sample component.
- **This is plan Task 21.** Its call-site and removal-timeline questions are answered above; what is left is the effort breakdown and the decision on when to start (before Stencil 5, or earlier to drop `puppeteer`).

### Tickets (queued for confirmation, not created)

Drafts are in `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`: items 1 (vitest 5 and jsdom 30), 2 (migration to `@stencil/vitest`) and 3 (`@colordx/core`).

## 3. Runtimes — Node and pnpm

Planning only. `@types/node` is handled here because the right version is "the major of the Node we run", not the registry's latest.

### Node

- **Now:** `.node-version` 22.23.3, root `engines.node` `>=22`. The newest Node 22 patch is 22.23.4 (2026-10-20), so a patch-level runtime update exists today.
- **Schedule (nodejs/Release, checked 2026-10-30):**

| Line | Active LTS from | Maintenance from | End of life | Newest version |
| --- | --- | --- | --- | --- |
| 22 "Jod" | 2024-10-29 | 2025-10-21 | **2027-04-30** | 22.23.4 |
| 24 "Krypton" | 2025-10-28 | **2026-10-20** (now) | 2028-04-30 | 24.22.2 |
| 26 "Lithium" | **2026-10-28** (now) | 2027-10-20 | 2029-04-30 | 26.13.0 |

- **This changes the draft in `EOA-18749-release-process-followup-tickets.md` item 3,** which treats Node 24 as the newer LTS. Node 26 became an Active LTS two days before this review, and Node 24 has been in maintenance since 2026-10-20.
- **Declared Node support of the tools that matter** (declared, not tested): `release-it` 21.1.1 `^22.22.2 || ^24.15.0 || >=26`; `@commitlint/cli` 21.2.4 `>=22.12`; `vite` 7.3.1 `^20.19 || >=22.12`; `vitest` 5.0.5 and `@stencil/vitest` `^22.12 || ^24 || >=26`; `jsdom` 30 `^22.22.2 || ^24.15 || >=26`; `puppeteer` 25 `>=22.12`; `playwright` `>=20`; `lint-staged` 16 `>=20.17`; `eslint` 9 `^18.18 || ^20.9 || >=21.1`; `@stencil/core` 4.45.1 `>=16`; `storybook`, `turbo` and `chromatic` declare none. `vue-testapp` already uses `@tsconfig/node24`.
- **`@types/node` today** is on four different majors (22.19.11, 24.10.13, 24.12.0, 25.2.3) against a Node 22 runtime; 25 is not an LTS line. The four rows are decided by the Node choice: align every workspace to the major of the chosen runtime.
- **Options:** (A) stay on 22 with the patch update, EOL 2027-04-30; (B) move to 24, about 18 months of runway; (C) move to 26, about 30 months of runway but two days old as an LTS. Every tool above declares support for all three lines; `release-it` and `jsdom` 30 set the floor at 22.22.2 / 24.15.
- **Recommendation to decide with DevOps:** do not stay on 22 past mid-2027. Choose between 24 and 26 after a short spike that runs the repository's gates (lint, unit tests, builds, `validate:all`, a release dry run) under each version locally with `fnm`; this costs hours, not days. The Jenkins agents' available versions (DevOps question 17) decide what is possible.
- **Effort:** small to medium; mostly verification and documentation (`.node-version`, `.nvmrc`, `engines.node`, README, `@types/node`, the `@tsconfig/node*` packages).

### pnpm

- **Now:** `packageManager` `pnpm@11.28.2`; the newest 11.x is 11.28.9 (Node `>=22.13`), so a patch-level update exists; the newest overall is 12.16.1 (12.0.0 released 2026-08-26).
- **pnpm 12.0.0 major changes (6) against this repository:**

| Change | Impact here |
| --- | --- |
| Git dependencies on known hosts resolve to canonical HTTPS | None: no git dependencies |
| Unrecognized settings in `pnpm-workspace.yaml` now fail with `ERR_PNPM_UNRECOGNIZED_WORKSPACE_SETTINGS` | Our file has `packages` and `allowBuilds`; confirm both are valid in 12 before the upgrade |
| Dependency cycles broken in a fixed order during peer resolution | Expect a one-time lockfile rewrite; commit it separately |
| `packageImportMethod: auto` tries hardlinks first on Linux | Jenkins only; no action |
| `engineStrict` now fails on incompatible optional subtrees | `engineStrict` is not set |
| `--frozen-lockfile false` unsupported | No occurrence in the repository's scripts; CI files outside the repository must be checked |

- **Open question:** the committed `pnpm-lock.yaml` contains an environment section pinning `packageManagerDependencies.pnpm` to 12.4.2 while `packageManager` says 11.28.2. Find out what writes it before the upgrade.
- **Order:** pnpm after the Node decision (pnpm 12 itself accepts `>=18`); take the 11.28.9 patch independently.
- **Effort:** small to medium (verification across macOS, Windows and Jenkins).

### Tickets

Existing drafts: items 2 (pnpm) and 3 (Node) of `EOA-18749-release-process-followup-tickets.md`. Item 3 needs its premise corrected (see above); that file was not edited here.

## 4. Follow-ups logged by this task

1. `@colordx/core` 5.6.0 → 7.3.0 (plan Task 22, deferred).
2. Correct item 3 of the release-process follow-up file (Node 26 is the newest LTS; Node 24 is in maintenance).
3. Patch-level runtime updates available today: Node 22.23.4 and pnpm 11.28.9.
4. Decide whether to keep `puppeteer` and the unused `e2e` scripts until the Stencil test runner migration (Task 21).

## 5. Family d2 — lint (Task 5)

**Data date:** 2026-10-30. Measured first-hand in a disposable git worktree of the committed tree (nothing changed in the working branch).

### Rows and targets

| Package | Current | Target | Where declared |
| --- | --- | --- | --- |
| `eslint` | 9.39.2 (docs, web-components, react-testapp), 9.39.4 (vue-testapp) | 10.13.0 | all four workspaces with a lint config |
| `@eslint/js` | 9.39.2 | 10.0.1 (peer `eslint ^10.0.0`, so it moves with `eslint`) | docs, web-components, react-testapp |
| `eslint-plugin-jsdoc` | 62.7.1 | 65.4.2 | web-components |
| `globals` | 16.5.0 (react-testapp); docs is already on 17.13.0 | 17.13.0 | react-testapp |

ESLint 10.14.0 was published 4 hours before the review, so 10.13.0 is the newest version older than the 1-day `minimumReleaseAge`.

### Where it is used

Four flat configs: `apps/boreal-docs/eslint.config.js`, `examples/react-testapp/eslint.config.js`, `examples/vue-testapp/eslint.config.ts`, `packages/boreal-web-components/eslint.config.ts`. All use `defineConfig` from `eslint/config`; none uses `FlatCompat`, `.eslintrc`, the `tseslint.config()` helper, ESLint flags or `eslint-env` comments. The two TypeScript configs rely on `jiti` (2.7.0 installed; ESLint 10 needs 2.2.0 or later).

### Breaking changes (ESLint 10 migration guide) against this repository

| Change | Impact here |
| --- | --- |
| Node `^20.19 \|\| ^22.13 \|\| >=24` | Met (22.23.3) |
| `eslint:recommended` adds `no-unassigned-vars`, `no-useless-assignment`, `preserve-caught-error` | Active as errors in web-components, docs and react-testapp; **0 findings** |
| JSX references are now tracked | **0 new reports** in the `.tsx` files linted |
| `eslint-env` comments become errors | None in the codebase |
| `jiti` below 2.2.0 unsupported | Met (2.7.0) |
| Removed `.eslintrc` support, config lookup flag, `radix` / `func-names` / other rule schema changes, plugin-author API removals | Not used |

### Measured result

ESLint 10.13.0 with `@eslint/js` 10.0.1, installed in a worktree that first reproduced the current baseline exactly:

| Workspace | ESLint 9 (baseline) | ESLint 10 |
| --- | --- | --- |
| `boreal-docs` | 0 errors, 9 warnings | identical |
| `react-testapp` | 0 / 0 | identical |
| `vue-testapp` | 0 / 0 | identical |
| `boreal-web-components` | 0 errors, 50 warnings (799 files) | identical **after the workaround below**; crashes without it |

`pnpm peers check` stayed clean after the upgrade.

### Plugin compatibility with ESLint 10 (installed versions)

All accept ESLint 10: `typescript-eslint` 8.58.2 (`^8.57 || ^9 || ^10`), `@stencil/eslint-plugin` 1.4.0, `eslint-plugin-jsdoc` 62.7.1, `eslint-plugin-storybook` (`>=8`), `eslint-plugin-react-hooks` 7.1.1 (first accepted in 7.1.0), `eslint-plugin-react-refresh` 0.5.7 (`^9 || ^10`), `eslint-plugin-vue` 10.12.0, `@vue/eslint-config-typescript` 14.9.0, `@vitest/eslint-plugin` (`>=8.57`), `eslint-config-prettier` (`>=7`), `eslint-plugin-oxlint` (no ESLint peer).

### One blocker, with a verified workaround

- **`eslint-plugin-react`.** `@stencil/eslint-plugin` 1.4.0 lists it as an *optional* peer but loads it unconditionally. Today pnpm installs `eslint-plugin-react` 7.37.5 because ESLint 9 satisfies its peer range. Its latest release (7.37.5, April 2025) peers `eslint ^3 … ^9.7`, so with ESLint 10 pnpm drops it and `eslint` in `boreal-web-components` crashes with `Cannot find module 'eslint-plugin-react'`.
- **Workaround verified:** declare `eslint-plugin-react@7.37.5` explicitly as a devDependency of `boreal-web-components`. pnpm prints an unmet-peer warning, and lint is identical (799 files, 0 errors, 50 warnings). Silencing the warning with `peerDependencyRules` was not tested.
- **Alternatives:** wait for `eslint-plugin-react` to support ESLint 10, or for `@stencil/eslint-plugin` to stop requiring it. Neither exists as a release today.

### Companion packages

- **`eslint-plugin-jsdoc` 62.7.1 → 65.4.2** is independent of ESLint 10 (62.7.1 already accepts it). 63.0.0 drops Node 20; 64.0.0 is ESM-only and requires Node `^22.22.2 || >=24.15.0` (the same floor as `jsdom` 30 and `release-it`); 65.0.0 makes `check-indentation` stricter. The config only references `jsdoc/check-tag-names`, so 65 has no visible impact. Confirm the CI Node version first.
- **`globals` 16.5.0 → 17.13.0:** the only breaking change is that `audioWorklet` is split out of `browser`. `boreal-docs` already runs 17.13.0 with identical results, so the `react-testapp` bump is trivial.

### Order, effort and gates

1. `globals` in `react-testapp` (trivial, any time).
2. `eslint` and `@eslint/js` together in all four workspaces, with the `eslint-plugin-react` workaround in `boreal-web-components`.
3. `eslint-plugin-jsdoc` 65 after the CI Node version is confirmed.
- **Effort:** small (about half a day); the measurement found no code changes.
- **Gates:** lint in all four workspaces with the same error and warning counts, `pnpm peers check` (or a documented exception), `pnpm validate:all`.
- **Independent of Task 13:** the `typescript-eslint` cap at `~8.58.2` is about rules added in 8.59, not about the ESLint version.

### Cross-family note for Task 7 (TypeScript)

`@stencil/eslint-plugin` 1.4.0 peers `typescript ^4.9.4 || ^5.0.0 || ^6.0.0`, which does not include TypeScript 7. Check it, and `typescript-eslint`'s own TypeScript range, when planning the TypeScript upgrade.

### Ticket

Queued for confirmation as item 4 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`.

## 6. Family d3 — Vite and its plugin (Task 6)

**Data date:** 2026-10-30. Measured first-hand in a disposable git worktree of the committed tree (nothing changed in the working branch).

### Rows and targets

| Package | Current | Target | Where declared |
| --- | --- | --- | --- |
| `vite` | 7.3.1 (`^7.2.4` in docs and `react-testapp`, `^7.3.1` in `vue-testapp`) | 8.3.5 (Node `^20.19 \|\| >=22.12`, met) | `boreal-docs`, `react-testapp`, `vue-testapp` |
| `@vitejs/plugin-react` | 5.1.4 | 6.1.2 (peer `vite ^8.0.0` only, so it moves with Vite 8) | `react-testapp` |
| `@rolldown/plugin-babel` (new) | none | `^0.2.4` (pre-1.0; see below) | `react-testapp` |

Stencil does not use Vite (its package has no Vite dependency or peer), so there is no Stencil constraint. Storybook's builder (`@storybook/web-components-vite` and `@storybook/builder-vite` 10.6.5) accepts Vite `^5 … ^8`, and the Chromatic packages have no Vite dependency or peer.

### Where it is used

Config files: `apps/boreal-docs/.storybook/main.ts` (Storybook `viteFinal`), `apps/boreal-docs/vitest.config.ts`, `examples/react-testapp/vite.config.ts`, `examples/vue-testapp/vite.config.ts`, `examples/vue-testapp/vitest.config.ts`. The library packages are not built with Vite.

### Breaking changes (Vite 8 migration guide) against this repository

| Change | Impact here |
| --- | --- |
| Rolldown and Oxc replace Rollup and esbuild | All three Vite consumers build; output of the Storybook site grows about 1% (JS 5.91 MB → 5.97 MB, 130 → 140 chunk files) |
| Default build target raised (Chrome 111, Safari 16.4, Firefox 114) | Applies to the Storybook site and the two test apps only |
| `build.rollupOptions` in `.storybook/main.ts` (`onwarn` filter for Stencil's `esm-es5`) | Still accepted: the build passed with the same single warning as before |
| `@vitejs/plugin-react` 6 removes the `babel` option | **Config rewrite needed in `react-testapp`** (below) |
| Missing Rolldown features (`system`/`amd` formats, a few hooks), extglobs, partial TS namespaces | Not used |

### Measured result

A/B inside one worktree, same machine, same commit:

| Build | Vite 7 | Vite 8 |
| --- | --- | --- |
| Storybook (`boreal-docs`) | passes, ~7 s | passes, ~7 s; Vite-built assets +0.8% |
| `react-testapp` (`tsc -b && vite build`) | passes | passes (React Compiler marker present in the bundle) |
| `vue-testapp` (type-check and build) | passes | passes, same size |

### What the upgrade requires

1. **React Compiler setup in `react-testapp`.** `react({ babel: { plugins: [['babel-plugin-react-compiler']] } })` no longer exists in `@vitejs/plugin-react` 6. Replacement (verified): `react()` plus `babel({ presets: [reactCompilerPreset()] })` from the new devDependency `@rolldown/plugin-babel`. `@vitejs/plugin-react` 6.1.2 only accepts `@rolldown/plugin-babel` `^0.1.7 || ^0.2.0`, so use `^0.2.4`; the latest (0.3.0) leaves an unmet peer. The package is pre-1.0 and new to the repository.
2. **Vitest must be 4.1 or later first.** `@vitest/mocker` 4.0.18 (inside the docs' vitest 4.0.18) peers Vite `^6 || ^7`, which Vite 8 violates; 4.1.0 accepts Vite 8. Task 4's vitest 5 upgrade covers this, so it comes first.
3. **Dev-only peer warnings in `vue-testapp`.** `vite-plugin-inspect` 11.3.3, `vite-dev-rpc` 1.1.0 and `vite-hot-client` 2.1.0, pulled in by `vite-plugin-vue-devtools` 8.2.1, still declare Vite `<= 7`. Newer releases of all three accept Vite 8 (12.1.0, 2.0.0, 2.2.0), but the devtools plugin pins the old ones. These warnings clear when `vite-plugin-vue-devtools` updates its dependencies; they do not affect builds.

### Order, effort and gates

1. Vitest family to 5 (Task 4, Track A).
2. `vite`, `@vitejs/plugin-react` and `@rolldown/plugin-babel` together in one change.
- **Effort:** small to medium (about one day): the config rewrite is short; most of the time is verification.
- **Gates:** Storybook build; the Storybook vitest addon run in `boreal-docs` (needs vitest 5 first; not run here); both test-app builds; a dev-server smoke test of each app (not run here); `pnpm validate:all`; `pnpm peers check` (the Vue helper warnings are the only expected exception).
- **Rollback:** revert the lockfile and the `react-testapp` config; nothing in the library packages changes.

### Ticket

Queued for confirmation as item 5 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`.

## 7. Family d4 — TypeScript (Task 7)

**Data date:** 2026-10-30. Measured first-hand in a disposable git worktree of the committed tree (nothing changed in the working branch). Sources: the official TypeScript 7.0 announcement and the package metadata.

### Row and target

| Package | Current | Target | Where declared |
| --- | --- | --- | --- |
| `typescript` | 5.9.3 | 7.0.2 (published 2026-07-08); 6.0.3 is the last JavaScript-based release | `boreal-react` `^5.9.3`, `boreal-vue` `^5.9.3`, `boreal-web-components` `^5.9.3`, `boreal-style-guidelines` `^5.8.2`, `boreal-docs` `~5.9.3`, `react-testapp` `~5.9.3`, `vue-testapp` `~5.9.3` |

### What TypeScript 7 is

- **A native compiler.** The `typescript` package ships platform binaries as optional dependencies; its root export is only a version module. **It ships no JavaScript API**; a new, different API is expected in 7.1. Tools that import the compiler API cannot use it.
- **Compatibility package.** `@typescript/typescript6` re-exports the TypeScript 6.0 API and installs a `tsc6` binary. The announcement recommends `"typescript": "npm:@typescript/typescript6@^6.0.2"` for the tools, plus `"@typescript/native": "npm:typescript@^7.0.2"` where the real `tsc` is wanted. Verified here: `tsc -v` reports 7.0.2, `require('typescript')` resolves to 6.0.2, and `pnpm peers check` is clean.
- **TypeScript 7 follows TypeScript 6's behavior.** Options deprecated in 6.0 become hard errors in 7 (`baseUrl`, `moduleResolution: node`/`node10`, `target: es5`, `downlevelIteration`, `module: amd/umd/system/none`, `esModuleInterop: false`, `alwaysStrict: false`, classic resolution) and defaults change: `strict` is `true`, `types` is `[]`, `rootDir` is the config directory, `module` is `esnext`, `noUncheckedSideEffectImports` is `true`. `tsc` with file arguments in a folder with a `tsconfig.json` needs `--ignoreConfig`.

### Tool compatibility

| Tool | TypeScript range it accepts | Consequence |
| --- | --- | --- |
| `typescript-eslint` 8.58.2 | `>=4.8.4 <6.1.0` | TypeScript 7 is rejected; needs the TypeScript 6 alias |
| `@stencil/eslint-plugin` 1.4.0 | `^4.9.4 \|\| ^5 \|\| ^6` | TypeScript 7 is rejected; needs the alias |
| `vue-tsc` 3.3.13 | `>=5.0.0` | works with the alias |
| `@vitest/eslint-plugin` 1.6.28 | `>=6.0.0` | **TypeScript 6 removes the reason for the hold at 1.6.27 (plan Task 15)** |
| `@stencil/core` 4.45.1 | bundles its own TypeScript **5.8.3** | independent of the workspace version; builds are unchanged |

### Where the build calls `tsc`

Only `boreal-react` and `boreal-vue` (`tsc -p . --outDir ./dist`) and `react-testapp` (`tsc -b && vite build`); `vue-testapp` uses `vue-tsc`; Stencil compiles `boreal-web-components` with its bundled TypeScript.

### Measured results

| Setup | Build (7 tasks) | Lint |
| --- | --- | --- |
| TypeScript 6.0.3 everywhere | fails in `boreal-react` and `boreal-vue` with `TS5011` until each `tsconfig` sets `rootDir`; passes after | docs, React and Vue identical; `boreal-web-components` 5 errors (0 before) and `strict-boolean-conditions` warnings 42 → 22 |
| TypeScript 7.0.2 `tsc` plus the TypeScript 6 alias for tools | passes, 7 of 7 | same as the line above |
| Same, with `strict: false` set in `boreal-web-components` | passes | 2 errors (both `no-unnecessary-type-assertion` in `bds-tree-menu-item.tsx`, lines 337 and 361) and 55 warnings (50 before) |

- **Published output:** the `dist` of `boreal-react` and `boreal-vue` is byte-identical between TypeScript 5.9.3 and 7.0.2 for every common file.
- **`boreal-web-components` `tsc --noEmit`:** 21 errors on TypeScript 5.9.3 today, all in five spec files (`bds-popover.positioning`, `bds-tab-group.events`, `bds-tooltip-events`, `bds-tab.events`, `bds-dialog.behavior`); the same 21 on TypeScript 7 with `strict: false`, so no new type errors. Without `strict: false` there are 151 (mostly strict-null), because TypeScript 6 and later enable `strict` by default; this is also what changes the lint results. No gate runs this check today.

### Configuration changes the upgrade needs

1. `boreal-react` and `boreal-vue` `tsconfig.json`: add `"rootDir": "./lib"` (TypeScript 6 `TS5011`).
2. `boreal-web-components` `tsconfig.json`: remove `baseUrl` (TypeScript 7 `TS5102`) and change the path alias to `"@/*": ["./src/*"]`; set `"strict": false` explicitly to keep today's behavior (enabling strict is a separate piece of work: 151 errors).
3. `boreal-docs` `tsconfig.json`: remove `baseUrl` (and then the `ignoreDeprecations` value). It is already invalid for TypeScript 5.9.3 (`TS5103`: it declares `"6.0"`), and it has two existing `TS6133` unused-variable errors that nothing checks.
4. The root `tsconfig.json` uses `module: commonjs` without `moduleResolution`. Its three children override it with `bundler`, so nothing breaks, but a new project inheriting it unchanged would hit the TypeScript 7 error.
5. Two `no-unnecessary-type-assertion` errors in `bds-tree-menu-item.tsx` to remove (same rule family as plan Task 13).

### Recommended order, effort and gates

1. **Adopt TypeScript 6.0.3 first.** Seven manifests plus the five config changes above. Effort: about one day. Gates: the full build, lint with no errors, `pnpm peers check`, unit tests (Stencil uses its own TypeScript), `pnpm validate:all`. This also lets `@vitest/eslint-plugin` leave its hold.
2. **TypeScript 7 side by side is optional and can wait.** It would change only three small `tsc` calls (the two wrappers and `react-testapp`) while tools stay on the TypeScript 6 API through an alias. The full benefit arrives when TypeScript 7.1 ships its API and `typescript-eslint` supports it. If speed or readiness matters earlier, the verified setup is in the measured results. Effort: about half a day.

### Ticket

Queued for confirmation as item 6 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`.

## 8. Family d5 — Chromatic (Task 8)

**Data date:** 2026-10-30. Measured first-hand in a disposable git worktree of the committed tree (nothing changed in the working branch). Nothing was uploaded to Chromatic.

### Rows and targets

| Package | Current | Target | Where declared |
| --- | --- | --- | --- |
| `chromatic` (CLI) | 15.2.0 | 18.13.6 (published 25 hours before the review, just past the 1-day rule) | `boreal-docs` |
| `@chromatic-com/storybook` (addon) | 4.1.3 | 5.6.0 | `boreal-docs` |

### Where it is used

- **Addon:** registered in `apps/boreal-docs/.storybook/main.ts`; there is no `chromatic.config` file.
- **CLI script** in `apps/boreal-docs/package.json`: `chromatic --exit-zero-on-changes --storybook-build-dir=storybook-static` — the only flags in use.
- **Callers:** root `deploy:docs` (`turbo run build --filter=@pxglobal/boreal-docs... && dotenv -- pnpm --filter @pxglobal/boreal-docs run chromatic`) and `release:publish` (`release:all` then `deploy:docs`). The project token (`CHROMATIC_PROJECT_TOKEN`) comes from the root `.env` through `dotenv`; the deploy runs from the release manager's machine (RELEASING.md), not from a pipeline in this repository.
- **Turborepo:** the build is owned by Turbo and Chromatic only uploads the existing directory, so the team memory about `--force-rebuild` not bypassing the Turbo cache does not apply to this flow.

### Breaking changes

| Release | Change | Impact here |
| --- | --- | --- |
| CLI 16.0.0 | drops Node 18 | none |
| CLI 17.0.0 | drops Node 20 and defines `engines` | none |
| CLI 18.0.0 | the task list renders with a new terminal UI (Clack) | output format of `deploy:docs` changes; nothing in the repository parses it |
| CLI 18.x | engines `node >=22.0.0`; binary is now `dist/bin.cjs` (same command names); new optional peer `@chromatic-com/vitest` | Node floor met (22.23.3); the Jenkins agents must be 22 or later if they ever run it |
| Addon 5.0.0 | requires Storybook 10.1 or later (peer range now `^10.1 … ^10.6 \|\| ^11`) | Storybook 10.6.5 is in range |

### Measured result

| Check | Result |
| --- | --- |
| `pnpm install` with both bumped | clean; `pnpm peers check` clean |
| Storybook build with addon 5.6.0 | passes, ~11 s; the same seven addons are registered (including the Chromatic one); `sb-addons` 1,212 → 1,244 KB; same single warning (chunk size) |
| `chromatic --version` | 18.13.6 |
| Flags in use in `chromatic --help` | `--storybook-build-dir` and `--exit-zero-on-changes` present; `CHROMATIC_PROJECT_TOKEN` still read |

### Not verified (needs the real project token)

An actual upload and snapshot run: that the new CLI authenticates, that the build is accepted, and that `--exit-zero-on-changes` still exits 0 when changes are detected. Publishing a build uses the Chromatic project and its snapshot quota and is outward-facing, so it was not done.

### Order, effort and gates

- No ordering constraint: the CLI and the addon are independent of Vite 8, vitest 5 and TypeScript; the addon only needs the Storybook already installed. Upgrade both together.
- **Effort:** small (under half a day).
- **Gates:** Storybook build; `chromatic --help` shows the flags in use; **one real `pnpm deploy:docs` run by the person who holds the token** (on the upgrade branch or as part of the next release) with the result checked in Chromatic; `pnpm peers check`.
- **Rollback:** revert the two versions in `apps/boreal-docs/package.json` and the lockfile.

### Ticket

Queued for confirmation as item 7 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`.

## 9. Family d6 — utilities (Task 9)

**Data date:** 2026-10-30. Measured first-hand in a disposable git worktree of the committed tree (nothing changed in the working branch).

### Rows and targets

| Package | Current | Target | Where declared | Release age of target |
| --- | --- | --- | --- | --- |
| `lint-staged` | 16.2.7 | 17.6.0 | root `package.json` | 829 h |
| `chalk` | 5.6.2 | 6.0.1 | `scripts-boreal` (dependency) | 808 h |
| `execa` | 9.6.1 | 10.2.1 | `scripts-boreal` (dependency) | 178 h |
| `npm-run-all2` | 8.0.4 | 9.0.4 | `vue-testapp` | 214 h |

### Where each is used

- **`lint-staged`:** `.lintstagedrc.js` (29 lines, ESM default export, function-style commands that run the `lint:fix` and `format` scripts of `boreal-web-components` and `boreal-docs`), invoked by `.husky/pre-commit` as `pnpm lint-staged`.
- **`chalk`:** one file, `scripts-boreal/lib/logger.js` (colour chains only: `blue`, `yellow`, `red`, `green`, `bold.bgBlue`).
- **`execa`:** one file, `scripts-boreal/lib/cmd.js`: `execa(command, args, { cwd, stdio: 'inherit' })` and `execa('pnpm', ['pack', '--json'], { cwd })` reading `stdout`. Both are used by `bin/publish.js`, `bin/boreal-pack.js` and `lib/install.js`, i.e. the `validate:pack` and `dev:pack` pipelines.
- **`npm-run-all2`:** two scripts in `vue-testapp`: `"build": "run-p type-check \"build-only {@}\" --"` and `"lint": "run-s lint:*"`.
- `scripts-boreal` is `"type": "module"` and not a published package, so its Node floor concerns contributors and CI only.

### Breaking changes against this repository

| Package | Breaking change | Impact here |
| --- | --- | --- |
| `lint-staged` 17 | Node `>=22.22.1`; verifies Git `>=2.32.0`; `yaml` becomes an optional dependency | Node met locally; config is JavaScript, so `yaml` is not needed |
| `chalk` 6 | Node `>=22`; numeric `FORCE_COLOR` is an exact level; `ansi256()` downsampled to 16 colours at level 1 | colour chains only; output may differ under `FORCE_COLOR=1` |
| `execa` 10 | Node `>=22`; the subprocess is a plain promise (`.on()`, `.send()` move to `subprocess.nodeChildProcess`); `execaCommand()` removed; the old `stdio: [..., 'ipc']` syntax removed; explicit `input` now wins over an inherited `stdin` | none of these is used by the two calls |
| `npm-run-all2` 9 | ESM only; Node `^22.22.2 \|\| ^24.15 \|\| >=26`; **glob patterns that match no script now succeed silently** | used only through its CLI, so ESM is irrelevant; `lint:*` matches two scripts today |

**ESM/CJS:** `chalk` and `execa` were already ESM-only at 5 and 9 and are imported from ESM files; no CommonJS consumer exists. `npm-run-all2` 9 becomes ESM-only but is called only through `run-p` and `run-s`.

**Combined Node floor: 22.22.2** (set by `npm-run-all2`; the others need 22.22.1 or 22). The local pin (22.23.3) meets it. The root `engines.node` is `>=22` and the README prerequisite says "Node.js 22+", so a contributor on 22.0 to 22.21 would meet `lint-staged` 17 at their next commit. The same floor already appears for `jsdom` 30, `release-it` 21.1.1 and `eslint-plugin-jsdoc` 64 (sections 2, 3 and 5). Confirm the Jenkins agents' Node version too (DevOps question 17).

### Measured result

| Check | Result |
| --- | --- |
| `pnpm install` and `pnpm peers check` with all four bumped | clean |
| Full workspace build (includes the Vue app's `run-p type-check "build-only {@}"`) | 7 of 7 tasks pass |
| `vue-testapp` lint (`run-s lint:*`) | exit 0 |
| `scripts-boreal` specs (`chalk` 6 and `execa` 10 code paths) | 5 files, 38 tests pass |
| `pnpm validate:all` (the real pack pipelines through `execa` and `chalk`) | passes, both pipelines complete, clean tree afterwards |
| `lint-staged` 17 on a staged change that survives formatting | exit 0; backup, `lint:fix`, `format`, restage, cleanup all succeed; the change stays staged |
| `lint-staged` 17 on a no-op change (blank lines only) | "prevented an empty git commit", exit 1: Prettier removes the change, which is the tool's safeguard |
| `lint-staged` 16.2.7 baseline on a staged change that survives formatting (current tree) | exit 0 |

### Order, effort and gates

- No ordering constraint with the other families. Decide the Node floor (section 3) first or together, because all four packages raise it to 22.22.2 and the hook runs on every contributor's machine.
- **Effort:** small (about half a day), mostly the `engines.node` and README prerequisite change.
- **Gates:** `lint-staged` on a real staged change, `pnpm validate:all`, the `scripts-boreal` specs, the Vue app `build` and `lint`, `pnpm peers check`.
- **Rollback:** revert the four version lines and the lockfile.
- **Exit semantics to keep:** `run-s lint:*` must still fail when a lint script fails; with `npm-run-all2` 9 it would also pass silently if both `lint:*` scripts were removed.

### Ticket

Queued for confirmation as item 8 of `ai-work/tickets/EOA-19635-dependency-upgrade-followup-tickets.md`.
