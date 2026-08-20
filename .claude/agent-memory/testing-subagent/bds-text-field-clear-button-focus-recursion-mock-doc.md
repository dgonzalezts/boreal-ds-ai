---
name: bds-text-field-clear-button-focus-recursion-mock-doc
description: clicking bds-text-field's clear (X) button in newSpecPage prints a caught "Maximum call stack size exceeded" RangeError to console.error, from an infinite focus->onFocus->focus loop in mock-doc — harmless to test outcomes but noisy; use suppressConsoleError()
metadata:
  type: project
---

`bds-text-field`'s `handleClear` (`packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`) ends with an explicit `(this.el as HTMLElement).querySelector<HTMLInputElement>('input')?.focus()`. The Host itself also has `onFocus={() => !this.readOnly && ... .focus()}`. In Stencil's `mock-doc` environment, calling `.focus()` on the inner `<input>` dispatches a `focus` event that bubbles up to the Host, re-triggering the Host's own `onFocus` handler, which calls `.focus()` again — an infinite loop. Real browsers don't re-fire `focus` on an already-focused element, but mock-doc's `MockInputElement.focus()` doesn't check that, so this recurses until Node's call stack overflows.

The recursion is caught somewhere inside mock-doc's event-dispatch machinery (`triggerEventListener`), so it does **not** throw out of the test or fail it — it just prints a `console.error` with a collapsed, very long stack trace (`RangeError: Maximum call stack size exceeded`) every time this code path runs (clicking the clear button, or anything else that calls `.focus()` on the field's inner input while the field is mounted).

**Why:** hit while writing `bds-date-picker.events.spec.ts`'s "slotted field's own clear (bdsClear) commits an empty value" tests — output was flooded with this trace even though every assertion passed.

**How to apply:** any spec file that clicks a `bds-text-field`'s clear button (`button.bds-text-field__action--clear`) should call `suppressConsoleError()` at the describe/file level to keep output readable — this is a pre-existing `bds-text-field`/mock-doc interaction quirk, not something to "fix" as part of an unrelated testing task. Candidate for promotion to `.agents/memory/` since it affects every component that composes a clearable `bds-text-field` (e.g. `bds-select`, `bds-date-picker`).
