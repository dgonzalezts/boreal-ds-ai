# ADR 0015 — `bds-date-picker` preset date/time coverage semantics

**Date:** 2026-09-10
**Revised:** 2026-09-24
**Status:** Accepted

> **Revision (2026-09-24):** the manual-selection rule was originally keyed on **calendar type** — `basic` shifted, `expanded` never did. It is now **data-driven**: the shift applies to a manual selection whenever its two bounds carry the **same time-of-day**, regardless of calendar type. This leaves `basic` unchanged (its one shared field always shares a time) and makes `expanded` shift only when its two independent fields hold the same time. The change fixed a real defect: the old rule keyed on the selected *preset* rather than on the *values*, so clicking the trailing **Custom** item after a preset (without changing any date or time) silently altered the header, the footer summary, and the committed value. The Decision and Consequences below have been updated; the preset tables are unchanged.

---

## Context

`bds-date-picker`'s Phase 6 presets sidebar (Today, Yesterday, Last 7 days, Last 30 days, This month, Last month) computes a `{ start, end }` range for each built-in preset. When `with-time` is off, this is unambiguous — a naive calendar-date range, no time-of-day component, and the consumer's own backend decides how to interpret it (the same as any plain date-only range in this component). This ADR only concerns the combination of `range` + `with-time` together; nothing else is in scope.

Once `with-time` is on, each boundary becomes a real timestamp, and a genuine question arises: what time-of-day should a preset assign to its boundaries so that, e.g., "Last 7 days" actually covers all seven days rather than six-and-a-fraction? This surfaced as a concrete defect during Task 30's implementation: `basic`'s single shared time selector (one value applied to both `start` and `end`, per Task 23's own Figma-grounded design) collapsed same-day presets like "Today" into a **zero-duration range** (`start === end`, to the second), and under-covered multi-day presets by close to a full day.

Two candidate fixes were explored and rejected before landing on the final design (see Options Considered): forcing every boundary to a fixed `23:59` end-of-day, and computing an exact rolling time window ending at the current instant (`now`). Both were live options for a period during this design discussion; neither survived contact with `basic`'s architecture or the project's own "no discrepancy" requirement (below).

A separate, non-negotiable requirement emerged alongside the time-coverage question, driven directly by user feedback during this discussion: **the calendar grid highlighting, the popover header, the trigger field's displayed text after Apply, and the raw submitted `value`/`bdsChange` payload must never silently disagree with each other.** An earlier design (compute a precise boundary for the submitted value, but display a different, "nicer-looking" boundary in the header/trigger) was explicitly rejected because it meant the trigger field's displayed text would change the instant Apply was clicked, with no visible user action causing it — a real, visible inconsistency, not just an internal one.

---

## Non-Goals

- Does not change plain date-only range behavior (`range` without `with-time`) — that case has no time-of-day component and was never ambiguous.
- Does not change single-date (`calendarType='default'`) behavior at all — `default`+`with-time` is already a non-enforced, warned-against combination (`componentWillLoad`), and `default` never has a `start`/`end` pair to begin with, so no coverage question can arise there.
- Does not add a consumer-facing `presets` configuration prop (see ADR-pending Task 28 decision — presets are fixed).
- Does not solve the eventual Phase 7 range-summary footer's implementation — see Consequences for why this ADR's decision simplifies that task rather than requiring its own separate resolution.

---

## Options Considered

### Option A — Fixed `23:59` end-of-day boundary, per calendar type

Every preset's `end` sets `23:59` (this component's last representable minute, given its minute-only time granularity). `start` sets `00:00`.

Produces a duration exactly one minute short of a true 24h-multiple (e.g. "Today" spans 23h59m, not 24h) — a small but real imprecision. More seriously, it does not generalize to `basic`'s single shared time field at all: `basic` cannot hold `00:00` for `start` and `23:59` for `end` simultaneously, since both bounds read the same one value. Rejected.

### Option B — Exact rolling window ending at the current instant (`now`)

Modeled on a real library convention (`{ label: 'Last 7 Days', getValue: () => [dayjs().subtract(7, 'day'), dayjs()] }`) — produces a mathematically exact N×24h span for "Last 7 days"/"Last 30 days" by construction, since subtracting a whole number of days from `now` preserves the time-of-day exactly on both ends.

This works cleanly for presets whose start and end naturally share the same time-of-day (Last 7 days, Last 30 days, Yesterday, Last month), and was seriously considered for adoption in `expanded` (which can display two different times) while keeping `basic` on a different, `00:00`-based convention.

Rejected for two reasons. First, "Today" and "This month" are *not* naturally symmetric under this model — their start is day-aligned (`00:00`) while their end is `now` (whatever time it currently is), which are genuinely different times. This reproduces `basic`'s original defect (one shared field asked to hold two different values) for exactly these two presets, and would only cover *elapsed* hours of the current day rather than the whole day — meaning a "Today" clicked at 9am covers less than one clicked at 5pm, an inconsistency of its own. Second, and decisively: it broke the requirement (established directly during this design discussion) that presets produce **identical results in `basic` and `expanded`** — `now`-based precision is only achievable in `expanded`, reintroducing exactly the kind of calendar-type-specific branching this whole effort was trying to eliminate.

### Option C — Whole-day boundaries, end shifted to the start of the following period, identical in both calendar types

Every preset's `start` is a real, day-aligned boundary at `00:00`. Every preset's `end` is the **start of the day immediately after the last real day the preset covers** (also `00:00`) — mathematically identical to "the complete elapsed period," expressed as an exclusive boundary rather than an approximation like `23:59`. For "fully-elapsed" presets (Yesterday, Last month), this end boundary already exists as a natural period boundary (the start of today; the start of this month) — no separate "shift" step is even needed for those two, it falls out of the calendar-day arithmetic directly.

This produces an exact N×24h span for every preset, with the identical formula in `basic` and `expanded` — no calendar-type branching in the computation at all. It also resolves `basic`'s original defect: because both boundaries always share the same time-of-day (`00:00` for presets; for manual selection, whichever time the two bounds share — see Decision), `basic`'s single field is always sufficient, never asked to hold two different values.

The unavoidable cost: the header (and, per the "no discrepancy" requirement, the trigger field after Apply) must display this shifted end boundary — a date one calendar day past the last day the calendar grid actually highlights. A reference screenshot examined during this discussion (an unrelated library's "Last 7 Days" preset, visually spanning one more highlighted day than its own "7" label) demonstrated that this exact quirk — an exact-instant boundary landing one day past what a viewer might naively expect from day-granularity highlighting — is an established, explainable pattern in real date-range pickers, not a novel invention. Accepted.

---

## Decision

Adopt **Option C**. Concretely:

**`computePresetRange(key)`** returns the real, unshifted calendar-day range for a preset (used for grid highlighting and min/max bounds-checking, always).

| Preset | Start | End (real, unshifted) |
|---|---|---|
| Today | today | today |
| Yesterday | yesterday | yesterday |
| Last 7 days | today − 6 | today |
| Last 30 days | today − 29 | today |
| This month | 1st of this month | today |
| Last month | 1st of last month | last day of last month |

**`computePresetCoverageEnd(range, withTime)`** returns the boundary actually used for the header display and the submitted value when `with-time` is on: the real end + 1 day, at `00:00` (a no-op beyond that for Yesterday/Last month, whose real end already equals this). When `with-time` is off, returns the real end unchanged — no shift, since a date-only range has no time-of-day precision question at all.

| Preset | Start (submitted) | End (submitted, `with-time` on) | Grid selection (unaffected) |
|---|---|---|---|
| Today | today, `00:00` | tomorrow, `00:00` | today |
| Yesterday | yesterday, `00:00` | today, `00:00` | yesterday |
| Last 7 days | today−6, `00:00` | tomorrow, `00:00` | today−6 … today |
| Last 30 days | today−29, `00:00` | tomorrow, `00:00` | today−29 … today |
| This month | 1st of month, `00:00` | tomorrow, `00:00` | 1st … today |
| Last month | 1st of last month, `00:00` | 1st of this month, `00:00` | full last month |

**Both `basic` and `expanded` use this identical table for presets.** No calendar-type branching exists in preset computation.

**The coverage shift for manual selection is data-driven, not calendar-type-driven.** It applies whenever the range's two bounds carry the **same time-of-day** — i.e. whenever the selection is expressible as a whole number of days:

- **`basic`** (one shared time field, per Task 23's Figma-grounded design) satisfies this by construction — both bounds always read the same value. The end commits at the real last day + 1, at whatever time the shared field currently shows (not forced to `00:00` for manual selection, preserving the user's own input on both the real start and the shifted end). This is necessary, not optional: `basic`'s single field structurally cannot express "covers the whole last day" any other way, and a user has no way to work around that limitation themselves.
- **`expanded`** (independent start/end fields) shifts only when the two fields hold the **same** time — including the untouched `00:00` default. A deliberately different End time is taken exactly as set, with no adjustment: the user already has full, independent control to express whole-day coverage themselves, so overriding an explicit choice would be second-guessing input they are fully capable of getting right. The one further exception is a **same-day** `expanded` range whose equal Start/End time is non-midnight — a genuine zero-duration instant, not a whole-day span — which is left unshifted.

Keying the rule on the values rather than on the selection's provenance is deliberate: an earlier version shifted `expanded` only while a *preset* was the active selection, which meant clicking **Custom** afterward (with no change to any date or time) silently changed the header, the footer summary, and the committed value — a direct violation of the "no discrepancy" requirement in the Context above.

**Display consistency:** the popover header, from the moment a preset is clicked (or, for any manual selection whose bounds share a time-of-day, as soon as it produces a committable range), displays the exact same boundary used for the submitted value — the shifted end, not the real last day. This is identical in `basic` and `expanded`, since the rule no longer branches on calendar type. The trigger field's text after Apply reads the same boundary again. Only the calendar grid legitimately differs (highlighting the real days only) — an accepted, explained consequence of a day-granularity display representing an exact-instant boundary, not a hidden discrepancy, since the boundary's own text is identical everywhere else it appears.

---

## Consequences

- **`utils/presets.ts` (Task 29) needs rework**: the version shipped earlier the same day used the rejected `23:59` convention and needs updating to this ADR's table before Task 30 (which depends on it) can be considered complete.
- **Phase 7's range-summary footer (Task 35) is simplified, not complicated, by this decision**: because both calendar types now commit an exact whole-day-multiple duration for presets (and both do too for manual selections whose bounds share a time-of-day), the footer's "N days"/"N days, H hours, M minutes" summary can be computed via plain raw timestamp subtraction, with zero special-casing — it will always agree with the grid and header, since the underlying values are now exact. No inclusive-calendar-day-counting mechanism, separate from the raw duration, is needed.
- **A visible, permanent header quirk is introduced by design**: for every `range`+`with-time` selection where the coverage guarantee applies (i.e. wherever both bounds share a time-of-day), the header and trigger field display a date one calendar day past the last day highlighted on the grid. This must be documented plainly in the component's consumer-facing docs (`bds-date-picker.mdx`) as an intentional design choice with its rationale, not left for a consumer to discover and mistake for a bug.
- **Manual selection's shift is data-driven, not calendar-type-driven** — it applies whenever both bounds share a time-of-day: always for `basic` (one shared field), and for `expanded` when its two independent fields match. The visible consequence is that an `expanded` range with matching Start/End times shifts exactly as a `basic` one does, while an `expanded` range with a deliberately different End time does not. This is deliberate, grounded in "shift only when the selection is a whole-day span," and must be documented as such rather than presented as an unexplained inconsistency.
- **No consumer-facing API changes**: this ADR governs internal computation and display formatting only; no new props, no changed prop types.
