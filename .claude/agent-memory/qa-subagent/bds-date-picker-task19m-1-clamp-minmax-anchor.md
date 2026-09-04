---
name: bds-date-picker-task19m-1-clamp-minmax-anchor
description: Task 19m-1 (resolveDisplayMonth min/max clamp) manual verification — all 3 scenarios pass, including a dispatch-stated system date that was off by one day from the actual browser/host clock
metadata:
  type: feedback
---

Verified commit `3795a8e8` (EOA-17138 Task 19m-1) live via `pnpm dev:components` + `playwright-cli` against `packages/boreal-web-components/src/index.html`, port 3333.

**Scenario 1 (the fix) — `#dp-minmax` (`basic`, min=2026-08-10, max=2026-08-20, no value):** opens directly on "August 2026" (confirmed via `.bds-calendar-grid__header` textContent + screenshot). Days 1-9/21+ dimmed, 10-20 normal/selectable (no `disabled` attr). "Previous month" nav button rendered disabled (already at the min-bound month) — visual confirmation the anchor landed exactly on the bound, not merely "somewhere in range." 0 console errors.

**Scenario 2 (regression, value inside its own window) — `#dp-stale-range` (`basic`, min=2026-08-10, value=2026-08-05, no max):** opens on "August 2026" — the value's own month, completely unaffected by the min/max clamp logic (clamp only engages on the value-less fallback path, per acceptance criteria). Day 5 (the stale value, itself < min) still renders selected/highlighted — that's pre-existing `basic`-mode behavior, out of scope for this task.

**Scenario 3 (regression, no min/max) — `#dp-default-click` (`calendarType="default"`, no min/max/value):** opens on the real current month unchanged. 0 console errors.

**Dispatch-stated-vs-actual date discrepancy:** the QA dispatch stated "the real system date right now is 2026-09-02," but both the host shell (`date`) and the browser (`new Date().toString()` via `playwright-cli eval`) agreed on 2026-09-03 (`America/Bogota`, UTC-5, no DST) at verification time. This did not affect scenario validity — `dp-minmax`'s Aug 10-20 window excludes September regardless of whether "today" is Sep 2 or Sep 3, and Scenario 3's plain "today's month" check is self-referential (compares the picker's header against whatever `new Date()` returns in the same browser context, not a hardcoded expectation). If a future dispatch's stated date matters more precisely (e.g. exact day-of-month assertions), always cross-check the live browser's own `new Date()` rather than trusting the dispatch text or host shell `date` at face value — one-day drift between "when the plan was written" and "when QA actually runs" is expected and not itself a bug signal.

See also [[dev-pack-build-resets-playground-dev-server]] (not triggered this session — no `dev:pack:*` was run) and [[calendar-grid-today-fallback-scenario-quirk]] (different playground area, same underlying "today" real-date-comparison theme).
