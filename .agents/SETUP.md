# AI Configuration — Boreal DS

Personal AI agent configuration, IDE instructions, and development guidelines for the [Boreal DS](https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds) monorepo. These files are for local use only and are not part of the shared codebase.

---

## What's in this repo

Three canonical directories hold all AI artefacts:

| Directory  | Purpose                                                                     |
| ---------- | --------------------------------------------------------------------------- |
| `.agents/` | Canonical tooling: agent definitions, skills, commands, memory, scripts     |
| `ai-docs/` | Reference documentation: guidelines, decisions, diagrams, instruction files |
| `ai-work/` | Working artefacts: plans, reviews, sessions, tickets, QA, research          |

Three mirror facades expose content to specific tools via per-entry symlinks:

| Facade                  | Points to           | Used by              |
| ----------------------- | ------------------- | -------------------- |
| `.claude/agents/`       | `.agents/agents/`   | Claude Code          |
| `.claude/commands/`     | `.agents/commands/` | Claude Code          |
| `.claude/memory/`       | `.agents/memory/`   | Claude Code          |
| `.claude/skills/`       | `.agents/skills/`   | Claude Code          |
| `.cursor/agents/`       | `.agents/agents/`   | Cursor               |
| `.cursor/skills/`       | `.agents/skills/`   | Cursor               |
| `.github/instructions/` | `ai-docs/docs/`     | GitHub Copilot / IDE |

---

## How it works

All six directories are excluded from the main repository tracking via `.git/info/exclude`:

- They never appear as untracked files in `git status` on the main branches
- They are never pushed to the `origin` remote (Bitbucket)
- They are tracked independently on an orphan `ai-config` branch in a separate `ai` remote

---

## Setup (for a new machine)

### 1. Clone the main repo

```bash
git clone ssh://git@bitbucket.c11.telesign.com:7999/dev/boreal-ds.git
cd boreal-ds
```

### 2. Add the ai remote

```bash
git remote add ai https://github.com/dgonzalezts/boreal-ds-ai.git
```

### 3. Restore the AI config files onto disk

```bash
git fetch ai
git checkout ai/main -- .agents ai-docs ai-work .claude .cursor .github
git rm --cached -r .agents ai-docs ai-work .claude .cursor .github
```

### 4. Exclude the folders from the main repo

Add to `.git/info/exclude` (located at `<repo-root>/.git/info/exclude`):

```
# AI and IDE configuration — tracked in a separate private remote, not in origin
.agents/
ai-docs/
ai-work/
.claude/
.cursor/
.github/
```

### 5. Add the `aisync` function to your shell

Add the `aisync` function to your `~/.functions` (or equivalent shell config file):

```bash
# Sync AI scaffold dirs to the ai-config branch and push to the ai remote.
# Usage: aisync [repo-path]   (defaults to the current git repo root)
function aisync() {
  local root
  root=$(git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null)
  if [[ -z "$root" ]]; then
    printf "\033[31mERROR:\033[0m Not inside a git repository\n"
    return 1
  fi
  bash "$root/.agents/scripts/aisync.sh" "$root"
}
```

---

## Daily workflow

Edit any files inside `.agents/`, `ai-docs/`, or `ai-work/` freely while on any branch. When ready to save and push:

```bash
aisync
```

That's it. The script:

1. Adds a git worktree checked out to `ai-config` in a sibling directory
2. Rsyncs all scaffold directories into the worktree (including deletions)
3. Commits with a timestamped message and pushes to `ai/main`
4. Removes the worktree — your working directory is never touched

After pushing, run the symlink reconciler to keep the mirror facades in sync:

```bash
bash .agents/scripts/sync-symlinks.sh
```

---

## Pushing manually (without `aisync`)

```bash
root=$(git rev-parse --show-toplevel)
wt="$root/../ai-sync-worktree"
git worktree add "$wt" ai-config
for d in .agents ai-docs ai-work .claude .cursor .github; do
  rsync -a --delete --links "$root/$d" "$wt/"
done
git -C "$wt" add -f .agents ai-docs ai-work .claude .cursor .github
git -C "$wt" commit -m "sync: update AI configuration"
git -C "$wt" push ai ai-config:main
git worktree remove "$wt"
```
