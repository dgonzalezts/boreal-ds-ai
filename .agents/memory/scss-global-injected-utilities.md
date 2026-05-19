# SCSS — Globally Injected Utilities

## Fact

`_commons.scss` and `_interactions.scss` (both under `packages/boreal-web-components/src/styles/`) are injected into **every** component stylesheet via `injectGlobalPaths` in `stencil.config.ts`:

```ts
injectGlobalPaths: [
  resolve(styleGuidelinesDir, 'stencil/_index.scss'),
  resolve(__dirname, 'src/styles/_commons.scss'),
  resolve(__dirname, 'src/styles/_interactions.scss'),
].map(p => p.replace(/\\/g, '/')),
```

**No `@use` or `@import` is needed in any component `.scss` file.** All symbols are already in scope.

---

## What each file provides

### `_commons.scss`

| Symbol         | Type        | Use for                              |
| -------------- | ----------- | ------------------------------------ |
| `%flex-center` | placeholder | `display: flex; align-items: center` |

```scss
// ✅ Correct
.bds-radio__content {
  @extend %flex-center;
  gap: $boreal-spacing-3xs;
}

// ❌ Avoid — redundant raw declarations
.bds-radio__content {
  display: flex;
  align-items: center;
  gap: $boreal-spacing-3xs;
}
```

### `_interactions.scss`

| Symbol                                            | Type     | Use for                                                         |
| ------------------------------------------------- | -------- | --------------------------------------------------------------- |
| `bds-focus-ring($outer, $inner)`                  | mixin    | Keyboard focus ring (`box-shadow`)                              |
| `bds-focus-ring-value($outer, $inner)`            | function | Focus ring value when composing with other shadows              |
| `bds-hover-shadow($color)`                        | mixin    | Elevation shadow on hover                                       |
| `bds-shadow-inset($color)`                        | function | Inset shadow value for active/pressed states                    |
| `bds-active-shadow-inset($outer, $inner, $inset)` | mixin    | Combined focus ring + inset shadow for active/pressed           |
| `bds-transition-surface`                          | mixin    | Transition for `background-color`, `border-color`, `box-shadow` |
| `bds-transition-visibility`                       | mixin    | Transition for `opacity`                                        |
| `bds-transition-action`                           | mixin    | Transition for `color` and `opacity`                            |
| `bds-icon($size, $font-size)`                     | mixin    | Consistent sizing for `<em>` icon elements                      |

```scss
// ✅ Correct — use shared mixins
.bds-radio__button {
  @include bds-transition-surface;
}

bds-radio:focus-visible .bds-radio__button {
  @include bds-focus-ring($boreal-stroke-focus, $boreal-ui-inverse);
}

bds-radio:hover:not(.--disabled) .bds-radio__button {
  @include bds-hover-shadow(rgba(19, 19, 22, 0.15));
}

// ❌ Avoid — raw declarations that duplicate shared logic
.bds-radio__button {
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease,
    box-shadow 0.3s ease;
  box-shadow:
    0 0 0 1px white,
    0 0 0 3px blue;
}
```

---

## Common mistake to avoid

Adding `@use "../../styles/interactions"` or similar at the top of a component SCSS file. This causes a Sass "already loaded" error because the file is already injected globally. The symbols are in scope unconditionally — just use them.
