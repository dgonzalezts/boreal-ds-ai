# Stencil Composite Components — Light DOM Event Boundary

Any Stencil composite component that accepts child components via named slots and re-emits their events must call `event.stopPropagation()` before re-emitting. Without it, consumers receive each event twice.

## Why this happens

Slotted child elements remain in the **light DOM** — they are not placed inside a shadow boundary. Their events bubble naturally up the DOM tree to the composite host element. When the host also listens to the same event via `addElementListener` and re-emits its own version, both the original (bubbled) and the re-emission reach external listeners.

## Canonical example — `bds-select` (BUG-001)

`bds-select` accepts `bds-list-menu` via `<slot name="list">` and `bds-text-field` via `<slot name="field">`. Both are light DOM. The component's `listenListMenu()` method (`bds-select.tsx:151`) adds a listener on `bdsList` and calls `this.setValue()` which re-emits `bdsChange` and `valueChange` — but never calls `stopPropagation()`.

**Result per user selection:** 4 events fire instead of 2.

Additionally, the two `valueChange` firings carry different `detail` values:
- `bds-select` re-emits `detail: "option2"` (the **value key**)
- `bds-text-field` bubbles `detail: "Option 2"` (the **display label**, set when `updateElementAttr(this.bdsField, 'value', labelText)` triggers `@Watch('value')` → `this.valueChange.emit(next)`)

A consumer listening to `valueChange` on the host receives two firings with different semantic meanings. Vue `v-model` or any handler that reads `event.detail` may silently bind the display label instead of the value key.

## Fix pattern

All changes belong in the **host composite component only** — child components are not touched.

```typescript
// In the listener that re-emits: stop the child's event first
addElementListener(this.bdsList, 'bdsChange', (event: Event) => {
  event.stopPropagation(); // prevent bds-list-menu's event reaching consumers
  const value = (event as CustomEvent<string | undefined>).detail ?? '';
  this.setValue(value);
});

// For every child event the host owns but does NOT re-emit:
// add a stop-propagation-only guard
addElementListener(this.bdsField, 'valueChange', (event: Event) => {
  event.stopPropagation();
});
addElementListener(this.bdsField, 'bdsChange', (event: Event) => {
  event.stopPropagation();
});
```

## How to detect this pattern in other composite components

1. Open the story in Storybook with the Actions panel wired (see `storybook-action-wiring-web-components.md`)
2. Trigger a single interaction
3. If the Actions panel shows more entries than expected, check `from` (i.e. `e.target.localName`) on each entry
4. Any entry where `from` is a child element name (not the host) is a leaked event — a `stopPropagation()` guard is missing

Alternative DevTools technique:
```javascript
monitorEvents($0, ['bdsChange', 'valueChange']) // $0 = host element selected in Elements panel
// interact, then:
unmonitorEvents($0)
```

Component source: `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`
Bug report: `ai-work/qa/bug-reports/BUG-001-bds-select-valuechange-double-fire.md`
Test case: TC-FUNC-011 in `ai-work/qa/test-plans/bds-select-test-plan.md`
