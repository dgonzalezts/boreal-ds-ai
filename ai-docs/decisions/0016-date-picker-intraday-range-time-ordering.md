# ADR 0016 — `bds-date-picker` same-day intraday range time-ordering semantics

**Date:** 2026-09-21
**Status:** Accepted

---

## Context

`expanded + range + with-time` already correctly commits a genuine intraday range (same calendar day, two distinct times) when reached via preset-then-manual-edit: ADR 0015's coverage shift (as revised 2026-09-24) applies only when a range's two bounds share the **same** time-of-day, so two distinct start/end times leave `rangeEndShiftApplies` false, and the commit path combines each bound independently via `combineDateTimeToUTC`. Nothing downstream special-cases `rangeStart === rangeEnd`.

Task 34d makes this state reachable via a plain calendar interaction for the first time: a second click on the day already selected as `rangeStart` will set `rangeEnd = rangeStart` (today, that click is a no-op). Once reachable this way, nothing stops a user from setting an End time earlier than the Start time on the same day (e.g. Start `14:00`, End `09:00`). No validation anywhere in the commit path currently catches this — `buildRangeCommitValue`/the Apply-button-enabled check only require both bounds to be non-null, never `start <= end` at the time-of-day level.

This is a narrower, sibling question to ADR 0015: that ADR resolved how a *day-granularity* boundary should be represented as an exact instant; this ADR resolves what a *literally inverted* instant pair means when a user actually produces one.

---

## Non-Goals

- Does not change `basic`'s behavior — its single shared time field cannot express two different times regardless, so an inverted same-day pair cannot occur there in the first place.
- Does not change `expanded`'s existing multi-day range-click logic, or any behavior for `rangeStart !== rangeEnd`.
- Does not change preset-driven ranges — every built-in preset sets both bounds' time fields to `00:00` (per ADR 0015), so a preset can never itself produce an inverted pair. This ADR only concerns manually-set, independent start/end times on a same-day selection.
- Does not add a new consumer-facing prop, validator, or error-message slot.

---

## Options Considered

### Option 1 — Block

Disable Apply (or show an inline error) when `endTime < startTime` on a same-day range.

Safe and explicit, but introduces inline field-level validation UI this component has never needed anywhere else — every other invalid/incomplete state (an in-progress range with only `rangeStart` set, an out-of-bounds `min`/`max` click) is handled by simply disabling Apply with no per-field error messaging. Adding a first-of-its-kind error affordance for one narrow case is a disproportionate amount of new UI surface for what it solves.

### Option 2 — Allow as-is

Commit the inverted range unchanged (`start` timestamp textually later than `end` timestamp).

Simplest to implement, but breaks an invariant this component has guaranteed for every value it has ever produced, across both v2 and v3: `end >= start`, always. This is exactly the kind of "silent disagreement" ADR 0015 treated as non-negotiable to avoid (there, between the grid/header/value; here, within the value itself). Consumers downstream (backend range queries, chart libraries, any code doing `end - start`) would receive a negative duration with no signal anything unusual happened. Rejected.

### Option 3 — Auto-shift +1 day

Reinterpret `14:00–09:00` as an overnight window: `14:00` today through `09:00` the *following* day. Consistent with ADR 0015's own precedent of resolving a display/commit ambiguity via a semantic date shift computed from a real anchor, rather than blocking input or emitting an invalid value. A recognized pattern in other date-range pickers (overnight/red-eye bookings, hotel checkout-past-midnight, night-shift schedules).

Correct and consistent with prior art, but silent: the user set `09:00` intending "today at 9am" and it becomes "tomorrow at 9am" with no on-screen indication of the reinterpretation — discoverable only after Apply, by reading the committed value's date. This is the exact kind of currently-invisible discrepancy ADR 0015 went out of its way to eliminate for the coverage shift (Decision → "Display consistency"); Option 3 alone would reintroduce that class of problem for this narrower case.

### Option 4 — Hybrid: auto-shift, made visible (chosen)

Same shift as Option 3, but surfaced live: the labeled `Start:`/`End:` header (already capable of showing a per-bound date, not just a time, per Phase 5) explicitly displays the *resolved* end date the moment the inversion occurs — e.g. `End: Sep 19, 09:00` instead of `End: Sep 18, 09:00` — so the user sees the reinterpretation before Apply, not after.

---

## Decision

Adopt **Option 4**.

**Scope of the shift:** applies whenever `expanded + range + with-time` produces a same-day selection (`rangeStart === rangeEnd`) with `endHour`/`endMinute` earlier than `startHour`/`startMinute` — evaluated as a general condition on the draft state, not special-cased to "reached via Task 34d's double-click." There is no other currently-reachable path to a same-day-with-inverted-time state (every built-in preset commits `00:00`/`00:00`, never inverted; `basic` cannot express two different times), so this decision has no retroactive effect on any existing behavior — it only ever activates for the new interaction Task 34d introduces. Should some other path to this same state exist in the future, this same general condition governs it identically, with no separate special-casing required.

**Mechanics, following ADR 0015's own pattern of a real anchor plus a separately-computed display/commit boundary:**

- The *real click* stays exactly what the user did — `draft.rangeStart === draft.rangeEnd` is never mutated by this ADR; the underlying same-day selection is not rewritten into a two-day one.
- Whenever the inversion condition holds, the *effective end date* used for the header display, the calendar grid, and the Apply commit is `rangeEnd + 1 day` — the real end day's time fields, anchored to the following calendar day. This is computed the same way ADR 0015's `computePresetCoverageEnd` computes its own shifted boundary: derived from the real anchor at display/commit time, never mutating `draft.rangeStart`/`draft.rangeEnd` themselves.
- The labeled `Start:`/`End:` header **and** the calendar grid both show this resolved end date live, as soon as the inversion exists in the draft — not only after Apply. This is the "hybrid" half of the decision: the shift is real from the moment it applies, and both surfaces a user is already looking at (the header text and the grid) reflect it together, not just one of them.
- **Revised from this ADR's original acceptance (2026-09-22):** the first accepted version of this decision left the calendar grid unchanged, following ADR 0015's precedent of the grid always showing only the real, unshifted day(s). That precedent doesn't transfer cleanly here: for ADR 0015's coverage shift, the "extra day" is a technicality — the grid still shows the complete, meaningful selection (e.g. all 7 days of "Last 7 days"). For this ADR's inversion case, the second day *is* the meaningful part of the selection — a real calendar cell the user is deliberately including in an overnight window, not an instant-boundary technicality. Suppressing it from the grid hid something substantive rather than something precise, and produced a live-selection-vs-reopen inconsistency: the grid showed one day during live selection but two days after a reopen (see Consequences), for the identical committed value. Highlighting the resolved span live removes that inconsistency by construction — reopening now shows the same thing live selection already showed, because both use the same effective-end computation.
- The trigger field's text after Apply reads the same resolved boundary the header showed before Apply — no discrepancy between what was shown during selection and what was committed, matching ADR 0015's "no silent disagreement" requirement.
- The committed `{ start, end }` value has `end > start` as a real, valid instant ordering, restoring the invariant every other value this component produces already guarantees.

**Implication for Task 34d:** its acceptance criteria's "per Task 34c's decision, implement whichever of block/allow/shift/hybrid was chosen" resolves to Option 4 as specified above — Task 34d's own scope is to wire this shift-and-display logic into the commit path and the labeled header, using the same-day double-click interaction it introduces as the (currently only) way to reach the triggering state.

---

## Consequences

- **A second, narrower quirk is introduced, on top of ADR 0015's own.** For the specific case of a same-day `expanded` selection with an inverted end time, the header (and, per the 2026-09-22 revision above, the grid) shows a resolved boundary one day past the real day the user clicked — analogous to, but distinct from, ADR 0015's coverage-shift quirk (which applies to presets and to any manual selection whose two bounds share a time-of-day, day-granularity, always +1 day, and never touches the grid). This one applies only to a manually-inverted same-day `expanded` pair, and must be documented alongside ADR 0015's existing quirk in `bds-date-picker.mdx`, not conflated with it — they have different triggers and, now, different grid behavior, even though both resolve via the same "+1 day, shown explicitly" mechanism.
- **The reopen-consistency gap this revision closes:** because the grid now highlights the resolved span live, the grid state after Apply → close → reopen matches what live selection already showed — there is no longer a separate reopen-only ambiguity to document or accept as a limitation. (An earlier, since-superseded version of this ADR's implementation had briefly documented such a limitation; it no longer applies.)
- **No consumer-facing API changes**: this ADR governs internal validation/display logic only; no new props, no error-message slot, no changed prop types.
- **`basic` is entirely unaffected** — confirmed structurally impossible for `basic` to reach the triggering condition, so no `basic`-side changes or documentation caveats are needed.
- **Sets a reusable precedent**: any future same-day-or-ambiguous-ordering case this component encounters should default to this same "shift the ambiguous boundary from a real anchor, display the shift live at the point of ambiguity" pattern rather than introducing new blocking-validation UI, unless a future case demonstrates this pattern doesn't fit.
