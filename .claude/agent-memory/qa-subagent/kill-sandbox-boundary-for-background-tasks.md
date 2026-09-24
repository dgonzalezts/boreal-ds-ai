---
name: kill-sandbox-boundary-for-background-tasks
description: Plain `kill`/`kill -9` from the Bash tool silently fails against processes from earlier tool calls — use TaskStop for tracked background tasks, dangerouslyDisableSandbox:true kill for genuine OS orphans
metadata:
  type: feedback
---

Sending `kill`/`kill -9` to a PID from a normal (sandboxed) Bash tool call can silently fail — the
command returns a nonzero exit code with no useful stderr, even though the target process is still
alive and fully visible via `ps aux` (same user, no filesystem permission issue). This looks identical
to "process already gone" if the failure branch is swallowed with `2>/dev/null` — do not trust a
kill-loop's "already gone" echo as proof of death; always re-verify with a fresh `ps aux`/`ps -p` after
attempting to kill.

**Why:** the Bash tool sandbox appears to restrict signaling processes it did not itself spawn in the
current call, including processes started by *earlier* Bash tool calls in the same session (background
tasks in particular). Read-only inspection (`ps`) is unaffected — only the signal-sending syscall is
restricted.

**How to apply:**
- To stop a background task started with `run_in_background: true`, use the `TaskStop` tool with its
  task ID — this reliably kills the entire process tree (verified: it took down a 7-deep descendant
  chain including a spawned Vite dev server in one call). Do not attempt to `kill` it manually first.
- `TaskStop` only works while the harness still tracks the task. Once a task is reported "completed" or
  "failed" by the harness (even if its child processes lingered/orphaned — e.g. a Vite dev server that
  outlived its parent `pnpm`/`publish.js` chain), `TaskStop` returns "No task found" and you must fall
  back to a direct `kill -9 <pid...>` with `dangerouslyDisableSandbox: true`.
- Before using `dangerouslyDisableSandbox: true` to kill anything, trace the full process tree first
  (`ps -p <pid> -o pid,ppid,command`, walk parent and children) and confirm every PID's command line —
  other agents/subagents in the same session can have their own legitimate long-running processes
  (e.g. a `stencil build && stencil test` run from a specialist subagent actively verifying a fix, or a
  named background agent doing documentation work) that must not be killed just because they showed up
  in the same `ps aux` grep as a stale pipeline.
- In zsh, an unquoted `$VAR` holding a space-separated PID list does **not** word-split by default
  (unlike bash) — `for pid in $PIDS; do kill $pid; done` will pass the whole string as one argument to
  `kill` and fail with "illegal pid". Pass PIDs as literal space-separated arguments to a single `kill`
  call instead, or explicitly quote/split.

See also [[dev-pack-pipeline-commands]] for the specific pipeline this was discovered while cleaning up.

## `lsof -ti:<port>` returns CLIENTS too — never feed it straight into `kill`

The documented teardown idiom (`lsof -ti:<port> | xargs kill`) is unsafe on a machine where the
user has a real browser open. `lsof -ti:<port>` lists every process with a socket on that port,
including **client** connections — a Brave/Chrome tab pointed at `localhost:<port>` shows up
alongside the actual dev server. Confirmed 2026-09-23 (EOA-17662 Task 39): `lsof -ti:3333` returned
the Stencil dev-server worker **and** a `Brave Browser Helper --type=utility --sub-type=network`
process; killing both took down the user's browser network-service helper (Brave respawned it, so
no lasting damage, but it was collateral).

**How to apply:** always restrict to the listening socket before killing —
`lsof -sTCP:LISTEN -ti:<port>` — and print `ps -o pid,ppid,command -p <pids>` first to confirm
every PID is the process you actually mean to stop. Only then kill.

Companion zsh gotcha (also hit here): `PIDS=$(lsof -ti:3333); kill $PIDS` fails with
`illegal pid: 21319\n83454` — an unquoted `$VAR` holding newline-separated PIDs is passed as a
single argument. Pass PIDs as literal space-separated arguments, or split explicitly.
