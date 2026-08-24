# AI Configuration — Boreal DS

Personal AI agent configuration, IDE instructions, and development guidelines for the [Boreal DS](https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds) monorepo. These files are for local use only and are not part of the shared codebase.

---

## What's in this repo

Three canonical directories hold all AI artefacts:

| Directory  | Purpose                                                                 |
| ---------- | ----------------------------------------------------------------------- |
| `.agents/` | Canonical tooling: agent definitions, skills, commands, memory, scripts |
| `ai-docs/` | Reference documentation: guidelines, decisions, diagrams                |
| `ai-work/` | Working artefacts: plans, reviews, sessions, tickets, QA, research      |

Four mirror facades expose content to specific tools via per-entry symlinks (one, `.opencode/agent/`, is generated rather than symlinked — see note below):

| Facade                            | Points to                         | Used by                               |
| --------------------------------- | --------------------------------- | -------------------------------------- |
| `.claude/CLAUDE.md`               | `.agents/AGENTS.md`               | Claude Code                           |
| `.claude/agents/`                 | `.agents/agents/`                 | Claude Code                           |
| `.claude/commands/`               | `.agents/commands/`               | Claude Code                           |
| `.claude/memory/`                 | `.agents/memory/`                 | Claude Code                           |
| `.claude/rules/`                  | `.agents/rules/`                  | Claude Code                           |
| `.claude/skills/`                 | `.agents/skills/`                 | Claude Code                           |
| `.cursor/agents/`                 | `.agents/agents/`                 | Cursor                                |
| `.cursor/commands/`               | `.agents/commands/`               | Cursor                                |
| `.cursor/rules/`                  | `.agents/rules/`                  | Cursor (renamed \\\*.mdc)             |
| `.cursor/skills/`                 | `.agents/skills/`                 | Cursor                                |
| `.github/copilot-instructions.md` | `.agents/copilot-instructions.md` | GitHub Copilot (always-on)            |
| `.github/prompts/`                | `.agents/commands/`               | GitHub Copilot (renamed \*.prompt.md) |
| `AGENTS.md` (repo root)           | `.agents/AGENTS.md`               | OpenCode                              |
| `.opencode/command/`              | `.agents/commands/`               | OpenCode                              |
| `.opencode/agent/`                | *generated from* `.agents/agents/` | OpenCode                              |

`.agents/skills/` needs no OpenCode facade — OpenCode natively searches that path as one of its documented skill-discovery locations (confirmed live).

`.opencode/agent/` is the one exception to the "per-entry symlink" rule: OpenCode's agent frontmatter schema is a strict validator that rejects Claude's `tools:` (comma-string with `Agent(...)` syntax) and `color:` (named color) shapes outright — this was discovered when a plain symlink here broke every OpenCode session with a hard config-parse error. `.agents/scripts/generate-opencode-agents.py` derives OpenCode-shaped frontmatter (`mode`, `permission.task`, an optional `tools: {bash: false}` restriction) from each canonical agent file, keeping the prose body byte-identical. Run it via `sync-symlinks.sh` (wired in automatically) — never hand-edit `.opencode/agent/*.md` directly, it's regenerated on every sync.

---

## How it works

All fifteen entries are excluded from the main repository tracking via `.git/info/exclude`:

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

### 2. Run the bootstrap script

From inside the repo root:

```bash
bash .agents/scripts/bootstrap.sh
```

This single command handles the rest of the setup idempotently:
- Adds the `ai` remote
- Restores all AI scaffold files from `ai/main` (if not already present)
- Adds all scaffold directories to `.git/info/exclude`
- Writes the `git aiboot` alias to `.git/config`
- Appends the `aisync` function to `~/.functions` (if not already present)
- Runs `sync-symlinks.sh` to wire up all mirror facades

If prompted to source `~/.functions`, add `source ~/.functions` to `~/.zshrc` or `~/.bashrc`.

**For subsequent worktrees**, use the alias instead:

```bash
git aiboot
```

This resolves to `bootstrap.sh` in the main repo regardless of which worktree it is run from.

---

## Daily workflow

Edit any files inside `.agents/`, `ai-docs/`, or `ai-work/` freely while on any branch. When ready to save and push:

```bash
aisync . "docs(agents): update memory management sections"
```

The second argument is the commit message. Omit it to fall back to a timestamped default (`sync: update AI configuration YYYY-MM-DD HH:MM`). The first argument is the repo path — use `.` for the current directory.

The script:

1. Adds a git worktree checked out to `ai-config` in a sibling directory
2. Rsyncs all scaffold directories into the worktree (including deletions)
3. Commits with your message and pushes to `ai/main`
4. Removes the worktree — your working directory is never touched

After pushing, run the symlink reconciler to keep the mirror facades in sync:

```bash
bash .agents/scripts/sync-symlinks.sh
```

---

## Amending the last sync commit

If you need to rewrite the most recent commit message on `ai-config`:

```bash
# 1. Switch to ai-config
git checkout ai-config

# 2. Amend the commit message
git commit --amend -m "your message here"

# 3. Force-push to the ai remote (rewrites the published commit)
git push ai ai-config:main --force-with-lease

# 4. Return to your working branch
git checkout -
```

---

## Pushing manually (without `aisync`)

```bash
root=$(git rev-parse --show-toplevel)
wt="$root/../ai-sync-worktree"
git worktree add "$wt" ai-config
for d in .agents ai-docs ai-work .claude .cursor .github .opencode AGENTS.md opencode.json; do
  rsync -a --delete --delete-excluded --links --exclude='node_modules' "$root/$d" "$wt/"
done
git -C "$wt" add -f .agents ai-docs ai-work .claude .cursor .github .opencode AGENTS.md opencode.json
git -C "$wt" commit -m "sync: update AI configuration"
git -C "$wt" push ai ai-config:main
git worktree remove "$wt"
```
