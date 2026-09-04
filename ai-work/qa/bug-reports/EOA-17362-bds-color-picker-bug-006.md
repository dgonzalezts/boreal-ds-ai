# BUG-006: `bds-color-picker` — the popover's dropper/eyedropper toggle button has no accessible name

**Severity:** Low
**Priority:** P3
**Type:** Accessibility
**Status:** Open
**Component:** `bds-color-picker` (via `bds-color-format`)
**Discovered during:** TC-A11Y-002 (incidental — surfaced as a repeated console warning throughout the whole QA pass)
**Affects:** Screen-reader users of any `bds-color-picker` instance

---

## Environment

- **Component:** `bds-color-format` (icon button rendered inside the popover, `<i class="bds-icon-dropper">`, no `label` prop / `aria-label`)
- **Browser:** Chrome (latest stable), via `playwright-cli`

---

## Description

Every `bds-color-picker` instance on the playground page logs, on mount:

```
[WARNING] [BorealDS Button] No accessible name found. Provide a "label" prop, visible text in the default slot, or an aria-label/aria-labelledby on the icon slot content.
```

This traces to the "dropper" (eyedropper) icon button rendered inside the popover's `bds-color-format` controls (`<button class="bds-button ..."><i slot="icon" class="bds-icon-dropper"></i></button>`), which has no `label` prop, no visible text, and no `aria-label`/`aria-labelledby` on the icon.

Note: the test plan's "Out of Scope" section explicitly excludes "Dropper functionality" (its click behavior), so this report is scoped narrowly to the **accessible name** of the button itself, which is a separate, in-scope concern under TC-A11Y-002 ("controls have meaningful accessible names") — a screen-reader user tabbing to this button today hears no discernible label regardless of whether its click behavior is exercised.

---

## Steps to Reproduce

1. Open `http://localhost:3333`.
2. Open any `bds-color-picker` popover.
3. Observe the DevTools console warning from `bds-button.entry.js`, or inspect the button's accessible name via the browser Accessibility panel.

---

## Expected Behaviour

The dropper button should have a discernible accessible name (e.g. `label="Pick color from screen"` or similar), satisfying TC-A11Y-002's "meaningful accessible names" requirement for all controls in the popover.

---

## Actual Behaviour

The button has no accessible name; `getComputedAccessibleNode`/screen readers announce it with no label, and the component's own internal `bds-button` guard logs a console warning on every mount.

---

## Impact

Low — the button is a secondary/advanced control (eyedropper), and its underlying functionality is explicitly out of scope for this ticket. However, the console warning fires on every single `bds-color-picker` mount across the whole application, and any screen-reader user who does reach the button gets no indication of its purpose.

---

## Suggested Fix

Add a `label` prop (visually hidden if a bare icon button is the desired visual treatment) to the dropper button in `bds-color-format.tsx`, e.g. `label="Pick a color from the screen"`.

---

## Related

- Test plan: `ai-work/qa/test-plans/EOA-17362-bds-color-picker-test-plan.md` → TC-A11Y-002
- Similar pattern previously tracked for another component: `ai-work/qa/bug-reports/2026-08-06-bds-button-accessible-name-remaining.md`
