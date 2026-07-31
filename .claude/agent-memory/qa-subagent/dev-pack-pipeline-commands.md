# dev:pack:react / dev:pack:vue — pipeline behavior and exact commands

**Never** start a plain `vite` dev server against a workspace-built `boreal-web-components` for a React/Vue testapp. `pnpm --filter boreal-web-components build` alone does not produce a dist shape that `@telesign/boreal-web-components` subpath imports (e.g. `@telesign/boreal-web-components/components/bds-avatar.js`) can resolve — Vite fails immediately with "Failed to resolve import" errors for every generated component import in the wrapper's `components.js`.

## The correct commands (run from repo root)

```bash
pnpm run dev:pack:react   # builds boreal-web-components + downstream deps, packs as a tarball, installs into examples/react-testapp, starts vite
pnpm run dev:pack:vue     # same, for examples/vue-testapp
```

Both are full `turbo run build --filter=...@telesign/boreal-web-components` invocations — they rebuild every downstream dependent (`boreal-react`, `boreal-vue`, `boreal-docs` via the Turborepo graph), so budget **1-2 minutes**, not seconds. Run in the background (`run_in_background: true`) and wait for the completion notification rather than polling with short sleeps.

Each pipeline ends by starting its own `vite` dev server automatically — no separate `vite` command needed afterward. React defaults to `5173`; if already taken (e.g. by a leftover Vue instance), Vite auto-falls-back to the next port (`5174` etc.) and prints it in the pipeline's own log tail.

## Critical: the pack is a tarball snapshot, not a live symlink

Editing `bds-table.tsx` (or any `boreal-web-components` source) and rebuilding does **not** propagate to an already-running testapp — `dev:pack:react`/`dev:pack:vue` installs a `.tgz` snapshot at that moment, not a workspace symlink. To pick up a component-level fix, kill the testapp's dev server and **re-run the full `dev:pack:*` command again** — there is no lighter-weight refresh path.

Your own app source files (`App.tsx`, `App.vue`) *do* hot-reload normally via Vite's own file watcher, since those live inside the testapp's own project, not the packed dependency.

## Cleanup

Kill by port before restarting, since the pipeline doesn't reuse an existing server:
```bash
lsof -ti:5173,5174 2>/dev/null | xargs -r kill
```

## Verification commands used post-change

```bash
# React
cd examples/react-testapp
npx tsc --noEmit -p tsconfig.app.json
npx eslint src/App.tsx

# Vue
cd examples/vue-testapp
npx vue-tsc --noEmit
npx eslint .
```

`vue-tsc --noEmit` from the CLI did **not** catch a real event-handler type mismatch (`BdsExpandEventDetail.row: RowData` vs. a hand-rolled `OrderRow`-typed handler) that the user's IDE language server correctly flagged. Treat IDE diagnostics as authoritative for template-binding type-checking specifically — don't assume a clean CLI `vue-tsc` run means the IDE will also be clean.
