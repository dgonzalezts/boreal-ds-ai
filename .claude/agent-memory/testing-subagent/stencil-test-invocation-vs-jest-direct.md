---
name: stencil-test-invocation-vs-jest-direct
description: "Always run Stencil tests via the npm test script, never by calling jest directly — direct invocation bypasses Stencil's Babel transform and TypeScript type-stripping. Also: how to correctly scope a run to one component."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 99cd22ae-fd66-49cc-965e-711730b0c117
---

Always use `pnpm --filter boreal-web-components run test -- <path-or-glob>` (never `pnpm exec jest ...` directly).

**Why:** Stencil builds its own Jest config internally when invoked through `stencil test --spec`. Calling `jest` directly skips that setup — TypeScript type annotations (e.g. `const ROWS: RowData[]`) are never stripped and ESM `import` statements are left untransformed, producing "Missing initializer in const declaration" and "Cannot use import statement outside a module" errors even in `.spec.ts` files.

**How to apply — scoping to one component:**

- **Do NOT use `--testPathPattern`.** Verified 2026-07-01 (Stencil 4.42.1): `stencil test --spec -- --testPathPattern=bds-tooltip` mangles the pattern into a character-class regex (`/b|d|s|-|t|o|o|l|t|i|p/i`), which matches nearly every file in the repo — this reproduces even with clean, unquoted args, so it is not a shell-quoting artifact but a bug/quirk in how Stencil's CLI forwards this specific flag to Jest. The earlier guidance in this file recommending `--testPathPattern` was wrong; corrected here.
- **Use a bare positional path/glob instead** — Stencil forwards this correctly: `pnpm --filter boreal-web-components run test -- src/components/overlays/bds-tooltip`.
- **Scope coverage stats with `--collectCoverageFrom`** — `test:coverage` computes the percentage against the project-wide `collectCoverageFrom` default even when only one component's specs ran, producing a misleadingly low number. Pass it explicitly: `pnpm --filter boreal-web-components run test:coverage -- src/components/overlays/bds-tooltip --collectCoverageFrom="src/components/overlays/bds-tooltip/bds-tooltip.tsx"`.
- **Use `--filter <package>`, not `cd <package> && pnpm run ...`.** `.agents/scripts/with-node.sh` internally does `cd "$(git rev-parse --show-toplevel)"` before exec'ing its argument, so a prior `cd packages/boreal-web-components &&` gets silently undone inside the wrapper and `pnpm run test` then fails with `Missing script` (it resolves against the workspace root, not the package). `--filter` is unaffected by cwd.

Full detail and copy-paste command examples: `.agents/skills/testing-knowledge/SKILL.md` §"Running the Spec Suite Scoped to One Component".
