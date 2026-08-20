---
name: bds-date-picker-open-and-sync-mechanics
description: bds-date-picker test setup gotchas — must open via field.click() (not popover.openPopover()) to exercise draft reset; format/locale prop changes made after mount do not re-sync the slotted field's displayed value, only value changes do
metadata:
  type: project
---

Two non-obvious mechanics in `bds-date-picker.tsx` (`packages/boreal-web-components/src/components/forms/bds-date-picker/bds-date-picker/`) that change what a test must do to exercise real behavior:

1. **Draft-reset-on-reopen lives on the click handler, not on the popover's own open lifecycle.** `listenClickTrigger` (the component's own `click` listener on the slotted field) is what calls `cloneDraftFromValue(this.value)` before opening — `bds-popover`'s `openPopover()` `@Method()` itself has no such hook. Calling `ctx.popover.openPopover()` directly in a test bypasses this reset entirely, so an abandoned draft from a previous session will incorrectly appear to persist. Tests asserting the "reopen resets an abandoned draft to the last committed value" behavior (Task 15) must open via `ctx.field.click()`, not `ctx.popover.openPopover()`.

2. **`syncFieldValue()` (which pushes the formatted display string onto the slotted field's `value` property) only runs from `componentDidLoad` and the `@Watch('value')` handler.** There is no `@Watch('format')` or `@Watch('locale')`. Changing `format` or `locale` on an already-mounted `bds-date-picker` does **not** re-format the trigger field's already-displayed text — only a subsequent `value` change does. To test locale's effect on the *trigger field's* display text, the locale must be set before the component's initial connect (e.g. build via `page.doc.createElement('bds-date-picker')`, set `.locale`/`.format`/`.value` as JS properties, append the slotted field child, then `page.body.appendChild(...)` — locale/object props can't be expressed as HTML attribute strings anyway). Locale's effect on the *calendar grid's* month/year header label, by contrast, **is** reactive post-mount, since `render()` reads `this.locale` directly on every render pass rather than through an imperative one-time sync.

**Why:** both discovered empirically while writing Task 20's Phase 1 spec suite — assuming either mechanism worked the "obvious" way (via `popover.openPopover()`, or via ordinary reactive re-render for locale) produced tests that silently asserted the wrong thing until cross-checked against actual `newSpecPage` output.

**How to apply:** reuse for any future `bds-date-picker` test work (Phase 2/v2 plan, range selection, etc.) — see `date-picker.test-utils.ts` in the component's `__test__/` directory for the working `renderDatePicker`/`openDatePicker` helpers built around these constraints.
