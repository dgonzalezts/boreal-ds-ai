# Vue `componentModels` wiring regenerates from the wrong-looking package

Adding a new `componentModels` entry to `packages/boreal-web-components/targets/vue-output-target.ts` (to wire a `v-model` binding for a new component/event pair) only takes effect after rebuilding **`boreal-web-components`**, not `boreal-vue`.

The Vue output target is a Stencil output target registered in `boreal-web-components/stencil.config.ts` — it's `stencil build` (run via that package's own build script) that regenerates `packages/boreal-vue/lib/components.ts`, even though the file being regenerated physically lives in a different package.

`packages/boreal-vue/lib/components.ts` is listed in `boreal-vue/.gitignore` — it is a pure build artifact, never git-tracked, and must never be hand-edited. If you find yourself wanting to add a `modelProp`/`modelUpdateEvent` pair directly in `components.ts`, that's a signal you edited the wrong file; go add the `componentModels` entry in `vue-output-target.ts` instead and rebuild.

**Command:** `pnpm --filter @telesign/boreal-web-components build` (with `fnm use` first, per repo convention) — not any `boreal-vue` script.

Confirmed while wiring `bds-table`'s `selectedRows`/`selectedRowsChange` v-model (EOA-14935 Task 8): the generated `BdsTable` proxy in `components.ts` gained the trailing `'selectedRows', 'selectedRowsChange', undefined` model-wiring args, matching the existing shape used for `BdsTextField`'s `value`/`valueChange` wiring.
