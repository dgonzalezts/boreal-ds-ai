# Failure-Mode Catalog — bds-date-picker

Created 2026-08-26, first testing-subagent dispatch for this component (pre-existed this pipeline). Audited the
component as it stands today — Phase 1 (v1) + Phase 2 (v2, time selector) — not just the current task's diff, per
"Existing component with no catalog yet."

Scope note: `bds-popover`'s new `content-band` slot is included here (rows FM-11/FM-12) because Task 5 explicitly
scopes it into this same consolidated test task, even though `bds-popover` is a different component.

---

### FM-01 | `withTime=false` never renders the time selector or `content-band` slot
- **ID:** FM-01
- **Category:** equivalence
- **Risk:** visual regression / accidental behavior change for the majority (Phase 1) usage if a future edit widens the render condition
- **Input that reveals it:** mount with `withTime` unset (default `false`)
- **Observed current behavior:** `bds-date-picker.tsx:467` — `{this.withTime && (<div slot="content-band">...)}`; when false, nothing is rendered into the `content-band` slot
- **Recommended contract:** no `[slot="content-band"]` element exists in the picker's light DOM when `withTime=false`
- **Contract status:** confirmed
- **Why it matters:** regression guard for Phase 1 callers, who never pass `withTime`
- **Covered by:** `bds-date-picker.time.spec.ts::'renders no content-band slot content when withTime is false'`

### FM-02 | `withTime=true` renders exactly one hour select and one minute select reflecting `draft.hour`/`draft.minute`
- **ID:** FM-02
- **Category:** equivalence
- **Risk:** wrong value shown to the user, or the two selects transposed
- **Input that reveals it:** mount with `with-time`, inspect the two `bds-select` values inside `[slot="content-band"]`
- **Observed current behavior:** `renderTimeSelector.tsx:42-85` renders hour then minute, each `value={toTwoDigits(...)}`
- **Recommended contract:** first select's value is `draft.hour` zero-padded, second is `draft.minute` zero-padded
- **Contract status:** confirmed
- **Why it matters:** core rendering contract of the whole feature
- **Covered by:** `bds-date-picker.time.spec.ts::'renders an hour and a minute select reflecting the current draft when withTime is true'`

### FM-03 | Changing the hour/minute select updates only `draft.hour`/`draft.minute`, never the committed `value`
- **ID:** FM-03
- **Category:** race-timing (draft-vs-committed boundary)
- **Risk:** a mid-edit time selection could leak into the public `value`/form submission before Apply
- **Input that reveals it:** open popover, change the hour select, read `component.value` before Apply
- **Observed current behavior:** `bds-date-picker.tsx:389-395` `handleHourChange`/`handleMinuteChange` only reassign `this.draft`
- **Recommended contract:** `value` (and `bdsChange`/`valueChange`) stay untouched until Apply
- **Contract status:** confirmed
- **Why it matters:** matches the picker's whole draft-until-Apply design already established for day selection
- **Covered by:** `bds-date-picker.time.spec.ts::'changing the hour select updates only the draft, leaving the committed value untouched'`

### FM-04 | `bds-select`'s own bubbling `bdsChange`/`valueChange` never reach the picker host as spurious events
- **ID:** FM-04
- **Category:** component-contract-bypass
- **Risk:** a consumer listening for `bds-date-picker`'s own `bdsChange`/`valueChange` would receive the inner select's raw string value instead — this is the exact bug Task 3 found and fixed
- **Input that reveals it:** attach a `bdsChange`/`valueChange` listener on the picker host, change the hour/minute select
- **Observed current behavior:** `renderTimeSelector.tsx:24-26,45-49,67-71` — both handlers call `event.stopPropagation()` before/inside the picker's own handler runs
- **Recommended contract:** the host-level listener sees zero events from internal select interaction (Apply is still the only path that emits)
- **Contract status:** confirmed
- **Why it matters:** protects a real, previously-shipped regression from recurring
- **Covered by:** `bds-date-picker.time.spec.ts::"does not let the inner select's bdsChange/valueChange reach the picker host"`

### FM-05 | Apply with `withTime=true` commits a UTC ISO datetime built from `draft.selectedDate` + `draft.hour`/`draft.minute` via `this.timezone`
- **ID:** FM-05
- **Category:** boundary
- **Risk:** wrong value committed to the form / wrong `bdsChange` payload
- **Input that reveals it:** select a day, change hour/minute, click Apply, inspect emitted `value`
- **Observed current behavior:** `bds-date-picker.tsx:411-416` calls `buildCommitValue(draft.selectedDate, draft.hour, draft.minute, withTime, timezone)`; `buildCommitValue` (pure function) already has coverage in `bds-date-picker.time-helpers.spec.ts`, but no component-level test drives this through the real Apply handler
- **Recommended contract:** emitted `value` matches `combineDateTimeToUTC` for the same inputs; two instances with different `timezone` and identical wall-clock draft produce different committed values
- **Contract status:** confirmed
- **Why it matters:** this is the integration seam the pure-function tests don't exercise — a wiring mistake (e.g. passing the wrong timezone prop) would not be caught by `time-helpers.spec.ts` alone
- **Covered by:** `bds-date-picker.time.spec.ts::'Apply commits a UTC ISO datetime matching combineDateTimeToUTC for the selected day and drafted time'`, `bds-date-picker.time.spec.ts::'produces different committed UTC values for two instances with different timezones and the same wall-clock selection'`

### FM-06 | Cancel discards any in-progress time-selector edits, reverting to the last committed value's hour/minute
- **ID:** FM-06
- **Category:** race-timing
- **Risk:** a user could Cancel and still have their unwanted time edit silently committed on next Apply if the draft weren't actually reset
- **Input that reveals it:** open with a committed `withTime` value, change hour/minute, click Cancel, reopen, inspect the selects again
- **Observed current behavior:** `bds-date-picker.tsx:419-422` `FOOTER_ACTION.CANCEL` calls `resetDraft(this.value, ...)`, discarding `this.draft`
- **Recommended contract:** after Cancel, the next open shows the last-committed hour/minute, not the abandoned edit
- **Contract status:** confirmed
- **Why it matters:** existing `events.spec.ts` only tests Cancel for day selection, not time — real gap
- **Covered by:** `bds-date-picker.time.spec.ts::'Cancel discards a drafted time change, reverting to the last committed hour/minute on reopen'`

### FM-07 | Opening the popover with an existing `withTime=true` committed `value` pre-populates hour/minute in the selects
- **ID:** FM-07
- **Category:** null-empty / equivalence
- **Risk:** stale or default (00:00) time shown instead of the actual committed time
- **Input that reveals it:** mount with a valid UTC ISO `value` and `with-time`, click the trigger, inspect the rendered selects
- **Observed current behavior:** `listenClickTrigger` (`bds-date-picker.tsx:349-356`) calls `resetDraft(this.value, this.withTime, this.timezone)`, which derives hour/minute via `extractDateTimeFromUTC` when the value is a valid UTC datetime (`draft-state.ts:56-58`)
- **Recommended contract:** the rendered hour/minute selects show the extracted values, not `00:00`
- **Contract status:** confirmed
- **Why it matters:** `resetDraft` itself is unit-tested in isolation; nothing currently confirms the component actually calls it with real committed state before render
- **Covered by:** `bds-date-picker.time.spec.ts::'opening with a committed UTC datetime value pre-populates the hour/minute selects'`

### FM-08 | `format` auto-switches to `'yyyy/MM/dd HH:mm'` on both the trigger field and popover header when `withTime=true` and `format` is left at its default
- **ID:** FM-08
- **Category:** equivalence
- **Risk:** time silently missing from the displayed value even though it's stored in `value`
- **Input that reveals it:** mount with `with-time`, no `format` prop, Apply a day+time, inspect `bdsField.value` and the popover header text
- **Observed current behavior:** `effectiveFormat` getter (`bds-date-picker.tsx:242-244`) substitutes `DEFAULT_DATE_TIME_FORMAT` when `this.format === DEFAULT_DATE_FORMAT`; both `syncFieldValue` and `render()`'s header text use `effectiveFormat`
- **Recommended contract:** both surfaces show `HH:mm` appended
- **Contract status:** confirmed
- **Why it matters:** explicit Task 3 acceptance criterion, currently exercised only at the pure-function level (`formatDraftForDisplay`/`formatValueForDisplay` in isolation), never through the real component + real prop defaults
- **Covered by:** `bds-date-picker.time.spec.ts::'auto-switches the trigger field display to include HH:mm when withTime is true and format is unset'`

### FM-09 | `withTime=false` leaves `format`'s default behavior completely unchanged (regression guard)
- **ID:** FM-09
- **Category:** equivalence
- **Risk:** the Phase 2 auto-switch logic accidentally affecting Phase 1 callers
- **Input that reveals it:** mount with `withTime=false` (default), no `format`, inspect displayed format
- **Observed current behavior:** `effectiveFormat` short-circuits to `this.format` (the plain `DEFAULT_DATE_FORMAT`) whenever `withTime` is false
- **Recommended contract:** unchanged `'yyyy/MM/dd'` — no `HH:mm`
- **Contract status:** confirmed
- **Why it matters:** direct regression guard named in Task 3/5's own acceptance criteria
- **Covered by:** already covered — `bds-date-picker.variants.spec.ts::'falls back to the default yyyy/MM/dd format when none is provided'` exercises the non-withTime default path; no conflict, this pre-existing test's assertion matches the row's contract

### FM-10 | An explicit `format` identical to the literal default string cannot be distinguished from "unset" by the current implementation
- **ID:** FM-10
- **Category:** boundary
- **Risk:** a consumer who explicitly passes `format="yyyy/MM/dd"` alongside `with-time` expecting no time suffix (per the documented "explicit format always wins, even one identical to the default" promise) will silently get the auto-switched `HH:mm` version instead
- **Input that reveals it:** mount with `with-time` and `format="yyyy/MM/dd"` (the exact literal default) set explicitly; compare against mounting with `with-time` and no `format` at all — both produce identical `effectiveFormat` output today, because the check is `this.format === DEFAULT_DATE_FORMAT`, which cannot tell "prop never set" apart from "prop set to the same string"
- **Observed current behavior:** `bds-date-picker.tsx:242-244` — single equality check, no "was this prop explicitly passed" tracking
- **Recommended contract:** **Ruled 2026-08-26 (human decision, option 2 — real fix, not a documented limitation):** `format` needs genuine prop-provenance tracking so an explicitly-set `format` — even one identical to `DEFAULT_DATE_FORMAT` — is distinguishable from `format` left unset, honoring Task 3's original plan promise literally. Business reason: this is a public-API contract the plan already committed to; silently downgrading it to "current behavior is the spec" would be exactly the kind of bug-as-contract promotion this pipeline exists to prevent. `frontend-subagent` is implementing the fix separately (not this subagent) — this row's test is written only once that fix has landed, against the corrected behavior.
- **Contract status:** confirmed
- **Why it matters:** public-API contract already committed to in the plan; a silent downgrade would encode the bug as the spec
- **Covered by:** `bds-date-picker.time.spec.ts::'keeps an explicit format identical to the default date-only format instead of auto-switching to include HH:mm'` — written 2026-08-26 against the corrected implementation (`format` is now `@Prop() readonly format?: string`, `effectiveFormat` checks `this.format !== undefined`)

### FM-11 | `bds-popover`'s `content-band` slot only renders its wrapper `<div>` when content is actually assigned to that slot
- **ID:** FM-11
- **Category:** null-empty
- **Risk:** an empty `.popover-content-band` wrapper would still take up layout space (border/padding) for the two other consumers that never use this slot
- **Input that reveals it:** mount a bare `bds-popover` with no `[slot="content-band"]` child; separately mount one with such a child
- **Observed current behavior:** `bds-popover.tsx:679-683` — `{this.hasContentBand && (<div class="popover-content-band">...)}`; `hasContentBand` computed via `hasSlotContent(this.el, 'content-band')` in `componentWillLoad` (`bds-popover.tsx:623-626`), which is a plain `querySelector('[slot="content-band"]') !== null` — no mock-doc reflection gotcha since a slot name is passed
- **Recommended contract:** wrapper element present iff content-band content exists; absent otherwise — zero behavior change for `bds-select`/`bds-dropdown`, the other two consumers, which never assign to this slot
- **Contract status:** confirmed
- **Why it matters:** currently zero coverage in any `bds-popover` spec file, explicitly called out in Task 5's own scope text
- **Covered by:** `bds-popover-basics.spec.ts::'renders the content-band wrapper when content is assigned to the content-band slot'`, `bds-popover-basics.spec.ts::'renders no content-band wrapper when no content is assigned to that slot'`

### FM-12 | `override componentWillLoad()` still calls `super.componentWillLoad()`, so `anchoredMixin`'s own setup (positioning) is intact
- **ID:** FM-12
- **Category:** component-contract-bypass
- **Risk:** a future edit to `bds-popover.tsx:623-626` that drops the `super.componentWillLoad()` call would silently break `openPopover()`/positioning for every consumer of `bds-popover` in the whole design system — this exact bug shipped once already (Task 4's status note)
- **Input that reveals it:** mount `bds-popover`, call `openPopover()`, assert it actually becomes visible (not just that no exception was thrown)
- **Observed current behavior:** `bds-popover.tsx:623-626` — `super.componentWillLoad()` is called before `this.hasContentBand = ...`
- **Recommended contract:** `openPopover()` continues to work end-to-end (visibility flips, position machinery runs) regardless of the `content-band` slot-detection addition
- **Contract status:** confirmed
- **Why it matters:** explicit regression guard named in Task 5's own scope text, protecting against a bug that already shipped once during this same task
- **Covered by:** `bds-popover-basics.spec.ts::'still opens and becomes visible via openPopover, confirming anchoredMixin componentWillLoad is not shadowed'`

### FM-13 | `resetDraft`'s malformed/mismatched-value fallback (`withTime=true` + a non-UTC-datetime committed `value`)
- **ID:** FM-13
- **Category:** null-empty
- **Risk:** `NaN`/`Invalid Date` propagating into the hour/minute selects, or a thrown exception, if `withTime` is toggled on after a v1-style naive value was already committed
- **Input that reveals it:** `resetDraft('2026-08-24', true, 'UTC')` — a naive date string, not a UTC datetime
- **Observed current behavior:** `draft-state.ts:56-62` falls back to `hour: 0, minute: 0`, keeping `selectedDate` if it parses as a naive ISO date
- **Recommended contract:** same as observed — no throw, default `00:00`
- **Contract status:** confirmed
- **Why it matters:** explicit Task 3 acceptance criterion
- **Covered by:** already covered — `bds-date-picker.time-helpers.spec.ts::'resetDraft falls back to 00:00 for a stale naive-date value when withTime=true'`; assertion matches this row's recommended contract exactly, no conflict

### FM-14 | Default (value-less) draft always defaults `hour`/`minute` to `00:00`, never blocking Apply on the user touching the time selects
- **ID:** FM-14
- **Category:** null-empty
- **Risk:** Apply silently blocked, or a `NaN` committed, for a fresh `withTime` picker the user never touches the time selects on
- **Input that reveals it:** `resetDraft('', true, 'UTC')`
- **Observed current behavior:** `draft-state.ts:52-54` returns `{ selectedDate: null, hour: 0, minute: 0 }`
- **Recommended contract:** same as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 3 acceptance criterion
- **Covered by:** already covered — `bds-date-picker.time-helpers.spec.ts::'resetDraft defaults to 00:00 with no committed value'`; no conflict

### FM-15 | The hour/minute selects use the `labels?.hour`/`labels?.minute` override mechanism, not hardcoded strings
- **ID:** FM-15
- **Category:** equivalence
- **Risk:** consumer-supplied i18n labels silently ignored
- **Input that reveals it:** mount with `with-time` and a custom `labels={{ hour: 'H', minute: 'M' }}`
- **Observed current behavior:** `renderTimeSelector.tsx:37,55,77` — `resolvedLabels = { ...DEFAULT_FOOTER_LABELS, ...labels }`, applied to each `bds-text-field`'s `label`
- **Recommended contract:** custom labels shown, defaulting to `'Hour'`/`'Minute'` when not overridden
- **Contract status:** confirmed
- **Why it matters:** existing `events.spec.ts` only tests footer button label overrides (`clean`/`cancel`/`apply`), not `hour`/`minute` — real, previously untracked gap
- **Covered by:** `bds-date-picker.time.spec.ts::'applies custom hour/minute labels from the labels prop onto the inner fields'`, `bds-date-picker.time.spec.ts::'falls back to the default Hour/Minute labels when none are provided'`

### FM-16 | `disabled` on the picker disables both hour/minute inner `bds-text-field`s
- **ID:** FM-16
- **Category:** component-contract-bypass
- **Risk:** a disabled picker still lets the user change the time via the still-enabled inner fields
- **Input that reveals it:** mount `disabled` + `with-time`, inspect the two `bds-text-field`s inside the time selector
- **Observed current behavior:** `renderTimeSelector.tsx:56,78` — `disabled={disabled}` forwarded from the `params.disabled` argument, which `bds-date-picker.tsx:472` sets to `this.isDisabled`
- **Recommended contract:** both inner fields disabled when the picker is disabled
- **Contract status:** confirmed
- **Why it matters:** existing `variants.spec.ts` "disables all three footer buttons" test covers the footer but not the time selector — real gap
- **Covered by:** `bds-date-picker.time.spec.ts::'disables both the hour and minute inner fields when the picker is disabled'`

### FM-17 | `compareDates`'s exact-equality return value (`0`) is what makes one-sided `min`/`max` bound checks inclusive
- **ID:** FM-17
- **Category:** boundary
- **Risk:** an off-by-one in a future edit to `isDateOutOfBounds`'s `< 0` / `> 0` comparisons could silently exclude the boundary day itself
- **Input that reveals it:** a date exactly equal to `min` or exactly equal to `max`
- **Observed current behavior:** `date-math.ts:42-54` `compareDates` returns exactly `0` for equal instants; `grid.ts:29-43` `isDateOutOfBounds` only excludes on strict `< 0` (before min) / `> 0` (after max), so `0` is always treated as in-range
- **Recommended contract:** both bounds inclusive
- **Contract status:** confirmed
- **Why it matters:** this is the Task 13 "date-math bound-checking correctness at boundary edges" item — already fully proven at both the unit (`date-math.spec.ts`) and integration (`grid.spec.ts`) level, no gap found
- **Covered by:** already covered — `date-math.spec.ts::compareDates > 'returns exactly 0 when the dates represent the same instant'`, `grid.spec.ts::generateMonthGrid > 'disables cells before the min bound and enables cells on or after it'` / `'disables cells after the max bound and enables cells on or before it'` / `'disables cells outside both bounds and enables cells within them, inclusive of both boundaries'`. No conflict; `date-math.spec.ts` left unmodified for this task.

### FM-18 | A disabled current-month day cell never emits `bdsDayClick` at the `bds-calendar-grid` unit level
- **ID:** FM-18
- **Category:** component-contract-bypass
- **Risk:** the grid's own inertness guard could be untested at the unit level even though picker-level integration tests happen to show the committed `value` doesn't change — that could mask the guard actually living in the wrong place (e.g. only enforced by the picker's Apply logic, not the grid itself)
- **Input that reveals it:** click a current-month `<td>` whose `cell.isDisabled` is `true`
- **Observed current behavior:** `bds-calendar-grid.tsx:66-72` `handleDayClick` returns early when `cell.isDisabled`, before `bdsDayClick.emit(...)` runs
- **Recommended contract:** zero `bdsDayClick` emissions for a disabled-cell click
- **Contract status:** confirmed
- **Why it matters:** existing coverage only proved this indirectly (`bds-date-picker.variants.spec.ts`'s "does not update the draft selection when a disabled day cell is clicked", now moved to `bds-date-picker.minmax.spec.ts`) — real gap at the `bds-calendar-grid` unit level, the file this task's own scope names
- **Covered by:** `bds-calendar-grid.variants.spec.ts::'does not emit bdsDayClick when a disabled current-month cell is clicked'`

### FM-19 | A committed value's day cell renders as both selected and disabled when it falls outside a since-tightened range
- **ID:** FM-19
- **Category:** null-empty / boundary
- **Risk:** a picker mounted with a `value` now outside `min`/`max` (bounds tightened after the value was set, or set together at mount) could either silently drop the selection highlight or throw, instead of showing both states at once
- **Input that reveals it:** mount with `value` + a `min`/`max` combination that excludes it, open the popover
- **Observed current behavior:** `bds-calendar-grid.tsx:74-82` `dayCellClassMap` computes `--selected` (`cell.isoDate === this.selectedDate`) and `--disabled` (`cell.isDisabled`) independently — nothing suppresses one when the other is true
- **Recommended contract:** the cell carries both classes simultaneously; no throw, no silently-dropped selection
- **Contract status:** confirmed
- **Why it matters:** this is the Task 13 "out-of-range initial `value` handling" item at the calendar-grid rendering layer — untested before this task
- **Covered by:** `bds-date-picker.minmax.spec.ts::"renders the committed value's day cell as both selected and disabled when it falls outside a tightened range"`

### FM-20 | An out-of-range value at mount is not visually flagged as an error until an actual validation attempt occurs
- **ID:** FM-20
- **Category:** race-timing
- **Risk:** a consumer would see red/error UI immediately on page load for a value merely stored out-of-range (e.g. loaded from a stale draft) before the user has done anything — a jarring, premature error state
- **Input that reveals it:** mount with `value` + `min`/`max` such that `rangeUnderflow`/`rangeOverflow` is true; inspect `field.error` before dispatching any `invalid` event or calling `checkValidity`/`reportValidity`
- **Observed current behavior:** `bds-date-picker.tsx:155` `isInvalid` only flips `true` inside `@Listen('invalid')`'s `handleInvalid` (line 248-253) — never set during `componentWillLoad`/`componentDidLoad`; `syncFieldError` (line 255-258) reads `this.isInvalid`, so the field stays `error=false` until a real validation attempt
- **Recommended contract:** `field.error` is `false` immediately after mount despite the underlying `ElementInternals` validity already being invalid; only flips `true` once `handleInvalid` runs
- **Contract status:** confirmed
- **Why it matters:** the other half of the Task 13 "out-of-range initial `value` handling" item — the existing suite proved the validator surfaces `rangeUnderflow`/`rangeOverflow` to `ElementInternals` on an out-of-range mount, but never proved the field stays visually calm until a real attempt; real gap
- **Covered by:** `bds-date-picker.minmax.spec.ts::'does not flag the field as an error immediately on mount with an out-of-range value, before any validation attempt'`

### FM-21 | A malformed/unparseable `min` or `max` string is treated as unbounded, not as a thrown error or an accidental always-disabled state
- **ID:** FM-21
- **Category:** null-empty
- **Risk:** a consumer typo (e.g. `min="2026-13-40"`) could crash the component or silently disable every day, instead of the presumably-intended safe fallback
- **Input that reveals it:** mount with `min="not-a-date"` (or `max`)
- **Observed current behavior:** `bds-date-picker.tsx:296-304` `minDate`/`maxDate` getters return `undefined` unless `isValidNaiveISODate` passes first — the same defensive pattern already used for `value` in `warnIfInvalidValue`
- **Recommended contract:** no throw; the malformed bound is treated as absent (unbounded on that side)
- **Contract status:** confirmed
- **Why it matters:** audit-found gap the plan's Task 13 list doesn't name explicitly, but falls under the same "date-math bound-checking correctness" umbrella — a malformed bound is the most likely real-world mistake to hit this code path
- **Covered by:** `bds-date-picker.minmax.spec.ts::'treats a malformed min value as unbounded rather than throwing or disabling every day'`, `bds-date-picker.minmax.spec.ts::'treats a malformed max value as unbounded rather than throwing or disabling every day'`

### FM-22 | `watchRange`'s already-invalid re-sync branch flips the field's error state back off once a range change makes the value valid again (and keeps it on when it doesn't)
- **ID:** FM-22
- **Category:** race-timing
- **Risk:** a field already showing an error (post-validation-attempt) for an out-of-range value could keep showing that error forever even after the consumer widens `min`/`max` to make the same value valid again — or the inverse, silently clear a still-invalid error
- **Input that reveals it:** trigger an `invalid` event against an out-of-range value (flips `isInvalid`/`field.error` to `true`), then change `min`/`max` after mount — once to a bound that now includes the value, once to a bound that still excludes it
- **Observed current behavior:** `bds-date-picker.tsx:226-234` `watchRange`'s `if (this.isInvalid) { this.isInvalid = !valid; this.syncFieldError(); }` branch — uncovered by any test before this task (confirmed via `--coverageReporters=text` showing lines 230-233 uncovered pre-fix)
- **Recommended contract:** `field.error` tracks the live validity on every `min`/`max` change once a validation attempt has already occurred, in both directions
- **Contract status:** confirmed
- **Why it matters:** direct coverage-gate gap found via the actual coverage report, not just a plan-list item — the exact kind of gap this task's own coverage-measurement step exists to catch
- **Covered by:** `bds-date-picker.minmax.spec.ts::'clears the field error once a widened min/max range makes an already-flagged value valid again'`, `bds-date-picker.minmax.spec.ts::'keeps the field flagged as an error when a narrowed max still excludes an already-flagged value'`

---

## Reconciliation against Task 13's stated unit-test list

Task 13's list ("date-math bound-checking correctness at boundary edges (inclusive min/max); disabled-cell rendering
and inertness (no click, tabindex="-1"); whole-month-disabled nav-guard behavior; rangeUnderflow/rangeOverflow
validators surfacing errorMessage/invalid state; out-of-range initial value handling") maps onto FM-17 through FM-22
above. FM-17 (boundary inclusivity) and the nav-guard behavior were already fully covered by Task 10/Task 11's
pre-existing suites (`date-math.spec.ts`, `grid.spec.ts`, and the min/max nav-guard tests moved into
`bds-date-picker.minmax.spec.ts`) — no plan-listed item assumed a `pending-decision` row was settled, since none of
FM-17 through FM-22 ever reached `pending-decision`.

Failure modes the audit found that the plan's list doesn't explicitly name: FM-18 (click-inertness specifically
untested at the `bds-calendar-grid` unit level, as opposed to proven only indirectly through a picker-level
integration test), FM-21 (malformed `min`/`max` string handling), and FM-22 (the `watchRange` already-invalid
re-sync branch, found via the actual coverage report showing lines 230-233 uncovered before this task's tests were
added — not visible from reading the plan or the validators alone).

## Pending-decision rows requiring a ruling before any test is written for them

None — FM-17 through FM-22 (Task 13's min/max additions) are all `confirmed` and carry a `Covered by` entry, same as
the pre-existing FM-01 through FM-16 rows from Task 5.

---

## Reconciliation against Task 5's stated unit-test list

Task 5's list ("zone conversion...; withTime=false naive-date regression; withTime=true UTC computation, timezone
override, pre-population, Cancel discarding time draft; resetDraft's fallback...; format auto-switch...; a11y (Tab
reachability, labeling); keyboard regression") maps cleanly onto FM-01 through FM-09, FM-13, FM-14 above, plus the
`content-band`/mixin-shadowing text (FM-11, FM-12). No plan-listed item assumes a `pending-decision` row is already
settled, **except** implicitly: the plan's "format auto-switch... explicit format always overriding the auto-switch"
line is the exact acceptance criterion FM-10 shows the implementation can't fully satisfy for the identical-value edge
case — the plan's list doesn't ask for that specific edge case explicitly, so it doesn't block writing the general
auto-switch/override tests (FM-08, and a separate confirmed non-identical-explicit-format-override test), only FM-10's own edge case.

Failure modes the audit found that the plan's list omits: FM-04 (event-name-collision stopPropagation regression
guard — already fixed once, worth locking in), FM-15 (hour/minute label override — the plan groups this under
"labeling" a11y but doesn't call out the labels-prop override specifically), FM-16 (disabled forwarding to the time
selector's own fields specifically, as opposed to the footer buttons the existing suite already covers).

## Pending-decision rows requiring a ruling before any test is written for them

None — all 16 rows are `confirmed` and carry a `Covered by` entry. FM-10 was the only row that reached this catalog
in `pending-decision` state; resolved 2026-08-26 (human ruling: option 2, real fix over documented limitation — see
FM-10's own row for the full decision and reasoning). This section is kept as a record that the catalog went through
a real pending-decision cycle, not evidence that one is still open — check each row's own `Contract status` as the
source of truth, not this summary.

---

## Extension — 2026-08-28, Task 15e (`calendarType`, Phase 3.5)

Extending the existing catalog per "Existing component under a new plan version" — audited `bds-date-picker.tsx` as
it stands today (post-Task 15c) for the `calendarType` feature specifically, not re-auditing Phase 1/2 rows above.

### FM-23 | `calendarType` defaults to `'default'` and is validated against the three declared values
- **ID:** FM-23
- **Category:** boundary
- **Risk:** an unrecognized or unset `calendar-type` attribute silently falling through to an unhandled render branch
- **Input that reveals it:** mount with no `calendar-type` attribute at all
- **Observed current behavior:** `bds-date-picker.tsx:125` — `@Prop() readonly calendarType: CalendarType = 'default'`; `componentWillLoad` (`:185`) calls `validatePropValue(Object.values(CALENDAR_TYPE), CALENDAR_TYPE.DEFAULT, ...)`
- **Recommended contract:** an unset `calendar-type` resolves to `'default'` at the instance level
- **Contract status:** confirmed
- **Why it matters:** every pre-existing spec file's `renderDatePicker()`/local helpers now inject `calendar-type="basic"` specifically because this default changed away from `'basic'` — the default itself has no dedicated assertion anywhere
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'defaults calendarType to \'default\' when the attribute is unset'`

### FM-24 | `default` mode commits a day click immediately and closes the popover, bypassing the draft/Apply flow
- **ID:** FM-24
- **Category:** race-timing
- **Risk:** a `default`-mode consumer would see no Apply step at all if this weren't wired, or (the opposite bug) would see the draft update but the value stay stale if the commit path were only reachable through the footer
- **Input that reveals it:** open a `calendar-type="default"` picker, click a day cell, inspect `value`/`bdsChange` and popover visibility without touching any footer
- **Observed current behavior:** `bds-date-picker.tsx:512-521` `handleDayClick` — after `selectDay`, `if (this.isDefaultCalendarType && this.draft.selectedDate !== null)` calls `commitValue(buildCommitValue(..., false, ...))` then `closePopover()`
- **Recommended contract:** one day click both commits `value` (emitting `bdsChange`/`valueChange`) and closes the popover, with no separate Apply step
- **Contract status:** confirmed
- **Why it matters:** this is `default` mode's entire reason for existing (per Figma's "Default" naming) — currently zero coverage
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'commits the clicked day and closes the popover immediately in default mode'`

### FM-25 | `default` mode renders no header, footer, or close button regardless of other props
- **ID:** FM-25
- **Category:** equivalence
- **Risk:** a prop combination (e.g. `required`, `with-time`) accidentally re-enabling chrome that `default` mode is supposed to always suppress
- **Input that reveals it:** mount `calendar-type="default"` with `required`, `with-time`, and `labels` all set; open the popover
- **Observed current behavior:** `bds-date-picker.tsx:575,583-585` — `showChrome = !this.isDefaultCalendarType`; `header`/`closable`/`footer` on `bds-popover` are all bound to the same single `showChrome` flag, independent of any other prop
- **Recommended contract:** no `.popover-header`, `.popover-header__close`, or `.popover-footer` element exists, for any prop combination, whenever `calendarType === 'default'`
- **Contract status:** confirmed
- **Why it matters:** `showChrome` is a single shared flag — a future edit adding a new prop-gated chrome branch could easily miss guarding it the same way; this locks the current "always off in default" contract in place
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'renders no header, footer, or close button in default mode regardless of other props'`

### FM-26 | `default` mode dismissal via popover close (no day clicked) leaves `value` untouched and emits nothing
- **ID:** FM-26
- **Category:** race-timing
- **Risk:** since `default` mode has no Cancel button, an accidental outside-click/Escape dismissal could either leak a half-selected day into `value` or throw, if the close path isn't fully independent of the commit path
- **Input that reveals it:** open a `default`-mode picker with an existing committed `value`, close the popover directly (simulating outside-click/Escape dismissal) without clicking a day
- **Observed current behavior:** dismissal only ever routes through `bds-popover`'s own `closePopover()`/light-dismiss machinery; `bds-date-picker.tsx` has no listener that commits on close — only `handleDayClick` (FM-24) ever calls `commitValue`
- **Recommended contract:** closing without a day click leaves `value` (and `bdsChange`/`valueChange`) exactly as they were before opening
- **Contract status:** confirmed
- **Why it matters:** `default` mode's whole selection model depends on commit being tied strictly to day click, never to close-as-such — worth locking in explicitly since there's no footer Cancel to fall back on
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'closing the popover without selecting a day leaves value unchanged in default mode'`

### FM-27 | `withTime` is fully force-ignored under `calendarType === 'default'` — no time selector, correct naive-date display, no spurious invalid-value warning, and min/max validation still fires
- **ID:** FM-27
- **Category:** equivalence
- **Risk:** four distinct regressions bundled in one prop combination: (a) a stray time selector rendering despite no chrome, (b) the trigger field showing a blank display after a `default`+`with-time` commit (the QA-found bug — `formatValueForDisplay` being called with the raw `withTime` prop instead of the mode-aware `effectiveWithTime` would treat the naive committed date as a malformed UTC datetime and blank it), (c) a spurious "not a valid UTC ISO datetime" console warning from the same root cause in `warnIfInvalidValue`, (d) `min`/`max` `rangeUnderflow`/`rangeOverflow` going inert because `valueDate` misparses the naive value as a UTC datetime and returns `undefined` (the QA-found validation-inert bug)
- **Input that reveals it:** mount `calendar-type="default" with-time min="…" max="…"`, click an out-of-range day, inspect the trigger field's displayed text, `console.warn` calls, and `internals.setValidity` calls via `formAssociatedCallback()`
- **Observed current behavior:** `effectiveWithTime` getter (`:299-301`) forces `false` whenever `isDefaultCalendarType`; it feeds `effectiveFormat` (`:303`), `syncFieldValue` (`:308-314`), `warnIfInvalidValue` (`:316-325`), and `valueDate` (`:339-345`) uniformly — all four surfaces are already routed through the same mode-aware getter, so the four regressions describe what breaks if any one of those call sites were reverted to the raw `this.withTime`, not current behavior
- **Recommended contract:** under `default`+`with-time`: no `[slot="content-band"]`/time selector renders (chrome-gated, same as FM-25); the trigger field shows the correct naive-date text after a commit; zero "not a valid UTC ISO datetime" warnings; `rangeUnderflow`/`rangeOverflow` still surface correctly to `ElementInternals`
- **Contract status:** confirmed
- **Why it matters:** both QA-found bugs (blank display, inert validation) were previously invisible to the unit suite — these are the regression tests closing that gap, per the plan's own framing
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'renders no time selector when with-time is set alongside default calendar type'`, `bds-date-picker.calendartype.spec.ts::'displays the correct naive-date text on the trigger field after a default-mode commit with with-time set (regression)'`, `bds-date-picker.calendartype.spec.ts::'does not warn about an invalid UTC datetime after a default-mode commit with with-time set (regression)'`, `bds-date-picker.calendartype.spec.ts::'still surfaces rangeUnderflow/rangeOverflow against a default-mode value with with-time set (regression)'`

### FM-28 | `componentWillLoad` logs a `with-time` + `default` warning exactly once, and never for `basic`/`expanded` or when `with-time` is unset
- **ID:** FM-28
- **Category:** equivalence
- **Risk:** either a missing warning (consumer silently loses time functionality with no clue why) or a false-positive warning firing for a perfectly valid `basic`/`expanded` + `with-time` combination
- **Input that reveals it:** four mounts: `default`+`with-time`, `default` without `with-time`, `basic`+`with-time`, `expanded`+`with-time`
- **Observed current behavior:** `bds-date-picker.tsx:186-191` — `if (this.isDefaultCalendarType && this.withTime) { this.logger.warn(...) }`, called once from `componentWillLoad`
- **Recommended contract:** warning fires only for the `default`+`with-time` combination; silent in the other three
- **Contract status:** confirmed
- **Why it matters:** the plan explicitly calls this "not a fully-silent no-op" — a documented, testable console contract, not just an internal implementation detail
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'warns once when with-time is set alongside default calendar type'`, `bds-date-picker.calendartype.spec.ts::'does not warn when calendarType is default and with-time is unset'`, `bds-date-picker.calendartype.spec.ts::'does not warn when with-time is set alongside basic or expanded calendar type'`

### FM-29 | `required`/`min`/`max` validation is identical between `default` and `basic` mode on a real validation attempt
- **ID:** FM-29
- **Category:** equivalence
- **Risk:** validation accidentally becoming footer-dependent (e.g. only wiring up on Apply) would silently disable required/range enforcement for `default` mode, which has no Apply step at all
- **Input that reveals it:** mount `calendar-type="default"` with `required`/`min`/`max` violated, dispatch a real `invalid` event (or call `checkValidity()`), compare `field.error`/validity against the same setup under `calendar-type="basic"`
- **Observed current behavior:** `updateValidity`/`validators`/`@Listen('invalid')` (`:272-282,375-409`) have no dependency on `showChrome`/`isDefaultCalendarType` at all — the field-anchored, attempt-triggered design is uniform across all three `calendarType` values
- **Recommended contract:** identical `field.error`/validity outcomes in `default` and `basic` mode for the same violated constraint and the same triggering attempt
- **Contract status:** confirmed
- **Why it matters:** explicit plan acceptance criterion for this task — confirms Task 15c's field-anchored design generalizes correctly to the no-footer mode
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'validates required/min/max identically in default and basic mode on a real validation attempt'`

### FM-30 | Explicit `calendar-type="basic"` reproduces every pre-`calendarType` behavior unchanged
- **ID:** FM-30
- **Category:** equivalence
- **Risk:** the Task 15c retrofit (injecting `calendar-type="basic"` into every pre-existing spec's markup) could mask a real behavior change if `basic` itself drifted from the original pre-`calendarType` contract
- **Input that reveals it:** mount `calendar-type="basic"` explicitly and drive the same draft-until-Apply day-selection flow the pre-`calendarType` suite already exercises
- **Observed current behavior:** `showChrome`/`isDefaultCalendarType` treat `'basic'` and `'expanded'` identically (`showChrome = !this.isDefaultCalendarType`); `handleDayClick`'s immediate-commit branch is gated on `isDefaultCalendarType` alone, so `'basic'` always takes the draft-then-Apply path
- **Recommended contract:** `calendar-type="basic"` shows full header/footer/close-button chrome and requires an explicit Apply to commit — a direct regression guard, not just an implicit assumption baked into every other spec file's helper
- **Contract status:** confirmed
- **Why it matters:** every other spec file's coverage of `basic`-mode behavior is incidental (a side effect of the retrofit helper's default); this is the one test that asserts it as an explicit, named contract
- **Covered by:** `bds-date-picker.calendartype.spec.ts::'calendar-type=\"basic\" renders full chrome and requires Apply to commit, unchanged from pre-calendarType behavior'`

## Reconciliation against Task 15e's stated unit-test list

Task 15e's list maps cleanly onto FM-23 through FM-30 above. No plan-listed item assumes a `pending-decision` row is
already settled — none of FM-23 through FM-30 ever reached `pending-decision`. The plan's own item 8 ("check whether
any un-patched `newSpecPage(...)` calls in basics/events/variants specs actually need `calendar-type=\"basic\"`") is
a file-audit task, not a failure mode in its own right, and is tracked in the task handoff instead of as a catalog row.

## Pending-decision rows requiring a ruling before any test is written for them

None — all of FM-23 through FM-30 are `confirmed` and carry a `Covered by` entry.

---

## Extension — 2026-09-03, Task 21 (Phase 4, range mode consolidated unit tests)

Extending the existing catalog per "Existing component under a new plan version" — audited `bds-date-picker.tsx`,
`bds-calendar-grid.tsx`, `utils/draft-state.ts`, `utils/value-mapping.ts`, and `services/date-engine/grid.ts` as they
stand today (post-Task 19q) for the range-mode feature Phase 4 built across Tasks 16-19r, not re-auditing the
Phase 1-3.5 rows above. Confirmed via grep before writing anything: `bds-date-picker.range.spec.ts` does not exist
yet (per the 2026-09-02 note left in the plan itself); zero existing spec file anywhere in this component's
`__test__/` directories references `selectRangeDay`, `resetRangeDraft`, `serializeRangeValue`, `isRangeValue`,
`bdsDayHover`/`bdsGridLeave`/`previewEnd` at the `bds-date-picker` orchestrator level, `calendarType="expanded"`, or
committed (non-preview) `isInRange`/`isRangeStart`/`isRangeEnd` day-state classes at the `bds-calendar-grid` level —
all of Phase 4's core logic is currently exercised by nothing but its own type system and manual QA.

### FM-31 | The `value`/`bdsChange`/`valueChange` union type accepts and emits both shapes correctly, and a shape mismatch (range mode fed a string value, or vice versa) is treated as absent rather than thrown
- **ID:** FM-31
- **Category:** equivalence / null-empty
- **Risk:** a consumer migrating between single-date and range mode, or accidentally leaving a stale `value` of the wrong shape, could crash the component or silently corrupt the draft instead of a clean "treat as unset" fallback
- **Input that reveals it:** mount `range` with an initial `value="2026-08-05"` (a plain string, the wrong shape for range mode); mount without `range` with an initial `value={{ start: '2026-08-05', end: '2026-08-10' }}` (the wrong shape for single-date mode); mount `range` with a valid `{ start, end }` initial value and confirm it hydrates the draft
- **Observed current behavior:** `rangeValue` getter (`bds-date-picker.tsx:560-562`) — `isRangeValue(this.value) ? this.value : null`; `resolveInitialDraft`/`resolveDraftDisplayMonth` both branch on `this.effectiveRange` and fall back to `resetRangeDraft(this.rangeValue ?? '')`/`resetDraft(this.stringValue, ...)` — a shape-mismatched `value` simply resolves to the "no value" empty draft on the wrong-mode side, no throw
- **Recommended contract:** range mode with a valid `{ start, end }` value hydrates `draft.rangeStart`/`draft.rangeEnd`; range mode with a plain string value (or single-date mode with an object value) is treated as unset, not thrown
- **Contract status:** confirmed
- **Why it matters:** zero coverage today for either the correct-shape happy path or the mismatched-shape defensive fallback — a real, previously invisible gap
- **Covered by:** `bds-date-picker.range.spec.ts::'hydrates rangeStart/rangeEnd from a valid initial { start, end } value in range mode'`, `bds-date-picker.range.spec.ts::'treats a string initial value as unset when range mode is enabled'`, `bds-date-picker.range.spec.ts::'treats an object initial value as unset when range mode is disabled'`

### FM-32 | `selectRangeDay`'s start/end/swap logic drives real day-click sequences identically under both `calendarType='basic'` and `'expanded'`
- **ID:** FM-32
- **Category:** equivalence / race-timing
- **Risk:** the documented "fresh selection resets both bounds; forward click extends end; backward-or-equal click swaps in a new start" contract could silently diverge between the two calendar types, or simply never be exercised at the real click-handler level (as opposed to `draft-state.ts`'s own doc comment, which is not itself a test)
- **Input that reveals it:** click day A then day B (B after A) — expect `rangeStart=A, rangeEnd=B`; click day A then day C (C before A) — expect `rangeStart=C, rangeEnd=null` (swap, not extend); click a complete range then click day D — expect a fresh `rangeStart=D, rangeEnd=null` (start-over, not a third bound); repeat the A→B sequence under `calendarType="expanded"` clicking B in the second calendar
- **Observed current behavior:** `selectRangeDay` (`utils/draft-state.ts:35-50`) — zero existing test coverage anywhere in the component's `__test__/` tree; `handleDayClick` (`bds-date-picker.tsx:337-351`) routes every `bdsDayClick` through it identically regardless of `calendarType`, and `renderCalendarPanel`'s two `bds-calendar-grid` instances both bubble the same `bdsDayClick` event type up to the same host listener
- **Recommended contract:** identical start/end/swap semantics regardless of which calendar (single, or either of the two `expanded` calendars) the click originated from
- **Contract status:** confirmed
- **Why it matters:** this is the actual selection logic a range-mode consumer depends on end-to-end; the plan's own Task 21 bullet names it explicitly and it currently has zero coverage
- **Covered by:** `bds-date-picker.range.spec.ts::'a forward second click sets rangeEnd, completing the range'`, `bds-date-picker.range.spec.ts::'a backward second click swaps in a new rangeStart instead of extending the range'`, `bds-date-picker.range.spec.ts::'clicking a day after a complete range starts a fresh range instead of extending it'`, `bds-date-picker.range.spec.ts::'produces the identical start/end/swap sequence when the second click lands in the expanded second calendar'`

### FM-33 | `expanded`'s dual-calendar navigation is permanently locked to consecutive months
- **ID:** FM-33
- **Category:** component-contract-bypass / boundary
- **Risk:** the whole point of Task 19m-3's fix — if the lock regressed, a user could navigate the two calendars into a non-consecutive, identical, or reversed state, defeating the entire dual-calendar range-picking UX
- **Input that reveals it:** mount `calendar-type="expanded"`, inspect the first calendar's Next button and the second calendar's Previous button (both must read `disabled` unconditionally, with no `min`/`max` set at all); click the first calendar's Previous button and confirm both calendars' displayed months shift back by exactly one; click the second calendar's Next button and confirm both shift forward by exactly one; repeat several times in combination and confirm the second calendar's month is always exactly one after the first's; separately, mount with a `min`/`max` window and confirm the first's Previous / second's Next still correctly disable at the boundary (nav-guard preserved on the two live buttons)
- **Observed current behavior:** `render()` (`bds-date-picker.tsx:730-753`) — first calendar's `nextDisabled: firstCalendarGuard.nextDisabled || this.isExpandedCalendarType` (always `true` under `expanded`, independent of `min`/`max`); second calendar's `prevDisabled: true` (hardcoded); second calendar's `nextDisabled: secondCalendarGuard.nextDisabled` (still min/max-guarded); first calendar's `prevDisabled: firstCalendarGuard.prevDisabled` (still min/max-guarded); `handleMonthNavigate` (`:381-387`) always shifts the single shared `displayYear`/`displayMonth` anchor by exactly one month regardless of which calendar's `bdsMonthNavigate` fired, and `secondDisplayYear`/`secondDisplayMonth` (`:583-589`) are always derived fresh as `anchor + 1` — there is no code path that can move the two calendars independently
- **Recommended contract:** exactly as observed — first Next and second Previous are unconditionally disabled from mount; the two remaining live buttons shift both calendars by the same one-month delta; the pair can never become non-consecutive
- **Contract status:** confirmed
- **Why it matters:** `calendarType="expanded"` has literally zero test coverage today (confirmed via grep — no spec file mounts it), despite an entire dedicated sub-task (19m-3) having shipped a bug fix for exactly this behavior
- **Covered by:** `bds-date-picker.range.spec.ts::'permanently disables the first calendar's Next and the second calendar's Previous button from mount'`, `bds-date-picker.range.spec.ts::'shifts both calendars back by one month when the first calendar's Previous is clicked'`, `bds-date-picker.range.spec.ts::'shifts both calendars forward by one month when the second calendar's Next is clicked'`, `bds-date-picker.range.spec.ts::'keeps the two calendars exactly one month apart through repeated alternating navigation'`, `bds-date-picker.range.spec.ts::'still disables the first calendar's Previous and the second calendar's Next at a min/max boundary'`

### FM-34 | Committed range day-state classes (`in-range`/`range-start`/`range-end`) render correctly at the `bds-calendar-grid` level, independent of the already-covered preview classes
- **ID:** FM-34
- **Category:** equivalence
- **Risk:** `bds-calendar-grid.variants.spec.ts` already covers the hover-preview `partial-*` classes (Task 19k) but has zero assertions on the committed range classes `dayCellClassMap` (`bds-calendar-grid.tsx:97-111`) also computes — a regression here (e.g. a class name typo, or the wrong `DayCell` field wired) would be invisible to the existing suite
- **Input that reveals it:** render a grid via `generateMonthGrid` with both `rangeStart`/`rangeEnd` set, inspect the exact three cells (start/interior/end) for `--range-start`/`--in-range`/`--range-end` respectively; render a grid with neither set and confirm zero cells carry any of the three classes
- **Observed current behavior:** `bds-calendar-grid.tsx:104-106` maps `cell.isInRange`/`cell.isRangeStart`/`cell.isRangeEnd` (already correctly computed by `grid.ts`'s `buildRangeFlags`, which has its own date-engine-level coverage per FM catalog precedent) onto `--in-range`/`--range-start`/`--range-end`; this component-level class-map wiring itself is untested
- **Recommended contract:** the range-start cell carries `--range-start` only, the range-end cell carries `--range-end` only, every strictly-interior cell carries `--in-range` only, and no cell carries more than one of the three simultaneously for a well-formed (non-degenerate) range
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("range day-state rendering... in isolation from single-date rendering"); mirrors the exact pattern the existing preview-class tests already established in the same file, just for the committed (non-preview) classes
- **Covered by:** `bds-calendar-grid.variants.spec.ts::'marks the range-start/interior/end cells with their own range-* classes'`, `bds-calendar-grid.variants.spec.ts::'renders no range-* classes when neither rangeStart nor rangeEnd is supplied'`

### FM-35 | `basic`'s single calendar renders identically to either of `expanded`'s two calendars for the same displayed month and draft
- **ID:** FM-35
- **Category:** equivalence
- **Risk:** `buildDisplayGrid`/`renderCalendarPanel` are shared between both calendar types, but nothing currently proves a `basic` picker's one calendar and an `expanded` picker's first calendar produce the same day-cell markup given the same year/month/range state — a future edit that special-cased one path could silently diverge them
- **Input that reveals it:** mount a `basic`+`range` picker and an `expanded`+`range` picker, both anchored to the same displayed month with the same committed range, and compare the rendered day-cell classes (`--in-range`/`--range-start`/`--range-end`/`--selected`/`--disabled`) cell-by-cell between the `basic` picker's sole calendar and the `expanded` picker's first calendar
- **Observed current behavior:** `renderCalendarPanel` (`helpers/renderCalendarPanel.tsx:29-48`) builds each calendar entry from the same `CalendarInstanceParams` shape regardless of count; `render()`'s first `calendars` push (`bds-date-picker.tsx:717-734`) uses the identical `buildDisplayGrid(...)` call signature whether or not a second entry is later pushed for `expanded`
- **Recommended contract:** byte-for-byte identical day-cell class output between `basic`'s one calendar and `expanded`'s first calendar, given identical displayed month/range/selection state
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet; the two code paths sharing one render helper is an implementation detail a consumer-facing test should lock in as an explicit contract, not leave as an assumption
- **Covered by:** `bds-date-picker.range.spec.ts::"renders the basic calendar identically to expanded's first calendar for the same displayed month and range"`

### FM-36 | Clean resets the range draft, commits an empty value, and leaves the popover open
- **ID:** FM-36
- **Category:** race-timing
- **Risk:** if Clean's popover-open behavior regressed to close (matching Cancel instead), a range-mode user would lose the "immediately start a new selection" UX the single-date mode already established and tested (Task 19n) — this is the exact behavior the plan calls out as needing its own distinct test, not folded into a generic bullet
- **Input that reveals it:** mount with a committed `{ start, end }` range value, open the popover, click Clean (footer label `'Clear'`), inspect `value`, `bdsChange`/`valueChange` payloads, `draft.rangeStart`/`draft.rangeEnd`, and whether `hidePopover` was called
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.CLEAN` branch (`bds-date-picker.tsx:416-422`) — `this.draft = this.effectiveRange ? resetRangeDraft('') : ...`; `this.previewEnd = null` when range; `this.commitValue('')`; **no** `closePopover()` call in this branch, matching the single-date Clean behavior already locked in by `bds-date-picker.events.spec.ts`'s `'Clean does not close the popover'` test
- **Recommended contract:** `draft.rangeStart`/`draft.rangeEnd` both become `null`; `value` becomes `''`; `bdsChange`/`valueChange` fire once each with `''`; the popover stays open (no `hidePopover` call)
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet demanding this be tested as its own distinct behavior, not merged with Cancel; zero range-mode coverage of either Clean or Cancel exists today
- **Covered by:** `bds-date-picker.range.spec.ts::'Clean resets the range draft and commits an empty value, leaving the popover open'`

### FM-37 | Cancel reverts the range draft to the last-committed `{ start, end }` (or empty, if none) and closes the popover
- **ID:** FM-37
- **Category:** race-timing
- **Risk:** the inverse of FM-36 — if Cancel's popover-close behavior regressed to stay open (matching Clean instead), or if it failed to actually revert an in-progress range edit, a user's abandoned edit could leak into the next open
- **Input that reveals it:** mount with a committed `{ start, end }` range value, open the popover, click a day to start a fresh in-progress selection (mutating the draft away from the committed value), click Cancel, inspect `value` (unchanged), `bdsChange` (not fired), whether `hidePopover` was called, and — reopening — that the draft shows the last-committed range again, not the abandoned edit; separately, repeat with no committed value at all (Cancel reverts to an empty draft)
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.CANCEL` branch (`bds-date-picker.tsx:407-415`) — `this.draft = this.effectiveRange ? resetRangeDraft(this.rangeValue ?? '') : ...`; `this.previewEnd = null` when range; `void this.bdsPopover?.closePopover()` unconditionally
- **Recommended contract:** `value`/`bdsChange` untouched; draft reverts to the last-committed range (or an empty range draft when nothing was ever committed); popover closes
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet demanding this be tested as its own distinct behavior from Clean; zero range-mode coverage exists today
- **Covered by:** `bds-date-picker.range.spec.ts::'Cancel reverts an in-progress range edit to the last-committed range and closes the popover'`, `bds-date-picker.range.spec.ts::'Cancel reverts to an empty range draft when nothing was ever committed'`

### FM-38 | Apply commits the correct `{ start, end }` shape identically regardless of `calendarType`, and is a no-op (but still closes) when only `rangeStart` is set
- **ID:** FM-38
- **Category:** equivalence / race-timing
- **Risk:** Apply's commit path could diverge between `basic`/`expanded`, or could commit a malformed/partial value (e.g. `{ start, end: null }`) if the mid-selection guard were missing
- **Input that reveals it:** complete a range (two clicks) under both `calendar-type="basic"` and `calendar-type="expanded"`, click Apply, compare the emitted `bdsChange`/`valueChange` detail shape; separately, click only one day (leaving `rangeEnd` null), click Apply, confirm no commit occurred but the popover still closed (mirroring the existing single-date "Apply with no draft selection still closes the popover" test)
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.APPLY` branch (`bds-date-picker.tsx:395-406`) — `calendarType` never appears in this branch's condition at all, only `this.effectiveRange`; the inner guard `this.draft.rangeStart !== null && this.draft.rangeEnd !== null` gates the commit, but `void this.bdsPopover?.closePopover()` runs unconditionally immediately after, regardless of whether that guard passed
- **Recommended contract:** identical `{ start, end }` emitted regardless of `calendarType`; a partial (single-bound) draft never commits but the popover still closes
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("Apply emitting the correct shape identically regardless of calendarType"); the partial-selection guard is the range-mode counterpart to an already-tested single-date behavior and deserves the same explicit lock-in
- **Covered by:** `bds-date-picker.range.spec.ts::'Apply commits the identical { start, end } shape under both basic and expanded calendarType'`, `bds-date-picker.range.spec.ts::'Apply with only rangeStart set does not commit but still closes the popover'`

### FM-39 | The hover-preview band's orchestrator-level wiring (`bdsDayHover`/`bdsGridLeave` → `previewEnd` state, shared across both `expanded` calendars) has zero coverage above the `bds-calendar-grid` unit level
- **ID:** FM-39
- **Category:** race-timing / component-contract-bypass
- **Risk:** `bds-calendar-grid.variants.spec.ts` already proves the grid renders `partial-*` classes correctly given a `previewEnd` prop, but nothing proves `bds-date-picker` itself correctly derives that prop from real hover/leave events, correctly guards it to only mid-selection range state, or correctly shares one `previewEnd` value across both `expanded` calendars — a wiring mistake here (e.g. the listener never attached, or gated on the wrong condition) would be invisible to the grid-level suite alone
- **Input that reveals it:** complete a `rangeStart`-only selection, hover a later day, confirm both calendars (under `expanded`) show the same preview band; hover a day before `rangeStart` and confirm no backward preview; hover `rangeStart` itself and confirm no preview; fire a real `mouseleave` on the grid and confirm the preview clears; click a day to complete the range and confirm the preview is cleared even without a `mouseleave`
- **Observed current behavior:** `@Listen('bdsDayHover') handleDayHover` (`bds-date-picker.tsx:353-367`) and `@Listen('bdsGridLeave') handleGridLeave` (`:369-372`) are the sole owners of `@State() previewEnd`; `handleDayClick` (`:342-344`) also resets `previewEnd` to `null` on every range-mode click; `render()` passes the same `previewEndDate` to both `buildDisplayGrid` calls when `expanded` (`:727,747`) — none of this is exercised by any existing `bds-date-picker` spec file (confirmed via grep, zero matches for `bdsDayHover`/`previewEnd` in that directory)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** real, previously invisible orchestration gap directly adjacent to the plan's named hover-preview feature (Task 19k), even though the plan's own Task 21 bullet list doesn't name it explicitly by that phrase — falls under the same "start/end selection... under both calendarType" and "range day-state rendering" umbrella the bullets do name, since the preview band is itself range day-state
- **Covered by:** `bds-date-picker.range.spec.ts::'shows a shared hover-preview band across both expanded calendars while only rangeStart is set'`, `bds-date-picker.range.spec.ts::'shows no preview band when hovering a day before rangeStart'`, `bds-date-picker.range.spec.ts::'shows no preview band when hovering rangeStart itself'`, `bds-date-picker.range.spec.ts::'clears the preview band on a real mouseleave of the grid'`, `bds-date-picker.range.spec.ts::'clears the preview band once a day click completes the range'`

### FM-40 | `rangeUnderflow`/`rangeOverflow` FACE validators are a deliberately inert no-op for range-mode values (min/max enforced only via UI cell-disabling, not FACE validity)
- **ID:** FM-40
- **Category:** component-contract-bypass
- **Risk:** without a locking test, a future edit to `valueDate`/`stringValue` (e.g. "fixing" it to also read range values) could silently start enforcing min/max validity for range mode in a way nothing else in the component was designed to support (no range-aware `valueDate` equivalent exists), or the reverse — a future edit could be assumed safe because "the validators already handle range" when they don't
- **Input that reveals it:** mount `range` with `min`/`max` set and a committed `{ start, end }` value straddling or exceeding those bounds, call `checkValidity()`/inspect `internals.validity`, confirm `rangeUnderflow`/`rangeOverflow` never flip regardless of the range value's actual relationship to `min`/`max`
- **Observed current behavior:** `valueDate` getter (`bds-date-picker.tsx:656-663`) reads `this.stringValue`, which is `''` for every range-mode `value` (`typeof this.value === 'string' ? this.value : ''`); the `rangeUnderflow`/`rangeOverflow` validators (`:640-647`) both short-circuit `true` whenever `value === undefined`, which is always the case here — this is an explicit, already-made engineering decision recorded in this plan's own Task 18a status note ("confirmed `rangeUnderflow`/`rangeOverflow` already no-op safely for range mode (no change needed there)"), not an undiscovered bug being newly promoted to spec
- **Recommended contract:** exactly as observed — `rangeUnderflow`/`rangeOverflow` never fire for a range-mode value, regardless of `min`/`max`; `valueMissing` (the one range-aware validator) continues to work correctly (already covered by FM's sibling `required`-forwarding tests, single-date side)
- **Contract status:** confirmed
- **Why it matters:** locks in an already-made, already-recorded design decision that currently has no regression test protecting it — exactly the "audit found a real coverage gap the plan's list didn't call out" case this catalog exists to catch, distinct from a fresh `pending-decision`
- **Covered by:** `bds-date-picker.range.spec.ts::'never surfaces rangeUnderflow/rangeOverflow for a range value, regardless of min/max'`

### FM-41 | A committed range value's FACE round-trip: `serializeRangeValue`'s comma-delimited form reaches `ElementInternals.setFormValue`, and the slotted field's own display syncs correctly
- **ID:** FM-41
- **Category:** null-empty / component-contract-bypass
- **Risk:** this is the exact bug found and fixed during Task 18a's manual QA (the range branch of `watchValue` originally skipped `syncFieldValue()`, leaving the slotted field independently invalid and blocking native form submission) — without a regression test, a similar future edit to `watchValue`/`formAssociatedCallback` could silently reintroduce it
- **Input that reveals it:** commit a range value via Apply, inspect `internals.setFormValue`'s call argument (expect the delimited string, not the raw object) and the slotted field's own displayed `value` (expect the formatted range text, not blank); separately, call `formAssociatedCallback()` directly with a pre-set range `value` and confirm the same serialized string is registered
- **Observed current behavior:** `watchValue`'s object branch (`bds-date-picker.tsx:225-234`) calls `setFormValue(this.internals, serializeRangeValue(next))` then `this.syncFieldValue()`; `formAssociatedCallback` (`:302-305`) calls `setFormValue(this.internals, this.rangeValue !== null ? serializeRangeValue(this.rangeValue) : this.stringValue)`; `serializeRangeValue` (`utils/value-mapping.ts:239-241`) returns `''` unless both `start`/`end` are non-empty
- **Recommended contract:** exactly as observed — `${start},${end}` reaches `ElementInternals`, the slotted field shows the formatted range text (via `syncFieldValue`'s `formatRangeForDisplay` branch), and an incomplete/empty range serializes to `''`
- **Contract status:** confirmed
- **Why it matters:** direct regression lock for a real, previously-shipped bug (Task 18a); zero test currently protects it in this component's own `__test__/` tree (`bds-date-picker.form.spec.ts` only covers the single-date string branch)
- **Covered by:** `bds-date-picker.range.spec.ts::'serializes a committed range value as a comma-delimited string for ElementInternals.setFormValue'`, `bds-date-picker.range.spec.ts::'syncs the slotted field's displayed value to the formatted range text after a range commit'`, `bds-date-picker.range.spec.ts::'formAssociatedCallback registers the serialized range string for a pre-set range value'`

### FM-42 | `expanded`+`range` renders two independent time selectors driven by the new per-bound `startHour`/`startMinute`/`endHour`/`endMinute` fields, each wired through the bound-aware `selectBoundHour`/`selectBoundMinute` selectors
- **ID:** FM-42
- **Category:** equivalence / component-contract-bypass
- **Risk:** if the `.map()` over `[RANGE_BOUND.START, RANGE_BOUND.END]` were wired to the wrong field, or `setBoundTime` dispatched to the shared `hour`/`minute` fields instead of the per-bound ones, the two selectors would silently desync or clobber each other on every keystroke
- **Input that reveals it:** mount `calendar-type="expanded"` + `range` + `with-time`, change the start selector's hour, confirm only `draft.startHour` changed; change the end selector's minute, confirm only `draft.endMinute` changed
- **Observed current behavior:** `render()` (`bds-date-picker.tsx:891-904`) maps over `[RANGE_BOUND.START, RANGE_BOUND.END]`, passing `bound === RANGE_BOUND.START ? this.draft.startHour : this.draft.endHour` (and the minute counterpart) into each `renderTimeSelector` call, with `onHourChange`/`onMinuteChange` calling `this.setBoundTime(bound, field, value)`, which dispatches to `selectBoundHour`/`selectBoundMinute` (`draft-state.ts:89-107`) keyed off `bound === 'start' ? 'startHour' : 'endHour'`
- **Recommended contract:** exactly as observed — each bound's selector reads and writes only its own pair of draft fields
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("independent start/end UTC computation via the new per-bound fields and their bound-aware selectors")
- **Covered by:** `bds-date-picker.time.spec.ts::'changing the start hour updates only startHour, leaving endHour untouched'`, `bds-date-picker.time.spec.ts::'changing the end minute updates only endMinute, leaving startMinute untouched'`

### FM-43 | `basic`+`range` and single-date mode share one time selector backed by the pre-existing single `hour`/`minute` fields, left untouched/unrepurposed by the new per-bound fields
- **ID:** FM-43
- **Category:** equivalence
- **Risk:** a careless refactor could repoint `basic`'s shared selector at one of the new per-bound fields (e.g. always `startHour`), silently breaking `basic`+`range`'s "one shared time for both bounds" contract
- **Input that reveals it:** mount `calendar-type="basic"` + `range` + `with-time`, change the single hour/minute selector, confirm `draft.hour`/`draft.minute` change while `draft.startHour`/`draft.endHour` stay at their defaults
- **Observed current behavior:** `render()`'s non-`expanded` branch (`bds-date-picker.tsx:906-913`) calls `renderTimeSelector` once with `hour: this.draft.hour, minute: this.draft.minute`, `onHourChange: this.handleHourChange`/`onMinuteChange: this.handleMinuteChange` — identical to the single-date-mode call, both routed through `selectHour`/`selectMinute` (`draft-state.ts:71-83`), which only ever touch `hour`/`minute`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("confirm these are untouched/unrepurposed by the new per-bound fields")
- **Covered by:** `bds-date-picker.time.spec.ts::'changing the shared hour updates draft.hour without touching startHour/endHour'`

### FM-44 | Only `expanded`+`range`'s two time selectors render a `Start:`/`End:` bound label (default English text or a `labels` override); `basic`+`range` and single-date render no label
- **ID:** FM-44
- **Category:** equivalence
- **Risk:** a missing `bound` prop pass-through would silently drop the disambiguating label consumers rely on to tell the two `expanded` selectors apart, or an incorrectly-always-set `bound` would wrongly label `basic`'s single shared selector
- **Input that reveals it:** mount `expanded`+`range`, confirm both selectors render `.bds-date-picker__time-bound-label` with `'Start:'`/`'End:'` text (default) and with an overriding `labels` prop; mount `basic`+`range` and single-date, confirm no such element exists at all
- **Observed current behavior:** `renderTimeSelector` (`helpers/renderTimeSelector.tsx:39-48`) only renders `<span class="bds-date-picker__time-bound-label">` when `bound !== undefined`, resolving text via `resolvedLabels.start`/`.end` (defaults `'Start:'`/`'End:'` from `DEFAULT_FOOTER_LABELS`); only the `expanded`+`range` render-path in `bds-date-picker.tsx` passes a `bound`, every other call site omits it
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("`expanded`'s `Start:`/`End:` time-selector labels render... with no `Start:`/`End:` label rendered" for `basic`)
- **Covered by:** `bds-date-picker.time.spec.ts::'renders two time selectors labeled Start:/End: by default'`, `bds-date-picker.time.spec.ts::'applies custom Start/End labels from the labels prop'`, `bds-date-picker.time.spec.ts::'renders a single shared time selector with no Start:/End: label'`, `bds-date-picker.time.spec.ts::'renders no Start:/End: bound label in single-date mode'`

### FM-45 | Apply's range-commit path combines each bound with its own drafted time independently under `expanded`, but applies one shared drafted time to both bounds under `basic`
- **ID:** FM-45
- **Category:** equivalence / race-timing
- **Risk:** swapping which set of fields `buildRangeCommitValue` receives per `calendarType`, or accidentally sharing one pair of fields across both branches, would commit the wrong UTC datetime for one or both bounds without any visible symptom short of inspecting the emitted value
- **Input that reveals it:** under `expanded`, draft two different times for start/end, click Apply, confirm the committed `{ start, end }` reflects each bound's own time via `combineDateTimeToUTC`; under `basic`, draft one time, click Apply, confirm both `start` and `end` are combined with that same time
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.APPLY` branch (`bds-date-picker.tsx:412-436`) calls `buildRangeCommitValue` with `this.draft.startHour, this.draft.startMinute, this.draft.endHour, this.draft.endMinute` when `this.isExpandedCalendarType`, and with `this.draft.hour, this.draft.minute, this.draft.hour, this.draft.minute` (same pair reused for both parameters) otherwise; `buildRangeCommitValue` (`utils/value-mapping.ts:303-317`) independently calls `combineDateTimeToUTC` once per bound with whatever hour/minute it was given
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("the Apply-commit path calling the UTC combination correctly per bound")
- **Covered by:** `bds-date-picker.time.spec.ts::'Apply combines each bound with its own drafted time independently'`, `bds-date-picker.time.spec.ts::'Apply applies the shared drafted time to both range bounds'`

### FM-46 | `resetRangeDraft` derives `startHour`/`startMinute`/`endHour`/`endMinute` independently from each bound of a committed UTC-datetime range value, and separately mirrors the start bound's time into the shared `hour`/`minute` fields — unconditionally, regardless of `calendarType`
- **ID:** FM-46
- **Category:** equivalence / null-empty
- **Risk:** since only one of the two field sets is ever read depending on `calendarType` (per FM-42/FM-43), a bug that populates only one set (or mixes up which bound feeds the shared fields) would stay invisible under one `calendarType` and only surface as wrong times under the other
- **Input that reveals it:** call `resetRangeDraft` directly with a `{ start, end }` value where both bounds are valid, distinct UTC datetimes; assert all six time fields (`hour`, `minute`, `startHour`, `startMinute`, `endHour`, `endMinute`) independently
- **Observed current behavior:** `resetRangeDraft` (`draft-state.ts:151-179`)'s `withTime` branch extracts `start`/`end` independently via `extractDateTimeFromUTC`, then returns an object setting `hour`/`minute` from `start`'s extraction *and* `startHour`/`startMinute`/`endHour`/`endMinute` from both bounds' own extractions in the same return statement
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** this is the single function both Cancel (FM-47) and the initial-mount/reopen draft hydration depend on — a mistake here silently breaks time hydration for whichever `calendarType` isn't currently being manually tested
- **Covered by:** `bds-date-picker.time-helpers.spec.ts::'resetRangeDraft derives independent per-bound hour/minute from valid UTC datetimes, and mirrors start into the shared hour/minute fields'`

### FM-47 | Cancel discards drafted time changes for both the per-bound (`expanded`) and shared (`basic`) fields, reverting to the last-committed range's times on reopen
- **ID:** FM-47
- **Category:** race-timing
- **Risk:** same class of bug as FM-06 (single-date Cancel) but for the newer per-bound fields specifically — a regression here would leave a drafted-but-uncommitted per-bound time visible after Cancel, or worse, silently commit it on the next Apply
- **Input that reveals it:** commit a range with distinct start/end times, reopen, draft new (different) times for both bounds, click Cancel, reopen again, confirm both selectors show the originally-committed times, not the discarded draft
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.CANCEL` branch (`bds-date-picker.tsx:445-453`) calls `resetRangeDraft(this.rangeValue ?? '', this.effectiveWithTime, this.timezone)` for range mode regardless of `calendarType`, which (per FM-46) always repopulates every time field from the last-committed value
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("Cancel discarding time drafts in both calendarType cases, including the new per-bound fields for expanded")
- **Covered by:** `bds-date-picker.time.spec.ts::'Cancel discards drafted per-bound time changes, reverting to the last committed times on reopen'`, `bds-date-picker.time.spec.ts::'Cancel discards the shared drafted time change, reverting on reopen'`

## Reconciliation against Task 21's stated unit-test list

Task 21's list ("range-value union type at the public API boundary; start/end selection and swap logic under both
`basic`/`expanded`; `expanded`'s consecutive-month nav lock; range day-state rendering in isolation from single-date
rendering; single-calendar range rendering renders identically to one of the two `expanded` calendars; Clean vs.
Cancel on range draft as two distinct behaviors; Apply emitting the correct shape identically regardless of
`calendarType`") maps directly onto FM-31 through FM-38 above. No plan-listed item assumes a `pending-decision` row
is already settled — none of FM-31 through FM-41 ever reached `pending-decision`.

Failure modes the audit found that the plan's list doesn't explicitly name: FM-39 (the hover-preview band's
orchestrator-level wiring — `bds-calendar-grid` itself already has grid-level coverage per the existing
`partial-*` tests, but nothing above that level exercises `bds-date-picker`'s own `bdsDayHover`/`bdsGridLeave`
listeners or the shared-`previewEnd`-across-both-`expanded`-calendars behavior), FM-40 (locking in the already-made
`rangeUnderflow`/`rangeOverflow`-is-inert-for-range design decision recorded in Task 18a's own status note, which
had no regression test protecting it), and FM-41 (the FACE round-trip regression lock for a real bug Task 18a's
manual QA already found and fixed once).

## Pending-decision rows requiring a ruling before any test is written for them

None — all of FM-31 through FM-41 are `confirmed` and carry a `Covered by` entry.

## Extension — 2026-09-09, Task 25 (Phase 5, dual time selector consolidated unit tests)

Extending the existing catalog per "Existing component under a new plan version" — audited `bds-date-picker.tsx`,
`utils/draft-state.ts`, `utils/value-mapping.ts`, `types/types.ts`, `types/enum.ts`, and
`helpers/renderTimeSelector.tsx` as they stand today (post the Phase 5 dual-time-selector implementation) for the
`expanded`/`basic` range-time feature, not re-auditing the Phase 1-4 rows above. Confirmed via grep before writing
anything: zero existing spec file references `selectBoundHour`, `selectBoundMinute`, `buildRangeCommitValue`,
`formatRangeValueForDisplay`, `RANGE_BOUND`, or `.bds-date-picker__time-bound-label` — this feature currently has no
automated coverage above the manual verification already performed for it.

### FM-42 | `expanded`+`range` renders two independent time selectors driven by the new per-bound `startHour`/`startMinute`/`endHour`/`endMinute` fields, each wired through the bound-aware `selectBoundHour`/`selectBoundMinute` selectors
- **ID:** FM-42
- **Category:** equivalence / component-contract-bypass
- **Risk:** if the `.map()` over `[RANGE_BOUND.START, RANGE_BOUND.END]` were wired to the wrong field, or `setBoundTime` dispatched to the shared `hour`/`minute` fields instead of the per-bound ones, the two selectors would silently desync or clobber each other on every keystroke
- **Input that reveals it:** mount `calendar-type="expanded"` + `range` + `with-time`, change the start selector's hour, confirm only `draft.startHour` changed; change the end selector's minute, confirm only `draft.endMinute` changed
- **Observed current behavior:** `render()` (`bds-date-picker.tsx:891-904`) maps over `[RANGE_BOUND.START, RANGE_BOUND.END]`, passing `bound === RANGE_BOUND.START ? this.draft.startHour : this.draft.endHour` (and the minute counterpart) into each `renderTimeSelector` call, with `onHourChange`/`onMinuteChange` calling `this.setBoundTime(bound, field, value)`, which dispatches to `selectBoundHour`/`selectBoundMinute` (`draft-state.ts:89-107`) keyed off `bound === 'start' ? 'startHour' : 'endHour'`
- **Recommended contract:** exactly as observed — each bound's selector reads and writes only its own pair of draft fields
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("independent start/end UTC computation via the new per-bound fields and their bound-aware selectors")
- **Covered by:** `bds-date-picker.time.spec.ts::'changing the start hour updates only startHour, leaving endHour untouched'`, `bds-date-picker.time.spec.ts::'changing the end minute updates only endMinute, leaving startMinute untouched'`

### FM-43 | `basic`+`range` and single-date mode share one time selector backed by the pre-existing single `hour`/`minute` fields, left untouched/unrepurposed by the new per-bound fields
- **ID:** FM-43
- **Category:** equivalence
- **Risk:** a careless refactor could repoint `basic`'s shared selector at one of the new per-bound fields (e.g. always `startHour`), silently breaking `basic`+`range`'s "one shared time for both bounds" contract
- **Input that reveals it:** mount `calendar-type="basic"` + `range` + `with-time`, change the single hour/minute selector, confirm `draft.hour`/`draft.minute` change while `draft.startHour`/`draft.endHour` stay at their defaults
- **Observed current behavior:** `render()`'s non-`expanded` branch (`bds-date-picker.tsx:906-913`) calls `renderTimeSelector` once with `hour: this.draft.hour, minute: this.draft.minute`, `onHourChange: this.handleHourChange`/`onMinuteChange: this.handleMinuteChange` — identical to the single-date-mode call, both routed through `selectHour`/`selectMinute` (`draft-state.ts:71-83`), which only ever touch `hour`/`minute`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("confirm these are untouched/unrepurposed by the new per-bound fields")
- **Covered by:** `bds-date-picker.time.spec.ts::'changing the shared hour updates draft.hour without touching startHour/endHour'`

### FM-44 | Only `expanded`+`range`'s two time selectors render a `Start:`/`End:` bound label (default English text or a `labels` override); `basic`+`range` and single-date render no label
- **ID:** FM-44
- **Category:** equivalence
- **Risk:** a missing `bound` prop pass-through would silently drop the disambiguating label consumers rely on to tell the two `expanded` selectors apart, or an incorrectly-always-set `bound` would wrongly label `basic`'s single shared selector
- **Input that reveals it:** mount `expanded`+`range`, confirm both selectors render `.bds-date-picker__time-bound-label` with `'Start:'`/`'End:'` text (default) and with an overriding `labels` prop; mount `basic`+`range` and single-date, confirm no such element exists at all
- **Observed current behavior:** `renderTimeSelector` (`helpers/renderTimeSelector.tsx:39-48`) only renders `<span class="bds-date-picker__time-bound-label">` when `bound !== undefined`, resolving text via `resolvedLabels.start`/`.end` (defaults `'Start:'`/`'End:'` from `DEFAULT_FOOTER_LABELS`); only the `expanded`+`range` render-path in `bds-date-picker.tsx` passes a `bound`, every other call site omits it
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("`expanded`'s `Start:`/`End:` time-selector labels render... with no `Start:`/`End:` label rendered" for `basic`)
- **Covered by:** `bds-date-picker.time.spec.ts::'renders two time selectors labeled Start:/End: by default'`, `bds-date-picker.time.spec.ts::'applies custom Start/End labels from the labels prop'`, `bds-date-picker.time.spec.ts::'renders a single shared time selector with no Start:/End: label'`, `bds-date-picker.time.spec.ts::'renders no Start:/End: bound label in single-date mode'`

### FM-45 | Apply's range-commit path combines each bound with its own drafted time independently under `expanded`, but applies one shared drafted time to both bounds under `basic`
- **ID:** FM-45
- **Category:** equivalence / race-timing
- **Risk:** swapping which set of fields `buildRangeCommitValue` receives per `calendarType`, or accidentally sharing one pair of fields across both branches, would commit the wrong UTC datetime for one or both bounds without any visible symptom short of inspecting the emitted value
- **Input that reveals it:** under `expanded`, draft two different times for start/end, click Apply, confirm the committed `{ start, end }` reflects each bound's own time via `combineDateTimeToUTC`; under `basic`, draft one time, click Apply, confirm both `start` and `end` are combined with that same time
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.APPLY` branch (`bds-date-picker.tsx:412-436`) calls `buildRangeCommitValue` with `this.draft.startHour, this.draft.startMinute, this.draft.endHour, this.draft.endMinute` when `this.isExpandedCalendarType`, and with `this.draft.hour, this.draft.minute, this.draft.hour, this.draft.minute` (same pair reused for both parameters) otherwise; `buildRangeCommitValue` (`utils/value-mapping.ts:303-317`) independently calls `combineDateTimeToUTC` once per bound with whatever hour/minute it was given
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct target of the plan's own Task 25 bullet ("the Apply-commit path calling the UTC combination correctly per bound")
- **Covered by:** `bds-date-picker.time.spec.ts::'Apply combines each bound with its own drafted time independently'`, `bds-date-picker.time.spec.ts::'Apply applies the shared drafted time to both range bounds'`

### FM-46 | `resetRangeDraft` derives `startHour`/`startMinute`/`endHour`/`endMinute` independently from each bound of a committed UTC-datetime range value, and separately mirrors the start bound's time into the shared `hour`/`minute` fields — unconditionally, regardless of `calendarType`
- **ID:** FM-46
- **Category:** equivalence / null-empty
- **Risk:** since only one of the two field sets is ever read depending on `calendarType` (per FM-42/FM-43), a bug that populates only one set (or mixes up which bound feeds the shared fields) would stay invisible under one `calendarType` and only surface as wrong times under the other
- **Input that reveals it:** call `resetRangeDraft` directly with a `{ start, end }` value where both bounds are valid, distinct UTC datetimes; assert all six time fields (`hour`, `minute`, `startHour`, `startMinute`, `endHour`, `endMinute`) independently
- **Observed current behavior:** `resetRangeDraft` (`draft-state.ts:151-179`)'s `withTime` branch extracts `start`/`end` independently via `extractDateTimeFromUTC`, then returns an object setting `hour`/`minute` from `start`'s extraction *and* `startHour`/`startMinute`/`endHour`/`endMinute` from both bounds' own extractions in the same return statement
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** this is the single function both Cancel (FM-47) and the initial-mount/reopen draft hydration depend on — a mistake here silently breaks time hydration for whichever `calendarType` isn't currently being manually tested
- **Covered by:** `bds-date-picker.time-helpers.spec.ts::'resetRangeDraft derives independent per-bound hour/minute from valid UTC datetimes, and mirrors start into the shared hour/minute fields'`

### FM-47 | Cancel discards drafted time changes for both the per-bound (`expanded`) and shared (`basic`) fields, reverting to the last-committed range's times on reopen
- **ID:** FM-47
- **Category:** race-timing
- **Risk:** same class of bug as FM-06 (single-date Cancel) but for the newer per-bound fields specifically — a regression here would leave a drafted-but-uncommitted per-bound time visible after Cancel, or worse, silently commit it on the next Apply
- **Input that reveals it:** commit a range with distinct start/end times, reopen, draft new (different) times for both bounds, click Cancel, reopen again, confirm both selectors show the originally-committed times, not the discarded draft
- **Observed current behavior:** `handleFooterAction`'s `FOOTER_ACTION.CANCEL` branch (`bds-date-picker.tsx:445-453`) calls `resetRangeDraft(this.rangeValue ?? '', this.effectiveWithTime, this.timezone)` for range mode regardless of `calendarType`, which (per FM-46) always repopulates every time field from the last-committed value
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan bullet ("Cancel discarding time drafts in both calendarType cases, including the new per-bound fields for expanded")
- **Covered by:** `bds-date-picker.time.spec.ts::'Cancel discards drafted per-bound time changes, reverting to the last committed times on reopen'`, `bds-date-picker.time.spec.ts::'Cancel discards the shared drafted time change, reverting on reopen'`

## Reconciliation against Task 25's stated unit-test list

Task 25's list ("`expanded` dual selector independent start/end UTC computation... `expanded`'s `Start:`/`End:` labels...
`basic`+`range` shared-time application... confirm untouched/unrepurposed... time-inclusive range formatter...
Apply-commit path calling `combineDateTimeToUTC` per bound... single-date Phase 2 regression... Cancel discarding
time drafts in both `calendarType` cases") maps directly onto FM-42 through FM-47 above, plus the pre-existing FM-02
(single-date regression, re-verified unaffected) and the `formatRangeValueForDisplay`/`buildRangeCommitValue`
plain-function coverage added to `bds-date-picker.time-helpers.spec.ts`. No plan-listed item assumes a
`pending-decision` row is already settled — none of FM-42 through FM-47 ever reached `pending-decision`.

One pre-existing, out-of-scope observation surfaced by this audit and *not* turned into a row: `resetRangeDraft`'s
`withTime` branch only hydrates from a committed value when **both** `start` and `end` independently pass
`isValidUtcDateTimeValue` (`draft-state.ts:160`) — if exactly one bound is malformed, the function falls through to
the naive-date branch, which also fails to parse the malformed UTC-format bound as a naive date, so *both*
`rangeStart` and `rangeEnd` end up `null` (not just the malformed one). This all-or-nothing gate predates Phase 5
(the single-bound version of this check existed before `startHour`/`endHour` were added) and is unrelated to
Phase 5's own dual-selector changes, so it is flagged here for visibility rather than given its own FM row or test —
raise it separately if a mixed valid/malformed range value turns out to be a real consumer scenario.

## Pending-decision rows requiring a ruling before any test is written for them

None — all of FM-42 through FM-47 are `confirmed` and carry a `Covered by` entry.

## Extension — 2026-09-11, Task 32 (Phase 6, presets sidebar consolidated unit tests)

Extending the existing catalog per "Existing component under a new plan version" — audited `utils/presets.ts`,
`utils/draft-state.ts`, `utils/value-mapping.ts`, `helpers/renderPresets.tsx`, `helpers/renderCalendarPanel.tsx`,
and the relevant slices of `bds-date-picker.tsx` (`handlePresetClick`, `rangeEndShiftApplies`, `resolveRangeEndIso`,
the `render()` container/date-time/calendars structure) as they stand today, post Tasks 29/30a/30b/31a. Confirmed
via grep before writing anything: zero existing spec file references `computePresetRange`, `computePresetCoverageEnd`,
`isPresetWithinBounds`, `selectPresetRange`, `renderPresets`, `BUILT_IN_PRESET_KEYS`, or `.bds-date-picker__preset` —
this entire feature area had zero automated coverage before this task, and `selectDay`/`selectRangeDay` (pre-existing,
unrelated to Phase 6) had never been unit-tested directly either, per this task's own backfill note.

### FM-48 | `computePresetRange`'s per-preset day arithmetic matches Task 29's final semantics for all six built-ins
- **ID:** FM-48
- **Category:** boundary / equivalence
- **Risk:** an off-by-one in any preset's day-count arithmetic (e.g. "Last 7 days" excluding today, or "This month" running to month-end instead of today) would silently mis-report ranges to a consumer relying on the documented semantics
- **Input that reveals it:** call `computePresetRange` for each of the six `BUILT_IN_PRESET_KEY` values against a fixed mocked "today"
- **Observed current behavior:** `presets.ts:30-49` `computeRawRange` — Today/Yesterday single-day; Last 7/30 days inclusive of today (7/30 days total, not N days *before* today); This month is month-to-date (`startOfMonth` through today); Last month is the full previous calendar month (`startOfMonth`/`endOfMonth` of `subMonths(today, 1)`)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** these are consumer-facing, previously undocumented-until-ADR-0015 semantics with real ambiguity (e.g. "This month" could plausibly have meant the full calendar month) — a wrong test would have encoded the wrong contract
- **Covered by:** `presets.spec.ts::'Today resolves to a single-day range covering only today'`, `'Yesterday resolves to a single-day range covering only yesterday'`, `'Last 7 days resolves to a 7-day range inclusive of today, not 7 days before today'`, `'Last 30 days resolves to a 30-day range inclusive of today, not 30 days before today'`, `'This month resolves to month-to-date (the 1st through today), not the full calendar month'`, `'Last month resolves to the full previous calendar month, start to end'`, `'never returns a with-time-shifted end for any preset, regardless of the caller'`

### FM-49 | `computePresetRange` computes "today" from the passed `timezone`, not the device clock, and re-derives it fresh on every call
- **ID:** FM-49
- **Category:** boundary / race-timing
- **Risk:** a consumer in a different timezone than the server/device running the picker would see the wrong "today" for every preset; a cached/memoized "today" would also silently go stale across a long-lived session or a real-time re-click
- **Input that reveals it:** call `computePresetRange` for two different `timezone` arguments against the same mocked instant chosen so their local calendar dates differ; call it again after advancing the mocked clock and confirm the result changes
- **Observed current behavior:** `presets.ts:62-66` — `new TZDate(new Date(), timezone)` read inline on every call, never cached
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 30a coverage requirement; a device-clock or cached-value regression here would be invisible to any test that only exercises a single timezone/instant
- **Covered by:** `presets.spec.ts::'computes distinct "today" values for two different timezones given the same instant'`, `'re-derives "today" fresh on every call rather than caching the first computed value'`

### FM-50 | `computePresetCoverageEnd`'s with-time end-boundary shift is off-unchanged / on-plus-one-day uniformly, with no double-shift for Yesterday/Last month
- **ID:** FM-50
- **Category:** boundary
- **Risk:** a naive per-preset special case (e.g. explicitly skipping the shift for Yesterday/Last month "since they already land on the boundary") would either double-shift them or under-shift the other four presets inconsistently
- **Input that reveals it:** call `computePresetCoverageEnd(range, false)` and `(range, true)` for every preset's real range
- **Observed current behavior:** `presets.ts:81-87` — single unconditional `withTime ? addDays(range.end, 1) : range.end`, no per-preset branching at all
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet naming Yesterday/Last month's "no double-shift" case specifically, since their shifted value coincidentally equals a different, easily-confusable milestone (today / start of current month)
- **Covered by:** `presets.spec.ts::'returns range.end unchanged when with-time is off, for every preset'`, `'shifts range.end forward by exactly one day when with-time is on, for a mid-range preset (Today)'`, `'shifts Last 7 days and Last 30 days forward by exactly one day past today'`, `"shifts Yesterday's end to exactly today, with no double-shift beyond the natural next-period boundary"`, `"shifts Last month's end to exactly the first day of the current month, with no double-shift"`

### FM-51 | `isPresetWithinBounds` operates on the real range only, with independently-optional min/max and inclusive boundaries
- **ID:** FM-51
- **Category:** boundary
- **Risk:** if a future edit accidentally fed the with-time-shifted coverage end into this check (instead of the real range), a preset landing exactly on `max` would wrongly disable itself the moment `with-time` is on; a non-inclusive boundary check would also wrongly disable an exact-match range
- **Input that reveals it:** a range fully inside, fully outside, and only partially outside `min`/`max`; a range exactly touching a bound; the same range compared against its own with-time-shifted counterpart
- **Observed current behavior:** `presets.ts:97-107` — compares `range.start`/`range.end` (never a shifted value) against optionally-set `min`/`max` via `compareDates`, `< 0`/`> 0` only (so `0` is always in-bounds)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct Task 29/32 coverage bullet; the real-vs-shifted distinction is exactly the kind of subtle mistake a careless refactor could introduce silently
- **Covered by:** `presets.spec.ts::'returns true for a range fully inside min and max'`, `'returns false for a range fully outside the bounds (entirely before min)'`, `'returns false for a range only partially outside the bounds, never clamping to true'`, `'treats each of min/max as independently optional, and both unset as unbounded'`, `'treats an exact-equality boundary (range touching min/max precisely) as inside, inclusive on both ends'`, `'operates on the real range, never a with-time-shifted coverage end'`

### FM-52 | Clicking a built-in preset sets `draft.rangeStart`/`rangeEnd` to the real unshifted days, and zeroes the relevant time field(s) when with-time is on
- **ID:** FM-52
- **Category:** equivalence
- **Risk:** a preset click could leak the shifted coverage end into the draft's own `rangeEnd` (double-applying the shift once more at commit time), or leave stale non-zero time fields from a prior manual edit
- **Input that reveals it:** click a preset under `basic`/`expanded` with with-time off and on, inspecting `draft.rangeStart`/`rangeEnd`/`hour`/`minute`/`startHour`/`startMinute`/`endHour`/`endMinute`
- **Observed current behavior:** `handlePresetClick` (`bds-date-picker.tsx:512-519`) calls `selectPresetRange(this.draft, range, this.effectiveWithTime)`; `selectPresetRange` (`draft-state.ts:81-105`) sets `rangeStart`/`rangeEnd` from the real `range.start`/`range.end` unconditionally, and zeroes all six time fields only when `withTime` is `true`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct Task 32 coverage bullet; the double-shift risk specifically is the kind of bug that would only surface downstream, at Apply, making this component-level draft assertion the more direct regression guard
- **Covered by:** `bds-date-picker.presets.spec.ts::'sets rangeStart/rangeEnd to the real range, unaffected by with-time coverage shifting'`, `'zeroes the shared hour/minute fields when with-time is on under basic'`, `"zeroes both bounds' independent time fields when with-time is on under expanded"`, `'marks the clicked preset as selected, and no other preset'`

### FM-53 | The popover header displays `computePresetCoverageEnd`'s shifted value as `End:` for an active with-time preset, identically in `basic` and `expanded`
- **ID:** FM-53
- **Category:** equivalence
- **Risk:** the header could show the real last day instead of the shifted coverage boundary, contradicting the value that will actually be committed on Apply — a visible, confusing mismatch a consumer would perceive as a bug
- **Input that reveals it:** click a with-time preset, read the `.bds-date-picker__range-value` header text for both `Start:`/`End:` under both `calendarType`s
- **Observed current behavior:** `render()`'s `rangeEndText` (`bds-date-picker.tsx:834-843`) always runs the resolved end through `resolveRangeEndIso`, which (per `rangeEndShiftApplies`, `:669-672`) shifts whenever a preset is active, regardless of `calendarType`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct Task 32 coverage bullet; this is the one visible surface a consumer sees before ever clicking Apply, so it must never disagree with the eventual commit
- **Covered by:** `bds-date-picker.presets.spec.ts::'shows the shifted end (not the real last day) under basic'`, `'shows the shifted end (not the real last day) under expanded, identically to basic'`

### FM-54 | `basic`+`range`+`with-time`'s Apply commit uses the coverage-shifted end for both preset-driven and manual selections
- **ID:** FM-54
- **Category:** boundary / equivalence
- **Risk:** since `basic` has only one shared time field, a manual (non-preset) range selection has no other way to express "cover the whole last day" — if the shift were gated on `selectedPreset !== 'custom'` under `basic` too (mirroring `expanded`'s own gating), a manual `basic` selection would under-cover its last day by nearly 24 hours with no way for the consumer to fix it, per ADR-0015
- **Input that reveals it:** complete a manual two-day range under `basic`+`with-time` (leaving the shared time at its `00:00` default, and separately with a user-set shared time), click Apply, inspect the committed `end`
- **Observed current behavior:** `rangeEndShiftApplies` (`bds-date-picker.tsx:669-672`) — `this.isExpandedCalendarType ? this.selectedPreset !== PRESET_KEY.CUSTOM : true` — under `basic` this is unconditionally `true`, independent of `selectedPreset`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** this is the exact `basic`-only special case the plan calls out explicitly, and the one most likely to be "fixed" incorrectly by someone assuming `basic`/`expanded` should behave symmetrically
- **Covered by:** `bds-date-picker.presets.spec.ts::'basic: a preset-driven commit uses the coverage-shifted end'`, `'basic: a manual selection with the shared time left at its default also uses the coverage-shifted end'`, `"basic: a manual selection with a user-set shared time preserves that time on both the real start and the shifted end"`

### FM-55 | `expanded`+`range`+`with-time`'s Apply commit shifts only for preset-driven selections; a manual selection commits each bound's own exact time with no shift
- **ID:** FM-55
- **Category:** equivalence
- **Risk:** the inverse of FM-54 — since `expanded` gives the consumer two fully independent time fields, silently shifting a manual selection's end would corrupt an intentionally precise, non-`00:00` end time the user explicitly set
- **Input that reveals it:** complete a manual two-day range under `expanded`+`with-time` with distinct, non-zero start/end times, click Apply, confirm the committed end matches the real last day (not shifted) at exactly the drafted time; separately, click a preset and confirm its commit **is** shifted
- **Observed current behavior:** same `rangeEndShiftApplies` getter as FM-54 — under `expanded`, `false` whenever `selectedPreset === PRESET_KEY.CUSTOM` (the state a manual day click or time edit always reverts to)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** direct Task 32 coverage bullet, explicitly contrasted against FM-54 as the other half of the same design decision
- **Covered by:** `bds-date-picker.presets.spec.ts::'expanded: a preset-driven commit uses the coverage-shifted end'`, `"expanded: a manual selection commit is completely unaffected by the shift, using each bound's own exact time"`

### FM-56 | A preset click while a selection is mid-progress overwrites rather than merges with the in-progress selection
- **ID:** FM-56
- **Category:** race-timing
- **Risk:** `selectPresetRange` fully replaces `rangeStart`/`rangeEnd` (per its own doc comment, "never routed through `selectRangeDay`"), but nothing before this task proved that end-to-end through a real click sequence — a wiring regression could instead merge or ignore the preset's range
- **Input that reveals it:** manually click one day (setting `rangeStart`, leaving `rangeEnd` null), then click a preset, and confirm the draft reflects only the preset's range
- **Observed current behavior:** `handlePresetClick` (`bds-date-picker.tsx:512-519`) unconditionally calls `selectPresetRange`, independent of the draft's prior state
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet
- **Covered by:** `bds-date-picker.presets.spec.ts::'overwrites an in-progress manual selection instead of merging with it'`

### FM-57 | Re-clicking the currently-selected preset recomputes its range rather than short-circuiting as a no-op
- **ID:** FM-57
- **Category:** race-timing
- **Risk:** a naive "already selected, skip" optimization would leave the user with a stale "Today"/"Last 7 days" range if real time had advanced since the first click (e.g. the popover left open overnight)
- **Input that reveals it:** click "Today", then advance the mocked clock and click "Today" again, confirming the draft's range changes to reflect the new "today"
- **Observed current behavior:** `handlePresetClick` has no identity/equality guard against `this.selectedPreset === key` — it always recomputes `computePresetRange(key, this.timezone)` fresh
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet; directly follows from FM-49's "never cached" contract but needed its own component-level proof through the real click handler
- **Covered by:** `bds-date-picker.presets.spec.ts::'recomputes rather than short-circuiting when the same preset is clicked again after "today" changes'`

### FM-58 | A manual day click or a manual time-selector edit each independently revert an active preset selection to Custom, preserving whatever time was already drafted
- **ID:** FM-58
- **Category:** race-timing
- **Risk:** if either revert path were missing, a user editing the calendar or the time selector after picking a preset would see the preset's button still marked selected despite having manually changed the underlying data — a stale, misleading UI state; separately, a careless revert implementation could reset the time fields to `00:00` instead of preserving the value already there
- **Input that reveals it:** click a preset, then independently (a) click a different day, (b) change the time selector, each time confirming `selectedPreset` becomes Custom and the untouched draft fields (time, for the day-click case; the range dates, for the time-edit case) carry over exactly
- **Observed current behavior:** `handleDayClick` (`bds-date-picker.tsx:360-375`) sets `this.selectedPreset = PRESET_KEY.CUSTOM` whenever `effectiveRange`, independent of `selectDay`/`selectRangeDay`'s own return value; `handleHourChange`/`handleMinuteChange`/`setBoundTime` (`:490-502,413-419`) do the same for time edits — neither path touches any field it doesn't own
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet, with the "assert the exact carried-over values, not just no crash" requirement called out specifically
- **Covered by:** `bds-date-picker.presets.spec.ts::'a manual day click reverts an active preset to Custom, preserving the already-drafted time'`, `'a manual time-selector edit reverts an active preset to Custom, preserving the edited value exactly'`

### FM-59 | "Custom" is selected by default on a fresh draft and is never reverse-matched from a value that numerically coincides with a preset's computed range
- **ID:** FM-59
- **Category:** equivalence
- **Risk:** an over-clever implementation could try to infer `selectedPreset` by comparing the committed/drafted range against each preset's live computation — which would be both wasteful and wrong the instant "today" moves and the coincidental match stops holding, silently reselecting the wrong preset's chrome
- **Input that reveals it:** mount fresh (no value) and confirm Custom is selected with no built-in preset marked; separately, mount with a committed range that exactly equals what "Last 7 days" currently computes, and confirm Custom (not "Last 7 days") is selected
- **Observed current behavior:** `@State() selectedPreset` (`bds-date-picker.tsx:151`) defaults to `PRESET_KEY.CUSTOM` and is only ever reassigned by explicit preset/Custom clicks, day clicks, time edits, or footer actions — never derived from `draft`/`value` content
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet naming this exact false-positive risk
- **Covered by:** `bds-date-picker.presets.spec.ts::'selects Custom by default on a fresh draft, with no built-in preset marked selected'`, `'keeps Custom selected even when a pre-existing value numerically coincides with what a preset would compute'`

### FM-60 | Clicking "Custom" directly marks it selected without altering `rangeStart`/`rangeEnd`/time
- **ID:** FM-60
- **Category:** component-contract-bypass
- **Risk:** `handleCustomClick` could have been (mis)implemented to also clear the draft (conflating "switch to Custom" with "start a fresh selection", which is a distinct, separately-triggered behavior)
- **Input that reveals it:** select a preset, then click "Custom", and confirm the draft's range/time fields are byte-for-byte unchanged from what the preset had set
- **Observed current behavior:** `handleCustomClick` (`bds-date-picker.tsx:421-423`) — `this.selectedPreset = PRESET_KEY.CUSTOM;` and nothing else
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet
- **Covered by:** `bds-date-picker.presets.spec.ts::'clicking Custom directly marks it selected without altering the draft'`

### FM-61 | A disabled (out-of-bounds) preset button does not update the draft when clicked, guarded by `handlePresetClick`'s own bounds check, not by the native `disabled` attribute
- **ID:** FM-61
- **Category:** component-contract-bypass
- **Risk:** `mock-doc`'s `.click()` unconditionally dispatches a click event regardless of the `disabled` attribute (confirmed by inspecting `@stencil/core/mock-doc`'s `click()` implementation) — if the only protection were the native attribute, a programmatic `.click()` (or a real browser bypass) would still corrupt the draft; the real guard must live in the handler itself
- **Input that reveals it:** mount with `min`/`max` excluding a preset's range, confirm the button carries `disabled`, call `.click()` on it directly, and confirm the draft is untouched
- **Observed current behavior:** `handlePresetClick` (`bds-date-picker.tsx:512-514`) — `if (!isPresetWithinBounds(range, this.minDate, this.maxDate)) return;`, evaluated independently of the button's own `disabled` attribute (`renderPresets.tsx:52,62`)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet; the mock-doc click-dispatch behavior means this test genuinely exercises the handler's own guard, not an artifact of the DOM refusing to fire the event
- **Covered by:** `bds-date-picker.presets.spec.ts::'does nothing when a disabled (out-of-bounds) preset is clicked'`

### FM-62 | Preset label text resolves from the `labels` prop, with correct English defaults and consumer overrides
- **ID:** FM-62
- **Category:** equivalence
- **Risk:** consumer-supplied i18n labels for the preset buttons could be silently ignored, mirroring the exact class of gap Task 25 found for the time-selector's own labels (FM-15)
- **Input that reveals it:** mount with no `labels` override, confirm every preset shows its English default text; set `labels.presetToday`/`labels.presetCustom`, confirm those two update while the rest keep their defaults
- **Observed current behavior:** `renderPresets.tsx:44-45` — `resolvedLabels = { ...DEFAULT_DATE_PICKER_LABELS, ...labels }`, applied per-button via `PRESET_LABEL_KEY`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 32 coverage bullet, mirroring Task 25's established labels-override test pattern (FM-15)
- **Covered by:** `bds-date-picker.presets.spec.ts::'renders every preset label using the English defaults when no labels override is provided'`, `'applies consumer-supplied preset label overrides from the labels prop'`

### FM-63 | Clicking a built-in preset sets `displayYear`/`displayMonth` from the preset's real `range.start`, in both `basic` and `expanded`; Cancel/Clean/Apply and manual selection leave them unchanged
- **ID:** FM-63
- **Category:** equivalence / race-timing
- **Risk:** without this navigation, clicking e.g. "Last month" while viewing the current month would leave the calendar showing the wrong month entirely, with the highlighted range invisible off-screen — a confusing, easily-missed UX gap; conversely, a careless implementation could navigate the calendar on every draft change (including Cancel/Clean/manual selection), causing jarring, unwanted scrolling
- **Input that reveals it:** click "Last month" while the calendar displays the current month, confirm it navigates to the preset's month, under both `calendarType`s (confirming `expanded`'s second calendar shifts too, staying one month ahead); separately, click a day manually and run Cancel/Clean, confirming the displayed month never moves
- **Observed current behavior:** `handlePresetClick` (`bds-date-picker.tsx:512-519`) sets `this.displayYear = range.start.getFullYear(); this.displayMonth = range.start.getMonth();` unconditionally after a successful preset click; no other handler (`handleDayClick`, `handleFooterAction`'s Cancel/Clean/Apply branches, `handleHourChange`/`handleMinuteChange`/`setBoundTime`) ever reassigns `displayYear`/`displayMonth`
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 30b coverage requirement folded into this task
- **Covered by:** `bds-date-picker.presets.spec.ts::"sets displayYear/displayMonth from the preset's real range start under basic"`, `"sets displayYear/displayMonth from the preset's real range start under expanded, shifting both calendars"`, `'leaves displayYear/displayMonth unchanged for manual selection, Cancel, and Clean'`

### FM-64 | `renderCalendarPanel`'s wrapper, and the `container`/`date-time`/`time-band` structure, render correctly across every `calendarType`/`with-time` combination, with no `slot="content-band"` anywhere
- **ID:** FM-64
- **Category:** equivalence
- **Risk:** Task 31a's markup restructuring (removing the old `.bds-date-picker__body`, always wrapping in `.calendars`, introducing `.date-time`/`.time-band`) had zero coverage before this task — a regression here would be a real, visible layout break with no automated signal; separately, a reintroduced `slot="content-band"` usage would silently target a slot that no longer exists on `bds-popover` at all (removed as dead code), producing orphaned, unrelocated content
- **Input that reveals it:** inspect the rendered DOM structure under `default` (no range/time), `basic`/`expanded` with and without `with-time`, for both a single grid and two grids
- **Observed current behavior:** `renderCalendarPanel.tsx:29-47` always returns `<div class="bds-date-picker__calendars">{grids}</div>` regardless of `calendars.length`; `bds-date-picker.tsx`'s `render()` (`:944-986`) renders `.calendars` as `.container`'s only non-presets child under `default`, or wraps it plus a conditionally-rendered `.time-band` inside `.date-time` under `basic`/`expanded`; no code path in this component references a `content-band` slot at all (confirmed via grep)
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 31a/32 coverage requirement; this is the first automated coverage of the restructured markup at all
- **Covered by:** `bds-date-picker.presets.spec.ts::'wraps a single grid (basic) in .bds-date-picker__calendars'`, `'wraps two grids (expanded) in a single .bds-date-picker__calendars element'`, `"renders .calendars as the container's only child under calendar-type=\"default\""`, `'wraps .calendars and .time-band inside .date-time when with-time is on, under basic/expanded'`, `'renders .date-time with no .time-band when with-time is off, under basic/expanded'`, `'renders no element carrying slot="content-band" under any configuration'`

### FM-65 | `resolveFallbackDisplayMonth` (via `resolveDisplayMonth`) and `generateMonthGrid`'s `now` option both compute "today" from an explicit input, never the device clock directly; `generateMonthGrid`'s own device-clock default is unchanged
- **ID:** FM-65
- **Category:** boundary
- **Risk:** the other two "today"-computing call sites in this component's dependency chain (besides `computePresetRange`, FM-49) could have been missed when the timezone-awareness work landed, leaving the display-month fallback or the grid's `isToday` flag still silently tied to the device clock while presets themselves were correctly fixed
- **Input that reveals it:** call `resolveDisplayMonth('', false, zone)` for two different timezones at an instant whose calendar month differs between them; call `generateMonthGrid` with an explicit `now` option and confirm it (not the device clock) decides `isToday`
- **Observed current behavior:** `value-mapping.ts:49-56` `resolveFallbackDisplayMonth` reads `new TZDate(new Date(), timezone)`, the same pattern as `computePresetRange`; `grid.ts:19,135` `generateMonthGrid`'s `now` option defaults to `new Date()` only when the caller omits it, and `buildDisplayGrid` (`value-mapping.ts:157-171`) always passes an explicit, timezone-derived `now` rather than relying on that default
- **Recommended contract:** exactly as observed
- **Contract status:** confirmed
- **Why it matters:** explicit Task 30a coverage requirement; closes the same class of gap as FM-49 for the two other call sites in the chain, and locks in `generateMonthGrid`'s pre-existing device-clock-default behavior as unchanged for every caller that doesn't pass `now`
- **Covered by:** `value-mapping.spec.ts::'computes the fallback month from the passed timezone, not a single global device clock'`, `grid.spec.ts::'uses an explicitly passed \`now\` option to decide isToday, independent of the device clock'`

### Backfill | `selectDay`/`selectRangeDay` direct unit coverage (pre-existing gap, unrelated to Phase 6's own new code)
Not a new failure mode in the catalog sense — `draft-state.spec.ts` was added purely to close a pre-existing coverage
gap the plan's own Task 32 text calls out: `selectDay`/`selectRangeDay` had never been unit-tested directly (only
indirectly, through full-component click simulation in `bds-date-picker.range.spec.ts`), unlike every sibling
function in the same file. Direct tests now cover: `selectDay`'s set/no-op branches; `selectRangeDay`'s fresh-start,
forward-extend, backward-swap, third-click-fresh-start, and both no-op cases (equal-to-`rangeStart` mid-selection,
and the edge case where a fresh-start's new `rangeStart` coincidentally equals the old completed range's `rangeEnd`).
See `draft-state.spec.ts` for the full list.

One pre-existing, out-of-scope observation surfaced by this audit and *not* turned into a row, since it is dead code
rather than a behavioral failure mode (nothing production-facing can ever reach it, so no test can be written against
it without first changing the guard conditions around it — out of this task's scope, which is tests only): three
defensive `return draft`/fallback branches are unreachable given their own enclosing guard conditions —
`selectRangeDay`'s inner check at `draft-state.ts:51` (can only be true when `draft.rangeStart` is a non-null string
equal to `isoDate` **and** `draft.rangeEnd === null`, but the enclosing `if` at `:50` only enters this branch when
`draft.rangeStart === null || draft.rangeEnd !== null` — both of which contradict the inner condition) and `:58`
(same shape, inside the mid-selection branch where `draft.rangeEnd` is always `null` by construction); and
`resolveFallbackDisplayMonth`'s `anchor === undefined` fallback at `value-mapping.ts:70-72` (unreachable because the
function already returns early at `:60-62` whenever both `validMin` and `validMax` are `undefined`, so `anchor` —
`validMax ?? validMin` — can never be `undefined` by the time it's checked). None of these affect any currently
observable contract; flagged here for visibility in case a future refactor of the surrounding guards changes that.

### FM-66 | A second click on the day already selected as `rangeStart` sets `rangeEnd` equal to it, confirming a one-day range, and returns a genuinely new draft reference
- **ID:** FM-66
- **Category:** race-timing
- **Risk:** the prior no-op behavior made a one-day same-day range structurally unreachable via the calendar UI; the fix must also not regress the reference-stability convention used elsewhere in this file (a no-op branch must return the same reference, a real-change branch must not)
- **Input that reveals it:** click a day, then click the same day again while `rangeEnd` is still `null`
- **Observed current behavior:** `selectRangeDay` (`draft-state.ts:61`) returns `{ ...draft, rangeEnd: isoDate }`, a new object, with `rangeStart === rangeEnd`
- **Recommended contract:** same as observed — a second click on `rangeStart` confirms a one-day range and must allocate a new draft (this is not the reference-stable no-op case; the resulting state genuinely differs from the input, `rangeEnd` going from `null` to a real value)
- **Contract status:** confirmed
- **Why it matters:** per ADR 0016 / Task 34d, this is the only way to manually reach a same-day `expanded+range+with-time` selection, which is itself the precondition for every other row below
- **Covered by:** `draft-state.spec.ts::'sets rangeEnd equal to rangeStart, confirming a one-day range, when the clicked day equals the already-selected rangeStart'`, `bds-date-picker.time.spec.ts::'a second click on the same day sets rangeEnd equal to rangeStart, enabling independent Start/End time edits'`

### FM-67 | A same-day `expanded+range+with-time` selection with End later than or equal to Start commits and displays with no date shift
- **ID:** FM-67
- **Category:** boundary
- **Risk:** a false-positive shift on a genuinely ordered (or zero-duration) same-day pair would silently corrupt a correct intraday selection into a spurious overnight one
- **Input that reveals it:** same-day selection with Start `14:00`/End `18:00` (later), and separately Start `14:00`/End `14:00` (equal)
- **Observed current behavior:** `resolveEffectiveRangeEndIso` (`bds-date-picker.tsx:748-764`) only shifts when `endMinutes < startMinutes` — strictly less than, so both "later" and "equal" leave `rangeEnd` unshifted
- **Recommended contract:** same as observed; the strict `<` is deliberate, matching ADR 0016's framing of the shift as resolving a literal inversion, not a same-instant or forward-ordered pair. A zero-duration same-day range (equal times) commits as literally the same instant, which is consistent with allowing a one-day range with identical bounds at all (FM-66) — nothing in ADR 0016 or Task 34d asks for a minimum duration
- **Contract status:** confirmed
- **Why it matters:** boundary correctness of the `<` vs `<=` comparison in the shift condition; flagged to the user as worth a final sanity check even though the code's intent reads as deliberate, since "no one explicitly asked to allow a zero-duration range" is a fair question to raise even where the implementation is internally consistent
- **Covered by:** `bds-date-picker.time.spec.ts::'a same-day range with End later than Start commits with no shift, matching the header'`, `bds-date-picker.time.spec.ts::'does not shift the effective end date when Start and End times are exactly equal on the same day'`

### FM-68 | A same-day `expanded+range+with-time` selection with End earlier than Start shifts the effective end date +1 day, shown live in the header before Apply and matching the trigger field text after Apply
- **ID:** FM-68
- **Category:** equivalence
- **Risk:** per ADR 0016, a silent shift (visible only after Apply) or a disagreement between the pre-Apply header and the post-Apply trigger field would reintroduce exactly the "silent disagreement" class of bug ADR 0015 was written to eliminate
- **Input that reveals it:** same-day selection, Start `14:00`, End `09:00` (inverted)
- **Observed current behavior:** `resolveEffectiveRangeEndIso` returns `rangeEnd + 1 day` once the inversion condition holds; both the header's `rangeEndText` (`bds-date-picker.tsx:909-918`) and the Apply commit's `commitRangeEnd` (`bds-date-picker.tsx:451-452`) call this same method, so they agree by construction; `syncFieldValue` (`bds-date-picker.tsx:800-818`) then formats the already-shifted committed value for the trigger field
- **Recommended contract:** same as observed
- **Contract status:** confirmed
- **Why it matters:** this is the core new behavior ADR 0016/Task 34d introduces; the pre-Apply/post-Apply text-equality requirement is the part a test that only checks the final committed value would miss entirely
- **Covered by:** `bds-date-picker.time.spec.ts::'a same-day range with End earlier than Start shifts the effective end +1 day, live in the header and at commit'`, `bds-date-picker.time.spec.ts::'shows the same resolved end date in the trigger field after Apply as the header showed before Apply'`

### FM-69 | `basic`+`range`+`with-time` cannot reach the inverted-same-day shift condition; its existing unconditional coverage shift applies unaffected
- **ID:** FM-69
- **Category:** component-contract-bypass
- **Risk:** if the new `isExpandedCalendarType`-gated condition in `resolveEffectiveRangeEndIso` were ever accidentally un-gated, `basic`'s single shared time field would be double-shifted or shifted for the wrong reason
- **Input that reveals it:** a same-day selection in `basic+range+with-time` (structurally has only one shared `hour`/`minute`, no independent `endHour`/`endMinute`)
- **Observed current behavior:** `isSameDayInvertedTime` (`bds-date-picker.tsx:754-759`) requires `this.isExpandedCalendarType`, so `basic` always short-circuits to `coverageShiftedEnd` — the pre-existing ADR 0015 unconditional shift (`rangeEndShiftApplies` returns `true` unconditionally for `basic`, per `bds-date-picker.tsx:726-728`)
- **Recommended contract:** same as observed — no interaction between the two ADRs' shifts for `basic`
- **Contract status:** confirmed
- **Why it matters:** explicit Task 34d/ADR 0016 acceptance criterion that `basic` is structurally unaffected, verified rather than assumed
- **Covered by:** `bds-date-picker.time.spec.ts::'a same-day selection in basic (structurally single shared time) never triggers the inverted-time shift'`

### FM-70 | `renderBanner` renders nothing when `banner` is unset or `banner.visible` is not exactly `true`
- **ID:** FM-70
- **Category:** null-empty
- **Risk:** an empty banner shell rendering when the consumer hasn't opted in, or a merely-truthy (non-boolean) `visible` value producing unexpected output, since the guard is a strict equality check rather than a plain falsy check
- **Input that reveals it:** `banner` unset; `banner` set with `visible` unset; `banner` set with `visible: false`
- **Observed current behavior:** `renderBanner.tsx:26` — `if (banner === undefined || banner.visible !== true) return null;`
- **Recommended contract:** same as observed
- **Contract status:** confirmed — plan's Task 35 design decision (2026-09-22): "`visible` default: `false` (or prop itself `undefined`) — renders nothing when unset, no empty banner shell"
- **Why it matters:** regression guard for the no-banner default state, across all three `calendarType` values
- **Covered by:** `bds-date-picker.banner.spec.ts::'renders no banner element when banner is unset'`, `'renders no banner element when banner.visible is false'`

### FM-71 | Banner `closable` defaults to `true` when unset, diverging from `bds-banner`'s own component-level default of `false`
- **ID:** FM-71
- **Category:** equivalence
- **Risk:** if this composing default ever regressed to a plain passthrough of `bds-banner`'s own default, every mockup-driven consumer relying on an always-dismissible banner would silently lose its close icon
- **Input that reveals it:** `banner` set with `closable` unset
- **Observed current behavior:** `renderBanner.tsx:28` — `const closable = banner.closable ?? true;`
- **Recommended contract:** same as observed
- **Contract status:** confirmed — plan's Task 35 design decision: "`closable` default: `true` — every mockup shows the close (`X`) icon by default, even though `bds-banner`'s own component-level default is `false`"
- **Why it matters:** explicit, deliberate divergence from the child component's own default; easy to regress unnoticed since both defaults are booleans
- **Covered by:** `bds-date-picker.banner.spec.ts::'shows a close button by default when banner.closable is unset'`

### FM-72 | Banner `state` defaults to `'info'` when unset
- **ID:** FM-72
- **Category:** equivalence
- **Risk:** a missing default would leave `bds-banner`'s own `variant` prop `undefined`, which happens to coincide with its own default, masking a regression here until a consumer explicitly overrides `state`
- **Input that reveals it:** `banner` set with `state` unset; separately, `state` explicitly set to a non-default variant
- **Observed current behavior:** `renderBanner.tsx:29` — `const state: StatusVariant = banner.state ?? 'info';`, forwarded to `bds-banner`'s `variant` prop
- **Recommended contract:** same as observed
- **Contract status:** confirmed — plan's Task 35 design decision: "`state` default: `'info'`, matching both `bds-banner`'s own default and every mockup"
- **Why it matters:** locks in the explicit default rather than relying on coincidental agreement with the child's own default
- **Covered by:** `bds-date-picker.banner.spec.ts::'renders the info variant by default when banner.state is unset'`, `'renders the variant matching an explicit banner.state override'`

### FM-73 | Banner dismissal via the close (`X`) button does not persist across a popover reopen
- **ID:** FM-73
- **Category:** race-timing
- **Risk:** without a reset, a consumer-set banner meant to always show on open could silently vanish forever after the user's first dismissal in a session
- **Input that reveals it:** open the popover, click `bds-banner`'s close icon, close the popover, reopen it
- **Observed current behavior:** `bds-date-picker.tsx:445-447` `handleBannerClose` sets `this.bannerDismissed = true`; `:1076-1079` renders `banner: this.bannerDismissed ? undefined : this.banner`; `:558-564` `listenClickTrigger` (guarded to only run when the popover is not already open) unconditionally resets `this.bannerDismissed = false` on every fresh open
- **Recommended contract:** same as observed
- **Contract status:** confirmed — plan's Task 36 note and TC-24 manual verification (2026-09-22): "confirmed reopening the popover re-shows the banner — a same-session dismissal does not persist"
- **Why it matters:** the plan explicitly flagged this as a boundary case needing an explicit ruling before implementation; now shipped and worth locking in with a regression test
- **Covered by:** `bds-date-picker.banner.spec.ts::'dismisses the banner when its close button is clicked'`, `'re-shows the banner after the popover is closed and reopened following a dismissal'`

### FM-74 | `renderBanner` never exposes `bds-banner`'s `actions` slot — structurally impossible, not merely unused
- **ID:** FM-74
- **Category:** component-contract-bypass
- **Risk:** a future edit wiring a consumer-supplied action element through would violate the "pure display surface, never drives date-picker-internal logic" contract; must be checked as an absence of the slotted DOM node, not just an absence of a prop, since `DatePickerBanner` has no field that could carry one anyway
- **Input that reveals it:** `banner` set with any `state` value
- **Observed current behavior:** `renderBanner.tsx:31-38` — the only children passed into `<bds-banner>` are `<span slot="title">` and the default-slot message text; no `slot="actions"` element exists anywhere in the source, and `DatePickerBanner` (`types.ts:3-9`) has no field that could produce one
- **Recommended contract:** same as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan acceptance criterion ("no `actions` slot exposed") that a future edit could violate without any type-level guard rail
- **Covered by:** `bds-date-picker.banner.spec.ts::'never renders an actions slot regardless of banner.state'`

### FM-75 | The footer's `Range:` label and its value are two independent elements, both present only when a range is committed
- **ID:** FM-75
- **Category:** null-empty
- **Risk:** rendering the label without a value (or vice versa) around the commit boundary would look broken; string-concatenating them instead of independent elements would prevent the label/value from being styled independently (per the Task 36 Figma audit)
- **Input that reveals it:** footer before any range is drafted/committed vs. after a range is selected
- **Observed current behavior:** `renderFooter.tsx:27-28` — `summary` is `''` until `rangeDuration !== undefined`; `:32-37` the `<Fragment>` wrapping both `.bds-date-picker__range-summary-label` and `.bds-date-picker__range-summary-value` spans only renders when `summary !== ''`, so both appear together or neither does
- **Recommended contract:** same as observed
- **Contract status:** confirmed — plan's Task 36 design decision 3: the label/value pair renders "only when a range is actually committed... NOT permanently rendered before any selection"
- **Why it matters:** the two-span structure is new (Task 36 fix); a regression collapsing it back to a single concatenated string, or rendering the label alone as permanent chrome, would both be silent visual regressions
- **Covered by:** `bds-date-picker.banner.spec.ts::'renders both the range-summary label and value once a range is committed'`, `'renders neither the range-summary label nor the value before any range is committed'`

### FM-76 | `showRangeTimeUnits` is wired to `isExpandedCalendarType` alone — `basic` always renders a days-only summary regardless of the underlying duration's hour/minute components
- **ID:** FM-76
- **Category:** equivalence
- **Risk:** if `basic`'s shared start/end time field ever produced a genuinely non-zero-hour/minute duration (e.g. a future change granting independent per-bound times under `basic`), an un-gated summary would leak time-unit text into a UI with no per-bound time selectors to explain it
- **Input that reveals it:** `basic` + `with-time`, non-zero shared hour, multi-day range
- **Observed current behavior:** `bds-date-picker.tsx:1120` — `showRangeTimeUnits: this.isExpandedCalendarType`; `formatRangeSummary` (`value-mapping.ts:379-397`) only appends the hours/minutes parts when `showTimeUnits` is `true`
- **Recommended contract:** same as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan hypothesis ("`basic`: days only / `expanded`: days/hours/minutes") that the plan itself flagged as needing verification against the actual `render()` wiring rather than being assumed
- **Covered by:** `bds-date-picker.banner.spec.ts::'never shows hour/minute text under basic, even with a non-zero shared hour set'`

### FM-77 | The footer's range-summary is derived from `this.draft` (not the committed `this.value`), so it updates live on every render while a range is still being selected, before Apply
- **ID:** FM-77
- **Category:** race-timing
- **Risk:** if the summary were derived from the committed value instead, it would read stale (frozen or blank) throughout the entire selection gesture and only "jump" to the correct text after Apply — the same class of stale-derived-value bug already fixed for the header/highlight code paths elsewhere in this catalog
- **Input that reveals it:** select a range's start day, then click a second, farther-away day, without pressing Apply
- **Observed current behavior:** `bds-date-picker.tsx:960-974` computes `rangeDuration` from `this.draft.rangeStart`/`durationRangeEndIso` (itself derived from `this.draft.rangeEnd`), never from `this.value`; recomputed on every `render()` call
- **Recommended contract:** same as observed
- **Contract status:** confirmed
- **Why it matters:** explicit plan acceptance criterion ("`banner` is expected to be reactive after mount... a consumer can update `banner.message` while the popover is already open") extended to the sibling range-summary feature landing in the same task; a stale-until-Apply summary would be a materially worse UX than the header/highlight already provide
- **Covered by:** `bds-date-picker.banner.spec.ts::'updates the footer summary live as a farther end day is selected, before Apply'`

## Pending-decision rows requiring a ruling before any test is written for them

None — all of FM-48 through FM-77 are `confirmed` and carry a `Covered by` entry. FM-67 records a boundary decision (equal-times same-day range does not shift) that reads as deliberate from the code but is worth a final human sanity check — flagged to the user in this session's report, not blocking.
