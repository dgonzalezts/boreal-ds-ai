# AI Configuration — Boreal DS

Personal AI agent configuration, IDE instructions, and development guidelines for the [Boreal DS](https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds) monorepo. These files are for local use only and are not part of the shared codebase.

---

## What's in this repo

This repository contains three folders that live inside the monorepo working directory:

| Folder     | Purpose                                                               |
| ---------- | --------------------------------------------------------------------- |
| `.ai/`     | Plans, decisions, guidelines, tickets, and research used by AI agents |
| `.claude/` | Claude-specific agent configuration, skills, memory, and prompts      |
| `.github/` | GitHub Copilot instructions, agent definitions, and prompt files      |

---

## How it works

These three folders are intentionally excluded from the main repository tracking via `.git/info/exclude`. This means:

- They never appear as untracked files in `git status` or VS Code Source Control on the main branches
- They are never pushed to the `origin` remote (Bitbucket)
- They are tracked independently on an orphan `ai-config` branch in this separate `ai` remote

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
git checkout ai/main -- .ai .claude .github
git rm --cached -r .ai .claude .github
```

### 4. Exclude the folders from the main repo

Add to `.git/info/exclude` (located at `<repo-root>/.git/info/exclude`):

```
# AI and IDE configuration — tracked in a separate private remote, not in origin
.ai/
.claude/
.github/
```

### 5. Add the `aisync` function to your shell

Add the `aisync` function to your `~/.functions` (or equivalent shell config file):

```bash
# Sync AI config folders (.ai, .claude, .github) to the ai-config branch and push to the ai remote
# Usage: aisync [repo-path]   (defaults to the current git repo root)
function aisync() {
  local root
  root=$(git -C "${1:-.}" rev-parse --show-toplevel 2>/dev/null)
  if [[ -z "$root" ]]; then
    printf "\033[31mERROR:\033[0m Not inside a git repository\n"
    return 1
  fi
  local current
  current=$(git -C "$root" branch --show-current)
  local tmpdir
  tmpdir=$(mktemp -d)
  cp -r "$root/.ai" "$root/.claude" "$root/.github" "$tmpdir/" 2>/dev/null
  git -C "$root" checkout ai-config
  cp -r "$tmpdir/." "$root/"
  git -C "$root" add -f .ai .claude .github
  git -C "$root" commit --allow-empty -m "sync: update AI configuration $(date +%Y-%m-%d)"
  git -C "$root" push ai ai-config:main
  git -C "$root" checkout "$current"
  cp -r "$tmpdir/." "$root/"
  git -C "$root" rm --cached -r .ai .claude .github 2>/dev/null
  rm -rf "$tmpdir"
}
```

---

## Daily workflow

Edit any files inside `.ai/`, `.claude/`, or `.github/` freely while on any branch. When ready to save and push:

```bash
aisync
```

That's it. The function:

1. Snapshots the current state of all three folders from disk
2. Switches to `ai-config`, restores the snapshot, commits, and pushes to the `ai` remote
3. Switches back to your original branch and restores the files on disk

---

## Pushing manually (without `aisync`)

```bash
git checkout ai-config
git add -f .ai .claude .github
git commit -m "sync: update AI configuration"
git push ai ai-config:main
git checkout release/current
# Restore files on disk and unstage from main repo
git checkout ai/main -- .ai .claude .github
git rm --cached -r .ai .claude .github
```
