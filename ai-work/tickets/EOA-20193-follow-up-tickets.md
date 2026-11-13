# Follow-up tickets from EOA-20193 (drafts, not in Jira)

Local drafts collected while executing `ai-work/plans/EOA-20193-dependency-upgrades-followup.md` (T21, item 5, decided 2026-11-13). Nothing here exists in Jira. Create a ticket from one only when someone picks it up, then record its ID in the plan. Evidence sits in the plan task named in each draft and, for the test runner, in `ai-work/research/2026-11-13-EOA-20193-stencil-vitest-migration-spike.md`.

Suggested priority is a first guess for triage, not a decision.

## 1. Fix focus loss when tabbing through a virtualized, selectable `bds-table` (from T13)

**Summary:** With `virtual` and `selectable`, Tab through the row checkboxes drops focus to `<body>` when the rendered window shifts

**Description:** In the Storybook story `data-visualization-table--with-virtualization` (5,000 rows, `max-height` 400 px, `virtual`), with `selectable` set from the console, Tab moves row by row (rows 1 to 14), then focus falls to `<body>` at row index 15, when the rendered window moves from rows 0 to 25 to rows 2 to 29. The next Tab restarts from the start of the page. The focused row is unmounted by the window and focus is not restored. A comparison build with `@tanstack/virtual-core` 3.17.1 (the `.worktrees/origin-feature-EOA-19856_tech-debt-V5` dist) produced the identical Tab sequence, so it is not caused by the virtual-core range change of EOA-20193 T13.

**Acceptance criteria:**
- Tabbing through at least 40 rows of a 5,000-row virtualized selectable table never loses focus; the focused row stays mounted (or focus moves to the next focusable row) while the window shifts.
- A unit or story-level test reproduces the focus loss before the fix.
- Checked in Chromium and WebKit.
- Effort: medium. Priority: high (keyboard accessibility defect).

## 2. Make keyboard End/Home and wheel scrolling reach the true edges of a virtualized `bds-table` (from T13)

**Summary:** On a virtualized table, End and Home on the scroll wrapper stop short of the real edges, and wheel scrolling drifts by a few pixels

**Description:** On the same story, End leaves the table about 917 px above the bottom (`scrollTop` 240,393 of 241,696) and Home lands at 350 to 540 instead of 0. `scrollHeight` grows while rows are measured (about 55 px real height against a 48 px estimate), so the target position computed from the first estimate is wrong. Wheel scrolling does reach the true start and end. Wheel steps also drift slightly (+5,000 px gives 6,384 against 6,300 expected). The 3.17.1 comparison build gave the same numbers (End 240,407 of 241,724, Home 539; +5,000 gives 6,391). Note also that `bds-table` has no ArrowDown row navigation (the wrapper scrolls natively).

**Acceptance criteria:**
- End and Home reach the real bottom and top of the table after at most one extra frame.
- The row height estimate matches the measured height for the default density, or the scroll target is corrected after measurement.
- A story test covers End and Home on a 5,000-row table.
- Effort: medium. Priority: medium.

## 3. Intermittent unhandled rejection in the `bds-date-picker` stories during the Storybook addon run (from T21 item 3)

**Summary:** `Error: [AnchoredMixin.show]: triggerSlot is required` is raised after the "Interactive Range Form Example" story test in about half of the Storybook vitest addon runs

**Description:** With `react` and `react-dom` declared in the docs app (T21 item 3), `pnpm exec vitest run --project storybook` in `apps/boreal-docs` passes 48 files and 606 tests in about 11 seconds. In 2 of 4 runs (and once in an earlier trial) the run still exits 1 because Vitest reports an unhandled rejection from `src/stories/forms/bds-date-picker/bds-date-picker.stories.ts`: `AnchoredMixin.show: triggerSlot is required`, raised from `openPopover` of `bds-popover` (stack: `onBeforeShow`, `show`, `openPopover`). One run reported two such errors. Hypotheses, none checked: the story or the date picker calls `openPopover` before the trigger slot has rendered, or a teardown race after the test ends. This blocks wiring the addon run into a gate (the docs app has no `test` script).

**Acceptance criteria:**
- Ten consecutive addon runs exit 0 with no unhandled errors.
- The cause is documented (story timing, component or mixin guard).
- A `test` script for the docs app and its place in the gates are decided.
- Effort: small to medium. Priority: medium.

## 4. `bds-color-picker` HEX field: invalid text stays after blur (from T14)

**Summary:** Typed invalid text (`zzz`, `#12`, empty) is rejected without changing the value, but it stays in the HEX field after blur

**Description:** From `#123456`, typing `zzz` shows `#zzz`, `#12` shows `#12`, and an empty value shows `#`; after Enter and Tab the value stays `#123456` and no event is emitted, but the field keeps the invalid text instead of snapping back. `handleHexBlur` in `bds-color-picker.tsx` is meant to reset the draft (`if (!isValidColorValue(this.hexDraft)) this.hexDraft = toHexString(this.hsva)`) but never visibly ran. The QA agent's unverified hypothesis: it is attached through `onBdsBlur`, and a capture listener on the host (`handleInternalBlur`) stops `bdsBlur` from non-host targets. Found in Storybook (Chromium) and not compared with an older build.

**Acceptance criteria:**
- After blur the HEX field shows the last valid value (or an explicit invalid state) for every invalid input.
- A spec covers the blur path.
- Effort: small. Priority: medium.

## 5. `bds-color-picker`: product decisions on 8-digit HEX input, invalid preset colors and HSL rounding (from T14)

**Summary:** Decide the intended behavior of three details of the color picker, then document or fix them

**Description:** (a) The HEX input has `maxlength=7`, so `#ff000080` cannot be typed; alpha has its own field, and an 8-digit value is accepted as the initial `value` (alpha shown as 50%). (b) Clicking a preset swatch whose entry is invalid (`not a color`, empty) sets the color to `#000000` (`parseColor` falls back to the default) instead of being ignored; the swatch itself renders as an empty checkerboard. The contrast helper no longer throws for such entries after EOA-20193 T14. (c) The HSL fields can differ from the HSL of the displayed hex by up to about 2% (for example `#E5CFCF` is HSL 0°/29.73%/85.49% but the picker shows 31%/86%) because the picker derives HSL from its unrounded HSV state; the maximum difference between `detail.hsl` and the HSV-to-HSL formula is 0.005. All three predate the `@colordx/core` upgrade.

**Acceptance criteria:**
- Each of the three has a recorded decision (keep, change, or document).
- Changes are covered by specs and by a note in the component documentation.
- Effort: small. Priority: low.

## 6. Add unit tests for the six `boreal-style-guidelines` generator files (from T10 and T21 item 3)

**Summary:** `css-generator`, `scss-generator`, `global-generator`, `generate`, `validate` and `constants` are at 0% coverage

**Description:** `pnpm --filter @pxglobal/boreal-style-guidelines test:coverage` fails its 80% thresholds (28% statements, 31.21% branches, 34.78% functions, 28.53% lines) because only `token-processor.ts` has tests (76.77% statements). The generators run on every `pnpm build` (`generate` and `validate` are build steps), so they are exercised but not measured. The numbers are identical on Vitest 4.0.18, so this predates the Vitest 5 upgrade. Nothing in the gates runs `test:coverage` today.

**Acceptance criteria:**
- Each generator has tests for its output and its failure paths.
- `test:coverage` passes at the existing 80% thresholds and is added to the standard gates.
- Effort: medium. Priority: low to medium.

## 7. Guard the published type declarations in the pack pipeline (from T21 item 4)

**Summary:** Fail the pack validation when the packed `@pxglobal/boreal-web-components` types do not pass a strict consumer type check

**Description:** EOA-20193 T21 item 4 fixed 14 errors that a consumer with `skipLibCheck: false` saw on the packed package (an unresolved `KEYBOARD`, `@/` aliases kept in `export ... from` re-exports, and test helper declarations pulled in through the `@/utils` barrel). Nothing prevents them from coming back: the test apps use `skipLibCheck: true`. Add a step to `validate:pack` (or a dedicated script in `scripts-boreal`) that installs the packed tarball with its dependencies in a scratch project and runs `tsc` with `skipLibCheck: false` on `import type { Components, JSX } from '@pxglobal/boreal-web-components'`, and also fails on any `'@/` specifier left in `dist/types` outside comments. Also decide whether to stop the `@/utils` barrel from re-exporting `./testing` (325 spec files import test helpers through it, so it needs a codemod).

**Acceptance criteria:**
- The check passes on the current package and fails when one of the three problems is reintroduced (verified once by hand).
- It runs as part of `pnpm validate:all`.
- Effort: small to medium. Priority: medium.

## 8. Migrate the web-components specs from Stencil's built-in runner to `@stencil/vitest` (from T15 to T17)

**Summary:** Replace Stencil's deprecated runner and remove `jest`, `jest-cli`, `@types/jest` and `puppeteer`

**Description:** Deferred on 2026-11-13. Stencil's runner is deprecated since 4.43 and removed in Stencil 5; Jest 30 is not supported on Stencil 4, so the four packages stay on their current versions (19 of the 75 findings of a full `pnpm audit` go through the Jest and Puppeteer chains; every test run prints the deprecation notice). Scope: 377 spec files, 331 using `newSpecPage` (2,752 call sites), options in use only `components` and `html`. Three routes were measured (full numbers, working configurations and the open decisions are in the research note): keep `newSpecPage` under Vitest 5 with a local transform plugin (352 of 377 files green, 97.1% of tests, about 1 to 2 days); convert to `render()` with the plugin in source mode (coverage preserved, about 6 to 9 days by a rough estimate); convert to `render()` on the documented dist route (works only with a dedicated test build config, no usable coverage). `newSpecPage` is still shipped in `@stencil/core` `5.0.0-rc.1`. Open decisions: which route, whether to own the ~55-line plugin fork until Stencil 5, v8 coverage or `@vitest/coverage-istanbul`, mock-doc as the DOM environment, and removing the unused `jest-junit` reporter line.

**Acceptance criteria:**
- All spec files pass on the chosen runner with equal or better coverage; `jest`, `jest-cli`, `@types/jest` and `puppeteer` are removed.
- `.husky/pre-push`, `turbo.json` inputs, the Stryker skill and templates, the test commands in `CONTRIBUTING.md` and the agent and skill files that name the runner are updated.
- The per-component mutation score on a sample component is unchanged.
- Effort: large. Priority: medium (blocks the Stencil 5 upgrade).

## 9. Upgrade Stencil to 5 (from T15)

**Summary:** Move `@stencil/core` from 4.45.x to 5 once it is released, and align the output targets

**Description:** `5.0.0-rc.0` and `5.0.0-rc.1` were published on 2026-11-12; there is no official release date (the support policy page lists v5 as preview, TBD). Stencil 5 removes the built-in test runner (see the ticket above), requires Node 22 or newer (met), and is expected to fix the `stencilVitestPlugin` failure on `extends Mixin(...)` components. Re-check `@stencil/react-output-target`, `@stencil/vue-output-target` (0.14.7; the `modelvalue` attribute leak was still present in 0.15.0), the Sass plugin, the generated component declarations and the `./components` export added in EOA-20193 T12.

**Acceptance criteria:**
- Build, lint, unit tests, coverage, the Storybook build and `pnpm validate:all` pass on Stencil 5.
- A real-browser check of a sample of components in the Storybook and in the React and Vue pack apps.
- Effort: large. Priority: medium. Depends on the previous ticket.

## 10. Add the dependency report script for the scheduled Jenkins stage (from T6b)

**Summary:** Add `pnpm deps:report`, a script that prints the outdated and production audit counts and exits non-zero only on unresolved high or critical production findings

**Description:** Deferred on 2026-11-11 (the Jenkins job does not exist, has no owner and no DevOps agreement). Build it only when DevOps confirms that a scheduled stage will call it; the Jenkins side (policy Phase 2) and the Renovate evaluation are drafted in `EOA-18749-release-process-followup-tickets.md`, draft 7. Design agreed in the T6 review:
- Three exit states: 0 clean, 1 high or critical production findings, 2 the check could not run or its output could not be parsed (registry unreachable, empty output, unexpected shape). A plain 0/1 would read a failed check as "no findings".
- Read counts from `metadata.vulnerabilities` of `pnpm audit --prod --json`; a result without that block is state 2. Capture real output as fixtures and add one test that pins the shape, so a pnpm upgrade fails loudly instead of reporting zero. pnpm 12 is now the pinned version (EOA-20193 T20): capture the fixtures from it, not from pnpm 11.
- `pnpm outdated -r` exits non-zero when anything is outdated and `pnpm audit` exits non-zero when it finds vulnerabilities: both are data, not script failure.
- `Cmd.run` in `scripts-boreal/lib/cmd.js` uses `stdio: 'inherit'` and rethrows on a non-zero exit, so extend `Cmd` first with a method that captures stdout and the exit code without rejecting; reuse `Logger`. No parallel implementation.
- Report production and dev outdated entries separately (`pnpm outdated -r --format json` is an object keyed by package name); count only production findings for the audit.
- Files: `scripts-boreal/bin/deps-report.js`, `scripts-boreal/lib/deps-report.js` (pure parsing functions), `scripts-boreal/lib/__tests__/deps-report.spec.js`, a root `deps:report` script, and the `scripts-boreal/README.md`.

**Acceptance criteria:**
- `pnpm deps:report` prints the outdated counts (major, minor, patch) and the production audit counts (critical, high, moderate, low); with nothing outdated and no findings it prints zero counts and exits 0.
- Parsing is covered by unit tests with fixture JSON and no network, including empty input and malformed JSON, at the 80% gate.
- The README lists the steps DevOps needs to run it monthly from Jenkins.
- Effort: small. Priority: low until the Jenkins stage is confirmed.

## 11. Sync the Confluence template page after the EOA-20193 merges (from T23)

**Summary:** Update the page "Monthly Dependency Maintenance Ticket Template" (space SENG, page 2469101953, version 1 of 2026-10-30) to match the local template

**Description:** The local template `ai-docs/templates/dependency-maintenance-ticket.md` was updated on 2026-11-13; the Confluence page was deliberately left until both pull requests are merged, so that it does not describe holds and gates that exist only on a branch. Changes to carry over: the new hold register (8 rows, with the tracked `:peer` overrides and the accepted `minimatch` production finding) in place of the six baseline holds, the pnpm 12 wording in the snapshot table and the runtime review, the check of the committed lockfile after each commit, the note that `release-it --dry-run` prints but does not run hooks, and the line about gates that cannot run in CI. Re-check the register against the merged state before publishing. It is an outward-facing change: show the diff to the owner before updating. A Jira ticket is optional; it can be done as a plain documentation task.

**Acceptance criteria:**
- The page matches the local template; no six-hold seed list and no "11 line" wording remain.
- The page history keeps version 1.
- Effort: small. Priority: low, after the merges.
