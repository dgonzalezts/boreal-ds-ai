# A stale generated `components.d.ts` fails the first build after a rebase

Verified in EOA-20193 (2026-11-13) on Stencil 4.45.2; also listed in the README troubleshooting table.

## The Problem

`packages/boreal-web-components/src/components.d.ts` is generated and gitignored. After a rebase onto a branch that changed component props it still describes the old props, and the first `pnpm build` fails with `Property 'x' does not exist on type 'Omit<...>'`.

## The Fix

Delete the file and rebuild:

```bash
rm packages/boreal-web-components/src/components.d.ts
pnpm build
```

## How to verify

The second build regenerates the file and passes. The error names a prop that exists in the source but not in the old declaration.

Related: [[stencil-worktree-missing-style-guidelines-dist]] (the other "first build in a changed checkout" failure).
