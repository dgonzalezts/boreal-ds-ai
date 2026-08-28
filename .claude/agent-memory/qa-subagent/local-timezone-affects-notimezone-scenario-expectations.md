---
name: local-timezone-affects-notimezone-scenario-expectations
description: This QA environment's system/browser timezone is America/Bogota (UTC-5, no DST) — plan-authored "expected" hour/minute values for withTime scenarios without an explicit `timezone` prop assume UTC-0 and will read as offset-by-5 here; verify the offset math instead of the literal digits
metadata:
  type: project
---

Confirmed via `Intl.DateTimeFormat().resolvedOptions().timeZone` in a live `playwright-cli` session and `date +%Z` on the host: this environment's timezone is `America/Bogota`, a fixed UTC-5 offset (no DST transitions).

For any `bds-date-picker` `withTime` scenario that does **not** pass an explicit `timezone` prop, the component falls back to the browser's local timezone — same `date-engine` conversion code path across web-components/React/Vue, confirmed identical across all three surfaces. A plan or scenario script that states "Hour shows 08, Minute shows 30" for a preloaded UTC value like `2026-08-24T08:30:00.000Z` was written assuming a UTC-0 local timezone; in this environment the same value correctly renders as Hour=03, Minute=30 (08:30 − 5h). This is NOT a bug — it's the documented timezone-aware contract working as designed (same conversion logic Scenario 2's Tokyo/LA divergence check exercises).

**How to apply:** when a scenario's stated pass criterion gives literal hour/minute digits and no `timezone` prop is set, recompute the expected local value using this environment's UTC-5 offset before comparing, rather than treating a mismatch against the literal plan text as a failure. Always cross-check by also confirming the calendar day cell carries the `--selected` class/is aria-selected, independent of the hour/minute digits, since that part of the assertion is timezone-independent.

Confirmed identically in React (`examples/react-testapp`) and Vue (`examples/vue-testapp`) wrappers during EOA-17138 Task 7 parity QA (2026-08-27) — not a wrapper-specific divergence.
