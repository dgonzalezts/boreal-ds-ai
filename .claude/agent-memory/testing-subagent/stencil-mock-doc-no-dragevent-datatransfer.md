---
name: stencil-mock-doc-no-dragevent-datatransfer
description: newSpecPage/mock-doc has no global DragEvent/DataTransfer; use the shared createDragDataTransferMock/createDragEvent helper instead of hand-rolling it per spec file
metadata:
  type: project
---

`@stencil/core/testing`'s `newSpecPage`/mock-doc environment does not define a global `DragEvent` or `DataTransfer` constructor. `new DragEvent(...)` throws in spec files.

**Fix is a shared helper, not a per-file workaround.** `src/utils/testing/mocks/dragDrop.ts` exports:

- `createDragDataTransferMock(): MockDataTransfer` — an in-memory-store-backed object implementing `dropEffect`/`effectAllowed`/`getData`/`setData`. Reuse the same instance across a `dragstart`/`dragover`/`drop`/`dragend` sequence to mimic the browser's single-payload-per-drag behavior.
- `createDragEvent(type: string, dataTransfer: MockDataTransfer): Event` — builds a plain `Event` with `dataTransfer` attached as a property, ready to `dispatchEvent`. `event.target`/`currentTarget` populate correctly since it's a real `Event` under the hood.

Both are exported through the `mocks/index.ts` barrel, so they resolve via `@/utils` exactly like `setupMutationObserverMock`/`setupResizeObserverMock`.

First used (and originally hand-rolled inline) in `src/components/data-visualization/bds-table/bds-table/__test__/bds-table.reorder.spec.ts`; extracted into the shared helper on 2026-07-31 specifically so `bds-card-header`'s own native drag/drop (six-dot `reorder` handle, which `bds-table`'s reorder feature deliberately mirrors) can reuse it once that component gets drag/drop test coverage — `bds-card-header`'s spec files had none as of this session.

See also [[stencil-scoped-test-invocation]] for how to run a single component's spec suite when validating changes here.
