---
name: component-types-dir-barrel-convention
description: Component types/ directories in practice use index.ts barrels (export * from ...) despite development-standards.md §3.3 "No Barrel Files" saying not to.
metadata:
  type: project
---

`ai-docs/guidelines/development-standards.md` §3.3 explicitly says not to create `index.ts` barrel files inside a component's `types/` directory ("hurt tree-shaking... import directly from source files"). Actual practice across the codebase contradicts this: a majority of components with more than one file in `types/` (e.g. `bds-toggle`, `bds-text-field`, `bds-tag-field`, `bds-number-field`, `bds-avatar`, `bds-pagination`, `bds-popover`, `bds-dialog`, `bds-tag`, `bds-toast`, `bds-checkbox-group`, `bds-step-item`, `bds-stepper`, `bds-grid`, `bds-grid-item`, `bds-toolbar`, `bds-toolbar-item`, `bds-flag`, `bds-slider`, `bds-search-bar`) ship an `index.ts` barrel re-exporting the interface/types/enum files. Single-file `types/` dirs (just one `IComponent.ts`) obviously have no barrel need.

**Why:** confirmed while implementing `bds-calendar-grid`'s types (Task 7, `bds-date-picker` plan, EOA-16692) — the task brief itself flagged this as "already resolved for `date-engine`'s own barrel" (see `services/date-engine/index.ts`, which also barrels despite the same written rule).

**How to apply:** when a component's `types/` directory has more than one file, add an `index.ts` barrel (`export * from './IComponent'`, `export * from './types'`, `export * from './enum'` if present) following the `bds-toggle` shape, even though the written guideline says not to. Do not treat the guideline doc as current ground truth for this specific rule — treat actual repo practice as authoritative here.
