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
| Optional attribute | `value=${args.value \|\| nothing}` | String props that should be omitted entirely (not rendered as `attr=""`) when the arg is empty |
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

**Optional attributes:**

```ts
html`<bds-text-field value=${args.value || nothing} placeholder=${args.placeholder || nothing}></bds-text-field>`;
```

`nothing` behaves differently by position: in a **child position** (above) it suppresses a text/element node; in an **attribute position** (`attr=${...}`) it removes the attribute entirely rather than rendering `attr=""`. Use `args.value || nothing` for optional string args so the "Show code" snippet stays clean when the arg is empty. This is distinct from `?attr=${bool}` (boolean-attribute binding, table above) — different binding syntax, different purpose.

**`ifDefined` as an alternative to `|| nothing`:**

```ts
import { ifDefined } from "lit/directives/if-defined.js";

html`<bds-table subheading=${ifDefined(args.subheading)}></bds-table>`;
```

`ifDefined` removes the attribute only when the value is strictly `undefined` — unlike `value || nothing`, it does not also strip an explicit empty string. This is the better fit when `meta.args` leaves an optional prop's default as `undefined` (rather than `''`), since that's the only state that should omit the attribute. Prefer `ifDefined` for that case; prefer `args.value || nothing` when the arg's "unset" state is genuinely an empty string. Both are sanctioned — pick based on what the arg's default actually is.

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

## When `docs.source.code` is unavoidable — and how to keep it formatted

`parameters.docs.source.code` overrides the auto-generated Source panel with a literal string. Storybook only runs `docs.source.transform` (the `formatHtmlSource` pipeline above) when `code` is **absent** — an explicit `code` string is displayed verbatim, bypassing that pipeline entirely (verified against the installed `@storybook/addon-docs` source, `useCode` in `blocks.js`: it computes the transformed snippet but discards it whenever `sourceParameters.code !== undefined`).

**Only reach for `code:` when the real `render` output would fail to teach the API correctly.** Concretely:

- The story demonstrates a JS-only prop or event (`.data=`, `.formatter=`, `@bdsSort=${...}`) — Lit's attribute/property/event bindings never appear in the rendered DOM's `outerHTML`, so the auto-transform silently omits them. This is the single most common reason `bds-table.stories.ts` overrides `code`.
- The real render uses a `Math.random()`-based id to avoid cross-story collisions — the docs should show a stable, copy-pasteable id like `#my-table` instead.
- The real render wraps setup in a Storybook/Lit-specific workaround (`componentOnReady().then(...)`, `requestAnimationFrame(...)`) that a real consumer never needs — the docs should show the direct, real-world call.

If none of those apply, don't add `code:` — let the real render and `formatHtmlSource` stay the single source of truth. Never write a `code:` override "just for consistency" or "just because a neighboring story has one" — every override is a second copy of behavior that must be kept in sync by hand, and un-synced copies are exactly the failure mode that has already shipped a live bug in this codebase (a story's interactive behavior broke while its `code:` string kept showing the old, working version).

**Formatting a `code:` string.** Because it bypasses `transform`, it gets none of `formatHtmlSource`'s formatting for free — left as a hand-typed literal, it drifts from the visual convention (multi-line attributes, trailing commas, arrow-function spacing) that every non-overridden story already shows via the transform. Fix this with Prettier's built-in embedded-language pragma — no custom script, no Storybook config, works automatically via the project's normal `pnpm format` / `prettier --write`:

```ts
const myStoryDocsSource = /* HTML */ `<bds-table id="my-table" subheading="Users">
  <bds-table-column col-key="name" label="Name"></bds-table-column>
</bds-table>

<script>
  document.querySelector('#my-table').data = [...];
</script>`;

export const MyStory: Story = {
  parameters: {
    docs: { source: { code: myStoryDocsSource } },
  },
  render: () => html`...`,
};
```

Two rules for this to work correctly:

1. **The `/* HTML */` comment must immediately precede the template literal.** Prettier's embedded-HTML formatter (also used for `lit-html`-tagged templates) triggers on this exact comment pragma, regardless of whether the literal is tagged — confirmed directly in `prettier/plugins/estree.mjs`'s `Do()`/`rn()` functions.
2. **Always hoist the string to a top-level `const` right before the story, never write it inline inside `parameters.docs.source.code`.** Prettier indents embedded content to match the *surrounding* nesting depth — inline inside `{ parameters: { docs: { source: { code: \`...\` } } } }` (5–6 levels deep), that indentation becomes literal leading whitespace baked into the string itself, which then renders as visibly over-indented code in the actual Docs panel. Hoisted to a top-level `const` (column 0, same pattern already used for `iconStyles`, `makeBasicTableRender`, etc.), the embedded content formats flush-left instead — matching how the Docs panel is supposed to look.

This pattern (pragma + top-level hoist) is standard Prettier behavior, not a project-specific tool — it applies to any `.stories.ts` file the same way, with zero setup beyond following the two rules above.

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

### MDX include name collisions across sub-components

When one `.stories.ts` file documents several related custom elements in a single shared `meta` (e.g. `bds-table`, `bds-table-column`, `bds-table-column-group`), all `<ArgTypes include={[...]}>` blocks for those elements resolve against the same flat `meta.argTypes` object. If two sub-components have a prop with the same displayed name (e.g. both `bds-table-column` and `bds-table-column-group` have `label`/`info`, with different meanings), you cannot add a second `label`/`info` entry with a `name:` override to disambiguate them — that recreates the exact collision `include` is meant to solve.

**Root cause**, read directly from the installed package (`node_modules/.pnpm/storybook@10.2.8*/node_modules/storybook/dist/_browser-chunks/chunk-2N4WE3KZ.js`, the real source behind `storybook/preview-api`'s `filterArgTypes`, which is what `<ArgTypes include={[...]}>` calls under the hood):

```js
filterArgTypes = (argTypes, include, exclude) => !include && !exclude ? argTypes : argTypes && pickBy(argTypes, (argType, key) => {
  let name = argType.name || key.toString();
  return !!(!include || matches(name, include)) && (!exclude || !matches(name, exclude));
});
```

`include` matches against each entry's *resolved display name* (`argType.name`, falling back to the object key) — not the raw JS object key. Two entries that both resolve to the same name can never be selectively addressed by `include`, regardless of their underlying object keys. This is a structural Storybook constraint, not a bug in this codebase's usage. Also confirmed via `@storybook/addon-docs`'s `blocks.d.ts`: `ArgTypesProps` always resolves through `of` — there is no way to pass a raw, standalone `argTypes` object bypassing `meta`.

**Fix — CSF3 per-story `argTypes` override.** A Storybook *story* (not just the shared `meta`) can declare its own local `argTypes` property (sibling to `parameters`/`render`) that merges over, and wins against, `meta.argTypes` for that one story's resolved context only — it does not mutate the shared object other stories/components read from.

Applied for `bds-table-column-group` in `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`: the `GroupedColumns` story declares its own `argTypes.label`/`argTypes.info` with group-specific descriptions. The MDX file then points its `bds-table-column-group` Properties block at that story, not at the whole module:

```mdx
<ArgTypes of={BdsTableStories.GroupedColumns} include={['label', 'info']} />
```

instead of `of={BdsTableStories}`. Verified live in Storybook: the `bds-table-column-group` table shows the group-specific descriptions, `bds-table-column`'s own table is unaffected, and there is no bleed-over in either direction.

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
- **Never give two `argTypes` entries a matching resolved `name` (via a `name:` override or otherwise) expecting `include` to tell them apart** — `filterArgTypes` matches on resolved name across the whole shared `meta.argTypes` object, not per sub-component; see "MDX include name collisions across sub-components" above for the per-story `argTypes` override that actually resolves this.

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
