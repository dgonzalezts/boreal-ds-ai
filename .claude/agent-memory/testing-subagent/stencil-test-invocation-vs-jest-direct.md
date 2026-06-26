---
name: stencil-test-invocation-vs-jest-direct
description: "Always run Stencil tests via the npm test script, never by calling jest directly — direct invocation bypasses Stencil's Babel transform and TypeScript type-stripping."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 99cd22ae-fd66-49cc-965e-711730b0c117
---

Always use `pnpm --filter boreal-web-components run test -- --testPathPattern="<pattern>"` (or `pnpm test` inside the package), never `pnpm exec jest --testPathPattern=...`.

**Why:** Stencil builds its own Jest config internally when invoked through `stencil test --spec`. Calling `jest` directly skips that setup — TypeScript type annotations (e.g. `const ROWS: RowData[]`) are never stripped and ESM `import` statements are left untransformed, producing "Missing initializer in const declaration" and "Cannot use import statement outside a module" errors even in `.spec.ts` files.

**How to apply:** Whenever writing or running unit tests in `boreal-web-components`, always go through the `test` npm script. The `--testPathPattern` flag is forwarded through to Jest by Stencil, so scoped runs still work: `pnpm run test -- --testPathPattern="data-visualization/bds-table"`.
