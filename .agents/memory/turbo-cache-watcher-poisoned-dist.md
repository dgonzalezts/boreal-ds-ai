---
name: turbo-cache-watcher-poisoned-dist
description: "A long-running stencil --watch can rewrite dist with pre-fix output, and Turbo caches those bytes under the current source hash — so validate:pack exits 0 on stale code. Grep the artifact that actually runs before trusting it."
---

# Turbo can cache a watcher-poisoned `dist`, so `validate:pack` passes on pre-fix code

**Mechanism.** A long-running `stencil build --watch` holds its program in memory from the moment it started. After the source changes, its next rebuild re-emits that older program into the shared `dist/`, `components-build/` and `www/` targets. `turbo run build --filter=…boreal-web-components` then hashes the *current* source and caches the *stale* output under it. Turbo trusts outputs, so the corruption is sticky: every later `dev:pack:*` / `validate:pack:*` restores pre-fix bytes and exits 0.

**Symptom pattern.** The browser behaves like the unfixed code while the worktree is correct; `--dry=json` shows `cache HIT` for the same hash before and after the fix; the installed pack's `dist/collection/.../<component>.js` lacks the fix.

**Detection — grep the artifact that will actually run**, never `packages/*/dist` (a watcher can rewrite it seconds later):

- `node_modules/.vite/deps/@pxglobal_boreal-<fw>.js` — the bundle the example apps execute.
- the installed pack under `node_modules/.pnpm/@pxglobal+boreal-<fw>@file+…/` → `dist/collection/...`.
- after `validate:pack`, the app's built bundle (`examples/*/dist/assets/index-*.js`).

**Recovery:** bust the cache with `pnpm exec turbo run build --filter=@pxglobal/boreal-web-components --force` (or a direct `pnpm --filter @pxglobal/boreal-web-components build`, which bypasses Turbo), re-grep, then re-run `validate:pack:*`. Do not kill another session's watcher.

**Rule:** a green `validate:pack` proves nothing about a component you just changed unless the artifact was grepped for a fix-specific marker. This is the packaging analogue of `stencil-dev-server-stale-lazy-chunk.md` (stale chunk served by the dev server — different root cause, different fix).

**Status:** found during EOA-19597 T18 and tracked as T44; the cache trap itself is not fixed, only worked around before trusting wrapper validation.

Related: `turbo-persistent-interactive-pty-hang.md` (different Turbo failure), `scripts-boreal-pack-pipeline.md` (where the build guarantee comes from).
