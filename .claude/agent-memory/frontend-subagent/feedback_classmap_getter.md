---
name: feedback_classmap_getter
description: Use a private classMap getter returning StyleModifiers for conditional class bindings — never build class strings with ternaries or string concatenation inline
metadata:
  type: feedback
---

Use a `private get classMap(): StyleModifiers` getter for any element that needs conditional classes, and bind it with `class={this.classMap}`. Import `StyleModifiers` from `@/types`.

```tsx
import type { StyleModifiers } from '@/types';

private get classMap(): StyleModifiers {
  return {
    [`${PREFIX}__wrapper`]: true,
    [`${PREFIX}__wrapper--empty`]: this.data.length === 0,
  };
}

// In render():
<div class={this.classMap}>
```

**Why:** Inline ternaries (`class={isEmpty ? 'a b' : 'a'}`) are hard to read and break down with more than two conditions. The `StyleModifiers` object pattern is the established Boreal DS convention — used in `bds-banner`, `bds-typography`, `bds-tag`, and others. Stencil's JSX handles object class maps natively.

**How to apply:** Whenever an element needs more than one static class or any conditional class, extract a `classMap` getter. Keep one getter per element that needs it (e.g. `wrapperClassMap`, `rowClassMap`). Never build class name strings with template literals or ternaries inline in JSX.

[[feedback_prefix_constant]]
