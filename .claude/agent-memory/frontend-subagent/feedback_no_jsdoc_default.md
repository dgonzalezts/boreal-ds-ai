---
name: feedback_no_jsdoc_default
description: Do not include @default tags in JSDoc on @Prop declarations — they are redundant when a default value is visible in the TypeScript initializer
metadata:
  type: feedback
---

Do not add `@default` tags to JSDoc blocks on `@Prop` declarations.

**Why:** The default value is already expressed by the TypeScript initializer (e.g. `readonly label: string = ''`). A `@default ''` tag duplicates that fact and creates a maintenance hazard — the two can drift out of sync. These tags were removed from `bds-table-column` during Task 3 cleanup.

**How to apply:** Write JSDoc only to describe what the prop does. Let the TypeScript initializer be the authoritative source for the default value.
