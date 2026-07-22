---
name: stencil-bds-pagination-requires-resizeobserver-mock
description: newSpecPage throws "ResizeObserver is not defined" when BdsPagination is registered as a real child component unless setupResizeObserverMock() is called
metadata:
  type: project
---

Any spec file that registers `BdsPagination` in `newSpecPage({ components: [...] })` (e.g. to assert on a real slotted `<bds-pagination slot="paginator">`'s rendered DOM or state) must also call `setupResizeObserverMock()` (from `@/utils`, same import group as `setupMutationObserverMock`) at the describe level — `BdsPagination.componentWillLoad` calls `setupResizeObserver()`, which does `new ResizeObserver(...)` unconditionally. Stencil's mock-doc has no `ResizeObserver` global, so omitting the mock throws `ReferenceError: ResizeObserver is not defined` for every test in the file, not just the ones directly touching the resize logic.

Confirmed precedent: `bds-table.rows.spec.ts` already calls both `setupMutationObserverMock()` and `setupResizeObserverMock()` for exactly this reason. Applied the same pair when adding `bds-table.skeleton.spec.ts`'s "paginator skeleton" tests (EOA-15507 Task 5b) — omitting `setupResizeObserverMock()` failed 5 of 6 new tests (only the no-paginator-slotted no-op test passed) until added.

**How to apply:** before writing any new spec file for a component that slots or wraps `bds-pagination` and registers it as a real child (not just tag presence), grep sibling spec files in the same `__test__/` directory for `setupResizeObserverMock` first — same "check siblings" convention as `suppressConsoleWarn`/`suppressConsoleError` in `testing-knowledge`.
