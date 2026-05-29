---
name: stencil-sass-injectGlobalPaths constraint
description: Three-way rule on SCSS in Stencil: injected files self-contained; component SCSS no @use of token pkg; SCSS partials (@use'd by components) MUST @use the token package themselves.
---

## Background

`@stencil/sass`'s `injectGlobalPaths` in `stencil.config.ts` prepends three files at the top of **every** component SCSS at build time:

1. `@telesign/boreal-style-guidelines/dist/stencil/_index.scss` — all `$boreal-*` tokens
2. `src/styles/_commons.scss`
3. `src/styles/_interactions.scss`

---

## Constraint 1 — Injected files must be self-contained

Stencil compiles each injected file standalone during builds and watch cycles. Any `$boreal-*` reference inside an injected partial will fail with "Undefined variable" if the token file is not also loaded by that partial.

**Approved pattern:** Add `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *;` at the top of an injected partial that needs tokens. Sass `@use` is idempotent — no double-definition errors.

---

## Constraint 2 — Component SCSS files must NOT @use the token package

`$boreal-*` tokens are already injected globally; adding a `@use` of the token package in a component SCSS file causes a **Sass double-import / variable redefinition error**.

All component SCSS files start directly with selectors — no `@use` at the top:

```scss
// bds-text-field.scss — CORRECT (no @use, tokens from injectGlobalPaths)
%field-inline-label {
  font-size: $boreal-typography-font-size-xs;
}
```

---

## Constraint 3 — SCSS partials (@use'd by components) MUST @use the token package

Sass's module system gives each file its **own isolated scope**. `injectGlobalPaths` prepends token definitions into the component SCSS file only — it does **not** flow into any partials accessed via `@use`. Partials must declare their own imports.

**Evidence:** `_selectable-button.scss` and `_selectable-group.scss` in `src/components/forms/_shared/` both declare:

```scss
@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *;
@use '../../../styles/_interactions' as *;  // only when mixins are needed
```

The component file (`bds-radio-button.scss`) that uses the partial does NOT repeat the import:

```scss
// bds-radio-button.scss — no @use of token package
@use '../../_shared/selectable-button' as *;
@include selectable-button('bds-radio-button');
```

**Rule:** Any shared SCSS partial that references `$boreal-*` variables or interaction mixins must `@use` them at the top of the partial. No leading comment block — start directly with `@use` statements. The path from `src/components/forms/_shared/` to the styles directory is `'../../../styles/_interactions'`.
