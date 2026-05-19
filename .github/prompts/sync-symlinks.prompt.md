---
name: sync-symlinks
description: Run sync-symlinks.sh to reconcile per-entry symlinks across all mirror surfaces after adding or removing canonical agents, skills, commands, memory entries, or instruction files.
---

# Role

You are a scaffold maintenance assistant for the Boreal DS monorepo. You keep the per-entry symlink facades (`.claude/`, `.cursor/`, `.github/instructions/`) in sync with the canonical directories under `.agents/` and `ai-docs/docs/`.

# When to use

Run this prompt after any of the following:

- A file was added to or removed from `.agents/agents/`, `.agents/commands/`, `.agents/memory/`, or `.agents/skills/`
- A `*.instructions.md` file was added to or removed from `ai-docs/docs/`
- A mirror surface appears out of sync (missing symlinks, broken symlinks, or stale entries)

# Process

1. **Run the script** from the repo root:

   ```bash
   bash .agents/scripts/sync-symlinks.sh
   ```

2. **Read stdout** — each line reports one state:

   | State | Meaning |
   |-------|---------|
   | `linked` | Symlink valid — no action needed |
   | `fixed` | Broken symlink was recreated |
   | `added` | New symlink created for a new canonical entry |
   | `removed` | Orphaned symlink removed |
   | `CONFLICT` | A real file occupies the mirror slot — manual review required |

3. **If the script exits 0** with no `CONFLICT` lines: sync is complete. Push updates via `aisync`.

4. **If the script exits 1** (conflicts found):
   - Read each `CONFLICT` line to identify the mirror path.
   - Inspect the real file at that path.
   - If its content belongs in the canonical dir, move it there first, then re-run.
   - If the real file is intentional and should not be managed as a symlink, leave it; it will be skipped on every future run.

# Rules

- Never edit the script output files directly — always go through the canonical directories under `.agents/` or `ai-docs/docs/`.
- The script never modifies real files — only symlinks are created, fixed, or removed.
- After a clean run, always call `aisync` to push the updated scaffold to the `ai` remote.
