---
name: stencil-jsx-boolean-aria-attr-empty-string
description: Stencil JSX renders aria-selected={true} as aria-selected="" (empty string), not the ARIA-spec-required "true"/"false" string
metadata:
  type: project
---

Found in `bds-calendar-grid.tsx` (`renderDayCell`, EOA-16692 Task 9 manual QA, 2026-08-14): `aria-selected={cell.isoDate === this.selectedDate}` renders in the DOM as `aria-selected=""` when true, not `aria-selected="true"`. Stencil's `h()` treats a boolean-valued `aria-*` prop the same as a native HTML boolean attribute (present-with-empty-value), but ARIA semantics require the literal string `"true"`/`"false"` — an empty string is not equivalent and some assistive tech may not announce it as selected. `aria-current={cell.isToday ? 'date' : undefined}` on the same component renders correctly because it's already a string value, not a boolean.

**Why:** confirmed via `querySelectorAll('td[aria-selected=true]')` returning 0 matches even though the correct cell had the `--selected` CSS class applied — the underlying attribute value was `""`, not `"true"`. Only found by inspecting `outerHTML` directly.

**How to apply:** when writing or reviewing Stencil JSX that sets a boolean-typed `aria-*` attribute, use `aria-selected={cell.isSelected ? 'true' : 'false'}` (explicit string) rather than passing a raw boolean. Flag this pattern in any component review; not yet filed as a fix (Task 9 QA report deferred it to the implementing agent / Task 11 a11y pass since it doesn't block Task 9's own checklist, which only requires CSS-class-based selection to be correct).
