# Sass design tokens resolve to CSS custom properties, not compile-time literals

`$boreal-*` Sass variables referenced inside a Stencil component's SCSS do **not** hold literal
values at Sass compile time. `stencil.config.ts`'s `sass({ injectGlobalPaths: [...] })` injects
`packages/boreal-styleguidelines/dist/stencil/_index.scss` — the variant that wraps every token as
`var(--boreal-*)` (for runtime theming) — not the literal-value variant
(`dist/scss/variables/_primitives.scss`).

Consequence: Sass arithmetic (`math.div()`, `+`, `-`, `*`) applied to these tokens does not throw a
compile error. Dart Sass treats an opaque `var(...)` string as a non-numeric value and falls back to
naive string concatenation — e.g. `$a + $b` where both are `var(--boreal-x)` strings produces
`var(--boreal-x)var(--boreal-y)` (no operator, no space), which is invalid CSS that browsers
silently discard. Any declaration depending on that expression resolves to nothing (effectively
`0` for spacing/sizing properties).

**Fix**: express all token arithmetic with CSS's native `calc()` instead of Sass math:

```scss
// Wrong — silently invalid at runtime, no build-time error
$icon-only-padding: ($height - $border - $icon-size) / 2;

// Right
$icon-only-padding: calc((#{$height} - #{$border-total} - #{$icon-size}) / 2);
```

If a value itself is a **sum of two tokens** (e.g. composing a missing token from two existing
ones), that sum must be wrapped in its own explicit `calc()` before being interpolated into a
larger `calc()` expression — nested `calc()` is valid CSS:

```scss
// Wrong — the "+" here is Sass string concatenation, not addition, and breaks the OUTER calc() too
$height: $boreal-spatial-layout-l + $boreal-spatial-layout-s;

// Right — valid nested calc()
$height: calc(#{$boreal-spatial-layout-l} + #{$boreal-spatial-layout-s});
```

Found while parameterizing `bds-button-size`'s mixin (`bds-button.scss`) to make icon-only buttons
an exact square per size (24/32/44px). The `lg` size has no single token matching 44px (the
`spatial-layout` scale jumps `32px` (`layout-l`) → `48px` (`layout-xl`)), so it's composed as
`layout-l + layout-s` (32+12) — the naive `+` version silently zeroed out the icon-only padding
calculation for `lg` only (the other two sizes use an exact single-token match and were unaffected),
producing a visibly non-square button that was easy to miss without an explicit pixel measurement.

**Takeaway**: never trust Sass arithmetic on any `$boreal-*` token in component SCSS — always use
`calc()`, and always wrap composed/summed tokens in their own nested `calc()` before combining them
further.
