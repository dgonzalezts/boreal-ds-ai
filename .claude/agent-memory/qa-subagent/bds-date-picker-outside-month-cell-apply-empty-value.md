---
name: bds-date-picker-outside-month-cell-apply-empty-value
description: RESOLVED — outside-month cell + Apply (and Apply with no draft selection at all) no longer fires bdsChange/valueChange with an empty value; handleFooterAction's APPLY case now guards on draft.selectedDate !== null
metadata:
  type: project
---

**RESOLVED (2026-08-19, EOA-16692 targeted regression QA).** `bds-date-picker.tsx`'s `handleFooterAction`'s `APPLY` case now only calls `commitValue()` when `this.draft.selectedDate !== null`; it still always closes the popover regardless. Verified via `packages/boreal-web-components/src/index.html` `#date-picker-footer-apply` scenario:
- Open + Apply with zero day clicks: `value` stays `''`, zero `bdsChange`/`valueChange` events, popover still closes (`aria-hidden="true"`).
- Click an outside-month cell (`Sunday, July 26th, 2026`, `.bds-calendar-grid__day--outside`, `aria-disabled` absent) then Apply: confirmed `bdsDayClick` never fires for that click (0 events), so the draft is genuinely untouched; Apply produces the same no-op result as above.
- Regression check — real in-month day (`Saturday, August 1st, 2026`) + Apply: `bdsDayClick` fires once, then Apply commits `value="2026-08-01"`, `bdsChange`/`valueChange` each fire exactly once with `"2026-08-01"`, field text becomes `"2026/08/01"` — unaffected by the guard.
- Regression check — Clean/`Clear` button (labeled "Clear" via `DEFAULT_FOOTER_LABELS`, not "Clean") on `#date-picker-footer-clean` (`value="2026-08-12"`): still unconditionally commits `''` and emits `bdsChange`/`valueChange` once each, regardless of the Apply-side guard.
- 0 console errors across the run (63 pre-existing unrelated warnings, e.g. missing-slotted-field warning scenario).

Original bug description (now historical) below.

---

During EOA-16692 `bds-date-picker` smoke QA (2026-08-19) in `packages/boreal-web-components/src/index.html`, clicking a previous/next-month overflow day cell (class `bds-calendar-grid__day--outside`) is NOT blocked by `aria-disabled` (it's a distinct class from disabled days, and is not `aria-disabled="true"`) — but clicking Apply afterward fires `bdsChange #1`/`valueChange #1` with an empty string value instead of either committing that date or being a no-op.

Confirmed in `#date-picker-footer-apply` scenario: outside-month cell "Sunday, July 26th, 2026" clicked while grid showed August 2026 → Apply → console logged `valueChange #1` with no value payload (blank), and trigger field stayed empty.

**Why:** discovered incidentally while executing TC-FUNC footer-actions smoke check — selector logic `[role=gridcell]:not([aria-disabled=true])` matches outside-month cells too since Stencil renders `aria-disabled=""` (not `"true"`) per [[stencil-jsx-boolean-aria-attr-empty-string]], so a naive query picks an unintended cell.

**How to apply:** (1) When picking a "clickable day" cell for any QA scenario, explicitly exclude `.bds-calendar-grid__day--outside` too, not just aria-disabled — outside-month days are a separate concern from disabled days. (2) This outside-month-cell-then-Apply-empty-value behavior itself was NOT part of the prescribed EOA-16692 smoke-check checklist and was not further investigated — flag it for the full TC-by-TC pass (test plan `ai-work/qa/test-plans/EOA-16692-bds-date-picker-test-plan.md`) to determine if outside-month cells should be selectable/navigate-to-that-month, or should be inert like disabled days.
