# Published `.d.ts` leaks: `@/` re-exports, unexported method types, test helpers via the utils barrel

Verified on Stencil 4.45.2 and TypeScript 6.0.3 (EOA-20193, 2026-11-13): 14 errors before the fixes, 0 after.

## The Problem

1. Stencil rewrites the `@/` path alias in `import` declarations of emitted `.d.ts` files but NOT in `export ... from '@/...'` re-exports. Those stay literally in `dist/types` and consumers cannot resolve them.
2. A named type referenced by a public `@Method()` signature must be an exported type. A `typeof CONST.x` expression whose constant is not imported leaves an unresolved name in the generated `components.d.ts`, silently `any` under `skipLibCheck: true`.
3. `src/utils/index.ts` re-exports `./testing`, so any public `.d.ts` that imports the `@/utils` barrel pulls test-helper declarations (the `jest` namespace) into every consumer's program.

## The Fix

- Type files that re-export use a relative path.
- Export the type used by a public `@Method()` signature and import it where it is referenced.
- Import from the narrow module (`@/utils/form`, `@/utils/constants`), never the `@/utils` barrel, in files that reach public declarations.

## How to verify

`pnpm pack` the package, install the tarball with its real dependencies in a scratch project OUTSIDE the repository, and run `tsc` with `skipLibCheck: false` on:

```ts
import type { Components, JSX } from '@pxglobal/boreal-web-components';
```

`skipLibCheck: true` hides every one of these problems. A guard step in the pack pipeline that does this automatically is only drafted, not implemented.

Related: [[typecheck-and-lint-scoped-invocation]], [[scripts-boreal-pack-pipeline]].
