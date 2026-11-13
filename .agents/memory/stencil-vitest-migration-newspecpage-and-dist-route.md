# Moving the specs to `@stencil/vitest`: what works for `newSpecPage` and for the dist route

Verified on Stencil 4.45.2, Vitest 5.1.0, `@stencil/vitest` 1.16.1, Node 22 (EOA-20193 spike, 2026-11-13). The migration is deferred; Stencil's Jest runner is deprecated and removed in Stencil 5. Full write-up: `ai-work/research/2026-11-13-EOA-20193-stencil-vitest-migration-spike.md`.

## Route A: keep `newSpecPage`

`newSpecPage` from `@stencil/core/testing` runs unchanged under Vitest 5 with a custom Vite transform plugin: 352 of 377 spec files green, 4,788 of 4,930 tests. `@stencil/core` 5.0.0-rc.1 still ships `newSpecPage` in `dist/testing/index.mjs` (package contents checked, not executed). `@stencil/vitest` itself has no `newSpecPage` and no codemod. The plugin must handle Mixin components: [[stencil-vitest-plugin-fails-on-mixin-components]].

## Route B2: the documented dist route (setup file importing built output)

Works only with a dedicated test build config:

- `extras.experimentalSlotFixes: true` empties the component DOM under mock-doc with prebuilt output (Jest's spec platform builds with it off). Keep it off.
- `minifyJs: true` breaks `render().instance` because `$lazyInstance$` is renamed. Set `minifyJs: false`.
- `render().root` is the first element of the fixture, not the first registered component. `render('')` throws.
- Native v8 coverage reports 0% on component source on this route; `vitest-monocart-coverage` did not map the `.tsx` files.
- `stencil-test --spec` is rejected by Vitest (`Unknown option --spec`). Working form: `stencil-test --project spec --stencil-config <file>`.
- Name the Vitest config `.mts`: the package has no `"type": "module"` and `.ts` prints the "ESM syntax in CJS" warning.

## How to verify

Re-run the samples from the spike document (`bds-badge`, `bds-checkbox`, `bds-pagination`): 125 of 125 on both routes with the settings above.

Related: [[stencil-vitest-replaces-global-htmlelement-and-event]], [[vitest-vi-fn-not-constructable]], [[stencil-scoped-test-invocation]].
