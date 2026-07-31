---
name: argtypes-name-collision-across-subcomponents
description: Two sub-components sharing a prop name (e.g. both have `label`) cannot both use `<ArgTypes include={['label']}>` in the same meta — Storybook filters by `name` across the whole shared argTypes object, not scoped per component.
metadata:
  type: project
---

Storybook's `<ArgTypes of={...} include={[...]}>` filters via `filterArgTypes` (see
`storybook/dist/_browser-chunks/chunk-2N4WE3KZ.js`), which does:

```js
let name = argType.name || key.toString();
return matches(name, include);
```

This runs over the **entire shared `argTypes` object** in the story file's `meta`, not scoped to
"the component this ArgTypes block is documenting." So if two Stencil components documented in the
same `.stories.ts` file (e.g. `bds-table-column` and `bds-table-column-group`) both have a prop
literally named `label`, and you give the second one an argTypes key with `name: 'label'` to match
its real HTML attribute, **both** `<ArgTypes include={['label']}>` blocks (the column's and the
group's) would render two rows — one bleeding in from the other component — because both argType
keys resolve to the same `name`.

**Fix actually shipped for `bds-table-column-group`'s `label`/`info` props (EOA-16000 `bds-table`
v4 documentation session):** a CSF3 per-story `argTypes` override, not a hand-authored Markdown
table. The `GroupedColumns` story in `bds-table.stories.ts` declares its own `argTypes.label` /
`argTypes.info` (a property sibling to `parameters`/`render` on the story object) with
group-specific descriptions — this merges over `meta.argTypes` for that one story's resolved
context only, without mutating the shared object other stories/components read from.
`bds-table.mdx`'s `### bds-table-column-group` section then points `<ArgTypes>` at that story
specifically:

```mdx
<ArgTypes of={BdsTableStories.GroupedColumns} include={['label', 'info']} />
```

instead of `of={BdsTableStories}` (the whole module/meta). Verified live in Storybook: the
`bds-table-column-group` table shows the group-specific descriptions, `bds-table-column`'s own
table is completely unaffected, zero bleed-over in either direction.

An earlier draft of this fix considered skipping `<ArgTypes>` entirely for the colliding
sub-component and hand-authoring a plain Markdown table instead (the precedent set by
`bds-toolbar.mdx`'s `### bds-toolbar-item` section). That approach is still valid as a fallback
when a per-story `argTypes` override isn't feasible, but the per-story override is the preferred
fix — it keeps `<ArgTypes>`'s auto-generated table (types, defaults, controls) instead of losing
that tooling entirely.

Canonical write-up with full root-cause detail: `ai-docs/guidelines/storybook-patterns.md` §
"MDX include name collisions across sub-components". Team-wide memory entry:
`.agents/memory/storybook-argtypes-name-collision.md`.

This is safe to reach for per-component — only use it when a name collision would otherwise occur;
default to a shared `<ArgTypes of={BdsXxxStories}>` block everywhere else per `storybook-patterns.md`.
