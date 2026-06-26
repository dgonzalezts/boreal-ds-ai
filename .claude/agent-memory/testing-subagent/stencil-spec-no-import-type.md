---
name: stencil-spec-no-import-type
description: "Spec files in boreal-web-components must not use `import type { X }` — Stencil's Babel transform does not support the standalone import type syntax."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 99cd22ae-fd66-49cc-965e-711730b0c117
---

Replace every `import type { X }` with `import { X }` in all `.spec.ts` files under `boreal-web-components`.

**Why:** Stencil's Jest pipeline uses Babel (not `ts-jest`) to transform TypeScript. Babel's TS plugin strips types by heuristic — it does not parse the `import type` keyword as a distinct construct unless `@babel/plugin-transform-typescript` is configured with `onlyRemoveTypeImports`. Without that config, `import type { Foo }` causes a parse error: "Unexpected token, expected 'from'". Plain `import { Foo }` is safe; Babel treats unused type-only imports as dead code during JS output.

**How to apply:** When writing or reviewing spec files, always use `import { Foo }` — never `import type { Foo }`. The TypeScript compiler still enforces type correctness at `tsc --noEmit` time regardless.
