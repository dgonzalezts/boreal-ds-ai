# Stencil mock-doc has no DragEvent or DataTransfer

Stencil's custom Jest test environment (`@stencil/core/testing`'s `jest-environment.js`, used by `newSpecPage`) does not define `DragEvent` or `DataTransfer` globally — `typeof DragEvent` and `typeof DataTransfer` are both `'undefined'`. This differs from `KeyboardEvent`/`MouseEvent`/`Event`, which are all available in mock-doc. Attempting `new DragEvent(...)` or `new DataTransfer()` in a spec file throws `ReferenceError` immediately.

## Working pattern — use the shared helper, don't hand-roll it

`src/utils/testing/mocks/dragDrop.ts` exports:

- `createDragDataTransferMock(): MockDataTransfer` — an in-memory-store-backed object implementing `dropEffect`/`effectAllowed`/`getData`/`setData`. Reuse the same instance across a `dragstart`/`dragover`/`drop`/`dragend` sequence so `setData` during `dragstart` is readable via `getData` during `drop`, mirroring real browser behaviour where one `DataTransfer` is shared for the whole drag gesture.
- `createDragEvent(type: string, dataTransfer: MockDataTransfer, relatedTarget?: EventTarget | null): Event` — builds a plain `Event` with `dataTransfer` (and, since EOA-16000's column-reorder cursor-flicker fix, an optional `relatedTarget`) attached as properties, ready to `dispatchEvent`. The `relatedTarget` parameter is backward-compatible — omit it and it defaults to `null`, matching every pre-existing 2-argument call site. Needed for testing `dragleave` handlers that inspect where the pointer is heading (e.g. a `th.contains(e.relatedTarget as Node)` guard to avoid clearing a drop-target highlight when the pointer is still within the same element's subtree).

Both are exported through the `mocks/index.ts` barrel, so they resolve via `@/utils` exactly like `setupMutationObserverMock`/`setupResizeObserverMock`.

`event.target`/`event.currentTarget` are still populated correctly by mock-doc's native `dispatchEvent` mechanism (standard `EventTarget` behaviour) when dispatched this way, so component code reading `(e.currentTarget as HTMLElement)` or `(e.target as HTMLElement).closest(...)` works unmodified — no special handling is needed for those.

## Scope

This is a cross-cutting mock-doc environment gap, not specific to any one component. Any component using native HTML5 drag/drop needs this workaround when writing its spec files. `bds-card-header` already ships a native-drag/drop `reorder` prop (six-dot handle) and would hit the identical gap if its drag/drop behaviour is covered by future spec files. `bds-table`'s column-reorder six-dot handle was modelled on that same pattern.

## Source

Discovered while writing `packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/__test__/bds-table.reorder.spec.ts` for `bds-table`'s column drag/drop reorder feature (EOA-16000). Documented in the testing guideline at `ai-docs/guidelines/stencil-unit-testing-patterns.md` § "Simulating native drag/drop events". Originally captured in per-scope memory at `.claude/agent-memory/testing-subagent/stencil-mock-doc-no-dragevent-datatransfer.md`.
