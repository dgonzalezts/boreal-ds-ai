# Testing Subagent — Per-Scope Memory Index

- [Stencil test invocation vs jest direct](stencil-test-invocation-vs-jest-direct.md) — Use `pnpm --filter <pkg> run test -- <path>`, never `pnpm exec jest` or `--testPathPattern` (mangled into a char-class regex by Stencil's CLI); scope coverage with `--collectCoverageFrom`
- [No import type in spec files](stencil-spec-no-import-type.md) — Use `import { X }` not `import type { X }` in `.spec.ts` — Stencil's Babel transform does not support the standalone import type syntax
- [mock-doc MouseEvent relatedTarget](stencil-mock-doc-mouseevent-relatedtarget.md) — pass `relatedTarget` directly in the event init dict (no `Object.defineProperty` needed); `Node.contains(self)` is `true`, making `x.contains(t) || x === t` guards partly dead code
