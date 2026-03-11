---
status: in progress
---

# Boreal Icons Strategy & Implementation Plan

**Document Version:** 1.0
**Date:** January 23, 2026
**Status:** Approved for Implementation

---

## Executive Summary

This document outlines the complete strategy for implementing and evolving the Boreal Design System icon library. The approach balances immediate alpha testing needs with long-term scalability through a phased rollout over 8-10 weeks.

**Key Decisions:**

- ✅ Start with icon font + S3 CDN (simplest for alpha)
- ✅ Add component wrappers in beta (better DX)
- ✅ Publish npm package at v1.0 (enterprise readiness)
- ⏳ SVG sprites as v2.0 optimization (if needed)

---

## Current State Assessment

### What We Have

**Assets:**

- 500+ icons as icon font
- CSS hosted on S3: `https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css`
- JSON manifest with icon names: `icons.json` (500+ entries)
- Storybook documentation with search functionality

**Current Usage:**

```html
<link
  rel="stylesheet"
  href="https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css"
/>
<em class="bds-icon-home" style="color: #000; font-size: 2rem;"></em>
```

**Pain Points:**

- Terminology confusion (argTypes named like props, but not a component)
- No type safety for icon names
- Manual class naming with `bds-icon-` prefix
- No component abstraction for better DX

---

## Icon Distribution Strategies Comparison

### Option 1: Icon Font (Current)

**How it works:** Single CSS file with all icons as font glyphs

**Pros:**

- Simple integration (one `<link>` tag)
- Works without build tools
- Small file size (~500KB compressed)
- Excellent browser support

**Cons:**

- Can't use multi-color icons
- All icons loaded upfront (no tree-shaking)
- Limited to single color via CSS

### Option 2: SVG Sprite Sheet

**How it works:** Single SVG file with all icons as `<symbol>` elements

**Pros:**

- Multi-color support
- Better rendering quality
- Smaller than font (~300KB)
- Full SVG styling control

**Cons:**

- Requires loading sprite file
- More complex setup
- Need extra build tooling

### Option 3: Individual SVG Files (Colibri Approach)

**How it works:** Separate `.svg` file per icon, dynamically imported

**Pros:**

- Perfect tree-shaking (only used icons bundled)
- Easy Git workflow (one file per icon)
- Granular cache invalidation
- No upfront loading cost

**Cons:**

- More network requests initially
- Requires build tools
- More complex build pipeline

### Decision: Start with Icon Font, Add SVG Sprites in v2.0+

**Rationale:**

- Alpha needs simple, fast integration
- 500+ icons is manageable as font
- Can migrate to sprites later without breaking users
- Font works for 90% of use cases

---

## Phased Implementation Plan

### Phase 1: Alpha/Beta (Weeks 1-2)

**Goal:** Validate with early adopters, clarify documentation

#### 1.1 Documentation Improvements

**Update Storybook argTypes naming:**

```typescript
// Before (confusing)
type StoryArgs = {
  name: string; // Sounds like a prop
  size?: string; // Sounds like a prop
  color?: string; // Sounds like a prop
  search?: string;
};

// After (clear)
type IconDisplayOptions = {
  iconClass: string; // CSS class name
  fontSize?: string; // CSS font-size value
  iconColor?: string; // CSS color value
  search?: string; // Search filter (docs only)
};
```

**Update argTypes descriptions:**

```typescript
argTypes: {
  iconClass: {
    control: 'text',
    description: 'CSS class name (e.g., "bds-icon-home"). Apply this to an <em> tag in your HTML.',
    table: {
      type: { summary: 'string (CSS class)' },
      category: 'Icon Configuration',
    },
  },
  fontSize: {
    control: 'text',
    description: 'CSS font-size value to control icon size (e.g., "2rem", "24px").',
    table: {
      type: { summary: 'string (CSS value)' },
      category: 'Styling',
    },
  },
  iconColor: {
    control: 'color',
    description: 'CSS color value for the icon (e.g., "#000", "rgb(255, 0, 0)", "currentColor").',
    table: {
      type: { summary: 'string (CSS color)' },
      category: 'Styling',
    },
  },
  search: {
    control: 'text',
    description: 'Filter icons by name in the AllIcons story.',
    table: {
      type: { summary: 'string' },
      category: 'Documentation Tools',
    },
  },
}
```

**Add clarifying note to Icons.mdx:**

```mdx
## Current Approach (Alpha)

Icons are distributed as **CSS font classes** via CDN. This approach:

- ✅ Works without build tools (just add a `<link>` tag)
- ✅ Simple integration for rapid testing
- ✅ Globally cached for performance
- ⏳ Component wrappers coming in Beta

> **Important**: The controls below demonstrate CSS attributes you'll use in your code,
> not component props. These are styling options for documentation purposes only.

## Roadmap

- **Phase 1 (Alpha/Beta)**: Icon font + CSS classes ← _We are here_
- **Phase 2 (Beta)**: Add `<boreal-icon>` component wrappers
- **Phase 3 (v1.0)**: npm package with TypeScript support
- **Phase 4 (v2.0+)**: SVG sprites (optional optimization)
```

#### 1.2 Feedback Collection

**Create feedback survey for alpha users:**

- How many icons do you typically use per page? (<10, 10-50, 50+, 100+)
- Do you need offline capability?
- Which framework are you using? (React, Vue, Svelte, Vanilla)
- Would you prefer a component API over CSS classes?
- Do you need TypeScript autocomplete for icon names?
- Any issues accessing S3/CDN resources?
- What's your target bundle size budget?

#### 1.3 Success Metrics

- ✅ 10+ teams using icons successfully
- ✅ < 5 critical issues reported
- ✅ Clear user preference data collected
- ✅ Framework usage breakdown documented

**Deliverables:**

- Updated Storybook documentation
- Feedback survey and collection system
- Usage analytics

**Duration:** 2 weeks
**Effort:** 0.5 developer + documentation writer

---

### Phase 2: Beta Release (Weeks 3-6)

**Goal:** Add component layer for better developer experience

**Decision Gate:** Review Phase 1 feedback

- If 70%+ users need components → Proceed
- If users happy with CSS → Skip to Phase 3

#### 2.1 Create Web Component (1 week)

**File structure:**

```
packages/boreal-web-components/src/components/
└── boreal-icon/
    ├── boreal-icon.tsx
    ├── boreal-icon.css
    ├── boreal-icon.stories.tsx
    ├── boreal-icon.spec.ts
    ├── icon-names.ts (generated)
    └── readme.md
```

**Component implementation:**

```typescript
// packages/boreal-web-components/src/components/boreal-icon/boreal-icon.tsx
import { Component, Prop, h } from '@stencil/core';

@Component({
  tag: 'boreal-icon',
  styleUrl: 'boreal-icon.css',
  shadow: true,
})
export class BorealIcon {
  /**
   * Icon name without 'bds-icon-' prefix
   * @example "home", "settings", "user"
   */
  @Prop() name!: string;

  /**
   * Size of the icon
   * @example "24px", "2rem", 24
   */
  @Prop() size: string | number = '24px';

  /**
   * Color of the icon
   * @example "#000", "currentColor", "var(--primary-color)"
   */
  @Prop() color: string = 'currentColor';

  /**
   * Accessible label for the icon
   * @example "Home", "Settings icon"
   */
  @Prop() label?: string;

  private get iconClass() {
    return this.name.startsWith('bds-icon-')
      ? this.name
      : `bds-icon-${this.name}`;
  }

  private get sizeValue() {
    return typeof this.size === 'number'
      ? `${this.size}px`
      : this.size;
  }

  render() {
    return (
      <em
        class={this.iconClass}
        style={{
          fontSize: this.sizeValue,
          color: this.color,
        }}
        aria-label={this.label || this.name}
        role="img"
      />
    );
  }
}
```

**boreal-icon.css:**

```css
/* Load icon font from S3 */
@import url("https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css");

:host {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

em {
  font-style: normal;
  line-height: 1;
}
```

**Backward compatibility:**

```html
<!-- Phase 1: Still works -->
<em class="bds-icon-home" style="font-size: 2rem;"></em>

<!-- Phase 2: New way (recommended) -->
<boreal-icon name="home" size="2rem"></boreal-icon>
```

#### 2.2 Generate React/Vue Wrappers (Automated)

Stencil automatically generates framework wrappers:

```bash
npm run build
```

Output:

```
packages/boreal-react/src/components/BorealIcon.tsx
packages/boreal-vue/src/components/BorealIcon.ts
```

**React usage:**

```tsx
import { BorealIcon } from "@boreal/react";

<BorealIcon name="home" size={24} color="primary" />;
```

**Vue usage:**

```vue
<template>
  <BorealIcon name="home" size="24" color="primary" />
</template>
```

#### 2.3 TypeScript Type Generation (2 days)

**Auto-generate icon name types from JSON:**

```typescript
// scripts/generate-icon-types.ts
import fs from "fs";
import icons from "../apps/boreal-docs/src/stories/Icons/icons/helpers/icons.json";

const iconNames = icons
  .map((icon) => icon.name.replace("bds-icon-", ""))
  .sort();

const iconNameType = iconNames.map((name) => `  | '${name}'`).join("\n");

const output = `
// This file is auto-generated. Do not edit manually.
// Generated from icons.json

export type IconName =
${iconNameType}
;

export const iconNames: IconName[] = [
${iconNames.map((name) => `  '${name}',`).join("\n")}
];

export const isValidIconName = (name: string): name is IconName => {
  return iconNames.includes(name as IconName);
};
`;

fs.writeFileSync(
  "./packages/boreal-web-components/src/components/boreal-icon/icon-names.ts",
  output,
);

console.log(`✅ Generated types for ${iconNames.length} icons`);
```

**Update component to use types:**

```typescript
import { IconName } from "./icon-names";

export class BorealIcon {
  @Prop() name!: IconName; // Now type-safe!
  // ...
}
```

**Add to build pipeline:**

```json
{
  "scripts": {
    "prebuild": "node scripts/generate-icon-types.ts",
    "build": "stencil build"
  }
}
```

#### 2.4 Update Documentation (2 days)

**Create new story: `Icons-Component.stories.tsx`**

```typescript
import type { BorealStory, BorealStoryMeta } from "@/types/stories";
import { html } from "lit";

type ComponentArgs = {
  name: string;
  size: string;
  color: string;
};

const meta: BorealStoryMeta<ComponentArgs> = {
  title: "images & icons/Icons/Component",
  component: "boreal-icon",
  argTypes: {
    name: {
      control: "text",
      description: "Icon name (without bds-icon- prefix)",
      table: {
        type: { summary: "IconName" },
        defaultValue: { summary: "home" },
      },
    },
    size: {
      control: "text",
      description: "Icon size",
      table: {
        type: { summary: "string | number" },
        defaultValue: { summary: "24px" },
      },
    },
    color: {
      control: "color",
      description: "Icon color",
      table: {
        type: { summary: "string" },
        defaultValue: { summary: "currentColor" },
      },
    },
  },
};

export default meta;

export const Default: BorealStory<ComponentArgs> = {
  args: {
    name: "home",
    size: "24px",
    color: "#000",
  },
  render: (args) => html`
    <boreal-icon
      name="${args.name}"
      size="${args.size}"
      color="${args.color}"
    ></boreal-icon>
  `,
};
```

**Update Icons.mdx:**

```mdx
## Using Components (Beta - Recommended)

Component wrappers provide a better developer experience with TypeScript support.

### Web Components

\`\`\`html
<boreal-icon name="home" size="24" color="currentColor"></boreal-icon>
\`\`\`

### React

\`\`\`tsx
import { BorealIcon } from '@boreal/react';

<BorealIcon name="home" size={24} color="primary" />
\`\`\`

### Vue

\`\`\`vue

<template>
  <BorealIcon name="home" size="24" color="primary" />
</template>

<script setup>import {BorealIcon} from '@boreal/vue';</script>

\`\`\`

## Raw CSS (Still Supported)

If you prefer not to use components:

\`\`\`html

<link
  rel="stylesheet"
  href="https://resources-borealds.s3.../boreal-styles.css"
/>
<em class="bds-icon-home" style="font-size: 24px; color: #000;"></em>
\`\`\`
```

**Deliverables:**

- `<boreal-icon>` web component
- React and Vue wrappers
- TypeScript types with autocomplete
- Updated Storybook documentation

**Duration:** 3 weeks
**Effort:** 1 developer full-time

---

### Phase 3: v1.0 Production (Weeks 7-10)

**Goal:** npm package, enterprise-ready, stable API

#### 3.1 Prepare npm Package Structure

```
@boreal/design-system/
├── dist/
│   ├── components/
│   │   └── boreal-icon/
│   ├── icons/
│   │   ├── boreal-icons.css    (Downloaded from S3)
│   │   ├── boreal-icons.woff2  (Downloaded from S3)
│   │   └── icon-names.json
│   └── types/
├── loader/
└── package.json
```

**package.json exports:**

```json
{
  "name": "@boreal/design-system",
  "version": "1.0.0",
  "main": "./dist/index.cjs.js",
  "module": "./dist/index.js",
  "types": "./dist/types/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs.js",
      "types": "./dist/types/index.d.ts"
    },
    "./icons": {
      "import": "./dist/components/boreal-icon/index.js",
      "types": "./dist/types/components/boreal-icon/index.d.ts"
    },
    "./icons/styles.css": "./dist/icons/boreal-icons.css",
    "./icons/names": "./dist/icons/icon-names.json"
  },
  "files": ["dist/", "loader/"]
}
```

#### 3.2 Build Process: Copy Assets from S3

```typescript
// scripts/copy-icon-assets.ts
import fs from "fs";
import https from "https";
import { pipeline } from "stream/promises";

const S3_BASE = "https://resources-borealds.s3.us-east-1.amazonaws.com/icons";
const VERSION = process.env.ICON_VERSION || "current";
const DIST_DIR = "./dist/icons";

async function downloadFile(url: string, destination: string) {
  const file = fs.createWriteStream(destination);
  return new Promise((resolve, reject) => {
    https
      .get(url, (response) => {
        response.pipe(file);
        file.on("finish", () => {
          file.close();
          resolve(true);
        });
      })
      .on("error", reject);
  });
}

async function copyIconAssets() {
  // Create dist directory
  if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
  }

  console.log(`📦 Downloading icon assets from S3 (version: ${VERSION})...`);

  // Download CSS file
  await downloadFile(
    `${S3_BASE}/${VERSION}/boreal-styles.css`,
    `${DIST_DIR}/boreal-icons.css`,
  );
  console.log("✅ Downloaded boreal-icons.css");

  // Download font files (extract URLs from CSS)
  const css = fs.readFileSync(`${DIST_DIR}/boreal-icons.css`, "utf-8");
  const fontUrls = [...css.matchAll(/url\(['"]?([^'"]+\.woff2?)['"']?\)/g)];

  for (const [, fontPath] of fontUrls) {
    const fontUrl = fontPath.startsWith("http")
      ? fontPath
      : `${S3_BASE}/${VERSION}/${fontPath}`;

    const fontFileName = fontPath.split("/").pop();
    await downloadFile(fontUrl, `${DIST_DIR}/${fontFileName}`);
    console.log(`✅ Downloaded ${fontFileName}`);
  }

  // Update CSS to use local font files
  let updatedCss = css;
  for (const [fullMatch, fontPath] of fontUrls) {
    const fontFileName = fontPath.split("/").pop();
    updatedCss = updatedCss.replace(fullMatch, `url('./${fontFileName}')`);
  }
  fs.writeFileSync(`${DIST_DIR}/boreal-icons.css`, updatedCss);

  console.log("✅ Icon assets copied successfully");
}

copyIconAssets().catch(console.error);
```

**Add to build pipeline:**

```json
{
  "scripts": {
    "prebuild": "npm run generate:icon-types && npm run copy:icon-assets",
    "generate:icon-types": "node scripts/generate-icon-types.ts",
    "copy:icon-assets": "node scripts/copy-icon-assets.ts",
    "build": "stencil build"
  }
}
```

#### 3.3 Versioning Strategy

**S3 folder structure:**

```
s3://resources-borealds/icons/
├── current/              # Always latest (for CDN users)
│   ├── boreal-styles.css
│   └── fonts/
├── v1.0.0/              # Pinned versions
│   ├── boreal-styles.css
│   └── fonts/
├── v1.0.1/
├── v1.1.0/
└── v2.0.0/
```

**Component can reference specific versions:**

```css
/* Development: Use latest */
@import url("https://resources-borealds.s3.../icons/current/boreal-styles.css");

/* Production: Pin version */
@import url("https://resources-borealds.s3.../icons/v1.0.0/boreal-styles.css");
```

#### 3.4 Documentation: Multiple Installation Methods

```mdx
# Icons

## Installation Options

### Option 1: CDN Only (No Build Tools Required)

Best for: Simple websites, quick prototyping

\`\`\`html

<!DOCTYPE html>

<html>
  <head>
    <link
      rel="stylesheet"
      href="https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css"
    />
  </head>
  <body>
    <em class="bds-icon-home" style="font-size: 2rem;"></em>
  </body>
</html>
\`\`\`

### Option 2: npm + Component (Recommended)

Best for: React, Vue, or modern web apps

\`\`\`bash
npm install @boreal/design-system
\`\`\`

\`\`\`tsx
import { BorealIcon } from '@boreal/design-system';

<BorealIcon name="home" size={24} color="primary" />
\`\`\`

### Option 3: npm + Self-Hosted CSS

Best for: Corporate environments that block external CDNs

\`\`\`bash
npm install @boreal/design-system
\`\`\`

\`\`\`tsx
import '@boreal/design-system/icons/styles.css';

<em class="bds-icon-home" style="font-size: 2rem;"></em>
\`\`\`

### Option 4: Framework-Specific Packages

\`\`\`bash

# React

npm install @boreal/react

# Vue

npm install @boreal/vue
\`\`\`

\`\`\`tsx
// React
import { BorealIcon } from '@boreal/react';

<BorealIcon name="home" />

// Vue
import { BorealIcon } from '@boreal/vue';

<BorealIcon name="home" />
\`\`\`
```

#### 3.5 Publish to npm

```bash
# Build all packages
npm run build

# Publish web components
cd packages/boreal-web-components
npm version 1.0.0
npm publish --access public

# Publish React wrapper
cd ../boreal-react
npm version 1.0.0
npm publish --access public

# Publish Vue wrapper
cd ../boreal-vue
npm version 1.0.0
npm publish --access public
```

**Deliverables:**

- npm package published
- Multiple installation methods documented
- Versioned S3 assets
- CI/CD pipeline for releases

**Duration:** 3 weeks
**Effort:** 1 developer + DevOps support

---

### Phase 4: v2.0+ Future Enhancements (Months 4-6)

**Goal:** Optimize for scale, add SVG sprite support

**Decision Gate:** Analyze v1.0 telemetry

- Average icons used per app?
- Bundle size complaints?
- Performance bottlenecks?
- Demand for multi-color icons?

**Only proceed if:**

- Apps using 100+ icons consistently
- Bundle size is a documented problem
- Multi-color icon requests
- Performance metrics show issues

#### 4.1 SVG Sprite Generator

```typescript
// tools/build-sprite.ts
import fs from "fs";
import { glob } from "glob";
import { optimize } from "svgo";

async function buildSprite() {
  console.log("🎨 Building SVG sprite...");

  // Find all SVG source files
  const svgFiles = glob.sync("assets/icons/source/*.svg");

  let sprite = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none">\n`;

  for (const file of svgFiles) {
    const name = file.replace(".svg", "").split("/").pop();
    const content = fs.readFileSync(file, "utf-8");

    // Optimize SVG
    const optimized = optimize(content, {
      plugins: [
        "removeDoctype",
        "removeXMLProcInst",
        "removeComments",
        "removeMetadata",
        "removeEditorsNSData",
        "cleanupAttrs",
        "mergeStyles",
        "inlineStyles",
      ],
    });

    const svgContent = optimized.data;

    // Extract viewBox
    const viewBoxMatch = svgContent.match(/viewBox="([^"]+)"/);
    const viewBox = viewBoxMatch ? viewBoxMatch[1] : "0 0 24 24";

    // Extract paths and shapes
    const innerContent = svgContent
      .replace(/<svg[^>]*>/, "")
      .replace(/<\/svg>/, "")
      .trim();

    sprite += `  <symbol id="bds-icon-${name}" viewBox="${viewBox}">\n`;
    sprite += `    ${innerContent}\n`;
    sprite += `  </symbol>\n`;
  }

  sprite += `</svg>`;

  fs.writeFileSync("./dist/icons/sprite.svg", sprite);
  console.log(`✅ Generated sprite with ${svgFiles.length} icons`);
}

buildSprite();
```

#### 4.2 Update Component to Support Both Strategies

```typescript
@Component({
  tag: 'boreal-icon',
  styleUrl: 'boreal-icon.css',
  shadow: true,
})
export class BorealIcon {
  @Prop() name!: IconName;
  @Prop() size: string | number = '24px';
  @Prop() color: string = 'currentColor';

  /**
   * Icon rendering strategy
   * - 'font': Use icon font (default, better browser support)
   * - 'sprite': Use SVG sprite (better for 100+ icons)
   */
  @Prop() strategy: 'font' | 'sprite' = 'font';

  private get iconClass() {
    return this.name.startsWith('bds-icon-')
      ? this.name
      : `bds-icon-${this.name}`;
  }

  private get sizeValue() {
    return typeof this.size === 'number'
      ? `${this.size}px`
      : this.size;
  }

  private renderFontIcon() {
    return (
      <em
        class={this.iconClass}
        style={{
          fontSize: this.sizeValue,
          color: this.color,
        }}
        role="img"
        aria-label={this.label || this.name}
      />
    );
  }

  private renderSpriteIcon() {
    return (
      <svg
        width={this.sizeValue}
        height={this.sizeValue}
        style={{ color: this.color }}
        role="img"
        aria-label={this.label || this.name}
      >
        <use href={`#${this.iconClass}`}></use>
      </svg>
    );
  }

  render() {
    return this.strategy === 'sprite'
      ? this.renderSpriteIcon()
      : this.renderFontIcon();
  }
}
```

#### 4.3 Usage Documentation

```mdx
## Performance Optimization (v2.0+)

For applications using 100+ icons, SVG sprites offer better performance:

### Setup Sprite

\`\`\`html

<!-- Load sprite once at app root -->

<script>
  fetch('/path/to/sprite.svg')
    .then(r => r.text())
    .then(svg => {
      const div = document.createElement('div');
      div.innerHTML = svg;
      div.style.display = 'none';
      document.body.insertBefore(div, document.body.firstChild);
    });
</script>

\`\`\`

### Use Sprite Strategy

\`\`\`tsx

<BorealIcon name="home" strategy="sprite" />
\`\`\`

### Bundle Size Comparison

| Strategy        | Total Size      | Best For         |
| --------------- | --------------- | ---------------- |
| Icon Font       | ~500KB          | < 100 icons used |
| SVG Sprite      | ~300KB          | 100+ icons used  |
| Individual SVGs | ~1.5KB per icon | < 20 icons used  |
```

**Deliverables:**

- SVG sprite generator
- Dual-strategy component
- Performance documentation
- Migration guide

**Duration:** 2-3 months (low priority)
**Effort:** 0.5 developer

---

## Component Integration Strategy

### How Components Use Icons Across Phases

All Boreal components that need icons (Button, Alert, Input, etc.) should follow this unified pattern.

### Phase 1: CSS Classes Only

**Example: Button Component**

```typescript
// packages/boreal-web-components/src/components/boreal-button/boreal-button.tsx
import { Component, Prop, h } from '@stencil/core';

@Component({
  tag: 'boreal-button',
  styleUrl: 'boreal-button.css',
  shadow: true,
})
export class BorealButton {
  @Prop() label: string;

  /**
   * Icon CSS class (e.g., "bds-icon-search")
   */
  @Prop() icon?: string;

  @Prop() iconPosition: 'left' | 'right' = 'left';

  private renderIcon() {
    if (!this.icon) return null;
    return <em class={this.icon}></em>;
  }

  render() {
    return (
      <button>
        {this.iconPosition === 'left' && this.renderIcon()}
        {this.label && <span>{this.label}</span>}
        {this.iconPosition === 'right' && this.renderIcon()}
      </button>
    );
  }
}
```

**boreal-button.css:**

```css
/* Import icon font */
@import url("https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css");

button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

em {
  font-style: normal;
  font-size: 1rem;
  line-height: 1;
}
```

**Usage:**

```html
<boreal-button label="Search" icon="bds-icon-search"></boreal-button>
```

### Phase 2: Hybrid Approach (Both CSS and Component)

**Updated Button Component:**

```typescript
import { Component, Prop, h, Element } from '@stencil/core';

@Component({
  tag: 'boreal-button',
  styleUrl: 'boreal-button.css',
  shadow: true,
})
export class BorealButton {
  @Element() el: HTMLElement;

  @Prop() label: string;

  /**
   * Icon name (without prefix) or CSS class
   * @example "search" or "bds-icon-search"
   */
  @Prop() icon?: string;

  @Prop() iconSize?: string = '1rem';
  @Prop() iconPosition: 'left' | 'right' = 'left';

  private renderIcon() {
    // Check if user provided custom slot
    const hasSlot = this.el.querySelector('[slot^="icon-"]');
    if (hasSlot) return null;

    if (!this.icon) return null;

    // Smart detection: Is it a full CSS class or just a name?
    const isLegacyClass = this.icon.startsWith('bds-icon-');

    // Check if boreal-icon component is available
    const hasIconComponent = customElements.get('boreal-icon');

    if (isLegacyClass || !hasIconComponent) {
      // Phase 1 compatibility: Use CSS class
      const className = isLegacyClass ? this.icon : `bds-icon-${this.icon}`;
      return <em class={className} style={{ fontSize: this.iconSize }}></em>;
    } else {
      // Phase 2: Use component
      return (
        <boreal-icon
          name={this.icon}
          size={this.iconSize}
          color="currentColor"
        ></boreal-icon>
      );
    }
  }

  render() {
    return (
      <button>
        {this.iconPosition === 'left' && (
          <slot name="icon-left">{this.renderIcon()}</slot>
        )}

        {this.label && <span>{this.label}</span>}

        {this.iconPosition === 'right' && (
          <slot name="icon-right">{this.renderIcon()}</slot>
        )}
      </button>
    );
  }
}
```

**All these usages work:**

```html
<!-- Option 1: Legacy CSS class (Phase 1 - still works) -->
<boreal-button label="Search" icon="bds-icon-search"></boreal-button>

<!-- Option 2: Icon name (Phase 2 - recommended) -->
<boreal-button label="Search" icon="search"></boreal-button>

<!-- Option 3: Custom slot (Phase 2 - advanced) -->
<boreal-button label="Search">
  <boreal-icon slot="icon-left" name="search" color="blue"></boreal-icon>
</boreal-button>

<!-- Option 4: Any custom content -->
<boreal-button label="Upload">
  <img slot="icon-left" src="/custom-icon.svg" />
</boreal-button>
```

### Phase 3: Component-First with TypeScript

**Final Button Implementation:**

```typescript
import { Component, Prop, h } from '@stencil/core';
import { IconName } from '../boreal-icon/icon-names';

@Component({
  tag: 'boreal-button',
  styleUrl: 'boreal-button.css',
  shadow: true,
})
export class BorealButton {
  @Prop() label: string;

  /**
   * Icon to display (typed!)
   */
  @Prop() icon?: IconName;

  @Prop() iconSize?: string = '1rem';
  @Prop() iconPosition: 'left' | 'right' = 'left';

  private renderIcon() {
    if (!this.icon) return null;

    return (
      <boreal-icon
        name={this.icon}
        size={this.iconSize}
        color="currentColor"
      ></boreal-icon>
    );
  }

  render() {
    return (
      <button>
        {this.iconPosition === 'left' && (
          <slot name="icon-left">{this.renderIcon()}</slot>
        )}

        {this.label && <span>{this.label}</span>}

        {this.iconPosition === 'right' && (
          <slot name="icon-right">{this.renderIcon()}</slot>
        )}
      </button>
    );
  }
}
```

**React/TypeScript usage with autocomplete:**

```tsx
import { BorealButton } from '@boreal/react';

// TypeScript validates icon names!
<BorealButton
  label="Search"
  icon="search"  // ✅ Autocomplete works
  iconSize="1.5rem"
/>

<BorealButton
  label="Invalid"
  icon="searrch"  // ❌ TypeScript error: Not a valid icon name
/>
```

### Component Patterns for Different Use Cases

#### 1. Predefined Icons (Alert, Badge)

```typescript
@Component({ tag: 'boreal-alert' })
export class BorealAlert {
  @Prop() type: 'info' | 'warning' | 'error' | 'success' = 'info';
  @Prop() message: string;
  @Prop() showIcon: boolean = true;

  private getIconForType(): IconName {
    const iconMap: Record<typeof this.type, IconName> = {
      info: 'info-circle',
      warning: 'alert-warning-high',
      error: 'close-circle',
      success: 'check-circle',
    };
    return iconMap[this.type];
  }

  render() {
    return (
      <div class={`alert alert--${this.type}`}>
        {this.showIcon && (
          <boreal-icon
            name={this.getIconForType()}
            size="20px"
          />
        )}
        <span>{this.message}</span>
      </div>
    );
  }
}
```

**Usage:**

```html
<!-- Icon automatically matches type -->
<boreal-alert type="warning" message="Be careful!" />
```

#### 2. Optional Icons (Input, Card)

```typescript
@Component({ tag: 'boreal-input' })
export class BorealInput {
  @Prop() placeholder: string;
  @Prop() prefixIcon?: IconName;
  @Prop() suffixIcon?: IconName;

  render() {
    return (
      <div class="input-wrapper">
        {this.prefixIcon && (
          <slot name="prefix">
            <boreal-icon name={this.prefixIcon} size="16px" />
          </slot>
        )}

        <input placeholder={this.placeholder} />

        {this.suffixIcon && (
          <slot name="suffix">
            <boreal-icon name={this.suffixIcon} size="16px" />
          </slot>
        )}
      </div>
    );
  }
}
```

**Usage:**

```html
<!-- With icon props -->
<boreal-input placeholder="Search..." prefix-icon="search" />

<!-- With custom slot -->
<boreal-input placeholder="Password">
  <boreal-icon slot="suffix" name="sight-on"></boreal-icon>
</boreal-input>
```

#### 3. Icon Collections (Navigation, Menu)

```typescript
interface NavItem {
  label: string;
  icon?: IconName;
  href: string;
  active?: boolean;
}

@Component({ tag: 'boreal-nav' })
export class BorealNav {
  @Prop() items: NavItem[] = [];

  render() {
    return (
      <nav>
        {this.items.map(item => (
          <a
            href={item.href}
            class={{ active: item.active }}
          >
            {item.icon && (
              <boreal-icon name={item.icon} size="20px" />
            )}
            <span>{item.label}</span>
          </a>
        ))}
      </nav>
    );
  }
}
```

**Usage:**

```tsx
const navItems: NavItem[] = [
  { label: "Home", icon: "home", href: "/", active: true },
  { label: "Settings", icon: "settings", href: "/settings" },
  { label: "Profile", icon: "person", href: "/profile" },
];

<BorealNav items={navItems} />;
```

### Migration Path for Component Authors

**All components should follow this pattern from day 1:**

```typescript
private renderIcon() {
  if (!this.icon) return null;

  // Phase 1: Only CSS works
  // Phase 2+: Component works if available
  const hasIconComponent = customElements.get('boreal-icon');
  const isLegacyClass = this.icon.startsWith('bds-icon-');

  if (isLegacyClass || !hasIconComponent) {
    // Fallback to CSS
    const className = isLegacyClass ? this.icon : `bds-icon-${this.icon}`;
    return <em class={className}></em>;
  }

  // Use component
  return <boreal-icon name={this.icon} />;
}
```

**This ensures:**

- ✅ Works in Phase 1 (CSS only)
- ✅ Automatically upgrades in Phase 2 (component available)
- ✅ No breaking changes needed

### Testing Strategy for Components with Icons

```typescript
// boreal-button.spec.ts
import { newSpecPage } from "@stencil/core/testing";
import { BorealButton } from "./boreal-button";
import { BorealIcon } from "../boreal-icon/boreal-icon";

describe("boreal-button with icons", () => {
  it("should render with CSS icon (Phase 1)", async () => {
    const page = await newSpecPage({
      components: [BorealButton],
      html: `<boreal-button icon="bds-icon-search" label="Search"></boreal-button>`,
    });

    const em = page.root.shadowRoot.querySelector("em");
    expect(em).not.toBeNull();
    expect(em.classList.contains("bds-icon-search")).toBe(true);
  });

  it("should render with icon component (Phase 2)", async () => {
    const page = await newSpecPage({
      components: [BorealButton, BorealIcon],
      html: `<boreal-button icon="search" label="Search"></boreal-button>`,
    });

    const icon = page.root.shadowRoot.querySelector("boreal-icon");
    expect(icon).not.toBeNull();
    expect(icon.getAttribute("name")).toBe("search");
  });

  it("should support custom icon via slot", async () => {
    const page = await newSpecPage({
      components: [BorealButton],
      html: `
        <boreal-button label="Search">
          <img slot="icon-left" src="/custom.svg" />
        </boreal-button>
      `,
    });

    const slot = page.root.shadowRoot.querySelector('slot[name="icon-left"]');
    expect(slot).not.toBeNull();
  });
});
```

---

## Timeline Summary

| Phase                   | Duration   | Key Deliverables                               | Effort         |
| ----------------------- | ---------- | ---------------------------------------------- | -------------- |
| **Phase 1: Alpha/Beta** | Weeks 1-2  | Documentation improvements, feedback           | 0.5 dev        |
| **Phase 2: Beta**       | Weeks 3-6  | Icon component, React/Vue wrappers, TypeScript | 1 dev          |
| **Phase 3: v1.0**       | Weeks 7-10 | npm package, versioning, production release    | 1 dev + DevOps |
| **Phase 4: v2.0+**      | Months 4-6 | SVG sprites (optional), optimization           | 0.5 dev        |

**Total time to production v1.0:** 8-10 weeks

---

## Decision Points & Gates

### After Phase 1 (Week 2)

**Review metrics:**

- User satisfaction with CSS approach
- Framework distribution (React/Vue/Vanilla)
- Component API demand

**Decision:** Proceed to Phase 2 if 70%+ users want components

### After Phase 2 (Week 6)

**Review metrics:**

- Component adoption rate
- TypeScript usage
- Bundle size concerns

**Decision:** Phase 3 npm package if 50%+ users prefer components

### After Phase 3 (Month 3)

**Review metrics:**

- Icons per app average
- Bundle size complaints
- Multi-color icon requests
- Performance issues

**Decision:** Phase 4 sprites if apps use 100+ icons consistently

---

## Success Metrics by Phase

### Phase 1 Success Criteria

- ✅ 10+ teams using icons successfully
- ✅ < 5 critical issues reported
- ✅ Clear user preference data collected
- ✅ Documentation clarity confirmed

### Phase 2 Success Criteria

- ✅ Component works in React, Vue, vanilla HTML
- ✅ 100% test coverage for icon component
- ✅ 80%+ TypeScript type coverage
- ✅ Storybook documentation complete
- ✅ Zero breaking changes from Phase 1

### Phase 3 Success Criteria

- ✅ npm packages published successfully
- ✅ 50+ weekly downloads within first month
- ✅ Both CDN and npm users satisfied
- ✅ < 3 critical bugs in first month
- ✅ Enterprise adoption (5+ companies)

### Phase 4 Success Criteria

- ✅ 20% bundle size reduction for heavy users
- ✅ No performance regressions
- ✅ Sprite adoption by 10%+ of users
- ✅ Multi-color icons working

---

## Risk Mitigation

### Risk: S3 Accessibility Issues

**Mitigation:** npm package provides self-hosted alternative

### Risk: Breaking Changes Between Phases

**Mitigation:** Always maintain backward compatibility, use feature detection

### Risk: TypeScript Type Maintenance

**Mitigation:** Auto-generate types from JSON in build pipeline

### Risk: Component Adoption Slower Than Expected

**Mitigation:** Keep CSS approach fully supported, don't force migration

### Risk: Bundle Size Complaints

**Mitigation:** Phase 4 sprites as optimization path

---

## Appendix: Key Code Snippets

### Auto-Generate Icon Types Script

```typescript
// scripts/generate-icon-types.ts
import fs from "fs";
import path from "path";
import icons from "../apps/boreal-docs/src/stories/Icons/icons/helpers/icons.json";

const iconNames = icons
  .map((icon) => icon.name.replace("bds-icon-", ""))
  .sort();

const output = `
// Auto-generated file - DO NOT EDIT
// Generated from icons.json on ${new Date().toISOString()}

export type IconName =
${iconNames.map((name) => `  | '${name}'`).join("\n")}
;

export const iconNames: readonly IconName[] = [
${iconNames.map((name) => `  '${name}',`).join("\n")}
] as const;

export const isValidIconName = (name: string): name is IconName => {
  return (iconNames as readonly string[]).includes(name);
};
`;

const outputPath = path.join(
  __dirname,
  "../packages/boreal-web-components/src/components/boreal-icon/icon-names.ts",
);

fs.writeFileSync(outputPath, output, "utf-8");
console.log(`✅ Generated types for ${iconNames.length} icons`);
```

### Copy S3 Assets Script

```typescript
// scripts/copy-icon-assets.ts
import fs from "fs";
import https from "https";
import path from "path";

const S3_BASE = "https://resources-borealds.s3.us-east-1.amazonaws.com/icons";
const VERSION = process.env.ICON_VERSION || "current";
const DIST_DIR = path.join(__dirname, "../dist/icons");

async function downloadFile(url: string, destination: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destination);
    https
      .get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(
            new Error(`Failed to download ${url}: ${response.statusCode}`),
          );
          return;
        }
        response.pipe(file);
        file.on("finish", () => {
          file.close();
          resolve();
        });
      })
      .on("error", reject);
  });
}

async function main() {
  if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
  }

  console.log(`📦 Downloading icon assets (version: ${VERSION})...`);

  // Download CSS
  const cssUrl = `${S3_BASE}/${VERSION}/boreal-styles.css`;
  const cssPath = path.join(DIST_DIR, "boreal-icons.css");
  await downloadFile(cssUrl, cssPath);
  console.log("✅ Downloaded CSS");

  // Parse CSS for font URLs and download fonts
  const css = fs.readFileSync(cssPath, "utf-8");
  const fontMatches = [...css.matchAll(/url\(['"]?([^'"]+\.woff2?)['"']?\)/g)];

  for (const [, fontPath] of fontMatches) {
    const fontUrl = fontPath.startsWith("http")
      ? fontPath
      : `${S3_BASE}/${VERSION}/${fontPath}`;

    const fontName = path.basename(fontPath);
    const fontDest = path.join(DIST_DIR, fontName);

    await downloadFile(fontUrl, fontDest);
    console.log(`✅ Downloaded ${fontName}`);
  }

  // Update CSS paths to local
  let updatedCss = css;
  for (const [match, fontPath] of fontMatches) {
    const fontName = path.basename(fontPath);
    updatedCss = updatedCss.replace(match, `url('./${fontName}')`);
  }
  fs.writeFileSync(cssPath, updatedCss);

  console.log("✅ All icon assets copied successfully");
}

main().catch(console.error);
```

---

## Recommended Next Steps

**Week 1:**

1. Update Icons.stories.tsx with new type naming (IconDisplayOptions)
2. Update argTypes descriptions to clarify CSS attributes
3. Add roadmap section to Icons.mdx
4. Create feedback survey for alpha users

**Week 2:** 5. Collect and analyze alpha feedback 6. Make decision on Phase 2 timing 7. If proceeding: Start BorealIcon component development

**Start building components (Button, Alert, Input) with the hybrid icon pattern NOW** - they'll work in Phase 1 and automatically upgrade in Phase 2.

---

**Document Owner:** Design System Team
**Last Updated:** January 23, 2026
**Next Review:** After Phase 1 completion (Week 2)

```
stories
  |-- icons
    |-- constants
      |-- prefix.ts
      |-- values.ts
    |-- helpers
      |-- getIcons.ts
      |-- icons.json
    |-- icons.stories.tsx
    |-- icons.mdx
utils
  |-- helpers.ts --> instead of disableControls.ts

```
