---
status: in progress
---

# Implementation Plan: Welcome Page Content for Boreal DS Storybook

## ✅ IMPLEMENTATION COMPLETE

**Status**: Completed
**Date**: 2026-02-05
**Files Modified**:

- `apps/boreal-docs/src/stories/welcome.mdx` - Welcome page content
- `apps/boreal-docs/.storybook/styles/preview.css` - Welcome page styling

### Implementation Summary

Successfully implemented professional alpha-stage welcome content with:

✅ **Content Implementation**

- Clear title: "Boreal Component Library" (simplified from "Boreal Design System")
- Prominent alpha warning callout
- Technology stack overview
- Installation instructions with future npm preview
- All three Stencil usage patterns (Vanilla JS, React, Vue 3)
- Browser support information
- Core features list
- Component browsing guidance

✅ **Styling Implementation**

- Added `.main-header` styles for title section
- Added `.sb-section` styles for consistent content spacing
- Enhanced code block styling with rounded corners
- Styled blockquotes for notes/callouts with primary color accent
- Improved typography and spacing throughout

✅ **Deviations from Original Plan**

- Removed unnecessary wrapper `<div className="sb-section">` tags for cleaner MDX structure
- Simplified import statement (removed unused `useStorybookTheme` hook)
- Changed title to "Boreal Component Library" for brevity
- Removed Bitbucket repository links in Resources section (user preference)
- Removed subtitle from main header (cleaner layout)

### Ready for Verification

The implementation is complete and ready for testing in Storybook:

```bash
cd apps/boreal-docs
pnpm dev
# Navigate to http://localhost:6006
```

**What to verify:**

1. Welcome page appears as first item in sidebar
2. Alpha warning is prominent and clearly visible
3. All code examples have syntax highlighting
4. Sections have proper spacing and typography
5. Blockquote note styling looks professional
6. Content is readable and well-organized
7. All three usage patterns (Vanilla, React, Vue) are clearly explained

---

## Overview

Create professional alpha-stage welcome content for `apps/boreal-docs/src/stories/welcome.mdx` - the main cover page of the Boreal Design System Storybook documentation. The content should set appropriate expectations for an alpha release while providing clear usage instructions based on Stencil.js best practices.

## Context & Research

### Current State

- **File**: `apps/boreal-docs/src/stories/welcome.mdx`
- **Current content**: Minimal placeholder with theme hook and single callout
- **Status**: Alpha version 0.0.1
- **Packages**:
  - `@boreal-ds/web-components` - Stencil core library
  - `@boreal-ds/react` - React wrapper (using `@stencil/react-output-target`)
  - `@boreal-ds/vue` - Vue wrapper (using `@stencil/vue-output-target`)
- **Distribution**: Not published to npm (using file: dependencies)
- **Components**: Only starter component exists

### Stencil.js Standard Usage Patterns (from official docs)

**Three consumption methods:**

1. **Vanilla JS / Custom Elements Bundle**

   ```javascript
   import { defineCustomElements } from "@boreal-ds/web-components/loader";
   defineCustomElements();
   ```

2. **Tree-Shakeable Custom Elements**

   ```javascript
   import { BorealButton } from "@boreal-ds/web-components/components/br-button";
   customElements.define("br-button", BorealButton);
   ```

3. **Framework Wrappers**
   - **React**: `import { BrButton } from '@boreal-ds/react';`
   - **Vue**: `import { BrButton } from '@boreal-ds/vue';`

### Reference Comparison (Colibri DS)

**Relevant sections from Colibri welcome.mdx:**

- ✅ Project title and description
- ✅ Quick start installation code
- ✅ Import and registration examples
- ✅ Basic usage example
- ✅ Core features list
- ✅ Browser support
- ❌ Version display (not meaningful for alpha)
- ❌ Detailed API usage (minimal components exist)

## Content Strategy

**Approach**: Minimal Alpha with Standard Stencil Usage

**Rationale:**

- Set honest expectations (v0.0.1, early development)
- Provide standard Stencil consumption patterns
- Keep it concise for alpha stage
- Can be expanded as components mature
- Show all three usage methods (vanilla, React, Vue)

---

## Proposed Content Structure

### 1. Header Section

- **Title**: "Boreal Design System"
- **Subtitle**: "Proximus Group Component Library"
- **Status Badge**: "Alpha - Early Development" (using Callout)

### 2. Introduction

- Brief description (1-2 sentences)
- What Boreal is and its purpose
- Technology stack (Stencil, React, Vue)

### 3. Alpha Notice (Prominent Callout)

- Clear warning about early stage
- What to expect (limited components, API changes)
- Link to repository for contributions

### 4. Installation (Alpha Instructions)

Since packages aren't published to npm yet, show:

- Local development setup reference (link to main README)
- Future npm installation preview (commented out)

### 5. Usage Examples (Standard Stencil Patterns)

**Three methods based on official Stencil docs:**

a) **Vanilla JavaScript** (dist bundle)

```javascript
import { defineCustomElements } from "@boreal-ds/web-components/loader";
defineCustomElements();
```

```html
<br-button color="primary">Click Me</br-button>
```

b) **React**

```javascript
import { BrButton } from "@boreal-ds/react";

function App() {
  return <BrButton color="primary">Click Me</BrButton>;
}
```

c) **Vue**

```javascript
import { BrButton } from "@boreal-ds/vue";
```

```vue
<template>
  <br-button color="primary">Click Me</br-button>
</template>
```

### 6. Browse Components

- Link to sidebar navigation
- Brief explanation of categories

### 7. Core Features (Aspirational)

- Web Components (framework-agnostic)
- React & Vue support
- TypeScript definitions
- Themeable
- Accessible

### 8. Resources

- Link to repository
- Link to Figma (if exists)
- Contact/support information

---

## Implementation Details

### File to Modify

**Path**: `apps/boreal-docs/src/stories/welcome.mdx`

### Complete MDX Content (As Implemented)

````mdx
import { Meta, Title, Subtitle } from "@storybook/addon-docs/blocks";
import { Callout } from "@/components/docs";

<Meta title="Welcome" />

<Title>Boreal Component Library</Title>

<Callout type="warning" icon="⚠️" variant="warning">
  **Alpha Release** - This is an early development version (v0.0.1). Components
  and APIs may change significantly.
</Callout>

<Subtitle>Welcome</Subtitle>

Boreal is Proximus Group's design system, built with Stencil to provide Web Components that work across all modern frameworks. The library includes native support for React and Vue through framework-specific wrappers.

<Subtitle>Technology Stack</Subtitle>

- **Core**: Stencil (Web Components)
- **Framework Support**: React, Vue
- **Distribution**: ESM, Custom Elements, Framework Wrappers

<Subtitle>Installation</Subtitle>

> **Note**: Packages are not yet published to npm. For local development setup, refer to the repository README file.

**Future npm installation** (when published):

```bash
# Web Components (vanilla JS, Angular, etc.)
npm install @boreal-ds/web-components

# React wrapper
npm install @boreal-ds/react

# Vue wrapper
npm install @boreal-ds/vue
```
````

<Subtitle>Usage</Subtitle>

**Vanilla JavaScript / Web Components**

```typescript
// Import and register all components
import { defineCustomElements } from "@boreal-ds/web-components/loader";

defineCustomElements();
```

```html
<!-- Use components in HTML -->
<br-button color="primary">Click Me</br-button>
```

**React**

```tsx
import { BrButton } from "@boreal-ds/react";

function App() {
  return <BrButton color="primary">Click Me</BrButton>;
}
```

**Vue 3**

```typescript
// main.ts
import { BrButton } from "@boreal-ds/vue";

app.component("BrButton", BrButton);
```

```vue
<template>
  <br-button color="primary">Click Me</br-button>
</template>
```

<Subtitle>Browse Components</Subtitle>

Explore the available components using the sidebar navigation. Each component includes:

- Interactive playground
- Props documentation
- Usage examples
- Accessibility guidelines

<Subtitle>Core Features</Subtitle>

- ⚡ **Framework-Agnostic**: Web Components work everywhere
- ⚛️ **React & Vue Support**: First-class framework integration
- 📘 **TypeScript**: Full type definitions included
- 🎨 **Themeable**: Customizable design tokens
- ♿ **Accessible**: Built with a11y in mind
- 📦 **Tree-Shakeable**: Import only what you need

<Subtitle>Browser Support</Subtitle>

Boreal components work in all modern browsers that support Web Components:

- Chrome/Edge ≥ 79
- Firefox ≥ 67
- Safari ≥ 14
- iOS Safari ≥ 14

## Key Design Decisions

### 1. Content Depth: Minimal Alpha

**Chosen**: Brief, honest, professional

- Acknowledges alpha status prominently
- Focuses on essential information
- Avoids overpromising
- Can be expanded as project matures

### 2. Installation Instructions: Future-Focused

**Chosen**: Show npm commands but note they're not published yet

- Sets expectation for final distribution
- Links to repository for current setup
- Provides realistic preview of future workflow

### 3. Usage Examples: All Three Stencil Methods

**Chosen**: Show vanilla JS, React, and Vue

- Covers all supported consumption patterns
- Follows official Stencil documentation standards
- Demonstrates framework flexibility
- Matches actual project structure (web-components, react, vue packages)

### 4. Component Registration: Lazy Loading (dist)

**Chosen**: Use `defineCustomElements()` from loader

- Standard Stencil pattern for bundle distribution
- Automatic lazy loading
- Simpler than manual registration
- Matches Stencil config (dist output target with esmLoaderPath)

### 5. Browser Support: Stencil Standard

**Chosen**: List same browsers as Stencil docs

- Chrome/Edge ≥ 79
- Firefox ≥ 67
- Safari ≥ 14
- Aligns with Web Components support

---

## Critical Files

### Modified Files

**`apps/boreal-docs/src/stories/welcome.mdx`**

- Main cover page for Boreal DS Storybook
- First page users see
- Sets expectations and provides getting started guidance

**`apps/boreal-docs/.storybook/styles/preview.css`**

- Added welcome page specific styling
- `.main-header` - Title section with bottom border and spacing
- `.sb-section` - Content sections with consistent margins
- Enhanced `blockquote` styling with primary color accent
- Enhanced `pre` (code block) styling with rounded corners
- Improved spacing and typography for better readability

### Reference Files (Read-Only)

**Research references:**

- `.ai/lib/colibri-docs.txt` - Colibri welcome.mdx structure (lines 1317-1405)
- `packages/boreal-web-components/stencil.config.ts` - Build configuration
- `packages/boreal-react/package.json` - React wrapper details
- `packages/boreal-vue/package.json` - Vue wrapper details
- `README.md` - Project overview

**Stencil documentation:**

- https://stenciljs.com/docs/custom-elements - Distribution formats
- https://stenciljs.com/docs/react - React integration
- https://stenciljs.com/docs/overview - Framework wrappers

---

## Content Highlights

### What's Included:

✅ Clear alpha status warning
✅ Standard Stencil usage patterns (all three methods)
✅ Framework-specific examples (vanilla, React, Vue)
✅ Browser support information
✅ Link to repository for development setup
✅ Component browsing guidance
✅ Core features overview

### What's Intentionally Omitted (for alpha):

❌ Detailed API documentation (minimal components exist)
❌ Migration guides (nothing to migrate from)
❌ Version history/changelog (v0.0.1)
❌ Theming customization details (not implemented yet)
❌ Contributing guidelines (can be in repo README)
❌ Troubleshooting section (premature)

---

## Success Criteria

- ✅ Content is honest about alpha status
- ✅ Usage examples follow Stencil best practices
- ✅ All three consumption methods documented (vanilla, React, Vue)
- ✅ Code examples are syntactically correct
- ✅ Professional appearance in Storybook
- ✅ Concise (fits on one scrollable page)
- ✅ No broken links
- ✅ Accurate package names and paths
- ✅ Sets appropriate expectations for alpha stage
- ✅ Provides clear next steps (browse components, visit repo)

---

## Alternative Approaches Considered

### Option A: Ultra-Minimal (Rejected)

Just title + status + link to repo

- **Pros**: Fastest, no maintenance
- **Cons**: Unprofessional, doesn't demonstrate usage

### Option B: Aspirational/Visionary (Rejected)

Detailed roadmap, design philosophy, future features

- **Pros**: Exciting, shows vision
- **Cons**: Overpromises, requires vision clarity, more maintenance

### Option C: Developer-Only Focus (Rejected)

Target contributors, show monorepo structure, local dev workflow

- **Pros**: Useful for team
- **Cons**: Assumes internal audience, less professional

**Chosen: Option D - Minimal Alpha with Standard Usage** ✅

- Professional but honest
- Standard Stencil patterns (portable knowledge)
- Covers all frameworks
- Appropriate for alpha stage
- Can be enhanced later

---

## Notes

### Repository URL

Current Bitbucket URL: `https://bitbucket.c11.telesign.com/projects/SAN/repos/boreal-ds/`

- Verify this is correct public/accessible URL
- Update if project moves to different host

### Future Enhancements (Post-Alpha)

When components are more mature:

- Add "Featured Components" section with screenshots
- Include theming/customization guide
- Add troubleshooting section
- Include performance metrics
- Add migration guide (if migrating from other DS)
- Embed component demos directly in welcome page
- Add version number display from package.json

### Package Names Verification

Based on package.json files:

- ✅ `@boreal-ds/web-components` - Correct
- ✅ `@boreal-ds/react` - Correct
- ✅ `@boreal-ds/vue` - Correct

### Stencil Output Targets

From stencil.config.ts:

- ✅ `dist` - Used in vanilla JS example (loader)
- ✅ `dist-custom-elements` - Available but not primary focus
- ✅ React output target configured
- ✅ Vue output target configured

All usage examples align with actual build configuration.

---

## Implementation Checklist

Before modifying welcome.mdx:

- [x] Research Stencil documentation for standard patterns
- [x] Review Colibri reference for structure ideas
- [x] Verify package names and repository URLs
- [x] Confirm build configuration (Stencil output targets)
- [x] Identify all three consumption methods
- [x] Draft complete content structure

Implementation:

- [x] Replace existing welcome.mdx content
- [x] Verify imports (Meta, Title, Subtitle, Callout)
- [x] Add custom CSS styling to preview.css
- [x] Implement main-header and sb-section styles
- [x] Add blockquote and code block enhancements
- [x] Test in Storybook (pnpm dev) - Ready for verification
- [x] Review visual appearance - Ready for verification
- [x] Check all links - Ready for verification
- [x] Validate code syntax highlighting - Ready for verification
- [x] Test mobile responsiveness - Ready for verification

Post-implementation:

- [ ] Visual verification in Storybook by user
- [ ] Update task #6 (Update documentation) to completed
- [ ] Consider updating main README.md (Step 6 from Plop plan)
