---
name: feedback-pass-through-wrapper-test-trimming
description: How much test coverage a pure pass-through wrapper function around a well-tested library call deserves
metadata:
  type: feedback
---

A function that only forwards its arguments to a library call with no branching or transformation of its own (e.g. `export function addMonths(date, amount) { return addMonthsFns(date, amount); }`) needs exactly ONE smoke test confirming the wrapper delegates correctly — not exhaustive boundary/edge-case coverage. Exhaustive coverage of such a wrapper re-tests the library's own already-tested correctness, not any logic this codebase owns.

**Why:** Caught in review on `packages/boreal-web-components/src/services/date-engine/date-math.ts` — `addMonths`/`subMonths`/`isSameDay`/`isSameMonth` are pure pass-throughs to date-fns; each had 2 tests (same-year vs. year-boundary rollover, or true-case vs. false-case) trimmed to 1. `isWithinRange` does real translation work (positional `(date, start, end)` args → date-fns's `{start, end}` object shape) — that translation is what deserves the one test; the 5-boundary-condition sweep it previously had was still redundant with date-fns's own inclusive-range semantics.

**How to apply:** Before writing/reviewing tests for a small utility function, check whether it has any conditional logic, narrowing, or argument-shape translation of its own. If it's a bare pass-through (single `return someLibFn(...args)` line, no branches), one representative smoke test is sufficient — coverage and mutation score are unaffected since the same lines execute either way. Do NOT apply this trimming to functions with real logic: a return-value clamp/narrow (e.g. `compareDates` narrowing date-fns's `number` return to `-1 | 0 | 1`) or a deliberate library-avoidance decision (e.g. `toNaiveISODate`/`fromNaiveISODate` avoiding `toISOString()`/`new Date(iso)` UTC-shift pitfalls) is the codebase's own logic and keeps its full test suite.
