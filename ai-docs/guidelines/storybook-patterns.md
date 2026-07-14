# Storybook Patterns

Verified patterns for story and MDX documentation files in `apps/boreal-docs`. All examples are derived from actual files — `bds-button.stories.ts`, `bds-text-field.stories.ts`, and their paired MDX files.

---

## File organisation

Each component has its own directory containing exactly two documentation files:

```
apps/boreal-docs/src/stories/<category>/<bds-component>/
├── <bds-component>.stories.ts   # Story definitions and interactive examples
└── <bds-component>.mdx          # Documentation narrative and Canvas layout
```

Use `.stories.ts` (not `.tsx`) unless the story file itself renders JSX — Lit's `html` tagged template does not require JSX compilation. Use `.stories.tsx` only when the render function returns actual JSX.

---

## Story file structure

### 1. StoryArgs type

Define a named `StoryArgs` type that lists every argument the stories use — both component props and slot/event helpers. This type drives the `argTypes` configuration and ensures TypeScript catches mismatches.

```ts
type StoryArgs = {
  // component props
  variant: ButtonVariant;
  disabled: boolean;
  // slot helpers (Storybook control that injects slot content)
  slotDefault: string;
  // event callback
  onBdsClick: () => void;
};

type Story = BorealStory<StoryArgs>;
```

`type Story = BorealStory<StoryArgs>` is declared here, before the meta, so each export can use the short form `export const Default: Story = { ... }`.

### 2. Meta object

```ts
import type { BorealStory, BorealStoryMeta } from '@/types/stories';
import { html } from 'lit';
import { formatHtmlSource } from '@/utils/formatters';

const meta = {
  title: 'Actions/Button',     // Storybook sidebar path: Category/ComponentName
  component: 'bds-button',     // Web component tag name (no class, no import)
  parameters: {
    docs: {
      source: {
        excludeDecorators: true,
        transform: formatHtmlSource,  // Strips <style> blocks, formats HTML with Prettier
      },
    },
  },
  argTypes: { ... },
  args: { ... },
} satisfies BorealStoryMeta<StoryArgs>;

export default meta;
```

`parameters` is required by `BorealStoryMeta`. The `formatHtmlSource` transform strips decorators' `<style>` tags and runs Prettier with `singleAttributePerLine: true` — giving clean, copyable HTML in the Source panel.

### 3. ArgTypes

Each entry in `argTypes` must specify `control`, `description`, and the full `table` shape:

```ts
argTypes: {
  variant: {
    control: { type: 'select' },
    options: ['default', 'outline', 'plain'],
    description: 'Visual style of the button.',
    table: {
      category: 'Core',
      type: { summary: `'default' | 'outline' | 'plain'` },
      defaultValue: { summary: 'default' },
    },
  },
  disabled: {
    control: 'boolean',
    description: 'Prevents user interaction when true.',
    table: {
      category: 'Core',
      type: { summary: 'boolean' },
      defaultValue: { summary: 'false' },
    },
  },
  slotDefault: {
    control: 'text',
    name: 'slot="default"',              // Overrides the displayed name in the Controls panel
    description: 'Content of the button.',
    table: {
      category: 'Slots',
      type: { summary: 'HTMLElement' },
      defaultValue: { summary: '' },
    },
  },
  onBdsClick: {
    action: 'clicked: bdsClick emitted',
    description: 'Callback fired when the button is clicked.',
    table: {
      category: 'Events',
    },
  },
},
```

**Category conventions:**

| Category | Contains                                                    |
| -------- | ----------------------------------------------------------- |
| `Core`   | Primary component props that affect behaviour or appearance |
| `Slots`  | Slot controls injected into the rendered template           |
| `Events` | Event callback handlers                                     |
| `a11y`   | Accessibility-only props (`label`, `aria-*`)                |

### 4. Shared render function

Extract the render logic into a named arrow function typed as `Story['render']`. Every story that renders the component the same way can then share it:

```ts
const renderButton: Story["render"] = (args) => html`
  <bds-button
    variant=${args.variant}
    ?disabled=${args.disabled}
    @bdsClick=${args.onBdsClick}
  >
    ${args.slotDefault}
  </bds-button>
`;
```

Stories override only the `args` they differ on:

```ts
/** Button default variant. */
export const Default: Story = {
  args: { variant: "default" },
  render: renderButton,
};

/** Button with outline variant. */
export const OutlineButton: Story = {
  args: { variant: "outline" },
  render: renderButton,
};
```

Add a JSDoc comment to every named story export — it becomes the story's description in the Docs panel.

---

## Lit template patterns

Stories use Lit's `html` tagged template literal. The component element is a standard web component — no framework wrapper needed.

| Binding           | Syntax                         | Use for                                                  |
| ----------------- | ------------------------------ | -------------------------------------------------------- |
| String / enum     | `variant=${args.variant}`      | Reflected string props                                   |
| Boolean attribute | `?disabled=${args.disabled}`   | Props that map to boolean HTML attributes                |
| JS property       | `.options=${args.options}`     | Objects, arrays, non-reflected props                     |
| Event listener    | `@bdsClick=${args.onBdsClick}` | Custom events (the `@` prefix equals `addEventListener`) |

**Conditional slot content:**

```ts
import { nothing } from "lit";

html`
  <bds-button>
    ${args.slotIcon
      ? html`<span slot="icon"><em class="bds-icon-settings"></em></span>`
      : nothing}
    ${args.slotDefault}
  </bds-button>
`;
```

Use `nothing` (not `undefined` or `''`) to suppress a slot — Lit renders `nothing` as an empty text node with no HTML output.

**Icon font styles:**

When a story needs the icon font, inject it via a Lit `css` tagged template inside the template:

```ts
import { html, css } from "lit";

const styles = css`
  @import url("https://resources-borealds.s3.us-east-1.amazonaws.com/icons/current/boreal-styles.css");
`;

const renderButton: Story["render"] = (args) => html`
  <style>
    ${styles}
  </style>
  <bds-button>${args.slotDefault}</bds-button>
`;
```

The `formatHtmlSource` transform strips `<style>` blocks before showing the source snippet, so these styles never appear in the "Show code" panel.

---

## MDX documentation structure

Each `.mdx` file is the primary documentation page for the component. Import from `@storybook/addon-docs/blocks` (not `@storybook/blocks`).

```mdx
import {
  Meta,
  Title,
  Subtitle,
  Canvas,
  ArgTypes,
  Description,
} from "@storybook/addon-docs/blocks";
import LinkTo from "@storybook/addon-links/react";
import { Callout, StoryName, DocsLinkTo } from "@/components/docs";
import * as BdsButtonStories from "./bds-button.stories";

<Meta of={BdsButtonStories} />

<Title of={BdsButtonStories} />

One or two sentences describing what the component is and its primary purpose.
```

### Standard subtitle order

Use this sequence. Omit sections that do not apply to the component.

| Subtitle                       | Required                           | Notes                                                     |
| ------------------------------ | ---------------------------------- | --------------------------------------------------------- |
| `How to use it`                | Always                             | Numbered steps: register, add tag, minimal HTML snippet   |
| `When to use it`               | Always                             | Bullet list of use cases; optional "Avoid when:"          |
| `Component preview`            | Always                             | Tip Callout + `<Canvas>` blocks for main variants         |
| **`## States`** (H2)           | When component has multiple states | Disabled, error, loading, readonly                        |
| **`## Form integration`** (H2) | Form components only               | Association, validation timing, interactive example       |
| `Accessibility`                | Always                             | ARIA attributes, keyboard navigation, screen reader notes |
| `Properties`                   | Always                             | `<ArgTypes of={BdsXxxStories} />`                         |
| `Interact with the component`  | Always                             | `<LinkTo>` pointing to the Default canvas story           |

> Note: "Component preview" and "States" sometimes use `<Subtitle>` and sometimes `## H2` headings depending on how prominent the section needs to be. Follow the precedent of the nearest existing component in the same category.

### MDX `include` completeness — silent-drop pitfall

`<ArgTypes of={BdsXxxStories} include={[...]}>` filters to only the names listed in `include`. If a name in that array has no matching key in the `.stories.ts` `argTypes` object, Storybook does not error or warn — it simply renders no row for it. This makes it easy to believe a prop/event is documented (it's right there in the `include` array) when it silently isn't.

**Before considering a component's docs complete, cross-check three lists against each other, not just two:**

1. Every `@Prop()`/`@Event()` in the component's `.tsx`.
2. Every key in `argTypes` in `.stories.ts`.
3. Every string in the MDX file's `<ArgTypes include={[...]}>` array(s) — components with sub-parts (e.g. `bds-table` + `bds-table-column`) may have more than one `<ArgTypes>` block, each with its own `include`.

All three must match. A name present in (3) but missing from (2) is the specific failure mode that shipped undetected in `bds-table` (EOA-14935) — `selected-rows`, `searchable`, and `selectedRowsChange` were listed in the MDX `include` array but had no `argTypes` entry, so the props/events table silently omitted all three despite looking complete in a source diff.

**Verification:** don't just review the diff — run `pnpm dev:docs` and visually confirm each prop/event row actually renders in the "Properties" panel for the component you touched.

### Canvas blocks

Reference story exports by name. Optionally add `<Description of={...} />` before the Canvas to show the story's JSDoc comment:

```mdx
### Default

<Description of={BdsButtonStories.Default} />
<Canvas
  className="bds-doc__canvas--with-background"
  of={BdsButtonStories.Default}
/>

### Outline

<Description of={BdsButtonStories.OutlineButton} />
<Canvas of={BdsButtonStories.OutlineButton} />
```

Use `className='bds-doc__canvas--with-background'` on the first story Canvas when the component needs a background for visibility (e.g. white components on a white page).

### Callout variants

```mdx
<Callout variant="tip" icon="💡">
  Click the **Show code** button in the bottom-right corner of the Canvas to
  copy the snippet.
</Callout>

<Callout variant="info" icon="ℹ️">
  Using React or Vue? See the{" "}
  <DocsLinkTo title="Framework Integration">
    Framework Integration guide
  </DocsLinkTo>
  .
</Callout>
```

Available variants: `tip`, `info`, `warning`, `error`.

### Table of contents (optional)

For complex components with many sections, add a Markdown link list immediately after the description. Use anchor IDs that match Storybook's heading-to-anchor conversion:

```mdx
<Subtitle>Table of contents</Subtitle>

- [How to use it](#how-to-use-it)
- [When to use it](#when-to-use-it)
- [Component preview](#component-preview)
- [States](#states)
- [Form integration](#form-integration)
- [Accessibility](#accessibility)
- [Properties](#properties)
- [Interact with the component](#interact-with-the-component)
```

Omit the table of contents for simple components with fewer than four sections.

---

## What NOT to do

- **Never use `tags: ['autodocs']`** — creates a generic, uncustomisable API dump. Always write a dedicated `.mdx` file instead.
- **Never import from `@storybook/blocks`** — use `@storybook/addon-docs/blocks` (this is what the project installs).
- **Never use `ColibriStoryMeta` / `ColibriStory`** — these are from a predecessor design system; the correct types are `BorealStoryMeta` / `BorealStory` from `@/types/stories`.
- **Never omit `parameters` from the meta** — `BorealStoryMeta` makes it required; always include the `docs.source` block with `formatHtmlSource`.
- **Never add a name to an MDX `<ArgTypes include={[...]}>` array without also adding a matching `argTypes` entry in `.stories.ts`** — see "MDX `include` completeness" above. This is the single most common way a documented-looking prop/event silently never renders.

---

## Hiding stories from navigation

Use `tags: ['!dev']` to exclude a story from the sidebar while keeping it accessible for embedding in an MDX `<Canvas>` block:

```ts
export const InternalExample: Story = {
  args: {
    variant: "internal",
  },
  render: renderComponent,
  tags: ["!dev"], // Hidden from sidebar, still reachable from MDX
};
```

Apply `tags: ['!dev']` when:

- The story is only meant to be embedded in an MDX `<Canvas>` block.
- It represents an edge case or internal usage that would clutter the component's navigation entry.
- It is a template or rendering helper that isn't useful as a standalone interactive story.

**Embedding in MDX:**

```mdx
import * as ButtonStories from "./bds-button.stories";

<Canvas of={ButtonStories.InternalExample} />
```
