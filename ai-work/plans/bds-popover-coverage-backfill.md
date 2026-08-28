---
ticket: —
component: bds-popover
status: pending
created: 2026-08-27
---

# bds-popover Coverage Backfill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Bring `bds-popover`'s unit-test coverage up to the project's ≥90% statement/branch two-phase quality gate by covering pre-existing, previously-untested branches — Watch-driven `activation`/`managed` reactivity, focus-outside/click-outside edge cases, `focus`/`active` activation-mode listener wiring, and arrow-positioning edge cases.

**Origin:** Discovered as Task 8b of [`EOA-17138-bds-date-picker-v2.md`](./EOA-17138-bds-date-picker-v2.md) during that plan's Task 5 failure-mode catalog audit. The gap is entirely pre-existing and unrelated to that plan's own `content-band` slot addition, which already has full, dedicated unit coverage (`bds-popover-basics.spec.ts`'s `content-band slot` and `positioning setup after the content-band slot-detection...` describe blocks). `bds-popover` is shared infrastructure — `bds-select`, `bds-dropdown`, and `bds-date-picker` all consume it — so this coverage pass is scoped to `bds-popover` alone; it does not touch any consumer.

**Measured baseline (2026-08-27, via this session's own `lcov.info` re-run — not guessed):** `bds-popover.tsx` — 177/218 lines (81.2%), 61/80 functions (76.25%), **112/183 branches (61.2%)**. Branches are the real bottleneck against the ≥90% gate; the uncovered lines cluster almost entirely in four behavior areas (see tasks below), not scattered across the whole file.

**Architecture:** Coverage-only backfill — no behavior changes, no new component code. Extends the four existing spec files, following the suite's established describe-block organization (`bds-popover behavior`, `bds-popover variants`, `bds-popover events`, `bds-popover — methods & keyboard`, `bds-popover accessibility`) rather than introducing new files.

**Tech Stack:** Stencil `newSpecPage`, Jest, this component's existing `setupPopoverMocks`/`suppressConsoleError`/`suppressConsoleWarn` test utilities (already imported by every spec file in this suite — reuse them, do not reintroduce equivalent setup).

**Note on commit messages below:** this plan has no Jira ticket (discovered as an internal follow-up, not filed against one). Commit messages below omit a `TICKET-ID` segment accordingly — confirm with the user before committing whether a ticket should be filed and referenced instead.

---

## Files to create / modify

| File                                                                       | Notes                                                                          |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `packages/boreal-web-components/src/components/overlays/bds-popover/__test__/bds-popover-variants.spec.ts` | Modify — `activation`/`managed` Watch reactivity, `focus`/`active` mode listener wiring |
| `packages/boreal-web-components/src/components/overlays/bds-popover/__test__/bds-popover-events.spec.ts`   | Modify — focus-outside/click-outside edge cases                               |
| `packages/boreal-web-components/src/components/overlays/bds-popover/__test__/bds-popover-basics.spec.ts`   | Modify — arrow-positioning edge cases (extends existing "positioning setup" describe block) |

**Critical reference file** (read before implementing): `packages/boreal-web-components/src/components/overlays/bds-popover/bds-popover.tsx` — every acceptance criterion below cites exact line numbers from this file as read on 2026-08-27; re-verify they still match before dispatching each task, since this plan may be picked up after other changes land.

---

## Task 1: `activation`/`managed` Watch-driven reactivity coverage

**Executor:** @testing-subagent
**Files:** `bds-popover-variants.spec.ts` (modify)

**Unit tests to cover:**

- `@Watch('activation') onActivationChange()` (lines 131–135): changing the `activation` prop at runtime unsubscribes the previous trigger listeners and resubscribes with the new activation mode — assert the old mode's listeners are gone and the new mode's listeners are attached (e.g. switching `click` → `focus` mid-session).
- `@Watch('managed') onManagedChange()` (lines 137–141): toggling `managed` at runtime resubscribes the trigger slot and re-runs `setupKeyboard()` — assert both effects happen, not just one.
- Coverage-phase only (≥90%); mutation testing is out of scope for this plan (see "Mutation testing" note at the end of this file).

**Manual test:** N/A — non-visual, validated via `pnpm test` and the coverage report only.

**Commit:** `git commit -m "test(bds-popover): backfill Watch-driven activation/managed reactivity coverage"`

---

## Task 2: Focus-outside and click-outside edge cases

**Executor:** @testing-subagent
**Files:** `bds-popover-events.spec.ts` (modify)

**Unit tests to cover:**

- `handleFocusOutside()` (line 263): returns immediately without hiding when `isVisible` is `false`.
- `handleFocusOutside()` (lines 265–270): does **not** hide the popover when focus lands inside the trigger (`listenTarget`, `triggerEl`, or `triggerSlot` — cover at least one of these three, since they're OR'd in the same guard) — this is the `focusInsideTrigger` branch.
- `handleFocusOutside()` (line 270): does **not** hide the popover when focus lands inside the floating content itself, including the exact-match case (`floatingContent === target`, not just `.contains`) — this is the `focusInsideFloating` branch.
- `handleFocusOutside()` (lines 272–273): hides the popover when focus genuinely lands outside both the trigger and the floating content.
- `attachClickOutside()`/`detachClickOutside()` (lines 226, 236): when `floatingOptions.closeOnClickOutside === false`, no `mousedown` listener is attached on open, and detaching is a no-op — assert clicking fully outside the popover does **not** close it in this configuration (regression guard distinguishing this from the default-`true` behavior already covered elsewhere in this suite).

**Manual test:** N/A — non-visual, validated via `pnpm test` and the coverage report only.

**Commit:** `git commit -m "test(bds-popover): backfill focus-outside and click-outside edge case coverage"`

---

## Task 3: `focus`/`active` activation-mode listener wiring

**Executor:** @testing-subagent
**Files:** `bds-popover-variants.spec.ts` (modify)

**Unit tests to cover:**

- `activation="focus"` (lines 400–405): `subscribe()` attaches `mousedown`/`focus`/`blur`/`click` listeners on the resolved target — assert all four are wired, not just that the popover opens.
- `handlePointerDown` → `handleFocus` interaction (lines 440–446): a `mousedown` on the trigger sets `isPointerInteraction = true`, which then suppresses the subsequent `handleFocus()` call from opening the popover (mouse-driven focus should not trigger `activation="focus"`'s open behavior — only genuine keyboard/programmatic focus should).
- `handleBlur()` (lines 449–457): resets `isPointerInteraction` and, via the `requestAnimationFrame` callback, hides the popover when focus does **not** move into the floating content or a descendant `bds-popover` — assert both the reset and the conditional hide; also cover the case where focus *does* move into the floating content (no hide).
- `activation="active"` (lines 408–411): `subscribe()` attaches `focus` and `click` listeners that directly call `handleFocus`/`handleClick` (distinct wiring path from `focus` mode's named handlers — verify both open on click and open on focus work for this mode).
- `unsubscribe()` (lines 430–437): when a nested `parentBds`-matching anchored trigger exists inside the unsubscribed trigger, `listenTarget` is correctly reassigned before `removeListeners` is called on the resolved target.
- `handleClick()` `ignoreNextClick` guard (lines 478–481): when `ignoreNextClick` is `true`, the click is swallowed — the flag and `isPointerInteraction` both reset, and `toggle()` is **not** called.

**Manual test:** N/A — non-visual, validated via `pnpm test` and the coverage report only.

**Commit:** `git commit -m "test(bds-popover): backfill focus and active activation-mode listener wiring coverage"`

---

## Task 4: Arrow-positioning edge cases

**Executor:** @testing-subagent
**Files:** `bds-popover-basics.spec.ts` (modify — extend the existing "positioning setup after the content-band slot-detection..." describe block; do not create a new describe block for this)

**Unit tests to cover:**

- `setArrowPosition()` (line 359 guard): does nothing (no style mutation) in each of its three independent skip conditions — `result.middlewareData?.arrow` is `undefined`, `disabled` is `true`, and `arrowElement.isConnected` is `false`. Cover each condition separately; they're independent branches in the same `&&` chain.
- `setArrowPosition()` start-placement branch (lines 362–364): for `placement` of `top-start` or `bottom-start`, `arrowX` resolves to `20` when `arrowData.x !== 0`, and to `undefined` when `arrowData.x === 0` — both outcomes need their own test.
- `handlePosition()` full-width branch (lines 326–337): when `width="full"` and a trigger slot is present, the floating content's inline width is updated only when the rounded new width differs from the rounded current width (assert both the update-happens and update-skipped cases), and `updatePosition` is invoked with a callback that re-applies `data-placement` and arrow position.
- `setAnchorElement()` (lines 607–609): when the popover is already `isVisible` at call time, `updatePosition` is invoked with the new trigger/floating content/options; when not visible, it is not.

**Manual test:** N/A — non-visual, validated via `pnpm test` and the coverage report only.

**Commit:** `git commit -m "test(bds-popover): backfill arrow-positioning and full-width repositioning edge case coverage"`

---

## Task 5: Coverage gate verification

**Executor:** @testing-subagent
**Files:** none (verification-only)

**Acceptance criteria:**

- Full `bds-popover` spec suite passes with zero failures.
- `bds-popover.tsx`'s own statement and branch coverage (not the workspace aggregate) is independently re-measured at ≥90% each, using the same `lcov.info` per-file extraction method this plan's baseline was measured with (or the project's standard `stencil test --spec --coverage` output for this file) — do not rely on the aggregate `Coverage summary` line, which mixes in every other component's file.
- If a real gap survives after Tasks 1–4, close it by extending the relevant task's spec file above — do not introduce a new task or new file for a leftover gap; this task's job is closing what Tasks 1–4 missed, not new scope.

**Manual test:** N/A — non-visual, validated via the coverage report only.

**Commit:** N/A — verification-only task; no code changes expected unless a genuine gap is found and closed per the acceptance criteria above (in which case, use that task's own commit message).

---

## Task 6 (discovered during this plan's authoring, 2026-08-27): `hasHeaderSlot`/`hasFooterSlot` dead-code flag — out of scope, not actioned here

**Status:** 🔲 flagged, not actioned.

**Finding:** `bds-popover.tsx`'s `hasHeaderSlot` (line 567) and `hasFooterSlot` (line 574) getters are never referenced anywhere — not in this file's own `render()` (which checks the `header`/`footer` `@Prop`s directly, not these getters), and not by any other file in the repo (confirmed via a repo-wide grep for both names, 2026-08-27). They are the two functions accounting for a chunk of this plan's baseline function-coverage gap (lines 568, 575 in the uncovered-lines list).

**Why this isn't folded into Tasks 1–4 above:** writing tests for genuinely dead code doesn't serve this plan's goal (real coverage of real behavior) — it would inflate the coverage numbers without protecting anything a consumer depends on. This is a deletion candidate, not a test-coverage gap, which is a different kind of change than the rest of this plan.

**Next step:** re-scope into its own small cleanup task (or fold into whichever task next touches `bds-popover.tsx` for an unrelated reason) — confirm with the user before deleting public-ish (unexported but non-private) class members, since removal is a judgment call this plan's coverage-only scope shouldn't make unilaterally.

---

## Mutation testing

Out of scope for this plan. This plan closes a **coverage**-phase gap only, per the project's two-phase quality gate (`testing-knowledge`'s ≥90% coverage → ≥90% mutation score sequence). `bds-popover` does not yet have its own Stryker config in this repo (unlike `bds-date-picker`, `bds-calendar-grid`, and `date-engine`, which each have one per the one-config-per-component convention) — standing one up is a separate, follow-up decision, not implied by closing this coverage gap.
