# Dependency upgrade follow-up tickets from EOA-19635 (drafts, not in Jira)

Local drafts produced by the major-update planning (`ai-work/research/2026-10-27-EOA-19635-major-updates.md`). Create a Jira ticket from one only when someone picks it up, then record its ID in the plan EOA-19635 row named in each heading. Suggested project: EOA, type: Task. Items 9 to 14 were added on 2026-10-30 when plan tasks 13 to 22 were re-scoped. Runtime upgrades (Node, pnpm) stay in `EOA-18749-release-process-followup-tickets.md` items 2 and 3.

**Update 2026-11-13:** 13 of the 14 drafts were executed in EOA-20193 (`ai-work/plans/EOA-20193-dependency-upgrades-followup.md`): 11 complete and 2 with a remainder (draft 6: TypeScript 7 not adopted; draft 9: the React half was dropped). Draft 2 was deferred. New follow-ups found along the way are drafted in `EOA-20193-follow-up-tickets.md`.

## 1. Upgrade the Vitest stack to 5 and jsdom to 30 (from Task 4)

**Status 2026-11-13:** done in EOA-20193 T10 (commit `80cc113a`, jsdom 30.1.3 and Vitest 5.1.0; squashed on merge).

**Summary:** Upgrade `vitest`, `@vitest/browser-playwright`, `@vitest/coverage-v8`, `@vitest/ui`, `jsdom` and `@types/jsdom`

**Description:** Move `vitest` 4.0.18 / 4.1.0 to 5.0.5 in `boreal-docs`, `boreal-style-guidelines`, `scripts-boreal` and `vue-testapp`, together with `@vitest/browser-playwright`, `@vitest/coverage-v8` and `@vitest/ui` (vitest 5 pins them to the same version). Then `jsdom` 28.1.0 → 30.1.3 and `@types/jsdom` 28 → 30 in `vue-testapp`.
- Vitest 5 breaking changes (`clearMocks` on by default, `test.workspace` → `test.projects`, `browser.api` → top-level `api`) do not apply to this repository today: no `vi.fn`, `vi.mock` or `vi.spyOn`, no `workspace`, no `browser.api`.
- Storybook's vitest addon 10.6.5 accepts vitest 4 or 5; vitest 5 accepts Vite 6.4 to 8, so this does not wait for the Vite 8 upgrade.
- `jsdom` 30 needs Node `^22.22.2 || ^24.15 || >=26`; confirm the Jenkins agents' Node version first.

**Acceptance criteria:**
- All four `vitest` packages resolve to the same 5.x version in every workspace.
- Lint, the spec files of `boreal-style-guidelines` and `scripts-boreal`, the Storybook build, the Storybook vitest addon run and `pnpm validate:all` pass.
- `jsdom` is upgraded only after the CI Node version is confirmed.
- Effort: small.

## 2. Migrate the Stencil unit tests from the built-in runner to `@stencil/vitest` (from Tasks 4 and 21)

**Status 2026-11-13:** deferred 2026-11-13 by the user (EOA-20193 T15 to T17): the spike and three measured routes are written up; see draft 8 in `EOA-20193-follow-up-tickets.md`.

**Summary:** Replace Stencil's deprecated built-in Jest/Puppeteer test runner with `@stencil/vitest`

**Description:** Stencil's built-in runner is deprecated since 4.43 and will be removed in Stencil 5; it does not support Jest 30 on Stencil 4, so `jest`, `jest-cli`, `@types/jest` and `puppeteer` cannot be upgraded in place. `@stencil/vitest` 1.16.1 accepts `@stencil/core ^4 || ^5` and `vitest ^2` to `^5`.
- Scope in `boreal-web-components`: 374 spec files, 337 using `newSpecPage` (2,756 call sites), 335 importing from `@stencil/core/testing`, 197 using Jest APIs (1,286 uses). Stencil's guide maps `newSpecPage` to `render`, moves `testing` options to a `vitest.config.ts`, and lets spec tests keep the mock DOM or use jsdom or happy-dom.
- `puppeteer` is used only by `stencil test --e2e` and the package has no e2e specs; the migration removes it and its Chrome download.
- Re-verify the 80% coverage thresholds and the per-component Stryker mutation setup on the new runner.
- Evaluate a codemod before starting.

**Acceptance criteria:**
- All spec files pass on `@stencil/vitest` with the same or better coverage; `jest`, `jest-cli`, `@types/jest` and `puppeteer` are removed.
- `pnpm validate:all` and the mutation score on a sample component are unchanged.
- The standards document and `CONTRIBUTING.md` describe the new test commands.
- Effort: large; schedule before Stencil 5.

## 3. Plan and upgrade `@colordx/core` 5 → 7 (from Task 4 reconciliation)

**Status 2026-11-13:** done in EOA-20193 T14 (commit `a02d0704`, `@colordx/core` 7.3.0; 110 characterization tests; an invalid-color guard was needed).

**Summary:** Upgrade the color library used by `bds-color-picker`

**Description:** `@colordx/core` 5.6.0 → 7.3.0 (two majors) is a runtime `dependency` of `boreal-web-components`, so it ships to consumers. Read both changelogs, list the `bds-color-picker` and related usage, and check that color parsing, formatting and alpha handling stay identical.

**Acceptance criteria:**
- Breaking changes and the affected components are listed.
- Color conversion behavior is covered by unit tests before and after the upgrade.
- Lint, unit tests with coverage, builds and `pnpm validate:all` pass.
- Effort: to be estimated after reading the changelogs.

## 4. Upgrade ESLint to 10 with its companions (from Task 5)

**Status 2026-11-13:** done in EOA-20193 T4 (commit `3979e79a`, ESLint 10; the `eslint-plugin-react` peer is handled with an `overrides` `:peer` entry since pnpm 12).

**Summary:** Upgrade `eslint` and `@eslint/js` to 10, plus `globals` 17 and `eslint-plugin-jsdoc` 65

**Description:** Move `eslint` 9.39.x to 10.13.0 and `@eslint/js` to 10.0.1 in `boreal-docs`, `boreal-web-components`, `react-testapp` and `vue-testapp`. A trial in a disposable worktree showed identical lint results in all four workspaces (0 errors; 9, 50, 0 and 0 warnings) and 0 findings from the three rules added to `eslint:recommended`.
- `@stencil/eslint-plugin` 1.4.0 loads its optional peer `eslint-plugin-react` unconditionally, and `eslint-plugin-react` 7.37.5 does not declare ESLint 10 support. Verified workaround: declare `eslint-plugin-react@7.37.5` as an explicit devDependency of `boreal-web-components` (pnpm prints an unmet-peer warning; decide whether to add a `peerDependencyRules` entry).
- Also move `globals` in `react-testapp` to 17.13.0 and, once the CI Node version is at least 22.22.2, `eslint-plugin-jsdoc` to 65.4.2.

**Acceptance criteria:**
- Lint passes in all four workspaces with the same error and warning counts.
- `pnpm peers check` is clean or the exception is documented.
- `pnpm validate:all` passes.
- Effort: small.

## 5. Upgrade Vite to 8 with its React plugin (from Task 6)

**Status 2026-11-13:** done in EOA-20193 T11 (commit `30cfc14c`, Vite 8.3.8 and `@vitejs/plugin-react` 6.3.0, React Compiler kept through `@rolldown/plugin-babel`).

**Summary:** Upgrade `vite` to 8, `@vitejs/plugin-react` to 6 and replace the removed Babel option

**Description:** Move `vite` 7.3.1 to 8.3.5 in `boreal-docs`, `react-testapp` and `vue-testapp`, and `@vitejs/plugin-react` 5.1.4 to 6.1.2. A trial in a disposable worktree built Storybook and both test apps on Vite 8; the Storybook output grows about 1%.
- Do the vitest 5 upgrade first (draft 1): `@vitest/mocker` 4.0.18 does not accept Vite 8.
- `@vitejs/plugin-react` 6 removes the `babel` option. In `react-testapp`, replace it with `react()` plus `babel({ presets: [reactCompilerPreset()] })` from the new devDependency `@rolldown/plugin-babel@^0.2.4` (0.3.0 is not accepted by plugin-react 6.1.2; the package is pre-1.0).
- Expect dev-only peer warnings in `vue-testapp` from `vite-plugin-vue-devtools`' older helper packages until it updates.

**Acceptance criteria:**
- The Storybook build, both test-app builds and `pnpm validate:all` pass; a dev-server smoke test of each app works; the Storybook vitest addon run passes.
- The React Compiler is still applied in `react-testapp`.
- `pnpm peers check` is clean except for the documented Vue helper warnings.
- Effort: small to medium.

## 6. Upgrade TypeScript to 6.0.3, then to 7 side by side (from Task 7)

**Status 2026-11-13:** partly done: TypeScript 6.0.3 in EOA-20193 T8 (commit `553f3be5`); TypeScript 7 (7.0.2) is NOT adopted and stays a hold until Stencil's bundled compiler and `typescript-eslint` support it.

**Summary:** Move the workspaces from TypeScript 5.9.3 to 6.0.3 and prepare TypeScript 7

**Description:** TypeScript 7.0.2 ships no JavaScript API (7.1 is expected to), so the plan is two steps:
1. Move all seven workspaces to TypeScript 6.0.3. A trial in a disposable worktree needs these config changes: `rootDir: "./lib"` in the `boreal-react` and `boreal-vue` tsconfigs (`TS5011`); remove `baseUrl` from the `boreal-web-components` and `boreal-docs` tsconfigs and change the web-components alias to `"@/*": ["./src/*"]`; set `strict: false` explicitly in `boreal-web-components` (TypeScript 6 and 7 turn strict on by default; without it there are 151 errors and different lint results); remove two unnecessary type assertions in `bds-tree-menu-item.tsx`.
2. Optionally adopt TypeScript 7.0.2 for the three `tsc` calls using the documented side-by-side aliases (`typescript` → `@typescript/typescript6`, `@typescript/native` → `typescript@^7.0.2`); verified to build and to produce byte-identical wrapper output. Full adoption waits for TypeScript 7.1's API and `typescript-eslint` support.
- `@vitest/eslint-plugin` can leave its hold at 1.6.27 once TypeScript 6 is in (its 1.6.28 requires `>=6.0.0`).

**Acceptance criteria:**
- Build, lint (no errors), `pnpm peers check`, unit tests and `pnpm validate:all` pass on TypeScript 6.0.3.
- Published `dist` of `boreal-react` and `boreal-vue` is unchanged.
- The `docs` and `web-components` tsconfigs no longer use `baseUrl`.
- Effort: about one day for step 1; about half a day for step 2.

## 7. Upgrade the Chromatic CLI to 18 and the Storybook addon to 5 (from Task 8)

**Status 2026-11-13:** committed in EOA-20193 T18 (commit `5385a955`, Chromatic 18.14.3 and addon 5.6.0, Storybook refreshed to 10.6.7); the real `pnpm deploy:docs` was run by the token holder on 2026-11-13 and reported successful.

**Summary:** Upgrade `chromatic` 15.2.0 to 18.13.6 and `@chromatic-com/storybook` 4.1.3 to 5.6.0

**Description:** Both live in `boreal-docs`. A trial in a disposable worktree installed both cleanly, built Storybook with the new addon (same addons registered, same single warning) and confirmed that the two CLI flags in use (`--storybook-build-dir`, `--exit-zero-on-changes`) and `CHROMATIC_PROJECT_TOKEN` still exist.
- CLI 16 and 17 drop Node 18 and 20; CLI 18 needs Node 22 or later and renders its progress with a new terminal UI.
- Addon 5 requires Storybook 10.1 or later (10.6.5 installed).
- Not verified: a real upload. The person holding `CHROMATIC_PROJECT_TOKEN` should run `pnpm deploy:docs` once after the upgrade and check the build in Chromatic, including that `--exit-zero-on-changes` still exits 0 when visual changes are detected.

**Acceptance criteria:**
- Storybook builds with the new addon and `pnpm peers check` is clean.
- One real `pnpm deploy:docs` publishes a build to Chromatic and exits as before.
- Effort: small.

## 8. Upgrade the build and hook utilities: lint-staged 17, chalk 6, execa 10, npm-run-all2 9 (from Task 9)

**Status 2026-11-13:** done in EOA-20193 T19 (commits `407b593d`, `6205af1a`; the root `engines.node` is now `^22.22.2 || ^24.15.0 || >=26.0.0`).

**Summary:** Upgrade `lint-staged`, `chalk`, `execa` and `npm-run-all2` to their latest majors and raise the documented Node floor

**Description:** `lint-staged` 16.2.7 to 17.6.0 (root), `chalk` 5.6.2 to 6.0.1 and `execa` 9.6.1 to 10.2.1 (`scripts-boreal`), `npm-run-all2` 8.0.4 to 9.0.4 (`vue-testapp`). A trial in a disposable worktree installed all four cleanly and passed the full build, the Vue app lint, the 38 `scripts-boreal` specs, `pnpm validate:all` and a real `lint-staged` run. None of the breaking changes touches the two `execa` calls, the colour chains or the two `npm-run-all2` scripts.
- All four raise the Node floor; the highest is `npm-run-all2` 9 at `^22.22.2 || ^24.15 || >=26`. The hook runs on every contributor's machine, so raise `engines.node` (now `>=22`) and the README prerequisite (now "22+") in the same change, and confirm the Jenkins agents' Node version.
- `npm-run-all2` 9: a glob that matches no script now succeeds silently; keep `lint:*` matching real scripts.

**Acceptance criteria:**
- `lint-staged` runs successfully on a real staged change; `pnpm validate:all`, the `scripts-boreal` specs, the Vue app `build` and `lint`, and `pnpm peers check` pass.
- `engines.node` and the README prerequisite state the new floor.
- Effort: small.

## 9. Add automated wrapper tests for Vue and React (from Task 20)

**Status 2026-11-13:** partly done in EOA-20193 T7, T7b and T7c (commits `3b9d5ba0`, `1c0c4f0e`, `bb6a708b`): the Vue half was built and found the `bds-toggle` `v-model` defect; the React half was dropped by decision.

**Summary:** Add automated tests for the `boreal-vue` and `boreal-react` wrappers in their test apps

**Description:** The wrapper packages have placeholder `test` scripts, so each bump to a wrapper runtime library (`@stencil/vue-output-target`, `@stencil/react-output-target`) relies on manual checks. `vue-testapp` already has `vitest`, `jsdom`, `@vue/test-utils` and a jsdom `vitest.config.ts`, with no test files.
- Spike first: confirm that the real Stencil components render and emit events inside jsdom. If they do not, use a stub custom element that sets its own host class.
- Vue: `componentModels` in `packages/boreal-web-components/targets/vue-output-target.ts` is a manual list, and a forgotten entry fails silently. React has no equivalent list.
- Motivation: `@stencil/vue-output-target` 0.13.1 to 0.14.7 rewrote the class-merging code and left the `v-model` path untouched.

**Acceptance criteria:**
- Vue: a data-driven test reads `custom-elements.json` and fails when a component with a model prop and model event has no `componentModels` entry; a class-merging test; a `v-model` smoke test.
- React (dropped if React is judged not worth the new tooling): every custom event is exposed as an `on<Event>` prop; a `className` test; an event smoke test.
- The root `pnpm test` runs the new tests and they pass. No inline comments and no ticket IDs in test names.
- Effort: medium; the spike decides the size.

## 10. Understand the Stencil 4.45.2 boolean-attribute change and remove the 4.45.1 pin (from Task 14)

**Status 2026-11-13:** done in EOA-20193 T5 (commit `44c50357`, `@stencil/core` `^4.45.2`; the behavior change is documented in the PR description).

**Summary:** Find out why `multiple="false"` and `error="false"` parse as `true` on form-associated components in Stencil 4.45.2

**Description:** With `@stencil/core` 4.45.2, three `bds-file-picker` tests fail because a string attribute `"false"` is parsed as `true`; 4.45.0 and 4.45.1 pass all 178 file-picker tests. Checked in Chromium on 4.45.1: `"false"` gives `false`. Today `@stencil/core` is pinned to exactly 4.45.1.
- Decide in a real browser what 4.45.2 does, since the unit tests run on the mock DOM.
- List the other form-associated components (those using `formAssociatedMixin`) with boolean props and check which tests pass `"false"` as an attribute.
- Use a live `<form>` check; unit tests cannot see form-associated behavior.
- `packages/boreal-vue` resolves `@stencil/core@4.45.2` as an inert peer of `@stencil/vue-output-target`; confirm when the pin is removed.

**Acceptance criteria:**
- The difference is understood and either fixed in the components, accepted with a migration note, or reported upstream.
- The exact pin becomes a caret range; the unit suite, build and `pnpm validate:all` pass.
- Effort: small to medium.

## 11. Resolve the `@tanstack/virtual-core` 3.19.6+ failures in `bds-search-bar` (from Task 16)

**Status 2026-11-13:** done in EOA-20193 T13 (commit `0f403dd0`; root cause was the test mock, range widened to `>=3.17.1 <3.20.0`, verified in Chromium and WebKit).

**Summary:** Find the cause of 24 `bds-search-bar` items-mode failures with `@tanstack/virtual-core` 3.19.6 and later, and decide the published range

**Description:** A bisect over every stable release from 3.17.1 to 3.19.8 showed 3.19.5 passing all 305 `bds-search-bar` tests and 3.19.6 failing 24, all in items mode (windowed suggestions). The range is capped at `>=3.17.1 <3.19.6`. `virtual-core` is a published runtime dependency declared as `^3.17.1`, so consumers resolve the newest 3.x whatever this repository does.
- Check `bds-table` against 3.19.6 and later too: `src/utils/dom/virtualWindow/virtual-window.ts` and `bds-table.tsx` use it.
- Decide whether the failure is real in a browser or only in the mock DOM (`utils/testing/mocks/layout.ts`).

**Acceptance criteria:**
- The cause is documented.
- The published range is kept capped with the reason recorded, or widened after a source or test fix.
- `bds-search-bar` specs pass at the newest allowed version and a live-browser check of the items-mode list passes.
- Effort: medium; this needs the user's decision on the published range.

## 12. Add a `./components` export and lift the `@stencil/react-output-target` hold (from Task 18)

**Status 2026-11-13:** done in EOA-20193 T12 (commits `2a67a532`, `d375d88f`; `@stencil/react-output-target` `^1.8.1`).

**Summary:** Export `./components` from `boreal-web-components` so `@stencil/react-output-target` 1.5.0 and later can be used

**Description:** From 1.5.0, `@stencil/react-output-target` generates `import type { Components }` (or `{ JSX }` in 1.5.1) from `@pxglobal/boreal-web-components/components`. The `exports` map has `./components/*.js` but no bare `./components`, so `tsc` in `boreal-react` fails with TS2307. The package is held at exactly 1.4.2. This changes the published package surface, so it needs the user's decision.
- Call site: `packages/boreal-web-components/targets/react-output-target.ts`. Check the Vue output target too.
- `components-build/index.d.ts` is the likely type target; confirm it is published and resolves from a consumer install, using the pack-based pipeline.

**Acceptance criteria:**
- `exports["./components"]` resolves its types from a packed tarball in the React and Vue test apps.
- `@stencil/react-output-target` moves to the newest version past the 1-day delay, as a range.
- `pnpm validate:all` passes.
- Effort: small to medium.

## 13. Clear the `typescript-eslint` 8.59+ type-assertion errors (from Task 13)

**Status 2026-11-13:** done in EOA-20193 T9 (commit `ca1dbe57`, `typescript-eslint` 8.72.2).

**Summary:** Remove or justify 38 unnecessary type assertions and lift the `~8.58.2` cap on `typescript-eslint`

**Description:** `typescript-eslint` 8.59.0 is the first version that raises 38 `@typescript-eslint/no-unnecessary-type-assertion` errors in 17 web-components files; 8.58.2 lints clean. Re-run the bisect at execution time. Check each flagged assertion, for example `(this.el as HTMLElement)` in `bds-text-field.tsx`, before removing it: it may be needed for another TypeScript version or for Stencil's JSX typing. If the TypeScript 6 upgrade (item 6) happens first, redo the count.

**Acceptance criteria:**
- Every flagged assertion is removed or justified, with no behavior change.
- The three `~8.58.2` caps become caret ranges.
- `pnpm lint` exits 0 and the web-components unit suite passes.
- Effort: small.

## 14. Update prettier to 3.9 and reformat the files it changes (from Task 19)

**Status 2026-11-13:** done in EOA-20193 T3 (commits `f9b1c273`, `f3b9400a`; Prettier 3.9.10 and the reformat).

**Summary:** Move the four `prettier` pins to 3.9.x with one formatting-only commit

**Description:** `format:check` passes at 3.8.0 and 3.8.1 and flags 2 + 14 files at 3.9.10 (`react-testapp` is not affected). `lint-staged` runs the `format` script on staged files, so these files would otherwise be reformatted in unrelated PRs. Docs pin prettier exactly at 3.8.1.

**Acceptance criteria:**
- All four `prettier` pins move to the same version older than the 1-day delay.
- The flagged files are reformatted in a commit that contains formatting changes only.
- Every `format:check` script passes.
- Effort: small.
