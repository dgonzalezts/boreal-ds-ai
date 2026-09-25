# Sass: `@media` inside a mixin splits the rule; reduced-motion overrides need `!important`

Discovered 2026-09-23 implementing Task 40a (`bds-calendar-grid` focus-ring transition flicker, EOA-17662). Two related, verified Sass/Stencil behaviours when adding a `prefers-reduced-motion` guard to state-specific transitions.

## 1. A nested `@media` inside a mixin splits the enclosing rule into duplicate-selector rules

Putting `@media { ... }` **inside** a mixin that is `@include`d mid-rule makes Sass emit the parent rule's declarations as **two rules with the identical selector**: the declarations *before* the `@media` stay in the first rule, the `@media` bubbles out, and the declarations *after* the include are emitted in a second, duplicate-selector rule (to preserve cascade order).

Real example: `bds-calendar-grid.scss`'s `.bds-calendar-grid__day:focus-visible` block declares `background-color`/`z-index`, then `@include transition-mixin` (which had an embedded `@media`), then `@include focus-ring-mixin` (`outline-width`/`box-shadow`). Compiled output split into two `.bds-calendar-grid__day:focus-visible { ... }` rules — harmless functionally, but noisy and confusing in a compiled-CSS audit.

**Avoid it:** keep transition mixins free of nested `@media`; add the reduced-motion guard as a separate block (see below).

## 2. A top-level `@media (prefers-reduced-motion: reduce)` override needs `!important` for state-specific transitions

The codebase convention (`bds-drawer.scss:76`, `bds-table.scss:514`, `bds-search-bar.scss:121`) is a top-level `@media (prefers-reduced-motion: reduce) { <tag> { ... transition: none } }`. That works when the transition lives on the plain base rule (equal specificity, media block later wins).

It does **not** work when the transition is declared on higher-specificity state rules (`:hover`, `:focus-visible`, `:active`, `:not(...)` compounds): the scoped media selector loses on specificity, so the state transition still animates under reduced motion.

**Fix used:** scope the guard under the root tag block (so it is not an unscoped top-level selector — see `stencil-light-dom-unscoped-selector-leak.md`) and use `transition: none !important`. `!important` is already used in the codebase (`bds-button.scss:162`, `bds-table.scss:249`, etc.); no stylelint rule forbids it.

```scss
@media (prefers-reduced-motion: reduce) {
  bds-calendar-grid {
    .#bds-calendar-grid__day,
    .#bds-calendar-grid__day-cap {
      transition: none !important;
    }
  }
}
```

## Verification technique

Build the package (`pnpm --filter @telesign/boreal-web-components build`) and read the **unminified** compiled artifact at `dist/collection/components/<path>/<component>.css` — far easier to audit than the minified hashed `www/build/p-*.entry.js` chunk (which still works via `grep -o 'transition:[^;}]*'`). Grep for `outline-width` in transitions and count `transition:` values to confirm which rules still animate.

Related: `scss-placeholder-refactor-verification-technique.md` (compiled-output inspection over raw-SCSS diff).
