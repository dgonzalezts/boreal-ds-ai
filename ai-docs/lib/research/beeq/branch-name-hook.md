# How `.husky/branch-name.sh` Works

## Trigger Chain

The script isn't run directly by Husky — it's wired through a chain of npm scripts:

1. **Husky's `pre-commit` hook** (`.husky/pre-commit`) fires on every `git commit` and simply runs:
   ```
   pnpm pre-commit
   ```
2. That maps to the `pre-commit` script in `package.json`:
   ```
   "pre-commit": "run-s lint:branch-name lint:staged"
   ```
   using `npm-run-all`'s `run-s` to run two scripts **sequentially** (branch check first, then staged-file linting).
3. `lint:branch-name` is:
   ```
   "lint:branch-name": "chmod 755 .husky/branch-name.sh && sh .husky/branch-name.sh"
   ```
   It first ensures the script is executable, then runs it with `sh`.

So: **`git commit` → Husky `pre-commit` → `pnpm pre-commit` → `lint:branch-name` → `branch-name.sh`**, and only if this passes does `lint:staged` (Biome format/lint via `lint-staged`) run afterward.

## Script Logic

```sh
local_branch_name="$(git rev-parse --abbrev-ref HEAD)"
allowed_branch_names="feat|fix|test|docs|style|chore|perf|refactor|revert|ci|build"

branch_name_check="^(($allowed_branch_names)\/[a-zA-Z0-9\-]+)$"
if [[ $local_branch_name != "main" && ! $local_branch_name =~ $branch_name_check ]]; then
    echo "$message"
    exit 1
fi
exit 0
```

1. **Get the current branch name** via `git rev-parse --abbrev-ref HEAD`.
2. **Define the allowed prefix list** — the same conventional-commit type vocabulary used elsewhere (minus `wip`/`release`, which appear in commitlint but not here).
3. **Build a regex** requiring the format `<prefix>/<name>`, where `<name>` may only contain alphanumerics and hyphens (`[a-zA-Z0-9\-]+`).
4. **Whitelist `main`** explicitly — direct commits on `main` bypass the check entirely (this matters since `main` doesn't match the `<prefix>/<name>` pattern).
5. **Any other branch** must match the regex, otherwise the commit is aborted (`exit 1`) with a colored error message explaining the naming contract; if it matches (or the branch is `main`), it exits `0` and lets the commit proceed.

Valid examples: `feat/add-tooltip`, `fix/select-backspace`, `chore/update-deps`
Invalid examples: `feature/foo` (wrong prefix), `fix_thing` (missing slash), `fix/thing_here` (underscore not allowed by `[a-zA-Z0-9\-]+`).

## Configuration Needed

None externally — it's fully **self-contained**:
- No config file, no environment variables, no `.commitlintrc`-style setup.
- The allowed prefixes and regex are **hardcoded inline** in the script itself. To change the accepted types you'd edit `allowed_branch_names` directly in `.husky/branch-name.sh`.
- The only "setup" required is that Husky hooks are installed, which happens automatically via the `"prepare": "husky"` script in `package.json` (runs on `pnpm install`), and that the script has the executable bit — which the `chmod 755` step self-heals on every run in case git checkout strips permissions (common when cloning on some systems or CI).

## Inconsistency Worth Noting

This list (`feat|fix|test|docs|style|chore|perf|refactor|revert|ci|build`) is slightly out of sync with `.commitlintrc.ts`'s `type-enum`, which additionally allows `wip` and `release` — so a branch named `wip/experiment` would fail the branch check even though a `wip:` commit would pass commitlint.

## When Is This Actually Enforced? (Commit-Time Only)

Validation happens **only on `git commit`**, not on branch creation and not on `git push`:

- **Branch creation is never validated.** `git checkout -b whatever` or `git branch whatever` succeeds regardless of name — the hook doesn't exist for that Git lifecycle event.
- **The check is deferred to the first local commit.** Only when `git commit` runs does `pre-commit` → `lint:branch-name` → `branch-name.sh` execute against `git rev-parse --abbrev-ref HEAD`. If the name is invalid, the commit is rejected at that point.
- **There is no `pre-push` hook** in `.husky/` (confirmed: only `branch-name.sh`, `commit-msg`, and `pre-commit` exist). So even if a commit somehow exists on a badly-named branch, nothing blocks `git push`.
- **There is no CI/server-side enforcement either** — `.github/workflows` (`publish.yml`, `github-pages.yml`) contain no branch-name check. A non-compliant branch that reaches `origin` (e.g., via bypass) would not be caught by GitHub Actions or by any repo branch-protection rule referenced in this repo.

### Practical Consequence

This is a **client-side-only, best-effort convention**, not a hard guarantee:
- It only protects developers who actually have the Husky hooks installed (i.e., ran `pnpm install`, triggering the `prepare: husky` script).
- It can be bypassed via `git commit --no-verify`, a disabled/overridden `core.hooksPath`, deleting `.husky/`, IDE/GUI clients that skip hooks, or CI/automated commits that never ran `pnpm install`.
- Since nothing re-validates the name at push, PR, or merge time, a non-compliant branch **can** reach `origin` and even get merged if the local hook was bypassed or never installed.

### Renaming a Non-Compliant Branch

Because the hook fires at commit time, a badly-named branch must be renamed **before the first commit succeeds** — there's nothing to push until a commit exists anyway.

Rename the branch you're currently on:
```bash
git branch -m feat/new-tooltip-support
```

Rename a different (non-checked-out) branch:
```bash
git branch -m old-branch-name feat/new-tooltip-support
```

If the branch was already pushed to `origin` (e.g., commits were made before Husky was installed, or with `--no-verify`), also sync the remote:
```bash
git push origin -u feat/new-tooltip-support   # push the renamed branch
git push origin --delete old-branch-name       # remove the stale remote branch
```

If the branch has zero commits yet, there's nothing for Git to "fix" — the hook never ran — but renaming with `-m` proactively avoids the rejection on the first commit.
