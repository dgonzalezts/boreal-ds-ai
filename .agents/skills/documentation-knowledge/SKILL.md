---
name: documentation-knowledge
description: Domain knowledge for writing Storybook stories and MDX documentation for Boreal DS components. Covers action wiring, source snippet overrides for non-primitive props, and Vite build quirks. Load proactively when writing stories, MDX docs, or JSDoc.
---

# Documentation Knowledge — Boreal DS

## Primary Reference

[`ai-docs/guidelines/development-standards.md`](../../../ai-docs/guidelines/development-standards.md) is the project's primary rules document. Read §5 (documentation strategy, JSDoc/CEM authoring, Storybook conventions) before writing stories or MDX. This skill provides scope-specific patterns and gotchas that complement — not replace — those rules.

**Directional rule:** procedures and patterns (how to wire actions, how to override source snippets) → live here. Rules, rationale, and constraints (JSDoc placement, CEM generation behavior) → live in `development-standards.md`.

Also read before writing docs:

- `ai-docs/guidelines/storybook-patterns.md` — canonical story structure, argTypes rules, and the two-type docs/story component rule
- `ai-docs/guidelines/jsdoc-template.md` — JSDoc on Stencil components: what to write, where, and what the CEM plugin generates automatically
- `ai-docs/guidelines/plop-generator-learnings.md` — Plop.js story generator: critical issues, Handlebars template patterns, and common pitfalls

---

## Action Wiring for Custom Events — Four-Level Pattern

Wiring `action()` to custom DOM events requires all four levels to be consistent. Getting any one wrong produces silent failures or unreadable Actions panel output.

### 1. Type declaration

```typescript
type StoryArgs = {
  bdsChange?: (payload: {
    detail: string;
    from: string;
    bubbles: boolean;
  }) => void;
};
```

The payload type must match exactly what the arrow function in the template binding extracts.

### 2. `argTypes`

```typescript
argTypes: {
  bdsChange: {
    description: 'Emitted when the selected value changes. `detail` carries the value key.',
    table: {
      category: 'Events',
      type: { summary: 'CustomEvent<string>' },
    },
    // Do NOT add `action: 'bdsChange'` here — legacy shorthand, silently ignored
  },
}
```

### 3. `args`

```typescript
import { action } from 'storybook/actions';

args: {
  bdsChange: action('bdsChange'),
},
```

The modern alternative is `fn().mockName('bdsChange')` from `storybook/test` — works as a Jest/Vitest spy inside `play()` interaction tests.

### 4. Template event binding

```typescript
@bdsChange=${(e: CustomEvent<string>) => args.bdsChange?.({ detail: e.detail, from: (e.target as Element).localName, bubbles: e.bubbles })}
```

The `?.` optional chain is required — `args.bdsChange` is `undefined` in snapshot tests.

**Why the arrow function wrapper is mandatory:** Direct binding `@bdsChange=${args.bdsChange}` passes the raw `CustomEvent` to `action()`. Storybook's serialiser reads only own enumerable keys — `detail`, `target`, `bubbles` are prototype accessor properties on `Event.prototype` and produce `{ __isClassInstance__: true, __className__: "CustomEvent" }`. The arrow function wrapper extracts needed data into a plain serialisable object.

**For standalone components** (single event source, no composite), pass `e.detail` directly:

```typescript
@bdsChange=${(e: CustomEvent<string>) => args.bdsChange?.(e.detail)}
```

---

## Props/Events Completeness Check — run before finishing any doc task

The rule (`development-standards.md` §5 "ArgTypes Rules") is that every `@Prop()`/`@Event()` must have an `argTypes` entry, no exceptions for props that feel JS-only or internal. This procedure is how to actually verify it, because the failure mode is silent: `<ArgTypes include={[...]}>` drops any name without a matching `argTypes` key with no error (see `storybook-patterns.md`'s "MDX `include` completeness" section). A source diff that "looks complete" can still ship a props table missing rows — this happened for real on `bds-table` (EOA-14935): three names were already in the MDX `include` array with no `argTypes` entry behind them, and nothing caught it until PR review.

Cross-check three lists against each other for every component you touch, not just two:

```bash
# 1. Every @Prop()/@Event() in the component source
grep -n "@Prop\|@Event" packages/boreal-web-components/src/components/**/<bds-component>.tsx

# 2. Every key in argTypes (.stories.ts) — read the file, don't just grep;
#    keys can be renamed via `name:` (e.g. `selectedRows` -> `selected-rows`)

# 3. Every string inside <ArgTypes include={[...]}> in the .mdx file —
#    check every <ArgTypes> block if the component has sub-parts
#    (e.g. bds-table + bds-table-column each get their own block)
```

All three must agree. Specifically watch for:

- A prop/event that exists in the `.tsx` but is missing from **both** (2) and (3) — the plain "forgot to document it" case.
- A name present in (3) but absent from (2) — the silent-drop case; `include` referencing a name is not evidence the row renders.
- A prop that "does nothing yet" (e.g. deferred/stubbed pending design specs) — still document it, but say so explicitly in the description so consumers aren't left guessing why nothing happens when they set it.

**Do not consider the task done from reading the diff.** Run `pnpm dev:docs` and visually confirm every prop/event you added actually renders as a row in the component's "Properties" panel.

---

## Source Snippet Override for Non-Primitive Props

When a story uses Lit property binding (`.propName=${value}`) for a non-primitive prop (array, object), the auto-generated "Show code" snippet is incomplete — Storybook only sees the serialised DOM and cannot reconstruct the JS property assignment.

**When this is required:**

1. A `@Prop()` has no `reflect: true`
2. The prop type is non-primitive (array, object, function)
3. The story uses Lit property binding (`.propName=${...}`)

**Fix — override with `parameters.docs.source.code`, as a top-level `const` tagged with the `/* HTML */` pragma:**

```typescript
const withValueDocsSource = /* HTML */ `<bds-checkbox-group id="my-group">
  <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
</bds-checkbox-group>

<script>
  const group = document.querySelector('#my-group');
  group.value = ['Option-A', 'Option-C'];
</script>`;

export const WithValue: BorealStory = {
  args: { value: ["Option-A", "Option-C"] },
  render: (args) => html`
    <bds-checkbox-group .value=${args.value}>
      <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
    </bds-checkbox-group>
  `,
  parameters: {
    docs: {
      source: { code: withValueDocsSource },
    },
  },
};
```

Pattern: add a unique `id`, show complete markup, include a `<script>` block with the DOM property assignment.

**Always write the override this way — never inline inside `parameters.docs.source.code`.** An explicit `code:` string bypasses `docs.source.transform` (the `formatHtmlSource`/Prettier pipeline) entirely, so it gets none of that formatting for free unless you provide it yourself. Two rules, both required:

1. **Precede the template literal with `/* HTML */`.** Prettier's embedded-language formatter recognizes this exact pragma on any plain (untagged) template literal and formats its contents as HTML — confirmed against the installed `prettier` package's `estree` plugin (`Do()`/`rn()` in `plugins/estree.mjs`). No custom script or Storybook config needed; the project's existing `pnpm format` / pre-commit `lint-staged` hook picks it up automatically.
2. **Hoist it to a top-level `const` right before the story, never write it inline inside the nested `parameters` object.** Prettier indents embedded content to match its surrounding nesting depth — 5–6 levels deep inside `parameters.docs.source.code`, that indentation becomes literal leading whitespace baked into the string, rendering as visibly over-indented code in the actual Docs panel. At the top level (column 0), it formats flush-left as intended.

Do not override when the prop reflects (`reflect: true`) and is primitive — the auto-generated snippet will be correct. Full rationale and a worked before/after: `ai-docs/guidelines/storybook-patterns.md` § "When `docs.source.code` is unavoidable — and how to keep it formatted".

---

## ArgTypes Name Collisions Across Sub-Components

When a single `.stories.ts` file's shared `meta` documents several related custom elements (e.g. `bds-table`, `bds-table-column`, `bds-table-column-group`), `<ArgTypes include={[...]}>` filters against the whole flat `meta.argTypes` object by resolved display name — never by the raw object key, and never scoped to "the sub-component this block documents." Two sub-components with a same-named prop (e.g. both have `label`) cannot be disambiguated by giving the second one an entry with a `name:` override — that recreates the exact collision `include` exists to solve. Confirmed against installed `storybook@10.2.8`'s `filterArgTypes` source.

**Fix:** declare a CSF3 per-story `argTypes` override (a property sibling to `parameters`/`render` on the story itself) with the sub-component-specific descriptions, then point the MDX block at that story — `<ArgTypes of={BdsXxxStories.SomeStory} include={[...]} />` — instead of at the whole module. Full write-up with the `bds-table-column-group` worked example: `ai-docs/guidelines/storybook-patterns.md` § "MDX include name collisions across sub-components"; memory entry: `.agents/memory/storybook-argtypes-name-collision.md`.

---

## Storybook + Vite Quirks

### Vite glob patterns in package exports

Vite does not support glob patterns in `package.json` exports. `@telesign/boreal-web-components/css/*` cannot be resolved automatically. Two aliases are registered in `viteFinal` in `apps/boreal-docs/.storybook/main.ts` to work around this — do not remove them.

### ESM-ES5 dynamic import warnings

Noisy warnings about dynamic imports of ESM modules are suppressed in two places in `apps/boreal-docs/.storybook/main.ts`:

- **Dev**: via a custom `createLogger` filtering `logger.warn` when the message includes both `'esm-es5'` and `'dynamic import'`
- **Prod build**: via `rollupOptions.onwarn` filtering when `warning.plugin === 'vite:import-analysis'` and `warning.id` includes `'esm-es5'`

These warnings are harmless. Do not remove the suppressions.
