---
name: stencil-bem-double-element-nesting-bug
description: Writing &__child-element inside an existing &__element{} block compounds into __element__child-element, not the intended sibling-level __child-element class
metadata:
  type: feedback
---

In a `.#{$prefix} { &__day { ... } }` structure, `&` inside the `&__day { }` block resolves to the *compiled* `.bds-calendar-grid__day` selector — so writing `&__day-bkgd` there produces `.bds-calendar-grid__day__day-bkgd`, not the intended sibling-level `.bds-calendar-grid__day-bkgd`.

**Why:** caught building `bds-calendar-grid`'s Task 19i two-layer (`Bkgd`/`Selected`) cell geometry — a new BEM element (`__day-bkgd`) nested for DOM/CSS locality inside its logical parent element's (`__day`) rule block, using the same `&__x` shorthand that's correct one level up (directly inside `.#{$prefix} { }`).

**How to apply:** when a new BEM element genuinely needs to live inside another element's rule block (for descendant-selector locality, e.g. modifier-scoped rules like `&--in-range .foo { }`), reference it with the **literal** class selector (`.#{$prefix}__day-bkgd`), never `&__day-bkgd`. Reserve bare `&__x` shorthand for blocks nested directly under the root `.#{$prefix} { }` selector only — one level of `&` = one BEM element, not stacked. `pnpm --filter @telesign/boreal-web-components build` (Stencil transpile) does NOT catch this — it's a Sass compile-clean, semantically-wrong selector, only visible by inspecting compiled CSS or live rendering.
