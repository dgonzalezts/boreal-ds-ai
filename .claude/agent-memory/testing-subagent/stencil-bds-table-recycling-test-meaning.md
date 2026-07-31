---
name: stencil-bds-table-recycling-test-meaning
description: What "row recycling" actually means to test in bds-table's cache-backed cell rendering (formatter/template/row-detail), since Stencil keys <tr> by rowId
metadata:
  type: project
---

`bds-table.tsx` renders each body `<tr>` with `key={id}` (the row's own id), not a positional/index key. Confirmed via `bds-table.virtual.spec.ts`'s "reuses the same DOM node for a row across a sort instead of recreating it" test: sorting the same set of rows keeps the same DOM `<tr>` per row id, it does not shuffle DOM nodes across different row ids.

**Consequence for "row recycling" tests** (used for `applyCellFormatter`, `applyRowDetail`, and Task 3's `applyCellTemplate`, all backed by the shared `CellContentCache` keyed `` `${key}:${rowId}` `` with a `cached.row === row` identity guard): a real different-row-occupies-the-same-DOM-node scenario does not happen through Stencil's own vdom reconciliation in this component, because the key always matches the row id. The actual regression this cache guards against is **the same row id being re-supplied as a genuinely new object reference** (e.g. data reloaded from a server, same ids, new objects) — the map key hits but `cached.row !== row` fails the identity check, forcing a re-clone instead of serving stale content.

**How to write the test**: mirror `bds-table.formatter.spec.ts`'s "re-invokes the formatter for every row when data is reassigned to a genuinely new array" pattern — reassign `root.data = ROWS.map(row => ({ ...row, someField: 'changed' }))` (same ids, new objects, changed field) and assert the cached node/content is replaced, not reused. This is what a plan's "under virtualized scroll, recycling a `<tr>` to a different row" wording actually maps to in this codebase's implementation — it is not literally about `virtual="true"` windowing (though a companion `virtual="true"` + sort test, patched with the usual `offsetHeight`/`offsetWidth`/`getBoundingClientRect` mocks from [[stencil-tanstack-virtual-core-mock-doc-pattern]], is a reasonable belt-and-suspenders addition and does exercise the real virtualizer path).

Verified while writing `bds-table.template-cell.spec.ts` for EOA-16000 Task 3 (`<template slot="cell">` custom cell content), 2026-07-31.
