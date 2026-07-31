# Storybook ArgTypes Name Collisions Across Sub-Components

When one `.stories.ts` file documents several related custom elements in a single shared `meta` (e.g. `bds-table`, `bds-table-column`, `bds-table-column-group`), `<ArgTypes include={[...]}>` filters against the whole flat `meta.argTypes` object, not scoped per sub-component. Two sub-components with a same-named prop (e.g. `bds-table-column` and `bds-table-column-group` both have `label`/`info`, with different meanings) cannot be disambiguated by adding a second entry with a `name:` override — that recreates the exact collision `include` exists to solve.

**Root cause**, read directly from the installed package (`node_modules/.pnpm/storybook@10.2.8*/node_modules/storybook/dist/_browser-chunks/chunk-2N4WE3KZ.js`, the source behind `storybook/preview-api`'s `filterArgTypes`, which `<ArgTypes include={[...]}>` calls under the hood):

```js
filterArgTypes = (argTypes, include, exclude) => !include && !exclude ? argTypes : argTypes && pickBy(argTypes, (argType, key) => {
  let name = argType.name || key.toString();
  return !!(!include || matches(name, include)) && (!exclude || !matches(name, exclude));
});
```

`include` matches against each entry's *resolved display name* (`argType.name`, falling back to the object key) — not the raw object key. Two entries resolving to the same name can never be selectively addressed by `include`. This is a structural Storybook constraint, not a bug in this codebase's usage. Also confirmed via `@storybook/addon-docs`'s `blocks.d.ts`: `ArgTypesProps` always resolves through `of` — there is no way to pass a raw, standalone `argTypes` object bypassing `meta`.

**Fix — CSF3 per-story `argTypes` override.** A Storybook *story* (not just the shared `meta`) can declare its own local `argTypes` property (sibling to `parameters`/`render`) that merges over, and wins against, `meta.argTypes` for that one story's resolved context only — it does not mutate the shared object other stories/components read from.

Applied for `bds-table-column-group` in `apps/boreal-docs/src/stories/data-visualization/bds-table/bds-table.stories.ts`: the `GroupedColumns` story declares its own `argTypes.label`/`argTypes.info` with group-specific descriptions. The MDX file then points its `bds-table-column-group` Properties block at that story instead of the whole module:

```mdx
<ArgTypes of={BdsTableStories.GroupedColumns} include={['label', 'info']} />
```

instead of `of={BdsTableStories}`. Verified live in Storybook: the `bds-table-column-group` table shows the group-specific descriptions, `bds-table-column`'s own table is unaffected, zero bleed-over in either direction.

Canonical guideline write-up: `ai-docs/guidelines/storybook-patterns.md` § "MDX include name collisions across sub-components".

Source: `bds-table` v4 documentation session (EOA-16000).
