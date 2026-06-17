---
name: feedback_prefix_constant
description: Declare const PREFIX = 'bds-component' as const at the top of every component file and use it in all class name template literals
metadata:
  type: feedback
---

Declare a top-level `PREFIX` constant at the top of every Stencil component file and use it for all class name strings:

```tsx
const PREFIX = 'bds-table' as const;

// In render helpers:
<td class={`${PREFIX}__empty-state`} />
<span class={`${PREFIX}__empty-text`} />
```

**Why:** Prevents typos in BEM class names, makes component-wide renames a one-line change, and makes the BEM block name the single source of truth in the file. Without it, class strings are scattered and can diverge silently.

**How to apply:** Add `const PREFIX = 'bds-<tag-name>' as const;` immediately after imports in every new component file, before the `@Component` decorator. Use template literals everywhere a class name references the block — never hardcode `'bds-table__something'` as a plain string.
