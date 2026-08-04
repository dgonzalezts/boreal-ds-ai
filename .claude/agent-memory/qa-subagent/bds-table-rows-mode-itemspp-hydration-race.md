---
name: bds-table-rows-mode-itemspp-hydration-race
description: bds-table silently ignores a non-default items-per-page on a slotted bds-pagination when .rows is set immediately after markup
metadata:
  type: project
---

`bds-table`'s rows-mode pagination setup (`onRowsChange` at `bds-table.tsx:297`, `setupRowsPagination` at `bds-table.tsx:1147`) reads `paginationEl.itemsPerPage` synchronously off the live slotted `<bds-pagination>` DOM element at the moment `.rows` is assigned. If the paginator hasn't finished hydrating yet — which it hasn't if a consumer sets `.rows` from an inline `<script>` immediately following the markup (a very common integration pattern, module-script execution is deferred past HTML parse) — this read returns the paginator's class-default `itemsPerPage` (10), not the attribute-declared value. The table then silently paginates as if `items-per-page` were 10 regardless of what was declared.

**Repro:** `<bds-pagination slot="paginator" items-per-page="5">` + `table.rows = [...]` set in an immediately-following `<script>` block → table behaves as itemsPerPage=10.

**Why it stayed hidden:** every existing playground example (Task 8's `selectAllPages` tables) happens to use `items-per-page="10"`, matching the default, so the bug is invisible unless a non-default value is used.

**How to apply:** when building any manual-QA scenario for `bds-table` rows-mode + pagination, either use `items-per-page="10"` (the default) or verify the actual rendered page boundaries via DOM query before trusting the declared `items-per-page` value — don't assume a non-default value took effect. Reported to team-lead 2026-08-04 during EOA-16000 Task 10 QA (not fixed, out of scope for that task).
