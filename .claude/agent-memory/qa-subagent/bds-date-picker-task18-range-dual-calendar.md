---
name: bds-date-picker-task18-range-dual-calendar
description: EOA-17138 Task 18 manual test results for bds-date-picker range/dual-calendar orchestration, plus a Stencil async-render timing gotcha hit while scripting rapid calendar-cell clicks via eval.
metadata:
  type: project
---

Task 18 (`bds-date-picker` `range` prop + dual-calendar `expanded`/`basic` orchestration) manually verified via web-components playground on 2026-08-31 — all 4 scenarios plus regression pass. Header format uses the default `yyyy/MM/dd – yyyy/MM/dd` (en dash) token, not a hardcoded "Mon DD" string — that's expected (same default-format mechanism as single-date mode), not a deviation from the plan's illustrative example.

**Gotcha:** when scripting rapid sequential calendar-cell `.click()` calls via `playwright-cli eval` (e.g. click, then immediately read `className`/header text in a *separate* eval call), the read can catch stale DOM from before Stencil's async re-render commits — a swap/selection that looks like a no-op is often just a render-timing race, not a real bug. Confirmed by re-querying a few hundred ms later (next eval call) and seeing the correct post-click state. Prefer reading state in a *later* eval call, not the same one that fires the click, when the assertion needs a settled render.

**Why:** avoids false-negative bug reports on range/selection logic when verifying via raw DOM eval instead of visible waits.

**How to apply:** any future manual QA scripting click→immediate-read against Stencil components (not just `bds-date-picker`) via `playwright-cli eval` should split click and assertion into separate calls, or add a short wait, before concluding a click "did nothing."
