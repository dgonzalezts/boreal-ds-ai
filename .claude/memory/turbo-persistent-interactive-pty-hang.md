# Turborepo — `persistent: true` PTY Hang in Headless Environments

## The Problem

Turbo's `persistent` task flag implies `"interactive": true` by default. This causes Turbo to allocate a PTY (pseudo-terminal) for the child process. In headless environments (GitHub Actions, Docker, any shell without a controlling TTY) and on Windows with a cold Turbo daemon, PTY allocation deadlocks silently — the process never starts, produces no output, and never errors.

This manifests as `pnpm dev:components` hanging indefinitely with no feedback. It does **not** manifest on macOS local developer machines when the Turbo daemon was already warm from a previous session, which is why the bug is invisible in day-to-day development.

Confirmed affected environments:
- `windows-latest` GitHub Actions runners (cold daemon)
- `ubuntu-latest` GitHub Actions runners (headless, no TTY)

## The Fix

Add `"interactive": false` explicitly to any `persistent` dev task in `turbo.json`:

```json
"dev": {
  "dependsOn": ["^build"],
  "persistent": true,
  "interactive": false,
  "cache": false
}
```

This is sufficient for bare `pnpm dev` (all packages) and any direct `turbo run dev` invocations.

## The Complementary Fix — Bypass Turbo for Primary Dev Workflows

For the named dev scripts in the root `package.json` (`dev:components`, `dev:docs`), bypassing Turbo entirely is safer and eliminates the PTY issue entirely for those paths. The pattern is to build prerequisites sequentially via pnpm filter, then delegate the watch step directly to the package:

```json
"dev:components": "pnpm --filter=@telesign/boreal-style-guidelines build && pnpm --filter=@telesign/boreal-web-components dev",
"dev:docs": "pnpm --filter=@telesign/boreal-style-guidelines build && pnpm --filter=@telesign/boreal-web-components build && pnpm --filter=@telesign/boreal-docs dev"
```

The two fixes are complementary, not redundant:
- Root `package.json` changes cover the primary developer workflows (`dev:components`, `dev:docs`)
- `"interactive": false` covers `pnpm dev` (all packages) and direct `turbo run dev` calls

## The Race Condition — Avoid `dev` Scripts That Alias `build`

If a package's `dev` script is just an alias for `build` (e.g. `"dev": "rimraf dist && build"`), running `pnpm dev` across all packages in parallel will trigger that `rimraf dist` at the same time another package's `dev` watcher is reading from that dist. This causes flapping failures that are timing-dependent and hard to reproduce.

The rule: if a package has no real watch process, it must not have a `dev` script at all. Remove it; the root `dev:components` script handles the prerequisite build explicitly.

## Source

Windows-specific `pnpm dev:components` hang debugging session (2026-04-08). Reproduced and diagnosed via GitHub Actions `windows-latest` and `ubuntu-latest` runners.
