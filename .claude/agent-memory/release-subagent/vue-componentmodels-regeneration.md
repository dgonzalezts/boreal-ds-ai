---
name: vue-componentmodels-regeneration
description: How to add v-model wiring for a new bds-* component in the Vue output target and regenerate the proxy file
metadata:
  type: project
---

`packages/boreal-vue/lib/components.ts` is listed in `packages/boreal-vue/.gitignore` (`/lib/components.ts`) — it is a pure build artifact, never tracked in git, never hand-edited.

The source of truth for Vue v-model wiring is `packages/boreal-web-components/targets/vue-output-target.ts`'s `componentModels` array — each entry is `{ elements: [...], event: '<eventName>', targetAttr: '<propName>' }`.

To regenerate after editing `vue-output-target.ts`, build `boreal-web-components` (not `boreal-vue`) — the Vue output target runs as a Stencil output target during that package's `stencil build`, and `stencil.config.ts` imports it at line 5 (`import vueOutputTarget from './targets/vue-output-target'`) and registers it in `outputTargets` (line 62, `vueOutputTarget()`):

```bash
.agents/scripts/with-node.sh pnpm --filter @telesign/boreal-web-components build
```

This regenerates `../boreal-vue/lib/components.ts` as a side effect (`proxiesFile` points there). Confirm the new wiring by grepping the exported const, e.g. `grep -n "BdsTable\b" packages/boreal-vue/lib/components.ts` — a component with `componentModels` wiring gets a second generic param (`JSX.BdsTable, JSX.BdsTable["selectedRows"]>`) and two trailing string args on `defineContainer(...)` (`'selectedRows', 'selectedRowsChange', undefined`), matching the existing `BdsTextField` (`'value', 'valueChange', undefined`) pattern.

After regenerating, optionally verify the proxy type-checks standalone:

```bash
.agents/scripts/with-node.sh pnpm --filter @telesign/boreal-vue build
```

This runs `tsc -p . --outDir ./dist` against the freshly generated `components.ts` and will surface any type mismatch between the new `componentModels` entry and the underlying Stencil `@Prop`/`@Event` types.

See also [[release-sequencing-wc-react-vue]] in team memory for the overall release ordering these packages participate in.
