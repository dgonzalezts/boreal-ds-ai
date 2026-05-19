---
name: sync-symlinks
description: Use when a new agent, skill, command, memory entry, or instruction file is added or removed from a canonical directory and mirror symlinks need updating
---

# Sync Symlinks

## Overview

Run `sync-symlinks.sh` to reconcile per-entry symlinks across all mirror surfaces after any canonical directory change.

## When to invoke

- A file was added to or removed from any of:
  - `.agents/agents/` — agent definitions
  - `.agents/commands/` — Claude slash commands
  - `.agents/memory/` — memory entries
  - `.agents/skills/` — skill definitions
  - `ai-docs/docs/` — instruction files (`*.instructions.md`)
- After restoring or restructuring scaffold directories

## The Process

### Step 1: Run the script

From the repo root:

```bash
bash .agents/scripts/sync-symlinks.sh
```

### Step 2: Read the output

Each line reports one of these states for each entry:

| State | Meaning |
|-------|---------|
| `linked` | Symlink exists and is valid — no action needed |
| `fixed` | Broken symlink was recreated with the correct target |
| `added` | New symlink created for a newly added canonical entry |
| `removed` | Orphaned symlink removed (canonical entry no longer exists) |
| `CONFLICT` | A real file (not a symlink) occupies the mirror slot — **manual review required** |

### Step 3: Resolve conflicts (if any)

The script exits with code 1 and prints a `WARNING` line when conflicts are found. For each `CONFLICT` entry:

1. Inspect the real file at the mirror path (e.g. `.claude/agents/my-agent.md`)
2. If its content belongs in the canonical dir, move it there first: `mv .claude/agents/my-agent.md .agents/agents/my-agent.md`
3. Re-run the script — it will now create the symlink

### Step 4: Sync to remote

After the script completes cleanly (exit 0), push the updated scaffold:

```bash
aisync
```

## Notes

- The script never modifies real files — only symlinks are created, fixed, or removed.
- The `.github/instructions/` surface only manages `*.instructions.md` files; other files in that directory are left alone.
- Mirror directories are created automatically if they do not exist.
