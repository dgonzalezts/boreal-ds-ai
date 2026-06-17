---
name: feedback_scss_bem_nesting
description: Always nest BEM elements and modifiers inside the block selector using Sass & — never write flat .bds-component__element selectors
metadata:
  type: feedback
---

Always write component SCSS using Sass `&` nesting inside the block selector. Never write flat `bds-table__element` selectors at the top level.

```scss
// Correct — nested BEM
bds-table {
  display: flex;

  &__wrapper {
    overflow-x: auto;
  }

  &__empty-state {
    text-align: center;
    padding: $boreal-spacing-2xl;
    background-color: $boreal-ui-default-lighter;
  }

  &__empty-text {
    font-size: $boreal-typography-font-size-xs;
    color: $boreal-text-default-light;
  }
}

// Wrong — flat selectors scattered across the file
// bds-table { display: flex; }
// .bds-table__wrapper { overflow-x: auto; }
// .bds-table__empty-state { ... }
```

**Why:** Nesting keeps all styles for a component in one block, making it immediately clear which element owns which rules. Flat selectors scatter definitions across the file and make it hard to audit the component's full visual surface. All existing Boreal DS components use nested BEM.

**How to apply:** The block selector is the tag name (`bds-table { }`) for light DOM components, or `:host { }` for shadow DOM (none exist in this project). All `__element` and `--modifier` rules go inside as `&__element` and `&--modifier`. Never write `.bds-component__element` at the top level.

[[feedback_prefix_constant]]
[[feedback_classmap_getter]]
