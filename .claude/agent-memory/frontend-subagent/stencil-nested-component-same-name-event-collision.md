---
name: stencil-nested-component-same-name-event-collision
description: Composing a child component whose bare @Event() shares a name with the parent's own public event causes duplicate/spurious bubbled events on the parent host
metadata:
  type: project
---

Composing `<bds-select>` inside `bds-date-picker`'s `renderTimeSelector.tsx` (EOA-17138 Task 3, single time selector) surfaced a real bug caught only via live browser testing, not `newSpecPage` unit tests: `bds-select` emits bare (bubbling, composed) `bdsChange`/`valueChange` events — the same names as `bds-date-picker`'s own public `@Event() bdsChange`/`@Event() valueChange`. Left unguarded, a consumer listening on the `bds-date-picker` host received TWO events per Apply: the inner select's raw hour/minute string (bubbled from deep inside the popover, wrong shape) followed by the picker's own correctly-typed value.

**Why:** Every `@Event()` in this codebase defaults to `bubbles: true, composed: true` unless explicitly overridden (see `[[feedback_custom_events_naming]]` for the `bds` + action naming rule, which doesn't prevent this collision since both components independently follow it). Any composed child whose event name matches a parent's own public event name will silently leak through the parent host's event surface unless stopped at the source.

**How to apply:** Whenever composing a `bds-*` child component (not just `bds-text-field`, which this component already guards via `stopFieldValueChange`) inside a component that itself emits an event of the same name, add an explicit `event.stopPropagation()` handler for every event name shared between parent and child — including events you don't otherwise care about (e.g. `valueChange` here had no functional handler, only a propagation-stopping one). `newSpecPage` unit tests won't catch this since bubbling through real DOM composition isn't always exercised the same way; verify via a live browser (`pnpm dev:components` + a listener on the host element) before considering a composite-child implementation done.
