# CSS Architecture & Consumer Setup Research

> Status: Research complete. Implementation deferred.
> Covers: `boreal-styleguidelines`, `boreal-web-components`, `boreal-react`, and the `react-testapp` example.

---

## Current State (as of this research session)

### What each CSS output file contains

| File | Contents | Source |
|---|---|---|
| `dist/css/boreal.css` | `:root {}` primitive tokens + `[data-theme="*"] {}` semantic tokens + compiled `_fonts.scss` + `reset.scss` + `_typography.scss` | `boreal-styleguidelines` generator |
| `build/boreal-web-components.css` | Icon font CDN `@import` only | `boreal-web-components/src/styles/main.scss` via Stencil `globalStyle` |

### Consumer setup (current)

```html
<!-- Tokens + fonts + reset + typography utilities -->
<link rel="stylesheet" href="/css/boreal.css" />

<!-- Icon font (via boreal-web-components.css) -->
<link rel="stylesheet" href="/build/boreal-web-components.css" />

<!-- Web components JS -->
<script type="module" src="/build/boreal-web-components.esm.js"></script>

<!-- Apply a theme -->
<body data-theme="telesign">
```

---

## Decisions Made This Session

### 1. `_typography.scss` rewritten to use CSS variables

**Before:** Used SCSS variables (`$boreal-text-default-darker`) via `@use "../../../dist/stencil/index"`.

**After:** Uses CSS custom properties directly (`var(--boreal-text-default-darker)`). No `@use` needed, no build-order dependency.

**Why:** The SCSS variables were wrappers around CSS vars anyway — zero runtime difference. The `@use` created a circular build dependency (styleguidelines output consumed by styleguidelines source).

### 2. `boreal-web-components/src/styles/_theme.scss` deleted

Confirmed orphaned — nothing imported it. `injectGlobalPaths` in `stencil.config.ts` already injects `dist/stencil/index` globally into every component. The local `_theme.scss` was a migration artifact.

### 3. `GlobalGenerator` compiles files from `src/styles/global/` automatically

The generator auto-discovers all `.scss` files in `src/styles/global/`, compiles them, and prepends the result before `:root {}` in both `global.css` and `boreal.css`. Files currently in that directory: `_fonts.scss`, `reset.scss`, `_typography.scss`.

### 4. Font `@import` must come before `:root {}`

CSS `@import` rules must precede all other rules. `css-generator.ts` was updated to prepend `additionalStyles` before the `:root {}` block instead of appending after.

---

## Architectural Analysis: Where Global Styles Should Live

### Current architecture (hybrid)

`_fonts.scss`, `reset.scss`, and `_typography.scss` live in `boreal-styleguidelines` but are only accessible to consumers because `stencil.config.ts` copies `dist/css/` into the web-components dist via the `copy` step. Final users never install `boreal-styleguidelines` directly.

### Aqua DS reference pattern

In `aqua-ds`, the equivalent files live in `aqua-web-components/src/globals/`:
- `icons.scss` — icon font CDN import
- `reset.scss` — base HTML/body styles
- `utility-classes.scss` — forwards from style-guidelines
- `variables.scss` — forwards CSS token files

`aqua-style-guidelines` owns only token generation (SCSS variables and CSS custom properties). All rendering concerns live in the component package.

### Ideal Boreal architecture (future target)

| Package | Owns |
|---|---|
| `boreal-styleguidelines` | Token generation only: `:root {}` CSS vars, SCSS variable files, SCSS maps |
| `boreal-web-components` | Everything rendering-related: fonts, reset, typography utilities, icon font |

This means moving `_fonts.scss`, `reset.scss`, and `_typography.scss` from `styleguidelines/src/styles/global/` to `web-components/src/styles/`, forwarded from `main.scss`.

**Why deferred:** Works correctly today. Migration adds no immediate consumer-facing value and requires updating the generator pipeline.

---

## Single Entry Point: The Target Architecture

The goal is one import for consumers, covering everything.

### How it works

`boreal-web-components.css` becomes the single entry point by inlining `boreal.css` via Sass `@use`:

```scss
/* main.scss */
@use '@telesign/boreal-style-guidelines/dist/css/boreal.css'; /* inlines tokens */
@import url('https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css');
@forward './fonts';
@forward './reset';
@forward './typography';
```

### Why `@use` works here (not `@import`)

Tested against `sass-embedded@1.97.3` (used by `@stencil/sass@3.2.3`):

| Syntax | Result |
|---|---|
| `@use 'file.css'` | **Inlines** content — correct behavior |
| `@import 'file'` (no extension) | **Inlines** content |
| `@import 'file.css'` (with extension) | Emits CSS `@import` statement — does NOT inline |
| `@import url('...')` | Emits CSS `@import` — does NOT inline |

The `.css` extension in `@import` is Sass's signal to pass through as plain CSS. `@use` always inlines regardless of extension in modern Dart Sass.

### Consumer setup after migration

```html
<!-- Everything: tokens, fonts, reset, typography, icons -->
<link rel="stylesheet" href="/build/boreal-web-components.css" />
<script type="module" src="/build/boreal-web-components.esm.js"></script>
<body data-theme="telesign">
```

```ts
// React/Vue
import '@telesign/boreal-react/css/boreal-web-components.css';
```

Advanced consumers who want tokens only can still import `boreal.css` directly via the package `exports` field.

---

## Icon Font: `boreal-web-components.css` vs Direct S3 URL

**Recommendation: always use `boreal-web-components.css`.**

The S3 URL is an implementation detail. If the CDN path changes (migration, versioning, self-hosting), consumers referencing the URL directly must update their code manually. With `boreal-web-components.css` as the entry point, only `main.scss` needs updating — all consumers pick it up on next install.

---

## `boreal-web-components.css` Naming

The current filename is technically accurate but not descriptive to consumers. Stencil derives it from the namespace and cannot be configured. A post-build rename step would be needed to change it. Not worth the effort at this stage — address through documentation instead.

---

## Shadow DOM Status

Components use **neither** `shadow: true` nor `scoped: true`. Stencil's default mode — no Shadow DOM. Component styles are injected as plain `<style>` tags into the light DOM `<head>`. This means:

- CSS from `boreal.css` cascades normally into component internals
- `reset.scss` applies to component elements without redeclaration
- `box-sizing` and `font-family` declarations in individual component SCSS files (`bds-typography.scss`, `bds-banner.scss`) are redundant and can be removed in a future cleanup

---

## Files Changed This Session

| File | Change |
|---|---|
| `boreal-styleguidelines/src/generators/css-generator.ts` | Prepend `additionalStyles` before `:root {}` (was appended after) |
| `boreal-styleguidelines/src/styles/global/_typography.scss` | Rewritten to use `var(--boreal-*)` instead of `$boreal-*` SCSS vars, `@use` removed |
| `boreal-web-components/src/styles/_theme.scss` | Deleted (orphaned duplicate of `dist/stencil/_theme.scss`) |
| `boreal-web-components/src/styles/main.scss` | Icon `@import` restored/uncommented |

---

## Open Tasks (Future)

- [ ] Migrate `_fonts.scss`, `reset.scss`, `_typography.scss` from `styleguidelines` to `web-components/src/styles/` globals
- [ ] Implement single entry point: `@use boreal.css` from `main.scss`
- [ ] Remove redundant `box-sizing`/`font-family` declarations from `bds-typography.scss` and `bds-banner.scss`
- [ ] Update `react-testapp` to import `boreal-web-components.css` and set `data-theme`
- [ ] Expose `boreal-web-components.css` via `exports` in `boreal-react` package
