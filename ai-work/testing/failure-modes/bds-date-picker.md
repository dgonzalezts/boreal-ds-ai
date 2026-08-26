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
