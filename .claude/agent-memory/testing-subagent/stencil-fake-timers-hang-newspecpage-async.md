---
name: stencil-fake-timers-hang-newspecpage-async
description: jest.useFakeTimers() active during any newSpecPage render/waitForChanges call hangs the test until Jest's default timeout, rather than failing fast
metadata:
  type: project
---

Calling `jest.useFakeTimers()` before `await newSpecPage(...)` or `await page.waitForChanges()` (e.g. to freeze "now" for a `generateMonthGrid`-style fixture) does not throw — it silently hangs until Jest's default test timeout (~22.5s) and reports "Exceeded timeout", not a timer-related error. Root cause: Stencil's internal render/task-queue scheduling relies on real macrotasks (setTimeout/rAF polyfill) that fake timers intercept and never auto-advance.

**How to apply:** when a fixture needs a frozen system time (e.g. `generateMonthGrid`'s `isToday` computation), scope `jest.useFakeTimers()` / `jest.setSystemTime()` / `jest.useRealTimers()` tightly around the *synchronous* fixture-building call only — never let fake timers be active across an `await newSpecPage(...)` or `await page.waitForChanges()` boundary. Verified while writing `bds-calendar-grid` variant specs (EOA-16692 Task 9): freezing time in a helper like `generateMonthGridAtSystemTime()` that toggles real timers back on before returning avoided the hang entirely.

Candidate for promotion to `.agents/memory/` — this applies to any Stencil component test needing `jest.setSystemTime` alongside `newSpecPage`, not just this component.
