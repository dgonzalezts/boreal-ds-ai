---
name: bds-calendar-grid-argtypes-omits-plumbing-props
description: The reference-only bds-calendar-grid ArgTypes table in bds-date-picker.mdx omits 7 real grid props — a known, task-approved gap, not a docs bug to silently "fix"
metadata:
  type: project
---

`bds-date-picker.mdx` documents the internal `bds-calendar-grid` in a reference-only
`### bds-calendar-grid` subsection with an `<ArgTypes include={[...]}>` list. Both the
`bds-date-picker.stories.ts` `argTypes` object and that include array cover only:
`grid`, `year`, `month`, `selectedDate`, `locale`, plus the six events (`bdsDayClick`,
`bdsDayFocus`, `bdsDayHover`, `bdsGridFocusLeave`, `bdsGridLeave`, `bdsMonthNavigate`).

The component's actual `@Prop()` surface (see
`bds-calendar-grid/bds-calendar-grid.tsx`) also declares **`max`, `min`, `now`,
`prevDisabled`, `nextDisabled`, `rangeStart`, `rangeEnd`** — none of which has an
`argTypes` entry or an `include` entry, so per [[argtypes-name-collision-across-subcomponents]]
none renders a row in the Properties panel. `min`/`max`/`now`/`rangeStart`/`rangeEnd` were
added across the Phase 9 commits (EOA-17662) to feed the month/year quick-picker generators
(`generateMonthPickerGrid`/`generateYearPickerGrid`), not to extend the public API.

**Why this is intentional, not a defect to fix opportunistically:** Task 51 (Phase 9 docs)
explicitly scoped the work as "no `ArgTypes` changes — the quick-picker adds no public
prop/event". `bds-calendar-grid` is internal plumbing the orchestrator feeds; its curated
reference table deliberately lists the props a consumer is most likely to see. Do **not**
add rows for the seven omitted props without a task that asks for it — it would contradict
an explicit scope boundary and inflate a reference table for an internal component.

**How to apply:** when the Props/Events Completeness Check flags these grid props as
undocumented, report it as a known pre-existing gap rather than "fixing" it. If a future
task does ask for full grid-prop coverage, the two edits are: add `argTypes` entries (all
tagged `**Internal bds-calendar-grid prop…**` like the existing ones) and add the names to
the `include` array at `bds-date-picker.mdx` `### bds-calendar-grid`.
