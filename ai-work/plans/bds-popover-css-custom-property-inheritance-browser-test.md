---
ticket: —
component: bds-popover
status: pending
created: 2026-09-03
---

# `bds-popover` CSS custom-property-inheritance browser regression test

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Add a durable, browser-driven regression test that protects the nested-popover CSS custom-property-inheritance fixes discovered in `EOA-17138-bds-date-picker-v2.md` (Task 4 and its 2026-08-26 follow-up) — a bug class `newSpecPage`'s JSDOM environment cannot catch, since it never computes real cascaded/inherited CSS custom-property values.

**Origin:** Discovered as Task 8c of [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md) during that plan's Task 4 follow-up (nested-`bds-select`-popover padding-leak bug — a value set via a light-DOM custom property kept carrying down through the tree regardless of which selector originally set it). `bds-popover` is shared infrastructure (`bds-select`, `bds-dropdown`, and `bds-date-picker` all consume it), so this test belongs to `bds-popover` itself, not any one consumer.

**Why this needed its own plan (not folded into a Phase task):** it requires real browser layout/computed-style assertions (Playwright or equivalent), not `newSpecPage` — a different test tier than the rest of the date-picker v2 plan's unit-test tasks, and one that repo hasn't established a convention for yet. Per that plan's own `plan-execution.md`-driven rule, an accumulated `pending` follow-up like this must be either completed or re-scoped into its own tracked plan before the parent plan can be considered done — this file is that re-scoping, done with the user's explicit confirmation (2026-09-03).

**Known-good manual re-verification (2026-08-27, interim, not a durable test):** re-ran the exact scenario live via `mcp__playwright__*` on `packages/boreal-web-components/src/index.html`'s `#dp1` `with-time` scenario. Opened the outer `bds-date-picker` popover, then the hour `bds-select`'s nested popover, and read `getComputedStyle` directly: outer `.popover-content` resolves `--popover-content-padding` to `12px 24px` (the date-picker's own override) while the nested `bds-select` popover's `.popover-content` resolves it to `0`/`0px` — no leak; also confirmed no horizontal overflow (`scrollWidth === clientWidth === 62px`) on the nested list. Both fixes hold as of that date. This was a one-off confidence check, not checked-in test coverage — the repo still had no `@playwright/test` harness at that time, so this bug class remained uncovered by CI. That interim result is the starting point for Task 1 below, not a substitute for it.

**Architecture:** Test-only addition — no behavior/component code changes expected. If the repo has no established browser-test harness yet (`@playwright/test` or equivalent) by the time this plan is picked up, Task 1 below must also stand one up (or confirm and reuse whatever convention has emerged since 2026-09-03) before writing the actual regression test.

**Tech Stack:** Playwright (or the repo's established browser-test harness, once one exists), against `pnpm dev:components`'s live dev server.

---

## Files to create / modify

| File                                                              | Notes                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| Browser-test harness config (new, if none exists yet)              | e.g. `playwright.config.ts` — confirm convention before creating                      |
| New browser-test spec file (path TBD by harness convention)        | Covers the nested-popover custom-property-inheritance regression                       |

**Critical reference file** (read before implementing): `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` — re-verify the current selectors/overrides still match this plan's description before dispatching, since this plan may be picked up well after 2026-09-03.

---

## Task 1: establish (or confirm) a browser-test harness and add the regression test

**Executor:** @testing-subagent (or @frontend-subagent if harness setup requires build/tooling changes beyond test authoring)
**Files:** per the "Files to create / modify" table above

**Acceptance criteria:**

- A browser-driven test (Playwright or the repo's established equivalent) opens `bds-date-picker` with `with-time` set, opens the hour/minute `bds-select` dropdown, and asserts the nested popover's computed `--popover-content-padding` resolves to the unset/component-default value (`0`/`0px`), not a leaked ancestor value (`12px 24px`).
- Covers both fixes discovered during the date-picker v2 plan: the direct-child-combinator + `initial` reset on `bds-date-picker > bds-popover`'s nested popovers, and the `bds-select bds-popover { --popover-content-padding: 0; }` override (2026-08-26 follow-up).
- Also asserts no horizontal overflow on the nested `bds-select` list (`scrollWidth === clientWidth`), matching the interim manual check above.
- Documents which test runner/harness is used and where its config lives, since no other task in the parent plan established one.
- If a harness already exists in the repo by the time this is picked up, reuse it — do not stand up a second, competing browser-test convention.

**Manual test (required):** `pnpm dev:components` — open `#dp1` (or the current equivalent `with-time` scenario), open the hour `bds-select` dropdown, confirm via the browser console/devtools that the nested popover's `--popover-content-padding` is unset/`0`, matching the automated test's assertion.

**Commit:** `git commit -m "test(bds-popover): add browser-driven nested-popover custom-property-inheritance regression test"`

---

## Task 2: coverage gate verification

**Executor:** @testing-subagent
**Files:** none (verification-only)

**Acceptance criteria:**

- The new browser test passes reliably (re-run at least twice to rule out flakiness from real layout timing).
- No regression in the existing `boreal-web-components` unit-test suite.

**Manual test:** N/A — verification-only.

**Commit:** N/A — verification-only task.
