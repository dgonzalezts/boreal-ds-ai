---
name: stencil-table-rowclickselects-pattern
description: bds-table rowClickSelects implementation pattern — module-level excluded-selector const, tr onClick wiring, reuse of existing handleRowSelect guard
metadata:
  type: project
---

`rowClickSelects` (EOA-16000 Task 12) was implemented as a thin `onClick` on the row `<tr>` in `renderRowTr`, delegating to the same `handleRowSelect` used by the checkbox — no duplicate `rowSelectable` guard needed since `handleRowSelect` already early-returns via `if (this.rowSelectable !== undefined && !this.rowSelectable(rowData)) return;` (confirmed shipped in Task 9, before this task started).

The exclusion selector (`button, a[href], [role="button"], input, select, textarea, .bds-table__resize-handle, [draggable="true"], .bds-table__td-checkbox, .bds-table__td-expand`) is defined once as a module-level `const ROW_CLICK_EXCLUDED_SELECTOR` built with a template literal referencing `PREFIX`, matching the file's existing pattern of inlining `.${PREFIX}__xxx` selectors directly in `closest()` calls (see `handleColumnArrowKey`, `handleCheckboxShiftCapture`). Promoting it to a named const (rather than inlining at the call site like those precedents) is justified because the selector is long and the excluded-elements list is itself part of the acceptance criteria — worth naming for readability/greppability.

**Prop/interface ordering note:** `bds-table.tsx`'s `@Prop()` block and `ITable.ts`'s interface are NOT strictly alphabetical — recent props (e.g. `rowSelectable` from Task 9) are appended at the end of their respective blocks rather than inserted at their alphabetical slot, to keep diffs minimal. `rowClickSelects` followed that same append-at-end convention, placed directly after `rowSelectable` in both files. Don't "fix" the ordering of unrelated existing props when adding a new one.

The private `handleRowClick` method, however, was inserted in roughly alphabetical position among the `private handle*` methods (immediately before `handleRowSelect`), which is the prevailing (though not 100% strict) convention for that section — mixing conventions between the props list (append-at-end) and the private-method list (alphabetical-ish) is intentional and matches observed file history, not an inconsistency to resolve.
