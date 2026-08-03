---
name: dev-pack-build-resets-playground-dev-server
description: Running dev:pack:react/dev:pack:vue concurrently with an active src/index.html playground session causes the Stencil dev-watch server to spuriously rebuild/live-reload, silently resetting all in-page state mid-test
metadata:
  type: feedback
---

Starting `pnpm run dev:pack:react` (or `dev:pack:vue`) in the background while actively driving
Playwright interactions against the raw `pnpm dev:components` playground (`src/index.html`, e.g.
port 3333) causes the **separate** `stencil build --dev --watch --serve` process to fire repeated
spurious `rebuild, boreal-web-components, dev mode, started ...` cycles (observed 3 rebuilds within
~40 seconds, despite no edits to any `src/` file during that window). Each rebuild live-reloads the
connected browser tab, which silently resets all in-page component state (e.g. a column reorder
that had just been confirmed via one `browser_evaluate` call was gone by the next call querying the
same DOM).

**Symptom that reveals this, not a real product bug:** a state-mutating interaction (drag/drop
reorder, form state, etc.) reads back correctly in a `browser_evaluate` call made immediately after
triggering it, but a *later* `browser_evaluate` call (even by the same tool, same tab) shows the
original/reverted state, with the header/body HTML looking freshly re-mounted.

**Why:** `dev:pack:react`/`dev:pack:vue` runs a full `turbo run build --filter=...@telesign/boreal-web-components`,
which invokes its own Stencil build pipeline against the identical `boreal-web-components` package.
Something in that build's output/cache-write path (exact file not yet isolated — worth investigating
if this resurfaces) is visible to the separate dev-watch process's file watcher, triggering it to
treat the package as changed and rebuild+reload, even though no `src/` source was hand-edited.

**How to apply:**
- Do not interleave live Playwright verification against the `pnpm dev:components` playground with
  an in-flight `dev:pack:react`/`dev:pack:vue` build. Either: (a) run the pack pipelines first and
  wait for their `vite ... Local: http://...` ready line before starting web-components-only
  interactive testing, or (b) finish all raw-web-components verification first, *then* kick off the
  pack pipelines for the React/Vue verification pass.
- If a rebuild storm is suspected (check the dev server's log for repeated unexplained `rebuild,
  boreal-web-components, dev mode, started` lines with no corresponding source edit), treat any
  state read since the last rebuild timestamp as unverified and redo the interaction after the log
  goes quiet.
- This is distinct from [[dev-pack-pipeline-commands]]'s "never launch dev:pack:react and
  dev:pack:vue concurrently" note (that one is about two pack pipelines racing Storybook's shared
  output directory) — this is about a pack pipeline racing the *raw web-components dev server*
  instead.

See also [[dev-pack-pipeline-commands]] and [[playwright-and-bds-button-conventions]].

**Confirmed again 2026-08-01, with a variant cause:** the storm doesn't require *you* to have just
started the pack pipeline in the current session — **stale/orphaned `dev:pack:react`/`dev:pack:vue`
processes left running from an earlier, unrelated session** (visible via `ps aux | grep -i "turbo run\|dev:pack"`,
often alive for 30+ minutes with their own `vite` server already serving on 5173/5174) reproduce the
identical rebuild-storm symptom against a brand-new `stencil build --dev --watch --serve` instance you
start afterward. Check for these leftover processes *before* starting any fresh raw dev server, not just
before starting your own pack pipeline. Killing the stale pipeline's process tree resolves it (rebuilds
stopped firing once the leftover `dev:pack:react`/`dev:pack:vue` trees were killed) — but see
[[plain-kill-can-take-down-unrelated-background-job]] before using plain `kill` on them, since it can
collaterally take down your own unrelated background dev server in the same Bash session.
