---
name: stencil-resizeobserver-callback-capture-and-conditional-data-col-key
description: How to manually trigger a mocked ResizeObserver's callback in newSpecPage tests, and a gotcha where bds-table's <th> only carries data-col-key conditionally
metadata:
  type: project
---

## Triggering a mocked `ResizeObserver` callback manually

`setupResizeObserverMock()` (`src/utils/testing/mocks/observers.ts`) replaces `global.ResizeObserver`
with a `jest.fn()` constructor mock but does not expose a way to invoke the callback the component
passed in. The established codebase pattern (originated in
`bds-pagination.behavior.spec.ts`, reused for `bds-table.pin-offsets.spec.ts`) is to read the
callback straight off the constructor mock's captured call arguments:

```ts
const resizeCallback = (global.ResizeObserver as unknown as jest.Mock).mock.calls.at(-1)?.[0] as
  | ((entries: unknown[]) => void)
  | undefined;
assertExists(resizeCallback, 'resize observer callback not captured');
resizeCallback([]);
```

`.at(-1)` grabs the most recently constructed observer, which is correct as long as only one
component under test in the file constructs a `ResizeObserver`. This works because
`setupResizeObserverMock`'s underlying mock is `jest.fn().mockImplementation(() => methods)` — the
constructor mock's own `.mock.calls` array records every `new ResizeObserver(cb)` call's arguments,
regardless of what the returned `methods` object looks like.

To assert `disconnectedCallback` calls `.disconnect()`, grab the live instance off
`page.rootInstance` (e.g. `(page.rootInstance as unknown as { resizeObserver?: { disconnect: jest.Mock } }).resizeObserver`)
rather than trying to intercept the shared mock — the returned `methods` object literal in
`observers.ts` is shared across every `new ResizeObserver()` call in the same describe block, so a
handle obtained via the component instance is the only reliable, test-scoped reference to that
particular disconnect spy.

## `bds-table`'s `<th>` only gets `data-col-key` conditionally

Unlike `<td>` (which always renders `data-col-key`), `bds-table.tsx`'s header `<th>` only sets
`data-col-key` when the column is `sortable` or currently pinned (`bds-table.tsx` header render,
`sortableProps`/`pinnedProps` spread). A `th[data-col-key="..."]` selector will not match an
unpinned, non-sortable column's header — locate it by column order
(`root.querySelectorAll('thead th')[index]`) or by its `.bds-table__th-label-text` text content
instead, then switch to the `data-col-key` selector only after the column becomes pinned/sortable.
