---
name: bds-table-column-visibility-technique
description: bds-table-column only reacts to childList DOM mutations; display:none on it has no visual effect — must remove/reinsert the element to hide/show a column in a story.
metadata:
  type: project
---

`<bds-table-column>` renders no visible DOM of its own (always `display: none` on its own host —
see its JSDoc in `bds-table-column.tsx`). The actual `<th>`/`<td>` cells are rendered by `bds-table`
from an internal `columns` array, refreshed only by a `MutationObserver` configured with
`{ childList: true, subtree: true }` (`bds-table.tsx` `componentDidLoad`) — it does **not** watch
`attributes`. Consequently, setting `col.style.display = 'none'` on a `<bds-table-column>` element
has zero effect on the rendered table: the column keeps rendering exactly as before.

**How to apply:** to actually hide/show a column from consumer/story code, remove the
`<bds-table-column>` element from the DOM (`col.remove()` / `table.removeChild(col)`) and
re-insert it (`table.insertBefore(col, nextStillAttachedSibling ?? null)`) to restore original
column order on re-show. This is the technique used in the `WithColumnVisibilityDropdown` story
(`apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`, EOA-16000 Task 13)
and documented in the "Column visibility" section of `bds-table.mdx`. A prior doc pass had written
the `display: none` approach as if it worked — corrected during this task after empirically
verifying via Playwright that it did not change the rendered `<th>` list.

See also [[argtypes-name-collision-across-subcomponents]] for other `bds-table` sub-component docs
gotchas.
