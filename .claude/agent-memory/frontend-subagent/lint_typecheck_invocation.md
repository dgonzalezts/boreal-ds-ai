---
name: lint-typecheck-invocation
description: How to run eslint/tsc scoped to boreal-web-components without triggering a repo-wide turbo run
metadata:
  type: project
---

`.agents/scripts/with-node.sh` always `cd`s to the git repo root (via `git rev-parse --show-toplevel`) before exec'ing the given command, even when invoked from a package subdirectory. So `with-node.sh pnpm exec eslint <file>` or `with-node.sh node_modules/.bin/eslint <file>` fails — `pnpm exec` resolves at the workspace root (no local `eslint` binary there) and the relative `node_modules/.bin/eslint` path no longer exists once cwd has moved to the root.

Plain `pnpm run lint` at the package level also fails for a targeted file list — the package's own `lint` script is `turbo run lint -- <extra args>`, and turbo fans that out to every workspace package (including `boreal-docs`, which chokes on a glob it doesn't recognize).

**Working invocation** for a scoped file check:
```
.agents/scripts/with-node.sh pnpm --filter @telesign/boreal-web-components exec eslint <path/relative/to/package> [...]
.agents/scripts/with-node.sh pnpm --filter @telesign/boreal-web-components exec tsc --noEmit
```
`pnpm --filter <package>` runs the command with that package as the effective root, sidestepping both the with-node.sh cwd reset and turbo's repo-wide fan-out. Paths passed to eslint must be relative to the package directory (e.g. `src/components/forms/...`), not the repo root.

Known pre-existing, unrelated `tsc --noEmit` failures (do not treat as new regressions) as of 2026-08: `bds-dialog.behavior.spec.ts` and `bds-tooltip-events.spec.ts` (Coords/MouseEvent type mismatches) — already flagged in `ai-work/plans/EOA-17138-bds-date-picker-v2.md` Task 11's status note.
