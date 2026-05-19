# GitHub Actions as a Reproducible Windows/Linux Debug Environment

## When to Use

When a bug is reported on Windows or Linux CI but no matching local machine is available, a temporary `workflow_dispatch` workflow on GitHub Actions is the fastest way to get a reproducible environment. This technique is preferable to attempting to install and configure a virtual machine locally.

## Setup Pattern

Create a workflow file directly via the GitHub web UI (not committed locally) and trigger it manually via the `workflow_dispatch` event. Key configuration choices:

```yaml
on:
  workflow_dispatch:

jobs:
  debug:
    runs-on: windows-latest   # or ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: pnpm install
      - name: Run suspect command (with timeout)
        run: pnpm dev:components
        timeout-minutes: 1
        continue-on-error: true
```

### Critical options

- `timeout-minutes: 1` on persistent/watch commands — lets them run long enough to observe startup behavior (output lines, errors, silence), then terminates cleanly. Without this the job blocks until the runner timeout kills the whole workflow.
- `continue-on-error: true` on the timed-out step — allows subsequent diagnostic steps to run even if the suspect command hangs or exits non-zero.

## Diagnostic Approach — Isolation Steps

Structure the workflow as a sequence of progressively narrower commands, each revealing one layer:

1. Verify Node.js and pnpm versions to confirm the environment is as expected
2. Run the top-level command (`pnpm dev:components`) with timeout to observe whether it hangs or errors
3. Run the constituent commands individually (build prerequisites, then the watch step) to identify which layer hangs
4. If Turbo is suspected, add `TURBO_LOG_ORDER=stream` and run with `--verbosity=3` to expose task scheduling decisions

## Keeping the Workflow File Off Local Branches

Create the debug workflow directly on the remote via the GitHub web UI. To prevent it from appearing in local git status or being committed, add it to `.git/info/exclude` (a local-only ignore file that is not committed):

```
.github/workflows/windows-debug.yml
```

This is preferable to `.gitignore` because it does not pollute the shared ignore rules.

## Cleanup

Delete the workflow file via the GitHub web UI once the bug is diagnosed and fixed. There is nothing to clean up locally if `.git/info/exclude` was used.

## Source

Windows-specific `pnpm dev:components` hang debugging session (2026-04-08).
