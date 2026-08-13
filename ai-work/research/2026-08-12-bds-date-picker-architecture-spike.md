---
ticket: EOA-16692
component: bds-date-picker
status: promoted
---

# Research Spike: bds-date-picker Architecture

**Date:** 2026-08-12
**Status:** Draft

---

## Goal

Resolve the cross-cutting architecture questions for `bds-date-picker` before task-level planning: whether to adopt a calendar-rendering or date-math library versus building in-house, what markup the calendar day-grid should use (native table vs. div+CSS-Grid), how to decompose the component (monolith vs. decoupled sub-components), and whether single-date and date-range ship as one component or two. These decisions are meant to survive scope changes across ADR-0003's later phases (3–8) — write them once here, link every future version plan back to this doc, rather than re-litigating per ticket. Mirrors the model set by `ai-work/research/2026-06-16-bds-table-column-api-spike.md`.

Governing ADRs: ADR-0001 (build in-house, no Shadow DOM), ADR-0002 (date-fns for date math), ADR-0003 (phased roadmap), ADR-0004/0005/0007 (value contract, draft-until-Apply state, locale/timezone). All six are status `Proposed`, not formally accepted, but treated as governing design intent.

---

## Options Evaluated

- **Calendar/date library** — adopt a calendar-rendering library (e.g. Cally, per `ai-docs/lib/beeq-date-picker.md`'s BEEQ precedent) vs. hand-roll on native `Intl`/`Date` vs. hand-roll on `date-fns`
- **Day-grid markup** — native `<table role="grid">` vs. `<div>` + CSS Grid
- **Component decomposition** — monolithic `bds-date-picker.tsx` vs. decoupled sibling sub-components (the `bds-table-column`-style pattern)
- **Single vs. range component** — one `bds-date-picker` with a `range` prop vs. two separate custom elements (`bds-date-picker` + `bds-date-range-picker`)

---

## Findings

### 1. Calendar/date library

BEEQ's `bq-date-picker` (`ai-docs/lib/beeq-date-picker.md`) uses Cally — a Lit-based, Shadow-DOM calendar-grid web component, lazy-loaded from a CDN — for grid rendering, and hand-rolls all text-input parsing/formatting on native `Intl`/`Date`. Notably, BEEQ has **no `date-fns` dependency at all**, not even for leap-year math: validation relies entirely on native `Date` object rollover behavior (`new Date(2023, 1, 29)` silently becomes March 1, so `getDate() === 29` fails and the input is correctly rejected — no hand-written leap-year rule anywhere in BEEQ's code).

This is a legitimate design for BEEQ, but Cally's Shadow DOM is exactly what ADR-0001 disqualifies for Boreal: Boreal is light-DOM only (no Shadow DOM anywhere in the system), and a Shadow-DOM dependency would wall off Boreal's `$boreal-*`/`var(--boreal-*)` tokens and styles from the calendar's internals — not a stylistic preference, a hard incompatibility with how every other Boreal component is styled.

That leaves the real choice: hand-roll on native `Intl`/`Date` (BEEQ's approach) or hand-roll on `date-fns` (ADR-0002's choice). `date-fns` wins here because ADR-0007 already commits Boreal to consumer-supplied `date-fns` `Locale` objects for the `locale` prop — pairing that with an internally native-`Intl`-based engine would mean maintaining two parallel locale systems in one component (the public prop speaks `date-fns`, the internal engine speaks `Intl`). A `date-fns`-based internal engine is the only choice consistent with the public API ADR-0007 already defines.

### 2. Day-grid markup

Verified directly against the W3C WAI-ARIA Authoring Practices Guide (APG), not inferred: the [Date Picker Dialog Example](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) uses `role="grid"` applied to a native `<table>` element, with `row`, `columnheader`, and `gridcell` roles **implied for free** by `tr`, `th`, and `td` tags respectively — no manual ARIA authoring needed beyond the one `role="grid"` override on the `<table>` itself. Confirmed via [MDN's `gridcell` role reference](https://developer.mozilla.org/docs/Web/Accessibility/ARIA/Roles/gridcell_role) as well.

This is the same reasoning `bds-table` already used in this codebase — native elements for free accessibility semantics — applied to a structurally identical problem (a calendar is genuinely tabular: rows = weeks, columns = weekdays). Using `<div>` + CSS Grid would require manually reconstructing every one of those roles by hand, with no spec-provided reference to check the implementation against.

**A gap the spec itself doesn't close**: the APG's own reference example has an [acknowledged, undocumented gap](https://lists.w3.org/Archives/Public/public-aria/2017Feb/0035.html) around disabled dates (e.g. dates before a minimum) — a proposed fix (marking the cell's interactive element `disabled`) was discussed on the public-aria mailing list but never folded into the official example. This means Phase 3 (min/max) cannot simply "follow the spec" for disabled-date treatment; it needs its own design decision, informed by (but not dictated by) prior art (see Roadmap Risks, item 4, below).

### 3. Component decomposition

Cross-checking against `bds-table`'s spike (`2026-06-16-bds-table-column-api-spike.md`, Extended Findings): `bds-table-column`/`bds-table-column-group` are separate registered custom elements **because consumers author them directly as declarative light-DOM children** — a public composition API need (`<bds-table><bds-table-column key="name">...`), not a code-organization choice. The applicable litmus test for any new sub-piece is therefore: *does it need independent identity for consumer composition, or for cross-orchestrator reuse — or is it just an internal rendering concern of one orchestrator?*

- **`bds-calendar-grid`** passes the test for the *reuse* reason, not consumer composition: ADR-0001 explicitly frames it as "a small, reusable, dumb component shared by every orchestrator" (this picker now, a future range picker later). It becomes a real registered custom element with its own component folder and full test suite — but with **no standalone Storybook story/MDX**, documented only as an internal implementation note inside `bds-date-picker.mdx`. This matches the confirmed, existing precedent: `bds-table-column`/`bds-table-column-group` and `bds-tab`/`bds-tab-content` are real dumb sibling components with zero separate docs entries in this codebase.
- **Footer, time selector, month header** fail both tests — single-use rendering concerns specific to `bds-date-picker` itself, with no reuse or consumer-authorship need. These stay as `helpers/*.tsx` render functions inside one `bds-date-picker.tsx`, matching `bds-table`'s own monolith-with-extracted-helpers shape (2130 lines, ~14 `@State` fields directly on the class, non-trivial logic pulled into `utils/`, no separate state-machine class) rather than becoming their own registered elements.

### 4. Single vs. range component (ADR-0006)

ADR-0006 ("Separate Components for Single Date and Date Range Pickers"), referenced by both ADR-0004 and ADR-0005 under "Links / Related Decisions," was never actually authored — confirmed via a direct Confluence search across the SENG space; no page with that title or number exists.

Resolved by inspecting the actual Figma component library directly (`search_design_system` against file `rtiE5zGA4aoOuxIQMgfD6h`), rather than inferring from the ADR title: in the current, active Boreal library `[BOR] DSG COMPONENTS → FORMS`, there are exactly two date-picker-related assets — `datePickerInput` (a single component, the text-field trigger) and `calendarPicker` (**one** `component_set`, key `9986f78154208d4c4b857e9a998fed76282753c1`). There is no separate "date range picker" component_set anywhere in the active library. Combined with the provided documentation screenshots, which show single-calendar and dual-calendar/presets/banner as two *variant states* ("Date picker collapsed" vs. "Date picker expanded") under one shared "Formatting" anatomy section rather than as two separately-documented components, this is concrete evidence that the design team modeled single-date and range as variants of one component, not as two independent components.

(The only other "date range" hits in the library search came from an unrelated, older `Telesign Design System` library — not the active Boreal one.)

---

## Recommendation

### No calendar UI library — build in-house on `date-fns`

Confirms ADR-0001/0002. Cally-style Shadow-DOM libraries are structurally incompatible with Boreal's light-DOM styling model. `date-fns` (not native `Intl`) is required internally because ADR-0007's public `locale` prop is already `date-fns`-shaped.

### Day-grid markup: native `<table role="grid">`

Matches the WAI-ARIA APG's own reference implementation verbatim and `bds-table`'s established codebase precedent. Requires a code comment justifying the `role="grid"` override on a `<table>` element, so a future maintainer doesn't "clean it up" thinking it's redundant.

### Component decomposition: `bds-calendar-grid` as the one necessary sibling, everything else stays in the `bds-date-picker` monolith

Apply the litmus test above per future sub-piece as new phases add UI (e.g. a presets sidebar in Phase 6 should be re-evaluated against the same test, not assumed to need its own component).

### Single component with a `range` prop, not two separate tags

Confirmed via the Figma library's own one-component-multiple-variants structure (component key `9986f78154208d4c4b857e9a998fed76282753c1`), not inferred. `bds-date-picker` should accept a `range: boolean` prop (or equivalent) that toggles single/dual-calendar behavior, matching how the design system already models it.

---

## Resolved Decisions

| Question | Decision | Rationale |
| --- | --- | --- |
| Calendar rendering library? | **None — build `bds-calendar-grid` in-house** | Cally's Shadow DOM is incompatible with Boreal's light-DOM styling model (ADR-0001) |
| Date-math library? | **`date-fns`** (not native `Intl`) | ADR-0002; also required for consistency with ADR-0007's `date-fns`-shaped `locale` prop |
| Day-grid markup? | **Native `<table role="grid">`** | Matches WAI-ARIA APG's own reference example verbatim; matches `bds-table`'s existing native-element precedent |
| `bds-calendar-grid` — separate component? | **Yes, but internal-only (no public Storybook docs)** | Passes the reuse test (ADR-0001, shared across future orchestrators), not the consumer-composition test |
| Footer / time selector / month header — separate components? | **No — stay as `helpers/*.tsx` inside `bds-date-picker.tsx`** | Fail both the reuse and consumer-composition tests; single-use rendering concerns |
| Single vs. range component (ADR-0006)? | **One component, `range` prop** | Confirmed via the active Figma library's own component structure — one `calendarPicker` component_set, not two |
| `date-engine` package location? | **`packages/boreal-web-components/src/services/date-engine/`** | Matches the existing `services/floating`, `services/logger` precedent for a cohesive, multi-file, cross-cutting subsystem — not a standalone pnpm package (ADR-0002 states it's never exposed publicly; no repo precedent for a standalone pure-logic package) |
| Versioning convention for future plans | **`ai-work/plans/<ticket>-bds-date-picker-vN.md`**, each linked from this spike doc | Matches `bds-table`'s exact precedent (`EOA-10576-bds-table-v1.md` → `EOA-14935-bds-table-v2.md` → `EOA-15507-bds-table-v3.md`) |

---

## Roadmap risks to track (ADR-0003's Phase 0–8 sequencing)

Reviewed against ADR-0003's phase roadmap. Overall the sequencing logic holds (min/max proven once against a single calendar before range duplicates it; locale/timezone established in Phase 0 before any UI; presets/banner scheduled after range, matching the docs — those elements only appear in the "expanded"/range variant screenshots, never in the single-date view). Four items worth tracking as later tickets approach, not blockers for this ticket:

1. **Accessibility/keyboard scope, Phase 8** — *closed, scope clarified*: "Phase 8" only defers calendar-specific arrow-key 2D grid traversal. Baseline keyboard operability (Tab reaches the trigger, Enter/Space opens the popover, footer buttons reachable) ships from Phase 1 via `bds-popover`'s existing keyboard handling. Do not read "Phase 8" as "unusable via keyboard until then."
2. **Value-shape evolution across phases** — *closed, not a concern*: Boreal DS is pre-alpha with no consumers yet, so a breaking `value` shape change when range ships (Phase 4, `string` → `string | {start, end}`) carries no migration cost. No special handling required beyond the loose typing this ticket already uses (kept only because it's free, not as risk mitigation).
3. **Single vs. range component (ADR-0006)** — *closed*, see Resolved Decisions above: one component, `range` prop, confirmed via the Figma library structure.
4. **Min/max disabled-date interaction design (Phase 3)** — *open, needs its own UX/UI design pass before Phase 3 implementation begins.* No Figma mockup exists beyond the generic "Day disabled" token on the Style page — no visual for boundary behavior, no indication of a message/tooltip on a disabled date, no spec for what happens when an entire visible month falls outside min/max. The WAI-ARIA APG itself has an acknowledged gap here (Finding 2 above), so this can't be resolved by reading the spec harder. Reference points for that design pass, verified via web search (not recalled):
   - [`useDatePicker` — React Aria (Adobe)](https://react-spectrum.adobe.com/react-aria/useDatePicker.html) / [`useDateRangePicker`](https://react-spectrum.adobe.com/react-aria/useDateRangePicker.html) — `isDateUnavailable` predicate pattern; the most flexible model of the group, from the team behind the Spectrum design system. Known pitfall: [a whole month can become unreachable via month-navigation when every date in it is disabled](https://github.com/adobe/react-spectrum/issues/6585) — worth designing around explicitly.
   - [Vaadin Date Picker docs](https://vaadin.com/docs/latest/components/date-picker) — recommends pairing min/max with **helper text informing the user of the accepted range**, rather than a silently-disabled cell with no explanation. (Vaadin's date picker was also one of the external options ADR-0001 considered and rejected — worth the cross-reference.)
   - [Accessible Date Pickers — React DayPicker](https://daypicker.dev/guides/accessibility) — confirms the `aria-disabled="true"` cell pattern and recommends an `aria-live` region (via a footer slot) to announce the selected date; relevant to Phase 8 too, not just Phase 3.
   - [Ant Design `disabledDate`](https://ant.design/components/date-picker/) and [their design-rationale blog post](https://ant.design/docs/blog/picker/) — the most directly relevant prior art for the *range* case (Phase 4+): the callback receives an `info.type` disambiguating "start" vs. "end" panel evaluation.
   - [MUI X `shouldDisableDate`/`disableFuture`](https://mui.com/x/react-date-pickers/validation/) — simplest convenience-prop model; known pitfall: [`shouldDisableDate` was found running against every possible date, not just visible ones](https://github.com/mui/mui-x/issues/4705) — a performance trap worth avoiding from the start.

---

## Version Backlog (ADR-0003 Phases 3–8)

Captured here so a future ticket-scoping session doesn't need this conversation's chat history to pick up where `EOA-16692` (v1) leaves off — mirrors `bds-table`'s spike doc's "v2 Backlog" section. Each item below reflects what the provided Figma/Notion documentation screenshots and legacy props table actually showed, not inference.

### Phase 3 — min/max date and time constraints (single)

- **Design coverage: thin.** The only visual reference is the generic "Day disabled" row on the Style page's token table (`background-color`/`text-color` tokens, no interaction spec). No mockup shows boundary-date behavior, a message/tooltip explaining why a date is disabled, or what happens when an entire visible month falls outside min/max.
- **Legacy props table reference** (behavioral prior art only, not an API to replicate — see Findings above): `minDate`/`maxDate` (string, "any valid date with the format established lower/greater than the other"), both defaulting to empty string (unbounded).
- **Needs before implementation**: a UX/UI design pass — see Roadmap risks item 4 above for reference points from React Aria, Vaadin, react-day-picker, Ant Design, and MUI X.
- **Reuse from v1**: `date-engine`'s `isWithinRange`/`compareDates` (implemented but unwired in `date-math.ts`, Task 4 of the v1 plan) and `DayCell.isDisabled` (already in `bds-calendar-grid`'s types, unwired dead capacity since Task 7) are both purpose-built for this phase — no new `date-engine` primitives should be needed, only wiring.

### Phase 4 — dual calendar (date range)

- **Component API**: resolved above (Findings/Resolved Decisions) — one `bds-date-picker` with a `range` prop, not a separate tag. Confirmed via the Figma library's single `calendarPicker` component_set.
- **Structure page pixel specs** (from the provided Figma structure screenshots, "Calendar range" section): Header 48px height, 16px icon, 24px left/right padding, 16px top/bottom padding. Option buttons (presets list items): 8px left/right padding, 8px top padding. Time selector: 48px height, 16px icon, 24px left/right padding, 8px top/bottom padding. Calendar body: 12px left/right padding, 24px top/bottom padding. Footer: 48px height, 24px left/right padding, 16px top/bottom padding.
- **Anatomy** (per the docs' "Date picker expanded" anatomy list): Header (optional) / Options (optional, the presets sidebar) / Calendar (collapsed or expanded) / Format (time-select, optional) / day rendering for next/previous month / Footer (optional).
- **Day states unique to range mode** (from the Style page's "Data states" callout, not needed for v1's single-date states): day-in-range, day-end-range, day-range (start/end) — distinct from the six single-date states (`bds-calendar-grid` v1 already implements default/hover/focus/selected/disabled/today; range mode adds these on top, likely via additional CSS classes on the same `<td role="gridcell">` structure rather than a markup change).
- **Legacy props table reference**: `isRange` (boolean, "whether the component displays one or two date selectors," default `true` in the legacy component — note this default inverts what v1 chose, single-date-only by default, worth a deliberate decision not an accidental carry-over), `showRanges`, `maxRange` (number/array, "range of times in days/weeks/years," default `-1` = unbounded).

### Phase 5 — dual time selection (start/end)

- **Visual reference exists**: the provided docs explicitly show this — "Inicio: 08:00" / "Fin: 10:30" dual hour:minute dropdown pairs, each pair following the same visual pattern as v1's Phase 2 single selector.
- **Reuse from v1**: Phase 2's `renderTimeSelector.tsx` (two `bds-select` instances) should be directly reusable twice (once for start, once for end) rather than needing new component logic — worth designing Phase 2's helper to accept a label/position parameter now if it's cheap, though v1's plan doesn't require this speculatively.
- **Legacy props table reference**: `resetTime` (boolean, "whether the time/minutes selectors restart to start and end of the day with any selection," default `false`) and `showTimeInRange` (boolean, default `true`) — both map to range-specific behaviors not needed until this phase.

### Phase 6 — presets sidebar

- **Visual reference exists, itemized exactly**: the provided docs show a fixed preset list — "Hoy" (Today), "Ayer" (Yesterday), "Últimos 7 días" (Last 7 days), "Últimos 30 días" (Last 30 days), "Este mes" (This month), "Último mes" (Last month), "Personalizado" (Custom) — the last one shown selected/highlighted (solid blue background) in the mockups, the others in a default/list style. Button option states shown: Default, Hover, Focus, Active, Disabled — each with both a default and selected visual variant per the Style page's "Options - Default" / "Options - Selected" comparison rows.
- **Legacy props table reference — this is the strongest prior art in the whole legacy table**: the `ranges` prop's default value is almost a verbatim spec for this list — `{'aqua.today': [], 'aqua.yesterday': [], 'aqua.last7Days': [], 'aqua.last30Days': [], 'aqua.thisMonth': [], 'aqua.lastMonth': []}` with documented semantics (`today`, `today-1`, `today-7,today`, `today-29,today`, `thisMonth,today`, `thisMonth-1`) — the naming doesn't carry over (namespaced `aqua.*` keys are from the prior non-Boreal implementation) but the six preset *semantics* match the Figma list item-for-item and should anchor the new API's preset-computation logic.
- **Needs before implementation**: whether presets are a fixed built-in list or consumer-configurable (the legacy `ranges` prop suggests configurable was already a solved problem elsewhere) — worth a deliberate decision, not a silent inheritance from the legacy shape.

### Phase 7 — info banner + footer range summary

- **Visual reference exists**: an info banner (blue background, info icon, title "Info", message text, closable via an `X` button) rendered inside the popover above the calendar; a footer range-summary text ("Rango: 18 días, 2 horas, 30 minutos" — "Range: 18 days, 2 hours, 30 minutes") to the left of the Limpiar/Cancelar/Aplicar buttons.
- **Legacy props table reference**: `infoBanner` prop shape — `{ title: String, close: Boolean, message: String, state: String, visible: Boolean }`, default empty object. The shape (not the prop name) is reusable prior art: title/message/closable/state/visible is a reasonable banner contract. `showDaysInRange` (boolean, default `true`) maps to the footer summary text specifically.

### Phase 8 — keyboard navigation, accessibility, RTL

- **Scope clarified** (Roadmap risks item 1, closed): only calendar-specific arrow-key 2D grid traversal is deferred here. Baseline keyboard operability (Tab, Enter/Space, Escape via `bds-popover`) ships from v1's Phase 1.
- **Direct implementation reference**: the [WAI-ARIA APG Date Picker Dialog Example](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) documents the exact keyboard interaction to implement — arrow-key cell traversal, month/year navigation hotkeys, and a live region announcing the month/year on change. `bds-calendar-grid`'s v1 markup (native `<table role="grid">`) was chosen specifically to make this phase additive rather than a rewrite.
- **Existing utility to reuse**: `src/utils/a11y/keyboard/navigation/grid-navigation.ts` already exists in the codebase and is generic — v1's Task 9 explicitly left a code comment identifying it as this phase's integration point rather than wiring it early.

---

## Implementation Plan (2026-08-12): `EOA-16692` (v1) scope decision

`EOA-16692` ("Implement Date Picker 0,1,2", assigned to the requesting engineer, status In Progress) commits ADR-0003's Phases 0–2 to implementation: the `date-engine`/`bds-calendar-grid` foundation, the single-date picker (no time), and its single time selector. Plan: [`ai-work/plans/EOA-16692-bds-date-picker-v1.md`](../plans/EOA-16692-bds-date-picker-v1.md). Ticket brief: [`ai-work/tickets/EOA-16692-bds-date-picker.md`](../tickets/EOA-16692-bds-date-picker.md).

Everything else in ADR-0003's roadmap (Phases 3–8: min/max, range, dual time, presets, banner, keyboard/a11y/RTL polish) is explicitly deferred — not scheduled, no plan file yet. Per the versioning convention resolved above, each future ticket gets its own `ai-work/plans/<ticket>-bds-date-picker-vN.md`, linked from this spike doc, rather than being folded into a single mega-plan.
