---
status: done
---

# Implementation Plan: Shared Storybook Components for Boreal DS

## Overview

Implement shared documentation components for the Boreal DS Storybook based on the Colibri reference implementation. This sprint delivers reusable components for both MDX documentation files (React) and story files (Lit), establishing a solid baseline for the alpha version.

## User Decisions (Confirmed)

- ✅ **Folder structure**: `docs/` and `story/` subdirectories under `src/components/`
- ✅ **React components**: Card, Container, DocsLinkTo (3 components)
- ✅ **Lit components**: CodeBlock, FormDemo, LayoutDemo, MainLogo (4 components)
- ✅ **Token prefix**: `--boreal-*` (aligned with styleguidelines branch)
- ✅ **Styling strategy**: Use hardcoded fallback values with CSS custom properties
- ✅ **CSS import**: Global import in `.storybook/preview.ts`
- ✅ **Visual testing**: Create dedicated test stories for each component
- ✅ **Callout migration**: Move to `docs/` folder (no backwards compatibility)

## Current State Analysis

### Existing Structure

```
apps/boreal-docs/src/
├── components/
│   └── Callout/              # React component (will be moved to docs/)
├── hooks/
│   └── useStorybookTheme.ts  # Theme detection hook (already exists)
├── stories/                   # Individual component stories
├── types/
│   └── stories.ts            # BorealStoryMeta types (already exists)
└── utils/
    ├── formatters.ts         # formatHtmlSource, toKebabCase (already exists)
    └── helpers.ts            # disableControls, wrapStoryContent (already exists)
```

### Design Token System

**Current State**:

- ✅ Token JSON definitions exist in `packages/boreal-styleguidelines/src/tokens/`
- ⚠️ CSS variable generation is **WIP** in `feature/styleguidelines-first-version` branch
- ⚠️ Existing Callout component uses `--col-*` (Colibri tokens) which **don't exist in Boreal**

**Target State** (from styleguidelines branch):

- **Prefix**: `--boreal-*` (defined in `CSS_VAR_PREFIX` constant)
- **Generation**: CSS files generated to `packages/boreal-styleguidelines/dist/css/`
  - `global.css` - Primitive tokens in `:root`
  - `theme-{name}.css` - Theme-specific tokens in `[data-theme="name"]`
- **Categories**: colors (ui, text, stroke, bg), typography, spacing, radius, depth
- **Themes**: proximus (default), masiv, telesign, bics
- **Theme switching**: Via `data-theme` attribute on body element

**Implementation Strategy**:

- Use CSS custom properties with **simple hardcoded fallback values**
- No complex extraction scripts - just reasonable approximations
- Pattern: `var(--boreal-token-name, fallback-value)`
- When tokens are generated, fallbacks will be automatically overridden
- **Refactor planned**: Remove fallbacks once token generation is stable

## Proposed Folder Structure

```
apps/boreal-docs/src/components/
├── docs/                     # React components for MDX files
│   ├── index.ts              # Barrel export
│   ├── Callout/              # ⚠️ MOVED from components/Callout/
│   │   ├── Callout.tsx
│   │   ├── Callout.module.css (updated with --boreal-* tokens)
│   │   └── index.ts
│   ├── Card/
│   │   ├── Card.tsx
│   │   ├── Card.module.css
│   │   └── index.ts
│   ├── Container/
│   │   ├── Container.tsx
│   │   ├── Container.module.css
│   │   └── index.ts
│   └── DocsLinkTo/
│       ├── DocsLinkTo.tsx
│       └── index.ts
└── story/                    # Lit components for story files
    ├── index.ts              # Barrel export
    ├── CodeBlock/
    │   ├── CodeBlock.ts
    │   ├── CodeBlock.styles.ts
    │   ├── highlight-js.styles.ts
    │   └── index.ts
    ├── FormDemo/
    │   ├── FormDemo.ts
    │   ├── FormDemo.styles.ts
    │   └── index.ts
    ├── LayoutDemo/
    │   ├── LayoutDemo.ts
    │   ├── LayoutDemo.styles.ts
    │   └── index.ts
    └── MainLogo/
        ├── MainLogo.ts
        ├── MainLogo.styles.ts
        └── index.ts
```

**Migration Note**: The existing `components/Callout/` will be **moved** to `components/docs/Callout/` for consistency.

### Test Stories Structure

**⚠️ TEMPORARY**: Test stories are for manual verification during development and will be **deleted after final verification**.

Each component will have a dedicated test story file for visual verification:

```
apps/boreal-docs/src/stories/shared-components/
├── Callout.stories.tsx       # Callout component visual tests (TEMP)
├── Card.stories.tsx          # Card component visual tests (TEMP)
├── Container.stories.tsx     # Container component visual tests (TEMP)
├── DocsLinkTo.stories.tsx    # DocsLinkTo component visual tests (TEMP)
├── CodeBlock.stories.tsx     # CodeBlock component visual tests (TEMP)
├── FormDemo.stories.tsx      # FormDemo component visual tests (TEMP)
├── LayoutDemo.stories.tsx    # LayoutDemo component visual tests (TEMP)
└── MainLogo.stories.tsx      # MainLogo component visual tests (TEMP)
```

**Lifecycle**: Create → Manual test → Verify all variants → Delete

## Component Summary

### React Components (for MDX)

1. **Callout** (migrated) - Info/warning/error callout boxes
2. **Card** - Content grouping with title/variants/sizes
3. **Container** - Documentation section wrapper
4. **DocsLinkTo** - Dynamic navigation between docs

### Lit Components (for Stories)

5. **CodeBlock** - Syntax-highlighted code display
6. **FormDemo** - Form demonstrations with live output
7. **LayoutDemo** - Layout component demonstrations
8. **MainLogo** - Brand logos with theme switching

## Implementation Phases

### Phase 1: Project Structure & Token Setup

1. Create directory structure (`docs/`, `story/`, `shared-components/`)
2. Create `tokens-fallback.css` with simple hardcoded approximations
3. Update `.storybook/preview.ts` to import fallback CSS

### Phase 2: Move & Update Callout

1. Move `components/Callout/` → `components/docs/Callout/`
2. Update `Callout.module.css` with `--boreal-*` tokens + fallbacks
3. Update import paths in `welcome.mdx`
4. Test Callout works correctly

### Phase 3: React Components (MDX)

Implement: Card → Container → DocsLinkTo

- Each component includes test story for verification
- Replace `--col-*` with `--boreal-*` + fallbacks

### Phase 4: Lit Components (Stories)

Implement: CodeBlock → FormDemo → LayoutDemo → MainLogo

- Each component includes test story for verification
- Replace `--col-*` with `--boreal-*` + fallbacks
- MainLogo requires brand SVG assets

### Phase 5: Documentation & Integration

1. Update barrel exports in `components/index.ts`
2. Update `Button.mdx` and `Icons.mdx` to use new components
3. Update CONTRIBUTING/PATTERNS documentation

### Phase 6: Manual Testing & Verification

1. Test all components with all themes
2. Cross-browser testing
3. Build verification
4. **DELETE all test stories after verification** ⚠️

### Phase 7: Token Refactor (Future)

When styleguidelines is complete:

1. Delete `tokens-fallback.css`
2. Import generated token CSS
3. Remove fallback values from component CSS

## Token Fallback CSS

**File**: `apps/boreal-docs/src/styles/tokens-fallback.css`

Simple hardcoded approximations (no complex scripts):

```css
:root {
  /* Colors - UI Backgrounds */
  --boreal-colors-ui-info-lighter: #e3f2fd;
  --boreal-colors-ui-success-lighter: #e8f5e9;
  --boreal-colors-ui-warning-lighter: #fff3e0;
  --boreal-colors-ui-danger-lighter: #ffebee;
  --boreal-colors-ui-default-dark: #f5f5f5;

  /* Colors - Strokes/Borders */
  --boreal-colors-stroke-info: #2196f3;
  --boreal-colors-stroke-success: #4caf50;
  --boreal-colors-stroke-warning: #ff9800;
  --boreal-colors-stroke-danger: #f44336;
  --boreal-colors-stroke-default: #e0e0e0;

  /* Colors - Text */
  --boreal-colors-text-primary: #1976d2;
  --boreal-colors-text-default: #424242;
  --boreal-colors-text-default-darker: #212121;

  /* Colors - Backgrounds */
  --boreal-colors-bg-default: #ffffff;

  /* Shadows */
  --boreal-depth-box-shadow-s: 0 2px 8px rgba(0, 0, 0, 0.1);

  /* Typography */
  --boreal-typography-font-family-primary:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
    Arial, sans-serif;
  --boreal-typography-font-size-s: 0.875rem;
  --boreal-typography-font-size-m: 1rem;
  --boreal-typography-font-size-l: 1.125rem;
  --boreal-typography-text-heading-regular-3xl: 2rem;

  /* Spacing/Radius */
  --boreal-radius-size-xs: 4px;
  --boreal-radius-size-s: 8px;
  --boreal-radius-size-m: 12px;

  /* Theme Colors */
  --boreal-theme-neutral-25: #fafafa;
  --boreal-theme-neutral-200: #eeeeee;
  --boreal-theme-neutral-600: #757575;
  --boreal-theme-neutral-700: #616161;
  --boreal-theme-primary-base: #1976d2;
  --boreal-theme-primary-dark: #1565c0;
  --boreal-theme-accent-base: #ff6b35;
  --boreal-theme-white: #ffffff;
  --boreal-theme-danger-dark: #d32f2f;
}
```

## Success Criteria

- ✅ All 8 components implemented (4 React + 4 Lit, including migrated Callout)
- ✅ `tokens-fallback.css` created with all required CSS custom properties
- ✅ Components follow existing Boreal DS patterns (BorealStoryMeta, CSS modules)
- ✅ Callout moved to `docs/` folder and updated with `--boreal-*` tokens
- ✅ Button.mdx and Icons.mdx updated to use new shared components
- ✅ Storybook builds without errors (with fallback tokens)
- ✅ All components work in both Canvas and Docs modes
- ✅ Theme switching works across all components (proximus, masiv, telesign, bics)
- ✅ All test stories created and manually verified
- ✅ **Test stories deleted after verification** ⚠️
- ✅ Documentation updated (CONTRIBUTING/PATTERNS)
- ✅ No console errors or warnings in Storybook
- ✅ CSS modules scope correctly across all components

## Critical Notes

### Token Strategy

- **Simple approach**: Hardcoded approximations (no extraction scripts)
- **Fallback pattern**: `var(--boreal-token-name, fallback-value)`
- **Temporary file**: `tokens-fallback.css` will be deleted when styleguidelines is complete

### Callout Migration

- Move from `components/Callout/` to `components/docs/Callout/`
- Update all import paths (no backwards compatibility)
- Update to use `--boreal-*` tokens + fallbacks

### Test Stories

- **Purpose**: Manual visual verification only
- **Lifecycle**: Create → Test → Verify → **DELETE**
- **Not committed**: Development-only artifacts

### Brand Assets

- MainLogo requires SVG assets for: proximus, masiv, telesign, bics
- Coordinate with design team for logo files

## Dependencies

All required dependencies are already installed:

- ✅ `react` (React components)
- ✅ `lit` (Lit components)
- ✅ `@storybook/addon-links` (DocsLinkTo navigation)
- ✅ `@storybook/csf` (toId helper)
- ✅ `highlight.js` (CodeBlock syntax highlighting)

No additional package installation required.
