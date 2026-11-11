---
name: typecheck-and-lint-scoped-invocation
description: "Type-check with the package's config path passed explicitly (the repo-root tsconfig is a legacy stub) and run eslint through `pnpm --filter` — a bare `pnpm exec eslint` does not resolve in this workspace."
---

# Type-check and lint one package without wading through unrelated errors

**`tsc` — always name the package config.**

```
pnpm --filter @pxglobal/boreal-web-components exec tsc --noEmit -p tsconfig.build.json
```

`pnpm --filter <pkg> exec` runs with the package directory as `cwd`, so `-p` resolves against that directory — use `tsconfig.build.json`, or an absolute path when invoking `tsc` from the repo root without `--filter`.

- `packages/boreal-web-components/tsconfig.build.json` extends the package config, includes only `src`, and excludes `src/**/__test__` and `src/utils/testing` — this is the clean gate and exits 0 on the current tree.
- `packages/boreal-web-components/tsconfig.json` includes `src/**/__test__`, so it also surfaces spec-only errors (known baseline: 1 in `bds-dialog.behavior.spec.ts`, 4 in `bds-tooltip-events.spec.ts`). Use it only when the specs genuinely need type-checking.
- The repo-root `tsconfig.json` is a legacy stub (`module: commonjs`, `lib: es6`, no `jsx`, no `include`, `noImplicitAny: false`). A bare `tsc --noEmit` from the repo root picks it up and produces thousands of errors about missing JSX flags and unresolved `@/` aliases that have nothing to do with the change. If the error count is in the thousands, check which config was used before investigating any of them.

**`eslint` — go through `--filter`.**

```
pnpm --filter @pxglobal/boreal-web-components exec eslint src/components/forms/... [...]
```

There is no root `eslint` dependency, so `pnpm exec eslint <file>` at the workspace root fails to resolve, and the package's own `lint` script fans out through Turbo to every package. Paths are relative to the package directory. `.agents/scripts/with-node.sh` `cd`s to the repo root before exec'ing, so `--filter` is what keeps the invocation scoped (`stencil-scoped-test-invocation.md`).

**Source:** recurring in every plan that type-checks or lints a single package; restated in EOA-19597 T20.
