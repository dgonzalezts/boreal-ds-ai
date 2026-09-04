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
