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

**Outside-month day cell interactivity — resolved (2026-08-14):** the open question of whether leading/trailing (out-of-month) day cells are clickable-but-muted or fully inert is resolved by treating visual treatment and interaction treatment as separable axes sourced from different authorities. Visual treatment (show the real day number, grayed via the `text/disabled` token, no separate "muted" cell variant) is sourced from Figma — already documented above in the "Instance-level component mapping" note and decoded in full in the `_DatePickerNumber` day-cell properties subsection below. Interaction treatment (non-focusable, non-clickable) is sourced from this same WAI-ARIA APG reference implementation, verified directly from source rather than inferred: [`datepicker-dialog.js`](https://github.com/w3c/aria-practices/blob/main/content/patterns/dialog-modal/examples/js/datepicker-dialog.js) sets `cell.tabIndex = -1` for all cells by default, uses `const flag = d.getMonth() != fd.getMonth()` to detect out-of-month days, and its click handler checks `isDayDisabled()` before acting — out-of-month cells fail that check, so clicks do nothing. Applied to Boreal: out-of-month cells stay permanently `tabindex="-1"` (never promoted into the tab sequence) and clicking them does not emit `bdsDayClick`. This requires no change to already-shipped work — `generateMonthGrid` (Task 3, 100% coverage) keeps its fixed 6-week/42-cell shape, and `isCurrentMonth` (already a `DayCell` field) is exactly what drives this render-only distinction.

An alternative was considered and rejected: MUI X's `showDaysOutsideCurrentMonth` prop (opt-in, default `false` — hides outside days entirely when off) paired with its separate `fixedWeekNumber` prop, investigated via the [React Date Calendar component docs](https://mui.com/x/react-date-pickers/date-calendar/) and three related issue/PR threads ([mui-x#6982](https://github.com/mui/mui-x/issues/6982), [material-ui#30479](https://github.com/mui/material-ui/issues/30479), [mui-x#5598](https://github.com/mui/mui-x/pull/5598)). Rejected because: (1) MUI's `false` default reflects MUI's own design, not Boreal's — Figma has no variant showing outside days hidden, so copying MUI's default would silently diverge from the actual design; (2) true parity (hiding outside days entirely, producing a variable 4–6 row grid) would require reworking `generateMonthGrid()`'s already-shipped fixed-6-week architecture, the same kind of scope-reopening avoided elsewhere this session (see the "Unscheduled — month/year quick-picker" precedent below); (3) a boolean toggle prop would also mean reopening Task 7's `ICalendarGrid` types (already done). A future variable-row/hide-outside-days mode remains a legitimate but separate, unscheduled backlog item.

### 3. Component decomposition

Cross-checking against `bds-table`'s spike (`2026-06-16-bds-table-column-api-spike.md`, Extended Findings): `bds-table-column`/`bds-table-column-group` are separate registered custom elements **because consumers author them directly as declarative light-DOM children** — a public composition API need (`<bds-table><bds-table-column key="name">...`), not a code-organization choice. The applicable litmus test for any new sub-piece is therefore: *does it need independent identity for consumer composition, or for cross-orchestrator reuse — or is it just an internal rendering concern of one orchestrator?*

- **`bds-calendar-grid`** passes the test for the *reuse* reason, not consumer composition: ADR-0001 explicitly frames it as "a small, reusable, dumb component shared by every orchestrator" (this picker now, a future range picker later). It becomes a real registered custom element with its own component folder and full test suite — but with **no standalone Storybook story/MDX**, documented only as an internal implementation note inside `bds-date-picker.mdx`. This matches the confirmed, existing precedent: `bds-table-column`/`bds-table-column-group` and `bds-tab`/`bds-tab-content` are real dumb sibling components with zero separate docs entries in this codebase.
- **Footer, time selector, month header** fail both tests — single-use rendering concerns specific to `bds-date-picker` itself, with no reuse or consumer-authorship need. These stay as `helpers/*.tsx` render functions inside one `bds-date-picker.tsx`, matching `bds-table`'s own monolith-with-extracted-helpers shape (2130 lines, ~14 `@State` fields directly on the class, non-trivial logic pulled into `utils/`, no separate state-machine class) rather than becoming their own registered elements.

#### Target light-DOM structure (2026-08-14, not yet built at the time — since revised, see 2026-08-19 correction below)

Derived directly from Tasks 13/14/15/16's acceptance criteria in `ai-work/plans/EOA-16692-bds-date-picker-v1.md`, cross-checked against `bds-popover.tsx`'s actual slot API (`header-icon`/`header-title`, default body slot, `footer-helper`/`footer-button` — confirmed by reading the component directly, not inferred):

**Correction (2026-08-19) — consumer-supplied trigger field:** the `<bds-text-field slot="field">` below was originally rendered internally by `bds-date-picker` itself (Task 13/14). This was found to make `label`/`sublabel`/`icon`/`helperText`/etc. impossible to configure, and was corrected to match `bds-select`'s own established pattern instead: `bds-date-picker` renders `<slot name="field"></slot>`, and the **consumer** supplies their own fully-configured `<bds-text-field slot="field">`, exactly as every `bds-select.stories.ts` example does. `bds-date-picker` pushes only `value` (computed display text) and `selectable`/`disabled` onto the consumer's field imperatively via `updateElementProp`, mirroring `bds-select.tsx`'s exact mechanism (`updateElementProp(this.bdsField, 'value', displayTexts)` etc.). See the plan's "Architecture Correction (2026-08-19)" section (after Task 16) for full rationale, and the Resolved Decisions table below.

```html
<bds-date-picker value="2026-08-14" format="yyyy/MM/dd" ...>

  <!-- Trigger: supplied by the CONSUMER (corrected 2026-08-19 — was previously
       rendered internally by bds-date-picker). bds-date-picker pushes `value`
       (computed display text) and `selectable`/`disabled` onto this element
       imperatively via updateElementProp, matching bds-select's exact pattern;
       everything else (label, sublabel, icon, helperText, placeholder, etc.)
       is the consumer's own configuration. -->
  <bds-text-field slot="field" label="Appointment date" ...>
  </bds-text-field>

  <!-- Floating panel: opened/closed via setListenElement/setAnchorElement
       against the trigger above (Task 14), footer prop enabled -->
  <bds-popover floating-options="{ hideArrow: this.hideArrow }" placement="bottom-start" footer>

    <!-- default (unnamed) slot = popover body -->
    <bds-calendar-grid                      <!-- composed via renderCalendarPanel.tsx, Task 15 -->
      grid="{...}"                          <!-- computed from displayYear/displayMonth @State -->
      year="{this.displayYear}"
      month="{this.displayMonth}"
      selected-date="{this.draft.selectedDate}"
    ></bds-calendar-grid>

    <!-- footer-button slot: three bds-buttons (Task 16) -->
    <bds-button slot="footer-button" variant="text">Clear</bds-button>
    <bds-button slot="footer-button" variant="outline">Cancel</bds-button>
    <bds-button slot="footer-button" variant="solid">Apply</bds-button>

  </bds-popover>
</bds-date-picker>
```

`bds-calendar-grid` sits inside `bds-popover`'s **default slot** (its body/content region) — `footer-helper`/`footer-button` carry the three action buttons. **Correction (2026-08-19):** the earlier version of this line said `header-icon`/`header-title` "go unused (Task 14 specifies no header)" — that was stale; the header row (icon + live date/time text + close ✕) shown in the Figma reference and already documented below in the Instance-level component mapping (line ~223) was never formally scoped into Task 14 until reopened a 4th time on 2026-08-19. `bds-date-picker` now slots a hardcoded `ICONS.CalendarDots` icon into `header-icon` and a `<span slot="header-title">` bound live to the draft/committed value (falling back to a new `headerPlaceholder` prop when empty) into `header-title` — see the plan's Task 14 4th-reopen note and the Resolved Decisions row below. This is directly relevant to Task 15's open question about whether `@Listen('bdsDayClick')` reliably catches events crossing that slot boundary, or whether the `addElementListener` runtime pattern (already used for the trigger in Task 14) is required instead.

**Resolved (2026-08-19, Task 19):** the `bds-button` `variant`/`color` values for Clean/Cancel/Apply, previously left illustrative/unspecified, are now implemented in `renderFooter.tsx`: Clean is unstyled default (`variant="default"`, `color="default"`, both implicit), Cancel is `variant="outline"`, Apply is `color="primary"` (implicit `variant="default"`) — matching the ghost/outline/solid-blue hierarchy confirmed against the Figma footer screenshot pull. The field-label ownership question (previously open, Task 19) is now **resolved** by the 2026-08-19 correction above — the consumer's own slotted field always supplies its own label; there is no `bds-date-picker`-owned label.

#### Target file structure (2026-08-18, for future reference)

Derived directly from `ai-work/plans/EOA-16692-bds-date-picker-v1.md`'s "Files to create / modify" table — reproduced here so a future version-plan session doesn't need to re-read the v1 plan to know where things live. Reflects the nesting correction from Task 7 (`bds-calendar-grid` nests inside `bds-date-picker/`'s shared parent folder, matching `bds-table`/`bds-table-column`'s precedent, not a flat sibling) and the "internal-only, no public docs" decision for `bds-calendar-grid` from Finding #3 above.

```
packages/boreal-web-components/src/
├── services/date-engine/                          # Phase 0 — pure logic, framework-agnostic
│   ├── types.ts                                    # MonthGrid, DayCell, WeekdayLabel, DateEngineLocale
│   ├── grid.ts                                      # generateMonthGrid, getWeekdayLabels
│   ├── date-math.ts                                 # addMonths/subMonths/isSameDay/isSameMonth/isWithinRange/compareDates/toNaiveISODate/fromNaiveISODate
│   ├── format.ts                                    # formatDisplayDate, getMonthYearLabel
│   ├── value.ts                                     # (Phase 2) combineDateTimeToUTC/extractDateTimeFromUTC via @date-fns/tz
│   ├── index.ts                                     # public barrel — only DateEngineLocale leaks date-fns types
│   ├── stryker.date-engine.config.mjs               # created v1 Task 23, re-run v2 Task 8 (value.ts) — per-unit mutation config
│   └── __test__/
│       ├── grid.spec.ts
│       ├── date-math.spec.ts
│       ├── format.spec.ts
│       └── value.spec.ts                            # (Phase 2)
│
└── components/forms/bds-date-picker/                # shared parent folder (orchestrator-named, per bds-table precedent)
    ├── bds-calendar-grid/                            # Phase 0 — dumb, controlled, reusable sibling
    │   ├── bds-calendar-grid.tsx
    │   ├── bds-calendar-grid.scss
    │   ├── stryker.bds-calendar-grid.config.mjs
    │   ├── types/
    │   │   ├── ICalendarGrid.ts
    │   │   ├── types.ts                              # CalendarGridDayClickDetail, CalendarGridMonthNavigateDetail
    │   │   └── index.ts
    │   └── __test__/
    │       ├── bds-calendar-grid.basics.spec.ts
    │       ├── bds-calendar-grid.events.spec.ts
    │       ├── bds-calendar-grid.variants.spec.ts
    │       └── bds-calendar-grid.a11y.spec.ts
    │
    └── bds-date-picker/                               # Phase 1–2 — orchestrator
        ├── bds-date-picker.tsx
        ├── bds-date-picker.scss
        ├── stryker.bds-date-picker.config.mjs
        ├── helpers/
        │   ├── renderCalendarPanel.tsx
        │   ├── renderFooter.tsx
        │   └── renderTimeSelector.tsx                 # (Phase 2)
        ├── utils/
        │   ├── draft-state.ts
        │   ├── value-mapping.ts
        │   └── index.ts
        ├── types/
        │   ├── IDatePicker.ts
        │   ├── enum.ts                                 # FOOTER_ACTION
        │   ├── types.ts                                 # DatePickerDraftState
        │   └── index.ts
        └── __test__/
            ├── bds-date-picker.basics.spec.ts
            ├── bds-date-picker.events.spec.ts
            ├── bds-date-picker.variants.spec.ts
            ├── bds-date-picker.form.spec.ts
            ├── bds-date-picker.keyboard.spec.ts
            ├── bds-date-picker.a11y.spec.ts
            └── bds-date-picker.time.spec.ts            # (Phase 2)

apps/boreal-docs/src/stories/forms/bds-date-picker/
├── bds-date-picker.stories.ts
└── bds-date-picker.mdx                                 # includes internal bds-calendar-grid note (no separate docs)
```

Plus one modified (never committed) file: `packages/boreal-web-components/src/index.html`, for playground scenarios only.

Authoritative source for this tree, task-by-task, is the v1 plan's Files table — this section is a snapshot, not a substitute for it. Future version plans (Phase 3+) should extend this tree here as new files land, per the versioning convention resolved elsewhere in this doc.

### 4. Single vs. range component (ADR-0006)

ADR-0006 ("Separate Components for Single Date and Date Range Pickers"), referenced by both ADR-0004 and ADR-0005 under "Links / Related Decisions," was never actually authored — confirmed via a direct Confluence search across the SENG space; no page with that title or number exists.

Resolved by inspecting the actual Figma component library directly (`search_design_system` against file `rtiE5zGA4aoOuxIQMgfD6h`), rather than inferring from the ADR title: in the current, active Boreal library `[BOR] DSG COMPONENTS → FORMS`, there are exactly two date-picker-related assets — `datePickerInput` (a single component, the text-field trigger) and `calendarPicker` (**one** `component_set`, key `9986f78154208d4c4b857e9a998fed76282753c1`). There is no separate "date range picker" component_set anywhere in the active library. Combined with the provided documentation screenshots, which show single-calendar and dual-calendar/presets/banner as two *variant states* ("Date picker collapsed" vs. "Date picker expanded") under one shared "Formatting" anatomy section rather than as two separately-documented components, this is concrete evidence that the design team modeled single-date and range as variants of one component, not as two independent components.

(The only other "date range" hits in the library search came from an unrelated, older `Telesign Design System` library — not the active Boreal one.)

**Instance-level corroboration (2026-08-14):** a direct `get_design_context` pull against `https://www.figma.com/design/rtiE5zGA4aoOuxIQMgfD6h/-BOR--DSG-COMPONENTS-%E2%86%92-FORMS?node-id=3181-25366&m=dev` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, nodeId `1537:17221`, instance name `datePickerInput`) resolved to the "Date picker expanded" / range variant of the same `calendarPicker` component_set identified above via `search_design_system` — concrete instance-level confirmation of the metadata-level finding, not a new or conflicting data point. **The ADR-0006 resolution above stands unchanged**: one component, `range` prop, no separate "date range picker" custom element.

### Instance-level component mapping (datePickerInput → bds-date-picker)

Structure found under the pulled `datePickerInput` instance:

| Figma layer | Maps to | Evidence |
| --- | --- | --- |
| `datePickerInput` (top-level instance) | `bds-date-picker` (orchestrator) | Instance root |
| `_DatePickerField` | `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx` | **Code Connect snippet, verbatim** — props seen: `header`, `slot`, `showSufix`, `prefixIcon`, `footer`, `charCounter`, `prefix`, `helperText`, `textFieldSlotType`, `label`, `displayPassword`, `icon`, `textFieldState`, `stateError`, `textFieldVariant`. Direct, tool-verified confirmation of this plan's existing `bds-text-field`-as-trigger decision. |
| `calendarPicker` (floating panel) | `bds-popover` | Drop-shadow, rounded-corner chrome consistent with popover styling |
| `Header Expanded Time picker` | n/a — range-variant only | "Starts"/"Ends" labels + close icon; not applicable to Phase 0–2 |
| `Ranges` (7× `_DatePickerRange`) | n/a — Phase 6 scope | Preset sidebar items; not applicable now |
| `Date/Time` → `Calendars` (2× `_DatePickerCalendar`) | n/a — confirms range variant | Two calendars side by side confirms this pull is the expanded/range variant, not the collapsed/single variant |
| `_DatePickerCalendar` → `_DatePickerCalendarMonth` → `Container` → `Header` | Task 9's month/year header + nav | `_Button/previous` (prev nav), `_Button/month-year` (labeled "Months years" — a dropdown-styled button, not plain text), `_DatePickerChevron` (next nav) |
| `Container` → `Days` (7× `Day`) | Task 9's `<thead>` weekday row | Weekday header labels |
| `Container` → `Numbers` (N× `_DatePickerNumber`) | Task 9's `<tbody>` day cells | Each contains a nested `Selected` layer (state background) and a text node (day number) |

Trailing/leading out-of-month days use the `text/disabled` design token on the day-number text and appear in the grid without any distinct "muted" wrapper — disabled styling is applied at the text-color level, not a separate cell variant.

**Correction (2026-08-14):** the original version of this note claimed no footer was present in the pulled instance. That was a false negative caused by response truncation, not a design fact — `get_design_context`'s code output was cut off partway through rendering the two calendars' day-number grids (each renders 30+ `_DatePickerNumber` instances with nested state layers), before reaching the `Body`'s later siblings. A follow-up `get_metadata` pull on the `Container` parent (`I1537:17221;14:23281;158:176502`) confirmed an `Expanded Footer` node (712×48, not hidden — unlike the sibling `Basic Footer`, `Header Basic Time picker`, and `Banner` nodes, which are all `hidden="true"`) containing a "Range labels" text block and a `Buttons` group of 3 instances. A direct `get_design_context` pull on that footer node returned only flattened background/shadow styling (no button markup — likely due to effects), but its screenshot is unambiguous: **Clean, Cancel, Apply**, with Apply as the primary filled button and a "Range: {duration}" label to its left — confirming the plan's existing Clean/Cancel/Apply footer decision. The "Range: …" label is range-variant-specific (Phase 6/7 scope) and not applicable to the Phase 0–2 single-date footer text. Lesson for future pulls: a `get_design_context` response that's suspiciously missing an expected structural element (like a footer) on a large/deeply-nested node should be treated as a possible truncation artifact and cross-checked with `get_metadata`, not read as a design fact.

**Resolved (2026-08-14):** the earlier note above said this pull was the expanded/range variant only, and that the collapsed/single-date variant's structure hadn't been pulled and was blocking Tasks 9–11 and Task 16. That is now resolved. The user provided six "Component playground" screenshots covering the `Basic`+`Range:off` (single-date) state directly, and a follow-up `get_design_context` pull against the `_Basic Time picker` node succeeded. Between the two: single-calendar layout confirmed via screenshot, header format confirmed (single icon + one date/time string + close ✕, no Starts/Ends split), footer confirmed (unlabeled Clean/Cancel/Apply, same three buttons as the already-confirmed `Expanded Footer` just without the range-duration label), and the time selector's structure confirmed via tool pull (see `_Basic Time picker` subsection above). Tasks 9–11 and Task 16 are unblocked; no further Figma node pull is required to proceed.

**New lesson — hidden/inactive-variant node pulls are unreliable (2026-08-14), distinct from the truncation lesson above:** two sibling nodes inside the same `Basic`/single-date `Container` were pulled alongside `_Basic Time picker` — `Header Basic Time picker` (`I1537:17221;14:23281;158:176503`) and `Basic Footer` (`I1537:17221;14:23281;158:176540`), both marked `hidden="true"` in `get_metadata` (i.e. inactive variant-state children). Both returned only a flattened, empty background/shadow shell — no text/icon children resolved, blank screenshot output — while the equally-hidden `_Basic Time picker` node resolved fully. This is a second, distinct failure mode from the earlier truncation lesson (that one had a clear response-size cause and was cross-checked via `get_metadata`); this one is not obviously a size issue — it appears inconsistent/unpredictable across hidden nodes rather than a simple truncation artifact. **Practical rule**: for a `hidden="true"` node where `get_design_context` returns an empty/flattened shell, do not retry the API call a third time — fall back to the user's own screenshot of the rendered playground state (visual ground truth) instead, since that's what actually unblocked this session's Tasks 9–11/16 despite the two empty pulls.

### `Calendar Type` property enum (2026-08-14, from user-provided properties panel screenshot)

The `calendarPicker` component_set exposes a `Calendar Type` variant property with three values, each a materially different structural layout (not just a style swap):

| `Calendar Type` | Structure | Other properties shown |
| --- | --- | --- |
| **Default** | Bare grid only — month header + nav, weekday row, day numbers. No popover chrome, no sidebar, no footer. | `End Date: true`, `Banner: false`, `Range: true` |
| **Basic** | Popover chrome + presets sidebar (Today/Yesterday/Last 7 days/Last 30 days/This month/Last month/Custom) + **one** calendar + **single** time selector (`08:30`) + footer (`Range: {n} days` / Clean / Cancel / Apply) | `End Date: true`, `Range: true`, `Banner: false` |
| **Expanded** | Same popover chrome + presets sidebar + **two** calendars side by side + **dual** (Start/End) time selectors + footer with a duration summary | `Range: true`, `End Date: true`, `Banner: false` |

`Default` is a structural match for `bds-calendar-grid` (Tasks 1–8, already built) — nav + weekday row + day cells, nothing else.

`Basic`'s footer (Clean/Cancel/Apply) matches this plan's Phase 1/2 footer decision. Earlier revisions of this section framed the presets sidebar as having "no exposed off-toggle" in the properties panel screenshot available at the time, raising a scope question about whether Phase 1/2 was deliberately deviating from `Basic`'s literal Figma structure.

**Corrected finding (2026-08-14, from user-provided "Component playground" screenshots + follow-up `get_design_context` pulls):** the presets sidebar's visibility is controlled by the `Range` property, not bundled unconditionally into `Basic`/`Expanded`. Live-rendered playground screenshots confirm: with `Calendar Type: Basic`, `Range: off`, `End Date: off`, `Banner: off`, the result is a single calendar + single time selector + unlabeled Clean/Cancel/Apply footer — **no presets sidebar** — while the same `Basic` type with `Range: on` shows the sidebar. The same pattern holds for `Expanded` (`Range: off` → no sidebar; `Range: on` → sidebar present). This means **Phase 1/2's single-date structure is not a deviation from Figma's `Basic` type — it is a literal, directly-observed Figma property combination** (`Basic` + `Range: false` + `End Date: false` + `Banner: false`), not a scoped-out simplification. The "known deviations from Figma" framing for Task 21's MDX note should be dropped for this specific point; there is no deviation to document here. (The presets sidebar itself remains out of scope for Phase 1/2 because `Range` is off in v1, not because it was deliberately omitted from an otherwise-matching `Basic` structure.)

**Structural match confirmed via screenshot** (`Calendar Type: Basic`, `Range: off`, `End Date: off`, `Banner: off`): one calendar (single month grid, one date selected solid blue, no dashed/range styling), single time selector (`08:30`), header is one line — `🗓 2021/07/20 08:30` (calendar icon + one date/time string + close ✕), **not** the two-value Starts/Ends header seen in the range variant — footer is Clean/Cancel/Apply only, with **no** "Range: X" label (label only appears when `Range` is on). No presets sidebar. This directly confirms the plan's existing Phase 1/2 footer and header decisions against real, tool-verified design data — see "Not yet resolved" correction below.

#### `_DatePickerNumber` day-cell properties (resolved 2026-08-14, ties to Task 9)

Drilling into the properties panel for `Calendar Type: Default`, `Banner: off` (the bare grid) revealed that the day-cell component, `_DatePickerNumber`, itself exposes **four** independent properties — `State`, `Selection`, `Type`, `Actual` — not the single `Selected` boolean assumed by the earlier "Instance-level component mapping" table above. The full enum for each and their semantics are now confirmed via the `_DatePickerNumber` component_set metadata (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, frame node `14:23554`, 144 total variants) plus 8 targeted `get_design_context` pulls on individual variant nodes.

**Full property enum:**

| Property | Values | Count |
| --- | --- | --- |
| `State` | `Default`, `Hover`, `Focus`, `Active`, `Disabled`, `Inactive` | 6 |
| `Selection` | `Default`, `Partial`, `Selected` | 3 |
| `Type` | `Default`, `Start`, `End`, `Full` | 4 |
| `Actual` | `True`, `False` | 2 |

Total 6×3×4×2 = 144 variants. For Phase 0–2 (single-date, no range), only `Type: Default` and `Selection: Default | Selected` are relevant — `Partial` selection and `Start`/`End`/`Full` types are Phase 4 range-only. This retroactively explains the cap-shape corner-rounding and dashed-border-on-blue-fill styling seen on node `14:24059` ("State=Default, Selection=Selected, Type=Start, Actual=True") during initial exploration: that was range styling, now correctly attributed and out of scope for v1.

**Decoded `Actual` semantics — correction to an earlier assumption:** `Actual` was previously guessed to mean "belongs to the currently displayed month" (in-month vs. out-of-month). That guess is **wrong**. Evidence from 8 targeted `get_design_context` pulls:

- Node `14:23555` (`State=Default, Selection=Default, Type=Default, Actual=False`): plain white bg, `text/default` (#272a2f) color, no border — same text color as `Actual=True`'s equivalent, contradicting the in-month/out-of-month theory (out-of-month cells use a visibly different, muted color, not this).
- Node `14:23651` (`State=Default, Selection=Default, Type=Default, Actual=True`): plain white bg, `text/default` color, plus a dashed 1px blue border (`stroke/primary-base`, `#0a5bfc`, `radius/xs` 4px corners).
- Node `14:23939` (`State=Default, Selection=Selected, Type=Default, Actual=False`): solid blue circle (`ui/primary-base`, `#0a5bfc`), white text (`text/inverse`), no border.
- Node `14:24035` (`State=Default, Selection=Selected, Type=Default, Actual=True`): same solid blue circle, white text, plus a dashed 1px white border (`stroke/inverse`) overlaid on top.
- Node `14:23571`/child `14:23573` (bg)/`14:23574` (text) (`State=Disabled, Selection=Default, Type=Default, Actual=False`): plain white bg, muted `text/disabled` (#b6b8be) color, no border. These are the exact same node IDs (`;14:23573`, `;14:23574`) that appeared as instance overrides on the real out-of-month trailing days in the original populated calendar pull earlier this session (the `Expanded`-variant `datePickerInput` instance's second-month leading days, numbers 1-4).

**Conclusion**: `Actual` is a "this date is today" indicator — it adds a dashed ring in the cell's existing accent color (blue on white bg, white on blue bg) independent of selection state. It is **not** a month-membership flag. Month-membership (in-month vs. out-of-month/unavailable) is instead conveyed entirely through **`State: Disabled`** (muted `text/disabled` grey text, no ring) — confirmed by direct node-ID match against the real populated calendar.

**State-to-token mapping (Phase 1/2-relevant subset, `Type: Default`):**

| State | Selection | Actual | Visual |
| --- | --- | --- | --- |
| Default | Default | False | White bg, `text/default` (#272a2f), no border |
| Default | Default | True (today) | White bg, `text/default`, dashed blue ring (`stroke/primary-base` #0a5bfc, `radius/xs` 4px) |
| Default | Selected | False | Solid blue circle (`ui/primary-base` #0a5bfc), `text/inverse` white text, no border |
| Default | Selected | True (today, selected) | Solid blue circle, white text, dashed white ring (`stroke/inverse`) overlaid |
| Disabled | Default | False | White bg, muted `text/disabled` (#b6b8be), no border — this is the out-of-month/unavailable-day styling |

**Other states, non-blocking caveats for Task 9:**

- `Hover` (node `14:23655`, `Actual: True` only pulled): light grey bg (`ui/default-lighter`, `#f7f7f8`) + dashed blue ring + drop-shadow (`0px 1px 2px rgba(19,19,22,0.15)`); Figma's generated markup renders this as a `<button>` element rather than a `<div>` — worth preserving as a UX cue (day cells should be real interactive elements, not just styled divs) but not a literal codegen instruction. `Hover` with `Actual: False` was not individually pulled — low-risk, verify empirically during Task 9 implementation.
- `Inactive` (node `14:23671`, `Actual: True`): near-invisible background tint only (`alpha/white-10`, i.e. `rgba(255,255,255,0.1)`) — no text/day-number node was returned at all in the resolved output, unlike every other state pulled. This appears to be a genuinely empty placeholder cell (no date rendered), not just a muted date. `generateMonthGrid()` always fills all 42 grid cells with real day numbers (leading/trailing days included), so there may be no use case for a literal blank cell in Phases 0-2; flag as a minor open question for whoever needs it later (possibly Phase 3 min/max, or simply unused) — non-blocking for Task 9.
- `Focus` and `Active` were not pulled this session — standard interaction states, lower priority; confirm empirically during Task 9 implementation rather than requiring another Figma round-trip now.

#### `_Basic Time picker` structural detail (v2 Task 4, Phase 2 time selector SCSS)

A follow-up `get_design_context` pull on node `I1537:17221;14:23281;158:176538` ("_Basic Time picker", the single hour:minute selector inside the `Basic`/single-date `Container`) resolved fully (unlike its flattened-empty siblings below) and gives real, tool-verified structure for [`EOA-16692-bds-date-picker-v2.md`](../plans/EOA-16692-bds-date-picker-v2.md)'s Task 4 (was Task 26 when this note was written, before Phase 2 was split into its own v2 plan): a `timer` icon (16×16) followed by two `Select` fields side by side, each 58px wide, each a bordered `Field` container (`border: var(--stroke/xs,1px) var(--stroke/default-light,#e3e3e6)`, `radius/xs` 4px corners, padding `spatial/padding/xs` 8px left / `spatial/padding/1xs` 6px right and vertical), each showing a 2-digit value (`08`, `30`) in 14px Inter Regular (`text/default-darker,#131316`) plus a 20×20 disclosure/chevron icon. Record this detail against that task when Phase 2's time selector is implemented.

`Expanded` (`Range: true`, two calendars, dual time) is the Phase 4 (range) + Phase 5 (dual time) + Phase 6 (presets) combination — matches the earlier "Instance-level component mapping" findings above. Also notable: `Basic` with `Range: true` and one calendar (an as-yet-unexplored single-calendar range mode) doesn't map to any phase in the current roadmap — flag for whoever picks up Phase 4, since it suggests range selection may not strictly require the dual-calendar `Expanded` layout in every case.

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
| Outside-month day cell interactivity? | **Visually shown (grayed, `text/disabled`), functionally inert (no click, not tab-focusable)** | Visual from Figma; interaction from the same WAI-ARIA APG reference already adopted for `<table role="grid">` markup; avoids reopening Tasks 3/7 |
| `bds-calendar-grid` — separate component? | **Yes, but internal-only (no public Storybook docs)** | Passes the reuse test (ADR-0001, shared across future orchestrators), not the consumer-composition test |
| Footer / time selector / month header — separate components? | **No — stay as `helpers/*.tsx` inside `bds-date-picker.tsx`** | Fail both the reuse and consumer-composition tests; single-use rendering concerns |
| Single vs. range component (ADR-0006)? | **One component, `range` prop** | Confirmed via the active Figma library's own component structure — one `calendarPicker` component_set, not two |
| `date-engine` package location? | **`packages/boreal-web-components/src/services/date-engine/`** | Matches the existing `services/floating`, `services/logger` precedent for a cohesive, multi-file, cross-cutting subsystem — not a standalone pnpm package (ADR-0002 states it's never exposed publicly; no repo precedent for a standalone pure-logic package) |
| Versioning convention for future plans | **`ai-work/plans/<ticket>-bds-date-picker-vN.md`**, each linked from this spike doc | Matches `bds-table`'s exact precedent (`EOA-10576-bds-table-v1.md` → `EOA-14935-bds-table-v2.md` → `EOA-15507-bds-table-v3.md`) |
| `hideArrow` default value (2026-08-18, corrected) | **`false`** (was originally `true`) — popover arrow renders by default, hidden only via explicit `hide-arrow="true"` | No boolean `@Prop()` in the codebase defaults to `true`; `stencil/ban-default-true` (ESLint) flags any that do, with no self-resolving condition. Ticket brief and plan corrected to match. |
| `bds-popover` `placement` for `bds-date-picker` (2026-08-18, new) | **Fixed `bottom-start`**, not user-configurable | Reference calendar-dialog design shows the arrow and panel consistently left-aligned under the trigger field (never centered/flipped); `bds-popover`'s own default (`bottom`, centered) doesn't match. Matches `bds-dropdown.tsx`'s existing `placement="bottom-start"` precedent (literal string, not the `POPOVER_POSITION` constant). |
| Trigger field composition — self-rendered vs. consumer-supplied (2026-08-19, corrected) | **Consumer-supplied**, matching `bds-select`'s exact pattern — `bds-date-picker` renders `<slot name="field">`, not its own `<bds-text-field>` | `bds-select.tsx` never renders its own field; it slots the consumer's own fully-configured `<bds-text-field>` and pushes only `value`/`selectable`/(and, for `bds-date-picker`, `disabled`) imperatively via `updateElementProp`. The original self-rendered approach made `label`/`sublabel`/`icon`/`helperText`/etc. impossible to configure — caught when the user asked how to pass those through. Mechanically viable in this light-DOM (no Shadow DOM) codebase because `stencil.config.ts`'s `extras.experimentalSlotFixes`/`experimentalScopedSlotChanges` are already enabled project-wide. |
| Popover header row (2026-08-19, new) | **Included in v1** — `header={true}`/`closable={true}` on `bds-popover`, hardcoded `ICONS.CalendarDots` icon, title bound live to `draft.selectedDate` (falls back to committed `value` after Apply/reopen), new `headerPlaceholder: string = 'Select a date'` prop for the empty state (matching MUI X's `toolbarPlaceholder` precedent) | Reference Figma image shows this header row; previously only a passing mention existed (see the now-corrected stale line above), no formal scope entry. Close button needs no extra wiring — `bds-popover`'s own `closable` already correctly reverts the draft on next open. Same `format` as the trigger for v1; a Start/End prefix for the range variant is out of scope, tracked in Phase 4 below. |

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
- **New backlog item (added 2026-08-19): popover header "Start"/"End" prefix.** v1's header title (added Task 14, 4th reopen) shows a single formatted date/placeholder, matching the `Basic`/`Range: off` Figma reference exactly. The `Range: true`/expanded variant's header shows two labeled values instead (see the "Instance-level component mapping" table above, `Header Expanded Time picker` row — "Starts"/"Ends" labels + close icon). This phase needs to decide the exact prefix presentation (e.g. "Start: 2026/08/12" / "End: 2026/08/20" on one line, or two lines) and whether `headerPlaceholder` needs a start/end pair of its own or stays a single string — not resolved here, deliberately deferred to whoever picks up Phase 4.

### Phase 5 — dual time selection (start/end)

- **Visual reference exists**: the provided docs explicitly show this — "Inicio: 08:00" / "Fin: 10:30" dual hour:minute dropdown pairs, each pair following the same visual pattern as v1's Phase 2 single selector.
- **Reuse from v1**: Phase 2's `renderTimeSelector.tsx` (two `bds-select` instances) should be directly reusable twice (once for start, once for end) rather than needing new component logic — worth designing Phase 2's helper to accept a label/position parameter now if it's cheap, though v1's plan doesn't require this speculatively.
- **Legacy props table reference**: `resetTime` (boolean, "whether the time/minutes selectors restart to start and end of the day with any selection," default `false`) and `showTimeInRange` (boolean, default `true`) — both map to range-specific behaviors not needed until this phase.

### Phase 6 — presets sidebar

- **Visual reference exists, itemized exactly**: the provided docs show a fixed preset list — "Hoy" (Today), "Ayer" (Yesterday), "Últimos 7 días" (Last 7 days), "Últimos 30 días" (Last 30 days), "Este mes" (This month), "Último mes" (Last month), "Personalizado" (Custom) — the last one shown selected/highlighted (solid blue background) in the mockups, the others in a default/list style. Button option states shown: Default, Hover, Focus, Active, Disabled — each with both a default and selected visual variant per the Style page's "Options - Default" / "Options - Selected" comparison rows.
- **Legacy props table reference — this is the strongest prior art in the whole legacy table**: the `ranges` prop's default value is almost a verbatim spec for this list — `{'aqua.today': [], 'aqua.yesterday': [], 'aqua.last7Days': [], 'aqua.last30Days': [], 'aqua.thisMonth': [], 'aqua.lastMonth': []}` with documented semantics (`today`, `today-1`, `today-7,today`, `today-29,today`, `thisMonth,today`, `thisMonth-1`) — the naming doesn't carry over (namespaced `aqua.*` keys are from the prior non-Boreal implementation) but the six preset *semantics* match the Figma list item-for-item and should anchor the new API's preset-computation logic.
- **Needs before implementation**: whether presets are a fixed built-in list or consumer-configurable (the legacy `ranges` prop suggests configurable was already a solved problem elsewhere) — worth a deliberate decision, not a silent inheritance from the legacy shape.
- **Node reference (2026-08-14)**: `_DatePickerRange` (fileKey `rtiE5zGA4aoOuxIQMgfD6h`, frame node `14:23420`) is the individual preset button component_set — 10 variants, `State` (5: Default/Hover/Focus/Active/Disabled) × `Selected` (2: True/False). Not pulled for exact tokens/spacing yet (deliberately, Phase 6 is unscheduled) — pull `get_design_context` against this node ID when Phase 6 is actually picked up, no need to relocate it in Figma first.

### Phase 7 — info banner + footer range summary

- **Visual reference exists**: an info banner (blue background, info icon, title "Info", message text, closable via an `X` button) rendered inside the popover above the calendar; a footer range-summary text ("Rango: 18 días, 2 horas, 30 minutos" — "Range: 18 days, 2 hours, 30 minutes") to the left of the Limpiar/Cancelar/Aplicar buttons.
- **Legacy props table reference**: `infoBanner` prop shape — `{ title: String, close: Boolean, message: String, state: String, visible: Boolean }`, default empty object. The shape (not the prop name) is reusable prior art: title/message/closable/state/visible is a reasonable banner contract. `showDaysInRange` (boolean, default `true`) maps to the footer summary text specifically.

### Phase 8 — keyboard navigation, accessibility, RTL

- **Scope clarified** (Roadmap risks item 1, closed): only calendar-specific arrow-key 2D grid traversal is deferred here. Baseline keyboard operability (Tab, Enter/Space, Escape via `bds-popover`) ships from v1's Phase 1.
- **Direct implementation reference**: the [WAI-ARIA APG Date Picker Dialog Example](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/) documents the exact keyboard interaction to implement — arrow-key cell traversal, month/year navigation hotkeys, and a live region announcing the month/year on change. `bds-calendar-grid`'s v1 markup (native `<table role="grid">`) was chosen specifically to make this phase additive rather than a rewrite.
- **Existing utility to reuse**: `src/utils/a11y/keyboard/navigation/grid-navigation.ts` already exists in the codebase and is generic — v1's Task 9 explicitly left a code comment identifying it as this phase's integration point rather than wiring it early.

### Unscheduled — month/year quick-picker (new, not yet phase-assigned)

- **What it is**: clicking the month/year header label opens an inline quick-picker — either a month-grid (Jan–Dec, current month dashed-outlined) or a year-grid (a 12-year range, current year dashed-outlined, future years greyed/disabled) — replacing the day grid in place, to let a user jump directly to a target month/year instead of stepping one month at a time via the prev/next nav buttons.
- **Confirmed present in Figma, confirmed out of ticket scope**: the `_DatePickerCalendar` composite (fileKey `rtiE5zGA4aoOuxIQMgfD6h`) explicitly shows three named states side by side — "Default" (plain day grid), "Default, W/ Month Picker" (month grid replaces the day grid), "Default, W/ Year Picker" (year grid replaces the day grid) — confirming these are interaction states of the same calendar component. A companion month-year label button's state matrix (~10 rows: Default/Hover/Focus/Active/Disabled × unselected/selected, e.g. "July 2020" plain vs. dashed-outlined) confirms the month/year header text is a real interactive button, not static text. Neither EOA-16692's Jira ticket description/acceptance criteria nor Task 9's current plan (`ai-work/plans/EOA-16692-bds-date-picker-v1.md`) mention this feature — a designed-but-not-yet-ticketed gap between Figma and the current ticket scope.
- **Explicitly deferred (2026-08-14)**: the user confirmed this is a real, designed feature but chose to defer it rather than expand Task 9's scope now. Task 9 ships the month/year header as plain static text (see Task 9's acceptance criteria and its 2026-08-14 clarifying note). This entry exists so the deferral is tracked, not silently dropped or silently folded into Task 9.
- **Phase assignment (reasoned 2026-08-14)**: this is not a Phase 3–8 item and not a task within `EOA-16692`. ADR-0003's Phase 3–8 roadmap is organized entirely around cross-cutting concerns the future range picker reuses (min/max, range, dual time, presets, banner, keyboard/RTL) — the quick-picker is an orthogonal single-calendar navigation enhancement that doesn't serve any of those, so it doesn't belong in that sequence. It's also absent from EOA-16692's own Jira "Out (later versions)" list, meaning it was never scoped into the roadmap in either direction. Per this project's own versioning precedent (`bds-table`'s v1→v2→v3, each a separate plan linked from one shared spike doc, adopted specifically to avoid the staleness bds-table hit when scope shifted mid-plan), this belongs in **its own future ticket and plan file**, not folded into `EOA-16692` as a sub-task (e.g. "Task 9a") and not squeezed into an existing Phase 3–8 slot. No ticket exists for it yet.
- **Node references (2026-08-14)**: `datePickerMonths` (node `14:24131`) and `datePickerYears` (node `14:24151`) are the two quick-picker grid components. `_DatePickerMonthYear` (node `14:23473`) is the individual cell component used inside both grids (e.g. one "Jul" or "2021" button), exposing its own `State` (Default/Hover/Focus/Active/Disabled), `State Actual` (True/False — presumed to be the `_DatePickerNumber`-style "is this the current month/year" indicator, not independently confirmed), and `Selected` (True/False) properties. None of these three nodes have been pulled for exact tokens/spacing — deliberately, since the feature is unscheduled; do that when it's actually picked up, not now.
- **Inferred interaction model (2026-08-14, not yet UX/UI-validated)**: a standard three-level drill-down hierarchy (day ↔ month ↔ year), matching the convention used by most mainstream date pickers (MUI X, Ant Design, react-day-picker, Vaadin) — clicking the header label goes up a level, clicking a cell goes down a level: (1) click the month/year label to open the month grid (12 months, a middle button showing the year, prev/next stepping by year); (2) click a month to resolve back to the day grid, now showing that month; (3) click the middle year button while in the month grid to open the year grid (a 12-year range, prev/next stepping by decade); (4) click a year to drill back down to the month grid for that year (not directly to a day) — this last step is inferred from the universal pattern, not directly observed in a Figma prototype/interaction spec. This model is a reasonable working assumption for whenever the feature is scheduled, but should get an explicit UX/UI confirmation at that point rather than being treated as settled now — deferred features don't warrant that validation effort today.

### Unscheduled — keyboard-typed date entry in the trigger field (new, not yet phase-assigned, 2026-08-19)

- **What it is**: a requirements review surfaced language ("Users can input dates either using a keyboard or by navigating the calendar UI; both options are immediately available when the desktop date picker is accessed") that the current v1 architecture doesn't satisfy — the trigger field is pushed `selectable={true}` (Task 14), matching `bds-select`'s non-editable, click/select-only mechanism. This requirement was present in the original brief but not reflected anywhere in the ticket/plan/spike doc until this review — a genuine gap, not a scope-creep request.
- **Scope of the gap**: distinct from calendar-grid keyboard *operability* (Tab/Enter/Space to open, Escape/click-outside to close — already shipped in Phase 1; full arrow-key 2D grid traversal is the already-tracked Phase 8 item). This is specifically about **typing a date string directly into the trigger field** as an alternative to clicking through the calendar.
- **Library/reference research (2026-08-19):**
  - **WAI-ARIA APG "Date Picker Dialog" example** (the same reference already adopted in this doc for `bds-calendar-grid`'s `<table role="grid">` markup, Finding 2) — the trigger is a plain `<input type="text">` with `aria-describedby` pointing to a format hint (e.g. "date format: mm/dd/yyyy"); freeform typing, parsed only when the dialog opens (to decide which day to pre-focus). No masking, no per-keystroke validation.
  - **WAI-ARIA APG "Date Picker Combobox" example** ([w3.org](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/examples/combobox-datepicker/)) — closer prior art still: `role="combobox"`, `aria-haspopup="dialog"`, `aria-expanded`, `aria-controls`, `aria-describedby` on the input itself. Opens via **Down Arrow / Alt+Down Arrow while the input has focus** (the primary keyboard path) — a "Choose Date" icon exists for pointer/touch/screen-reader users but is `tabindex="-1"` (excluded from the Tab sequence, not a prominent MUI-style adornment). Clicking elsewhere in the input just places the text cursor; it does not open the dialog. This is the most directly reusable reference for Boreal's case.
  - **Ant Design `DatePicker`** — freeform-typable by default; `inputReadOnly: boolean` is the opt-out prop to force click-only (the exact inverse of Boreal's current `selectable={true}` default). Confirms typable-by-default is itself a legitimate, common design choice, not exotic.
  - **MUI X `DatePicker`** — typable by default, but via a **segmented field** (month/day/year as individually-editable sections; typing a digit auto-advances with a "smart" max-length heuristic; arrow-up/down increments/decrements per section; Home/End jump to bounds). A fully-masked single-string alternative exists (`rifm`-based) but is explicitly framed as an advanced/opt-in customization, not the default.
  - **React Aria (Adobe)** `useDateFieldState`/`useDateSegment` — the underlying primitive MUI X's segmented pattern is built on; same per-segment model with `realtimeValidation`/`displayValidation` state.
  - **Native `<input type="date">`** — same segmented sub-field behavior at the platform level, already implicitly rejected by ADR-0001/0002 (no format/locale control, inconsistent cross-browser chrome, and — newly relevant here — its own native calendar-icon affordance would directly conflict with keeping the custom-styled `bds-calendar-grid` popover; the two calendar UIs can't coexist on one field without fragile, inconsistent icon-suppression hacks).
- **Three levels of input-level "enforcement" identified, independent of any native `type` attribute** (rejected adding `TEXT_FIELD_TYPES.DATE` — see rationale above, it bundles the browser's own locale-bound format and native calendar UI, which conflicts with the custom popover):
  1. **None** — freeform text, parsed against `format` only on blur/Enter/Apply (reuses `bds-text-field`'s existing `error`/`errorMessage`/`validation-timing` plumbing, matches the WAI-ARIA Dialog reference exactly). Lowest effort.
  2. **Character-class filtering + live auto-separator insertion** — block non-digit keystrokes, auto-insert `format`'s literal separators as digits are typed (e.g. `20260815` → `2026/08/15` live), while structural validity (Feb 30, month 13) is still caught by level 1's parse-on-commit step. No external masking library needed given `date-fns` format strings are simple token patterns. Medium-low effort; **recommended level for whenever this is picked up.**
  3. **Full segmented sub-fields** (MUI X/React Aria default) — see the detailed effort assessment below.
- **Level 3 effort assessment (2026-08-19), reasoned in detail:**
  - Requires: (a) a format-string → segment parser (token type/length/min/max per segment, dynamic day-max from month+year for leap years); (b) a genuinely fiddly per-segment state machine (smart auto-advance on "impossible first digit," arrow increment/decrement/wrap, arrow-key focus movement between segments distinct from normal text-cursor movement, backspace-merge-to-previous-segment, Home/End, click-to-focus-specific-segment); (c) a rendering model change — segments are `role="spinbutton"` spans, not one `<input>`, meaning either `bds-text-field` itself grows a new mode (risky: 17+ callers across the library, e.g. `bds-select`/`bds-search-bar`/`bds-tag-field`) or the trigger bypasses `bds-text-field` entirely, unwinding the already-shipped, already-QA'd Architecture Correction (consumer-supplied `<bds-text-field slot="field">`); (d) `DatePickerDraftState` rework to represent partially-typed (year+month filled, day empty) composition, not just `string | null`; (e) interplay with min/max (Phase 3), whose UX is *already* flagged open/unresolved in the Roadmap risks section below — segmented arrow-increment conventionally needs clamping, so this either pulls Phase 3 forward or ships inconsistent with every reference implementation; (f) i18n depth beyond segment ordering (segment order is free since `format` already encodes it, but placeholder-glyph translation and non-Latin numeral systems need an ICU-style calendar abstraction — React Aria leans on `@internationalized/date` for this; `date-engine` is plain `date-fns`, nothing at this level exists today); (g) zero existing Figma research for segment-level focus/placeholder/underline states — every other visual surface in this plan went through a dedicated research gate first (Task 19's checklist, Task 10's post-mortem on reactive pulls).
  - **Closest internal comparison**: `bds-calendar-grid` — a *simpler* primitive (no auto-advance, no arrow increment/wrap, no partial-value composition, no cross-segment backspace, no `spinbutton` ARIA modeling) — still took 5 tasks (types, scaffold, render+interaction, SCSS+a11y audit *reopened twice*, a11y unit tests).
  - **Net assessment**: comparable to or larger than the entire already-shipped Phase 0 (`date-engine` + `bds-calendar-grid`, 11 tasks), plus a new architecture-decision spike (replace vs. extend `bds-text-field`) comparable in scope to the original Architecture Correction, plus a blocking dependency on Phase 3's still-unresolved min/max UX design, plus an unscoped Figma research gate. Not a task or two — a phase of its own.
- **Decision (2026-08-19): explicitly deferred, out of scope for `EOA-16692` v1.** No level (1/2/3) is implemented in this ticket. If picked up later, level 2 (character-class filtering + auto-separators, composed with level 1's existing parse-on-commit validation) is the recommended starting point — it delivers the "can't type garbage" feel most consumers associate with native inputs without the level-3 architecture decision, min/max dependency, or new-primitive build. Level 3 remains a legitimate future option but should get its own ticket/plan (per this doc's versioning convention) once Phase 3's min/max UX is resolved and a dedicated Figma research pass covers segment-level states.
- **Also identified in passing, not actioned**: `bds-text-field`'s `iconRight` prop (currently purely decorative — `aria-hidden="true"`, no click handler, not focusable, used today only as `bds-select`'s visual dropdown-chevron hint) would need to become a genuine interactive control (button semantics, own event, accessible-name prop) if a MUI-style right-icon adornment were ever wanted as the calendar-open trigger. Per the WAI-ARIA Combobox reference above, this isn't actually necessary — reusing the trigger field's *existing* `icon`/`prefixIcon` (already part of the Figma `_DatePickerField` component per its Code Connect props) plus a Down-Arrow-while-focused keyboard shortcut achieves the same "click or type" outcome with zero new visual elements and no Figma deviation. Worth revisiting only if level 2/3 typing is picked up.

---

## Implementation Plan (2026-08-12): `EOA-16692` (v1) scope decision

`EOA-16692` ("Implement Date Picker 0,1,2", assigned to the requesting engineer, status In Progress) commits ADR-0003's Phases 0–2 to implementation: the `date-engine`/`bds-calendar-grid` foundation, the single-date picker (no time), and its single time selector. Plan: [`ai-work/plans/EOA-16692-bds-date-picker-v1.md`](../plans/EOA-16692-bds-date-picker-v1.md). Ticket brief: [`ai-work/tickets/EOA-16692-bds-date-picker.md`](../tickets/EOA-16692-bds-date-picker.md).

Everything else in ADR-0003's roadmap (Phases 3–8: min/max, range, dual time, presets, banner, keyboard/a11y/RTL polish) is explicitly deferred — not scheduled, no plan file yet. Per the versioning convention resolved above, each future ticket gets its own `ai-work/plans/<ticket>-bds-date-picker-vN.md`, linked from this spike doc, rather than being folded into a single mega-plan.
