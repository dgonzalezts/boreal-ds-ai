# Testing Subagent — Per-Scope Memory Index

- [Stencil test invocation vs jest direct](stencil-test-invocation-vs-jest-direct.md) — Always run tests via `pnpm run test`, never `pnpm exec jest` — direct Jest invocation bypasses Stencil's Babel transform
- [No import type in spec files](stencil-spec-no-import-type.md) — Use `import { X }` not `import type { X }` in `.spec.ts` — Stencil's Babel transform does not support the standalone import type syntax
