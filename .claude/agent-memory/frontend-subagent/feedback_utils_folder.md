---
name: feedback_utils_folder
description: Place component-local utility functions in a dedicated utils/ subfolder, not inline in the component file
metadata:
  type: feedback
---

Component-local utility functions (comparators, formatters, value readers) must live in a dedicated `utils/` subfolder alongside the component, not inline in the `.tsx` file.

**Why:** Inlining utilities in the component file inflates the component's size, mixes rendering concerns with data logic, and makes the utilities harder to test in isolation. The `bds-table` component places `readCellValue` and `toCellString` in `utils/bds-table-utils.ts`.

**How to apply:** Create `<component-dir>/utils/<component-name>-utils.ts` for all non-trivial helpers. Import from there into the component file. If a utility is general enough to be reused across components, move it to `@/utils/` instead.
