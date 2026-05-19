---
description: Documentation guidelines for Boreal DS. Load these instructions when writing or reviewing Storybook story files (.stories.ts), MDX documentation files (.mdx), or any content inside apps/boreal-docs.
applyTo: "apps/boreal-docs/**"
---

# Documentation Instructions — Boreal DS

## Overview

Every Boreal DS component requires two documentation files, both scaffolded via `pnpm generate:story`:

- `bds-[name].stories.ts` — interactive stories rendered in Storybook's Canvas
- `bds-[name].mdx` — prose documentation rendered in Storybook's Docs tab

All stories use **Lit 3.x** (`html` tagged template literals) for rendering. React and Vue are never used inside story or MDX files directly.

---

## Story File Structure

Every `.stories.ts` file must follow this five-section order:

```typescript
// 1. Imports
import { html, css } from "lit";
import { formatHtmlSource } from "@/utils/formatters";
import type { BorealStory, BorealStoryMeta } from "@/types/stories";

// 2. Type definitions
type StoryArgs = {
  variant: "default" | "ghost";
  disabled: boolean;
};
type Story = BorealStory<StoryArgs>;

// 3. Meta object — always uses satisfies BorealStoryMeta
const meta = {
  title: "Actions/Button",
  component: "bds-button",
  parameters: {
    docs: {
      source: { excludeDecorators: true, transform: formatHtmlSource },
    },
  },
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "ghost", "outline", "flat"],
      description: "Visual variant of the button",
      table: {
        category: "Appearance",
        type: { summary: "ButtonVariant" },
        defaultValue: { summary: "default" },
      },
    },
    disabled: {
      control: "boolean",
      description: "Disables the button",
      table: {
        category: "State",
        type: { summary: "boolean" },
        defaultValue: { summary: "false" },
      },
    },
  },
  args: {
    variant: "default",
    disabled: false,
  },
} satisfies BorealStoryMeta<StoryArgs>;

// 4. Styles block (delete if no story-scoped styles are needed)
const styles = css`
  .demo-wrapper {
    padding: 16px;
  }
`;

export default meta;

// 5. Story exports — shared render function + named variants
const renderButton: Story["render"] = (args) => html`
  <bds-button variant=${args.variant} ?disabled=${args.disabled}>
    Label
  </bds-button>
`;

/** Default state of the button */
export const Default: Story = { render: renderButton };

/** Disabled button */
export const Disabled: Story = {
  args: { disabled: true },
  render: renderButton,
};
```

### Key rules for story files

- **ArgTypes order controls panel order.** Arrange properties in `argTypes` in the exact order you want them to appear in the controls panel — no sorting parameter exists.
- **Always provide defaults in both `args` and `table.defaultValue`.** An `args` value without a `table.defaultValue` produces an empty defaults column in docs.
- **Storybook-only controls** (e.g. slot toggles): add `**Storybook control only, not a component prop.**` to the `description`. Place them last in `args`. Use `table: { disable: true }` to hide them from the docs props table.
- **Conditional controls**: use the `if` property in `argTypes` to show a control only when relevant:
  ```typescript
  maxCount: {
    if: { arg: 'showBadge', eq: true },
  }
  ```
  Set a "hidden" default in `args` (e.g. `maxCount: 0`) so the control is invisible by default.
- **Layout parameter**: set `parameters.layout` to control Canvas positioning. Use `'centered'` for small atoms, `'fullscreen'` for navigation/layout components, and `'padded'` (default) for everything else.
- **Hiding stories from navigation**: add `tags: ['!dev']` to any story that should appear only when embedded in MDX, not in the sidebar.
- **Excluding non-story exports**: use `excludeStories` in the meta object for exported template functions or mock data that are not stories.

### Property binding conventions

Use HTML attribute syntax (not property binding) for all `reflect: true` props, so attributes appear in the generated code snippets:

```typescript
// ✅ Correct — shows in code snippets
html`<bds-select value=${args.value || nothing}></bds-select>`;

// ❌ Incorrect — hidden from code snippets
html`<bds-select .value=${args.value}></bds-select>`;
```

Use the `nothing` literal from Lit when a prop is optional and should produce no attribute when unset:

```typescript
import { nothing } from "lit";
html`<bds-button label=${args.label || nothing}></bds-button>`;
```

---

## MDX Documentation Structure

Every `bds-[name].mdx` file must include the following sections in order:

````mdx
import {
  Meta,
  Stories,
  ArgTypes,
  Title,
  Subtitle,
} from "@storybook/addon-docs/blocks";
import LinkTo from "@storybook/addon-links/react";
import { StoryName, Callout } from "@/components/docs";
import * as BdsButtonStories from "./bds-button.stories";

<Meta of={BdsButtonStories} />
<Title of={BdsButtonStories} />

Brief description of the component's purpose.

<Subtitle>How to use it</Subtitle>

1. Install and import:

```ts
import "@telesign/boreal-web-components/bds-button";
```
````

2. Use in HTML:

```html
<bds-button variant="default">Label</bds-button>
```

<Subtitle>When to use it</Subtitle>

Use `bds-button` when...

<Subtitle>Component preview</Subtitle>

<Callout variant="tip" icon="💡">
  Click **Show code** in any preview snippet to copy the ready-to-use markup.
</Callout>

<Stories />

<Subtitle>Accessibility</Subtitle>

- **ARIA role**: `button`
- **Keyboard**: `Tab` to focus, `Enter` or `Space` to activate, `Escape` to cancel where applicable
- **Screen reader**: announces label and state (disabled)

<Subtitle>Properties</Subtitle>

<ArgTypes of={BdsButtonStories} />

<Subtitle>Interact with the component</Subtitle>

Navigate to the <LinkTo title={BdsButtonStories.default.title} story="default">Default</LinkTo> story to test controls, actions, and accessibility checks.

### Key rules for MDX files

- **Always use `<LinkTo>` for cross-story links** — never hardcode `/story/...` URLs. When linking to a story in the same file: `<LinkTo title={ComponentStories.default.title} story="default">`. When linking to another component, import its meta: `import * as OtherStories from './bds-other.stories'` then `<LinkTo title={OtherStories.default.title} story="default">`.
- **Usage examples must be copy-paste ready.** Every code block must produce valid, working HTML.
- **The accessibility section is mandatory.** Document: ARIA role, keyboard interactions (Tab, Enter, Escape, Arrow keys), and screen reader announcements.
- **Use `<Callout>` from `@/components/docs`** for tips, warnings, or important notes — do not use blockquotes.
- **Use `<Stories />` (automatic mode) by default.** Switch to manual `<Canvas of={Stories.Variant} />` only when specific ordering or annotation is needed.
- **Do not use React components in MDX** other than the blocks imported from `@storybook/addon-docs/blocks`, `@storybook/addon-links`, and `@/components/docs`. All interactive previews use the Storybook rendering pipeline.

---

## Two-Type Documentation Component Rule

| Type            | Location                                 | Framework              | Used in            |
| --------------- | ---------------------------------------- | ---------------------- | ------------------ |
| Docs component  | `apps/boreal-docs/src/components/docs/`  | React 19 + CSS Modules | MDX files only     |
| Story component | `apps/boreal-docs/src/components/story/` | Lit 3                  | `.stories.ts` only |

Never use a docs component inside a story Canvas, and never use a story component inside an MDX page.

---

## Common Mistakes to Avoid

- **Mixing argTypes order with category groups.** The panel respects `argTypes` key order regardless of category assignment.
- **Using empty string as a default.** `args: { variant: '' }` breaks controls that expect a valid option. Always use a real default value.
- **Property binding for `reflect: true` props.** Use attribute syntax (`variant=${args.variant}`) not property binding (`.variant=${args.variant}`) so the value appears in code snippets.
- **Forgetting `nothing` for optional props.** Without it, `undefined` renders as the string `"undefined"` in templates.
- **Using `<Canvas>` without importing it.** When in automatic mode (`<Stories />`), `<Canvas>` is not needed and its import will cause an error.
- **Hardcoding story navigation links.** Always use `<LinkTo>` so links survive title renames.

---

## JSDoc Requirements

Add JSDoc comments to every named story export:

```typescript
/**
 * Button in its default configuration. Demonstrates the primary color and medium size.
 */
export const Default: Story = { render: renderButton };

/**
 * Disabled state — the button is non-interactive and aria-disabled is set.
 */
export const Disabled: Story = {
  args: { disabled: true },
  render: renderButton,
};
```

Do not add JSDoc to the meta object, the `StoryArgs` type, or internal render functions.
