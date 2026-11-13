# Dependency commits: the lockfile goes missing, and `validate:all` discards uncommitted manifest edits

Verified on pnpm 11.28.2 and 12.18.0 during EOA-20193 (2026-11-11 to 2026-11-13).

## The Problem

- A commit can miss `pnpm-lock.yaml` even when it was staged earlier (happened twice).
- `pnpm validate:all` does not catch it, because it re-resolves without a frozen lockfile.
- `pnpm validate:all` also restores the manifests and the lockfile to HEAD on exit (`git checkout HEAD --`), discarding uncommitted edits.
- `pnpm update <pkg>` rewrites manifest ranges (happened with the Storybook packages and the vitest ESLint plugin).
- The `latest` dist-tag of pnpm can lag behind published versions: 12.18.0 was `latest` while 12.19.0 and 12.20.0 sat on `next-12`.

## The Fix

After each commit, as separate steps:

```bash
git show HEAD:pnpm-lock.yaml | grep '<new-version>'
pnpm install --frozen-lockfile
```

Only then run `pnpm validate:all` and push. Commit or stash manifest edits before running `validate:all`.

After `pnpm update <pkg>`, restore the manifest ranges from git and run `pnpm install --lockfile-only`.

To pin pnpm, use the version the `latest-N` tag points to (query the registry), not the bare `latest` tag.

## How to verify

`git show HEAD:pnpm-lock.yaml` contains the new versions, and `pnpm install --frozen-lockfile` exits 0 on a clean tree.

Related: [[scripts-boreal-pack-pipeline]].
