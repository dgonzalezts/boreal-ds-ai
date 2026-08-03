---
name: bds-table-th-leading-icon-layout
description: How to add a leading (left-of-label) icon/handle inside bds-table's <th>, since <th> itself is not a flex container
metadata:
  type: project
---

`bds-table.tsx`'s `renderTh` (`packages/boreal-web-components/src/components/data-visualization/bds-table/bds-table/bds-table.tsx`) renders a bare `<th>` whose only flex child is `<span class="bds-table__th-content">` (label + trailing actions, `justify-content: space-between`). The `<th>` element itself has no `display: flex` — it relies on default table-cell block layout, which works fine when `.th-content` is the sole child.

The six-dot column-reorder handle was relocated from inside `th-actions` (right side, grouped with sort/pin) to a leading sibling of `.th-content` (before the label), matching the `bds-card-header` precedent (`bds-card-header.tsx`, which places its six-dot icon in a leading `<bds-toolbar-start>`).

Because `<th>` now has two direct children instead of one, `bds-table.scss` needed a new rule to lay them out side by side:

```scss
th:has(> .bds-table__reorder-icon) {
  display: flex;
  align-items: center;
  gap: $boreal-spatial-gap-3xs;

  .bds-table__th-content {
    min-width: 0;
    flex: 1;
  }
}
```

Scoping the `display: flex` to `:has(> .bds-table__reorder-icon)` (rather than a blanket `th { display: flex }`) matters — a global rule would break the loading-skeleton `<th>`, group-header `<th>`, checkbox `<th>`, and expand-toggle `<th>`, none of which go through this code path. `:has()` is already used elsewhere in this file (`.bds-table__wrapper:has(...)`, `tbody:has(+ tfoot)`), so it's an accepted pattern here.

Any future leading icon/handle added to the regular column `<th>` should follow the same scoped `:has()` approach rather than modifying the bare `th { ... }` rule.
