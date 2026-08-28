---
name: stencil-turbo-build-cache-hit-false-positive
description: pnpm build from inside a package dir can silently replay a cached Turborepo log instead of re-checking edited source, giving a false "no type errors" result
metadata:
  type: project
---

Running `pnpm build` from inside `packages/boreal-web-components/` still invokes the
monorepo-wide Turborepo pipeline (it's not scoped to the package by cwd alone). If
Turbo has a cache entry for that task, the output says `cache hit, replaying logs` and
prints the *previous* run's log — including a stale "build finished" success — without
re-running `stencil build` against the just-edited source at all. Using this as a
type-check pass/fail signal after editing source is a false positive.

**How to apply:** to actually re-verify a source change (e.g. as the "run `tsc
--noEmit`" manual-test step in a plan, since this package has no standalone `tsc`
script), bypass the cache with `pnpm --filter @telesign/boreal-web-components build`
run via `with-node.sh`, or watch for `cache hit, replaying logs` in the output of a
plain `pnpm build` and re-run with `--force` / the `--filter` form if seen.

Related to [[turborepo-cache-vs-chromatic-force-rebuild]] (`.agents/memory/`) — same
root cause (Turbo cache), different consumer (this one is about type-check
verification, not Chromatic snapshot freshness). Candidate for promotion to
`.agents/memory/` since any subagent using `pnpm build` as a type-check proxy in this
monorepo can hit it, not just this scope.
