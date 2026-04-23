# PR Title

docs(boreal-docs): EOA-12029 add Storybook documentation for bds-grid and bds-grid-item

---

# PR Body

Adds the interactive Storybook stories and MDX documentation page for `bds-grid` and `bds-grid-item`, completing the three-branch delivery of the foundational grid system (implementation → tests → docs). Intended to merge into `feature/EOA-12029_grid_foundational_system_testing_DG`.

The stories file covers the full prop surface — column counts, gap sizes, breakpoint overrides, and `bds-grid-item` span/offset combinations — using live interactive controls. A `contrast.ts` utility was added to `boreal-docs` to compute accessible background swatches in the story canvas; it is a Storybook-only helper and does not ship in the component package.

Refs EOA-12029
