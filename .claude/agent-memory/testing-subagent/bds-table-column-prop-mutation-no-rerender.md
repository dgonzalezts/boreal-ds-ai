---
name: bds-table-column-prop-mutation-no-rerender
description: Setting a bds-table-column JS property (e.g. width) after bds-table has mounted does not trigger a bds-table re-render in newSpecPage tests
metadata:
  type: project
---

`bds-table` renders each `<th>`/`<td>` by reading properties directly off the live `HTMLBdsTableColumnElement` instances in `this.columns` at render time (e.g. `col.width`, `col.label`). It has no `@Watch` or MutationObserver hook on individual column *prop* changes — only on `childList`/`subtree` DOM mutations (add/remove elements). So setting `(col as unknown as { width: string }).width = '100px'` on an already-mounted column, then `await page.waitForChanges()`, does **not** cause `bds-table` to re-render, because nothing marks `bds-table`'s own Stencil instance dirty.

**How to apply:** when a spec needs a column-level prop (like `width`) reflected in `bds-table`'s rendered output, set it in the initial `html` string passed to `newSpecPage` (e.g. `<bds-table-column ... width="100px">`) so it's picked up during the column's own initial prop-from-attribute hydration, before `bds-table` ever renders. Do not try to mutate it post-mount and expect a re-render — confirmed while testing `bds-table-column-group`'s "group th never gets a width" guard (`bds-table.grouping.spec.ts`); the post-mount-mutation version failed with an empty string instead of the expected `100px` on the leaf `<th>`, even though `page.waitForChanges()` was awaited.

No existing sibling spec file (`bds-table.basics.spec.ts`, `.sort.spec.ts`, etc.) tests `width` rendering at all prior to this — there was no established pattern to copy, hence this note.
