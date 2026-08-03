---
name: storybook-docs-page-story-id-mismatch
description: bds-table's Storybook sidebar tag is "Table" but the docs/story path id is "data-visualization-table--*", not "data-visualization-bds-table--*"
metadata:
  type: project
---

Navigating directly to `?path=/docs/data-visualization-bds-table--overview` (guessing the id from
the component's tag name `bds-table`) 404s with "Couldn't find story matching". The actual title
configured in `bds-table.stories.ts`'s `meta.title` is `Data Visualization/Table`, which Storybook
slugs to `data-visualization-table--overview` (no `bds-` prefix) — the sidebar label is "Table",
not "Bds Table". Individual story ids follow the same pattern, e.g.
`data-visualization-table--reorderable-columns`.

**How to apply:** When navigating directly by URL for any `bds-table` doc/story instead of
clicking through the sidebar, use the `data-visualization-table--*` id family. If unsure of a
component's exact slug, click through the sidebar once first (or check `meta.title` in the
`.stories.ts` file) rather than guessing from the tag name.
