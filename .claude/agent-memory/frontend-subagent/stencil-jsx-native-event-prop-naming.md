---
name: stencil-jsx-native-event-prop-naming
description: Stencil JSX native event props follow the exact Window handler property name — focusin/focusout are `onFocusin`/`onFocusout`, not `onFocusIn`/`onFocusOut`
metadata:
  type: project
---

Stencil's JSX event-prop casing is **not** uniform camelCase. For `on*` props it resolves the listener name at runtime in `@stencil/core/internal/client/index.js` (`set-accessor.ts`, ~lines 2397–2404):

1. `let ln = memberName.toLowerCase()`
2. if `memberName[2] === '-'` → strip `on-`
3. else if `ln in window` → use `ln.slice(2)` (fully lowercased event name)
4. else → lowercase only the first char after `on`, preserve the rest

Because `window.onfocusin` / `window.onfocusout` exist (non-standard but real, and also stubbed on mock-doc's `MockWindow`), a JSX `onFocusIn` resolves to `ln.slice(2)` = `focusin` at runtime, but **TypeScript rejects it**: Stencil's JSX type in `@stencil/core/internal/stencil-public-runtime.d.ts` declares the member as `onFocusin?: (event: FocusEvent) => void` (and `onFocusout`). `tsc -p tsconfig.build.json` errors with `Property 'onFocusIn' does not exist ... Did you mean 'onFocusin'?`.

**Rule:** for an unfamiliar native event, match the casing to the `Window`/`GlobalEventHandlers` property name, not to general camelCase intuition. `onMouseEnter` keeps the capital `E` (there is no `window.onmouseenter` lowercased-prop of that exact name in the type), while `focusin`/`focusout` are lowercase in both the type and the runtime resolution.

- Found EOA-17662 Task 40c adding `onFocusin`/`onFocusout` (bubbling focus events) to `bds-calendar-grid`'s `<table>`.
- mock-doc defines `onfocusin`/`onfocusout` on its `MockWindow` (verified in `@stencil/core/mock-doc/index.js`), so the JSX prop resolves and fires under `newSpecPage` too — no `addElementListener` fallback needed.
- `event.currentTarget` is valid inside a JSX `on*` handler invoked synchronously during dispatch (used for the "focus left the table" containment check).
