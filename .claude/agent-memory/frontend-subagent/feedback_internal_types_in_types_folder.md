---
name: feedback_internal_types_in_types_folder
description: Even private, non-exported helper types (e.g. a virtualizer flat-row-entry union) belong in the component's types/I*.ts file, not declared inline in the .tsx
metadata:
  type: feedback
---

All new TypeScript types for a component — including types that are purely internal implementation detail and never exported from the component's own public API (e.g. a `FlatRowEntry` discriminated union used only to flatten rows for a virtualizer) — must be declared in the existing `types/IComponent.ts` file for that component, not inline near the top of the `.tsx` file.

**Why:** Coordinator correction during `bds-table` EOA-16000 Task 2 (row expand/collapse). I had declared a private `type FlatRowEntry = {...} | {...}` directly in `bds-table.tsx` next to `PREFIX`/`VIRTUAL_ESTIMATED_ROW_HEIGHT` constants, reasoning that since it wasn't exported or part of the public API it didn't need to live with the `BdsExpandEventDetail` event-detail interface already added to `types/ITable.ts`. That reasoning was wrong for this codebase — the convention is centralizing *all* type declarations (public event details, internal row/virtualizer shapes, whatever) in the dedicated `types/` file, keeping the `.tsx` file focused on logic/render only.

**How to apply:** Before adding any `type`/`interface` declaration in a component's `.tsx` file, check whether `types/I{Component}.ts` already exists (it almost always does for anything non-trivial) and add the new type there instead, exporting it and importing it back into the `.tsx`. Only declare a type inline in the `.tsx` if there is no `types/` file for that component at all and creating one would be clear overkill (rare — prefer creating the file). This applies even to discriminated unions/shapes that will never appear in `custom-elements.json` or any consumer-facing surface.
