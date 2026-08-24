# `aisync.sh`'s `git add -f` Bypasses `.gitignore` — Never Vendor Dependencies Under a Synced Target

## The Problem

`aisync.sh` force-adds every top-level target directory with `git add -f "${existing_targets[@]}"`. The `-f` flag is there deliberately — it's what lets normally-gitignored scaffold content get tracked on the `ai-config` branch at all — but it means **any** `.gitignore` or `.opencode/.gitignore` rule inside a synced target is silently overridden. A per-directory `.gitignore` cannot protect against this; `-f` bypasses it by design.

This bit us concretely: `npm install` was run inside `.opencode/` (to fix an editor type-checking diagnostic — see [[opencode-plugin-needs-own-tsconfig]]), which created `.opencode/node_modules/` (64MB, ~3800 files). The next `aisync` run rsynced it wholesale into the `ai-config` worktree and `git add -f .opencode` force-added it straight past whatever `.gitignore` existed there. It got committed and pushed to `ai/main` before anyone noticed — `aisync.sh`'s own output doesn't summarize file counts in a way that makes a 3829-file diff obviously alarming at a glance.

## The Fix

`.gitignore` is not sufficient protection for anything living inside an `aisync` target directory. The exclusion has to happen at the `rsync` step itself, before `git add -f` ever sees the files:

```bash
rsync -a --delete --delete-excluded --links --exclude='node_modules' "$root/$d" "$wt/"
```

Both flags matter, not just `--exclude`:
- `--exclude='node_modules'` alone only stops *new* copies — it does **not** delete a `node_modules` that's already present in the destination worktree (e.g. checked out from a prior commit that already has it tracked). Rsync protects excluded-pattern files from `--delete` by default.
- `--delete-excluded` is required to actually make excluded files get removed from the destination when they don't exist in source. Without it, a bloated commit's excluded content survives every subsequent sync untouched, because nothing ever explicitly tells rsync to reconcile it away — confirmed the hard way: adding just `--exclude` produced a follow-up commit with only 3 lines changed, when the actual fix required 3792 file deletions.

## The Broader Rule

Never run a real package-manager install (`npm install`, `pnpm install`, etc.) inside any directory listed in `aisync.sh`'s `targets` array without also adding that dependency-output directory to the rsync `--exclude`/`--delete-excluded` treatment. `.git/info/exclude` and per-directory `.gitignore` protect `git status`/`git add` on the *main* branches — they do nothing to protect the `ai-config` branch synced via `aisync`, because that path deliberately uses `-f`.

## Cleanup Note

The two commits that carried the accidental `node_modules` blob (`88b85fe2`, `c2de2a5d` at the time of this writing) still exist in `ai-config`'s history even though the branch tip is clean — the fix was a follow-up commit, not a history rewrite. A `git filter-repo`/rebase squash would fully reclaim that space but requires a force-push, so it was deliberately left for the user to request explicitly rather than done unilaterally.

## Source

AI-005 (OpenCode facade plan), post-completion follow-up.
