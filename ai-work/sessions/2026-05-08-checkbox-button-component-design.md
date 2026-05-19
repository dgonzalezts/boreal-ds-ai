# Session Summary — Checkbox Button Component Design

**Date:** 2026-05-08
**Agents:** GitHub Copilot
**Goal:** Determine whether `bds-radio-button` can be reused for checkbox semantics, define the new `bds-checkbox-button` component scope, and establish a shared SCSS strategy between the two leaf components.

---

## Key Findings

- `bds-radio-button` and a button-shaped checkbox share identical visual styling but have fundamentally different semantics: ARIA role (`radio` vs `checkbox`), selection model (mutually exclusive vs independent toggles), HTML input type (`radio` vs `checkbox`), and keyboard behavior (roving tabindex vs individual Tab focus).
- The same component cannot be reused for both — the ARIA role and keyboard navigation contract are incompatible.
- `bds-radio-group` already supports a `type` prop (`radio` | `radiobutton`) to switch between leaf variants. The checkbox side needs its own parallel: a `bds-checkbox-button` leaf and a `bds-checkbox-group` wrapper.
- `injectGlobalPaths` in `stencil.config.ts` prepends injected SCSS as raw text, making `$boreal-*` tokens and interaction mixins available in every component file without explicit imports. However, this scope does **not** propagate into partials loaded via `@use` — a `@use`-imported partial cannot see injected globals.
- `@import` (still valid in dart-sass, though deprecated) inherits the parent file's variable scope, including injected globals. A shared partial loaded with `@import` can use `$boreal-*` tokens without re-importing the token package.

---

## Decisions Made

### `bds-checkbox-button` is a distinct component

Not a variant or alias of `bds-radio-button`. Required changes relative to the radio counterpart:

| Concern                 | `bds-radio-button`    | `bds-checkbox-button`                  |
| ----------------------- | --------------------- | -------------------------------------- |
| Core action             | `select()` — one-way  | `toggle()` — two-way                   |
| Checked guard           | `if (checked) return` | Removed                                |
| `role`                  | `radio`               | `checkbox`                             |
| `input type`            | `radio`               | `checkbox`                             |
| `tabindex`              | Always `-1` (roving)  | `0` when enabled, `-1` when disabled   |
| Event `checked` payload | Always `true`         | `true` or `false`                      |
| Group responsibility    | Uncheck siblings      | Enforce `maxSelection`, disable extras |

A `@Watch('disabled')` is needed on the leaf to keep `tabindex` in sync when the parent group sets `disabled` directly.

### `bds-checkbox-group` wraps multi-selection

`maxSelection` lives on the group, not the leaf. The group listens to `bdsChange` from all children and disables all unchecked children when the selection count reaches the limit. When a checked item is toggled off, it re-enables them. The leaf component needs no awareness of `maxSelection`.

### Shared SCSS via `@import` of a `_shared` partial (Option C)

The shared styles live in a partial outside both component folders:

```
src/components/forms/
  _shared/
    _selectable-button.scss
  bds-radio-button/
  bds-checkbox-button/
```

The partial exposes a parameterized mixin. Each component SCSS file calls it with its own BEM prefix:

```scss
// _selectable-button.scss — no @use, inherits injected scope
@mixin selectable-button($prefix) {
  .#{$prefix} {
    // all shared rules using $boreal-* tokens and interaction mixins
  }
}

// bds-radio-button.scss
@import "../_shared/selectable-button";
@include selectable-button("bds-radio-button");

// bds-checkbox-button.scss
@import "../_shared/selectable-button";
@include selectable-button("bds-checkbox-button");
```

`@use` was considered but rejected: dart-sass module isolation means injected globals (tokens, mixins) are not visible inside a `@use`-loaded partial, causing build failures. `@import` avoids this entirely and matches the variable scoping model that `injectGlobalPaths` relies on.

Adding the partial to `injectGlobalPaths` was also considered and rejected — that slot is reserved for infrastructure (tokens, interaction primitives), not component-level shared styles.

---

## Open Questions

- Whether `bds-checkbox-group` should also be typed (i.e., support a `type` prop for a plain `bds-checkbox` layout variant, analogous to how `bds-radio-group` handles both `radio` and `radiobutton`). Not resolved in this session.
- Migration from `@import` to `@use` in the shared partial once the project decides to deprecate `@import` globally.

---

## Action Items

- [ ] Create `src/components/forms/_shared/_selectable-button.scss` with the parameterized mixin
- [ ] Scaffold `bds-checkbox-button` component with updated logic (toggle, role, tabindex, Watch)
- [ ] Scaffold `bds-checkbox-group` with `maxSelection` enforcement
- [ ] Update `bds-radio-button.scss` to use `@import` + `@include selectable-button('bds-radio-button')`

---

## Files to Create / Change

| File                                                                | Change                                                                     |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `src/components/forms/_shared/_selectable-button.scss`              | New file — shared mixin parameterized by BEM prefix                        |
| `src/components/forms/bds-radio-button/bds-radio-button.scss`       | Replace inline styles with `@import` + `@include`                          |
| `src/components/forms/bds-checkbox-button/bds-checkbox-button.tsx`  | New component — toggle semantics, `role=checkbox`, individual tabindex     |
| `src/components/forms/bds-checkbox-button/bds-checkbox-button.scss` | New file — `@import` + `@include selectable-button('bds-checkbox-button')` |
| `src/components/forms/bds-checkbox-button/types/ICheckboxButton.ts` | New interface + change detail type                                         |
| `src/components/forms/bds-checkbox-group/bds-checkbox-group.tsx`    | New group component — multi-selection, `maxSelection`, form-associated     |
