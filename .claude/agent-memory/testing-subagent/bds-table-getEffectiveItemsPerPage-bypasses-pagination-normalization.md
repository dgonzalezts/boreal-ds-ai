---
name: bds-table-geteffectiveitemsperpage-bypasses-pagination-normalization
description: bds-table's items-per-page attribute fallback reads the raw HTML attribute, bypassing bds-pagination's own itemsPerPage validation/normalization — matters when choosing test fixture values
metadata:
  type: project
---

`getEffectiveItemsPerPage` (`bds-table.tsx:1158-1160`) reads `paginationEl.getAttribute('items-per-page')` directly and uses `Number(...)` on it, without going through `bds-pagination`'s own `normalizeItemsPerPage` validation (which restricts values to `[10, 25, 50, 100]` by default and falls back to the first option, logging a `console.warn`, for anything else).

**Consequence for test fixtures**: an `items-per-page="5"` attribute on a slotted `<bds-pagination>` is silently accepted by `bds-table`'s slicing logic (visible rows = 5) even though `bds-pagination` itself would normalize its own `itemsPerPage` property to `10` and log a warning. Discovered while writing a regression test for the pagination-hydration-race fix ([[testing-task10-bugfix-regression]] session, EOA-16000 Task 10): using `items-per-page="5"` produced a passing test but leaked a `console.warn` and relied on an edge case (raw-attribute value outside the validated option set) rather than the intended "attribute honored before hydration" behavior. Fixed by using `items-per-page="25"` (a valid option) instead.

**How to apply**: when writing tests around `items-per-page`/pagination sizing on `bds-table`, always pick a value from bds-pagination's allowed options (`[10, 25, 50, 100]` unless the component's own `options` prop overrides it) unless the test is specifically targeting this bypass behavior itself.
