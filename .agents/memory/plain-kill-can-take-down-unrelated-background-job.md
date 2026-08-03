---
name: plain-kill-can-take-down-unrelated-background-job
description: Using plain `kill <pid>` in the Bash tool to stop a stale process from an EARLIER session can collaterally kill your OWN currently-running `&`/`disown`-backgrounded process in the same session, even though the PIDs are unrelated (no parent/child relationship)
metadata:
  type: feedback
---

Observed directly during a `bds-table` reorder re-verification pass (2026-07-31/08-01): a `pnpm --filter boreal-web-components exec stencil build --dev --watch --serve --port 3333` process was started via manual `&` + `disown` in one Bash call (not the tool's own `run_in_background` parameter). Several unrelated stale processes from an **earlier, separate session** (leftover `dev:pack:react`/`dev:pack:vue` pipelines, PIDs with no relation to the 3333 server) were then killed with a plain `kill <pid1> <pid2> ...` call. Immediately afterward, the 3333 server — which had **not** been targeted — also died, confirmed by its own log line `[ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL] Command was killed with SIGTERM` and the port going unreachable.

**Why (best available explanation, not fully root-caused):** all Bash tool invocations in a session likely share the same controlling terminal/session, so unrelated background jobs started via manual `&`/`disown` across different Bash calls can end up in a signal-related grouping that a plain `kill <pid>` on a sibling job's PID can affect, even without an explicit process-group kill (`kill -- -PID`) or parent/child relationship. This was not the case for two OTHER agents'/sessions' dev servers observed running concurrently on other ports (3335, 5173, 5174) at the time — those were unaffected, so the effect is not "any kill affects everything," but it reproduced once at real cost (a multi-minute rebuild had to be redone) and should be treated as a live hazard rather than a one-off fluke until root-caused further.

**How to apply:**

- Prefer the Bash tool's own `run_in_background: true` parameter over manual `command > log 2>&1 & disown` for any dev server you need to survive later, unrelated `kill` calls in the same session — tasks started this way are tracked by the harness (`TaskStop` can stop them individually) and were not observed to be affected by this collateral-kill behavior.
- If you must use manual `&`/`disown` (e.g. because you need a detached process outside harness tracking for some reason), immediately re-verify the server is still reachable (`curl`) after running ANY subsequent `kill` command in the same session, even against PIDs that look completely unrelated — don't assume "I only killed PID X" guarantees PID Y survives.
- See [[kill-sandbox-boundary-for-background-tasks]] for the separate, already-documented issue of plain `kill` silently failing against processes from *other* tool calls — this is a distinct failure mode (collateral death of a *survivor*, not failure to kill the *target*).

Source: `bds-table` v4 reorder QA re-verification session, promoted from `.claude/agent-memory/qa-subagent/plain-kill-can-take-down-unrelated-background-job.md` (original left unmodified).
