---
name: documentation-knowledge
description: Domain knowledge for writing Storybook stories and MDX documentation for Boreal DS components. Covers action wiring, source snippet overrides for non-primitive props, and Vite build quirks. Load proactively when writing stories, MDX docs, or JSDoc.
---

# Documentation Knowledge — Boreal DS

Primary references (read before writing docs):

- `ai-docs/guidelines/storybook-patterns.md` — canonical story structure and argTypes rules
- `ai-docs/guidelines/jsdoc-template.md` — JSDoc on Stencil components: what to write, where, and what the CEM plugin generates automatically
- `ai-docs/guidelines/plop-generator-learnings.md` — Plop.js story generator: critical issues, Handlebars template patterns, and common pitfalls
- `ai-docs/guidelines/storybook-patterns.md` — two-type docs/story component rule, MDX section requirements

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

## Source Snippet Override for Non-Primitive Props

When a story uses Lit property binding (`.propName=${value}`) for a non-primitive prop (array, object), the auto-generated "Show code" snippet is incomplete — Storybook only sees the serialised DOM and cannot reconstruct the JS property assignment.

**When this is required:**

1. A `@Prop()` has no `reflect: true`
2. The prop type is non-primitive (array, object, function)
3. The story uses Lit property binding (`.propName=${...}`)

**Fix — override with `parameters.docs.source.code`:**

```typescript
export const WithValue: BorealStory = {
  args: { value: ["Option-A", "Option-C"] },
  render: (args) => html`
    <bds-checkbox-group .value=${args.value}>
      <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
    </bds-checkbox-group>
  `,
  parameters: {
    docs: {
      source: {
        code: `<bds-checkbox-group id="my-group">
  <bds-checkbox-button value="Option-A">Option A</bds-checkbox-button>
</bds-checkbox-group>

<script>
  const group = document.querySelector('#my-group');
  group.value = ['Option-A', 'Option-C'];
</script>`,
      },
    },
  },
};
```

Pattern: add a unique `id`, show complete markup, include a `<script>` block with the DOM property assignment.

Do not override when the prop reflects (`reflect: true`) and is primitive — the auto-generated snippet will be correct.

---

## Storybook + Vite Quirks

### Vite glob patterns in package exports

Vite does not support glob patterns in `package.json` exports. `@telesign/boreal-web-components/css/*` cannot be resolved automatically. Two aliases are registered in `viteFinal` in `apps/boreal-docs/.storybook/main.ts` to work around this — do not remove them.

### ESM-ES5 dynamic import warnings

Noisy warnings about dynamic imports of ESM modules are suppressed in two places in `apps/boreal-docs/.storybook/main.ts`:

- **Dev**: via a custom `createLogger` filtering `logger.warn` when the message includes both `'esm-es5'` and `'dynamic import'`
- **Prod build**: via `rollupOptions.onwarn` filtering when `warning.plugin === 'vite:import-analysis'` and `warning.id` includes `'esm-es5'`

These warnings are harmless. Do not remove the suppressions.
