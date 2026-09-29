# bds-date-picker `expanded` focus hand-off — flush microtasks before waitForChanges

Verified 2026-09-28 (EOA-17662, cross-month arrow traversal tests).

## Async hand-off needs `flushMicrotasks()` BEFORE `waitForChanges()`

`bds-date-picker.tryHandOffFocus` (`bds-date-picker.tsx:471-501`) calls
`void sibling.focusDate(detail.focusDate).then(moved => { ... })`. The `.then` body runs as a
**microtask** after the keydown handler returns. On the `moved === false` branch it calls
`applyMonthNavigate(slot, detail)`, which sets `@State displayMonth`/`displayYear` **and** calls
`resetCalendarViews()` (an async `@Method()` on every grid).

In `newSpecPage`, dispatching the arrow then `await page.waitForChanges()` only flushes the renders
that the *synchronous* event handler scheduled. The microtask-deferred `applyMonthNavigate` renders —
and the closing of the sibling's quick-picker — happen after. Correct order:

```ts
dispatchKey(cell, KEYBOARD.ArrowRight);
await flushMicrotasks();          // let the focusDate(...).then(...) chain run
await ctx.page.waitForChanges();  // flush the renders it scheduled
```

`flushMicrotasks` is exported from `@/utils` (`src/utils/testing/helpers.ts`). Putting
`waitForChanges()` first leaves `displayMonth` correct only for the synchronous (non-fallback) paths
and leaves the sibling picker overlay still mounted for the hardened-fallback path.

The tests where the hand-off succeeds (sibling takes focus) or the window shifts *synchronously* for a
non-`expanded` picker work with either order, so the ordering bug only shows up in the fallback case.

## Opening a grid quick-picker moves DOM focus onto a month cell

Clicking `.bds-calendar-grid__header .bds-calendar-grid__label-button` sets `view = 'months'`;
`@Watch('view')` sets `_pendingViewFocus = true`, and `componentDidUpdate` then calls
`focusActiveViewPriorityCell()` → `focusPickerCellByKey` → `rovingTabindex` → **real focus on a month
picker `<td>`**. So a `focusDate(...)` test while `view !== 'days'` must assert DOM focus is
*unchanged*, not `toBeNull()`. `focusDate` itself returns `false` there because `getGridItems()`
returns the picker items and `indexOf(dayCellEl) === -1`.

## `componentDidUpdate` pending-ISO guard — drive it via a prop-only re-render

`_pendingFocusIsoDate` is a plain private field (no `@State`), so setting it schedules no render. To
exercise the guard: set it on `page.rootInstance`, then change a prop (`element.selectedDate = ...`)
and `await page.waitForChanges()`. `componentDidUpdate` reads it once and resets it. An ISO not in the
displayed month leaves DOM focus untouched (only `markTabbableCell` runs); an in-month ISO moves focus
via `focusCell`.
