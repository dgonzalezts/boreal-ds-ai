# AI Scaffold Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Restructure the AI scaffold from three ad-hoc folders (`.ai/`, `.claude/`, `.github/`) into three semantically clean canonical directories (`.agents/`, `ai-docs/`, `ai-work/`), with `.claude/`, `.cursor/`, and `.github/instructions/` as per-entry symlink facades, `aisync` promoted into a versioned shell script inside `.agents/`, and a `sync-symlinks` skill for on-demand symlink repair.

**Architecture:** `.agents/` is the canonical SSoT for all AI tooling (agents, skills, commands, memory, scripts). `ai-docs/` is the canonical SSoT for persisting knowledge (guidelines, decisions, diagrams, instructions). `ai-work/` holds all temporary work artifacts (plans, reviews, sessions, tickets, qa, research). Mirror directories (`.claude/`, `.cursor/`, `.github/instructions/`) contain **per-entry relative symlinks** pointing into the canonical dirs — following the specboot pattern where each agent/skill/instruction file gets its own symlink, so unmanaged entries in mirror dirs are never touched. A `sync-symlinks` skill drives symlink repair on demand. A Phase 2 consolidation pass deduplicates memory entries against guideline files.

**Tech Stack:** bash (symlinks via `ln -s`, shell scripts), zsh shell functions (`~/.functions` as thin wrapper), git (`ai-config` branch, `ai` remote), Claude Code skills (SKILL.md)

---

## Files to create / modify

### Phase 1 — Relocate

| File                                      | Notes                                                                                    |
| ----------------------------------------- | ---------------------------------------------------------------------------------------- |
| `.agents/agents/`                         | New — move from `.claude/agents/`                                                        |
| `.agents/commands/`                       | New — move from `.claude/commands/`                                                      |
| `.agents/memory/`                         | New — move from `.claude/memory/`                                                        |
| `.agents/scripts/aisync.sh`               | New — extract from `~/.functions`, canonical versioned script                            |
| `.agents/scripts/sync-symlinks.sh`        | New — per-entry symlink reconciliation script                                            |
| `.agents/skills/`                         | New — merge `.claude/skills/` into existing `.agents/skills/`                            |
| `.agents/skills/sync-symlinks/SKILL.md`   | New — Claude skill wrapping `sync-symlinks.sh`                                           |
| `ai-docs/guidelines/`                     | New — move from `.ai/guidelines/`                                                        |
| `ai-docs/decisions/`                      | New — move from `.ai/decisions/`                                                         |
| `ai-docs/diagrams/`                       | New — move from `.ai/diagrams/`                                                          |
| `ai-docs/lib/`                            | New — move from `.ai/lib/`                                                               |
| `ai-docs/docs/`                           | New — move from `.ai/docs/` + absorb `.github/instructions/` content                     |
| `ai-docs/copilot-agents/`                 | New — move from `.github/agents/`                                                        |
| `ai-work/plans/`                          | New — move from `.ai/plans/`                                                             |
| `ai-work/reviews/`                        | New — move from `.ai/reviews/`                                                           |
| `ai-work/sessions/`                       | New — move from `.ai/sessions/`                                                          |
| `ai-work/tickets/`                        | New — move from `.ai/tickets/`                                                           |
| `ai-work/qa/`                             | New — move from `.ai/qa/`                                                                |
| `ai-work/research/`                       | New — move from `.ai/research/`                                                          |
| `.claude/agents/`                         | Modify — replace real files with per-entry symlinks → `../../.agents/agents/<name>`      |
| `.claude/commands/`                       | Modify — replace real files with per-entry symlinks → `../../.agents/commands/<name>`    |
| `.claude/memory/`                         | Modify — replace real files with per-entry symlinks → `../../.agents/memory/<name>`      |
| `.claude/skills/`                         | Modify — replace real skill dirs with per-entry symlinks → `../../.agents/skills/<name>` |
| `.claude/CLAUDE.md`                       | Modify — update all path references                                                      |
| `.cursor/`                                | New — real directory; per-entry symlinks for agents and skills                           |
| `.github/instructions/*.instructions.md`  | Modify — replace each real file with per-entry symlink → `../../ai-docs/docs/<name>`     |
| `.github/agents/`                         | Remove — content moved to `ai-docs/copilot-agents/`                                      |
| `.github/copilot-instructions.md`         | Modify — slim down to a pointer to `ai-docs/docs/`                                       |
| `.github/prompts/sync-symlinks.prompt.md` | New — Copilot prompt equivalent of the `sync-symlinks` skill                             |
| `.ai/`                                    | Remove — all content migrated; directory deleted                                         |
| `~/.functions` `aisync`                   | Modify — thin wrapper delegating to `.agents/scripts/aisync.sh`                          |
| `.git/info/exclude`                       | Modify — update excluded paths to match new folder names                                 |

### Phase 2 — Consolidate (separate milestone, do not begin until Phase 1 is complete and verified)

| File                                                    | Notes                                                             |
| ------------------------------------------------------- | ----------------------------------------------------------------- |
| `ai-docs/guidelines/stencil-best-practices.md`          | Modify — absorb unique detail from overlapping memory entries     |
| `ai-docs/guidelines/stencil-unit-testing-patterns.md`   | Modify — absorb unique detail from overlapping memory entries     |
| `ai-docs/guidelines/code-practices-&-dev-guidelines.md` | Modify — absorb unique detail from overlapping memory entries     |
| `.agents/memory/MEMORY.md`                              | Modify — remove entries promoted to guidelines; add pointers      |
| `.agents/memory/*.md`                                   | Remove — entries that duplicate guideline content after promotion |
| `.github/copilot-instructions.md`                       | Modify — remove sections that duplicate `ai-docs/docs/` content   |

---

## Manual Sync Procedure (Tasks 1–6)

Until Task 7 updates `aisync` to include `.agents/`, `ai-docs/`, and `ai-work/`, run this single script to commit **and** push to the `ai` remote. Replace the `msg` value, then paste the whole block into one terminal run.

Uses a **git worktree** so the working directory is never touched — no branch switching, no snapshot/restore step, no risk of wiping local files.

```bash
(
  msg="chore(workspace): * <task description>"

  set -e
  root=$(git rev-parse --show-toplevel)
  wt="$root/../ai-sync-worktree"
  trap 'git -C "$root" worktree remove --force "$wt" 2>/dev/null || true' EXIT

  git -C "$root" worktree add "$wt" ai-config

  for d in .ai .claude .github .agents .cursor ai-docs ai-work; do
    if [ -e "$root/$d" ]; then
      rsync -a --delete --links "$root/$d" "$wt/"
    else
      rm -rf "$wt/$d"
    fi
  done

  git -C "$wt" add -f .ai .claude .github .agents .cursor ai-docs ai-work
  if git -C "$wt" diff --cached --quiet; then
    echo "aisync: nothing changed, skipping commit and push"
  else
    git -C "$wt" commit -m "$msg"
    git -C "$wt" push ai ai-config:main
  fi
)
```

> **`git worktree`** checks out `ai-config` into a sibling directory without touching the current working tree.
> **`rsync --delete --links`** mirrors each directory including deletions and preserves symlinks.
> **`trap`** ensures the worktree is always removed even if the script aborts.

---

## Phase 1 Tasks

---

### Task 1: Create `.agents/` canonical tooling structure

**Files:**

- `.agents/agents/` (create — copy content from `.claude/agents/`)
- `.agents/commands/` (create — copy content from `.claude/commands/`)
- `.agents/memory/` (create — copy content from `.claude/memory/`)
- `.agents/skills/` (modify — merge `.claude/skills/` into existing `.agents/skills/`)

**Acceptance criteria:**

- All files from `.claude/agents/`, `.claude/commands/`, `.claude/memory/`, and `.claude/skills/` are present under `.agents/` at equivalent paths
- The existing `.agents/skills/executing-plans/SKILL.md` is preserved without modification
- No files are deleted from `.claude/` yet — that happens in Task 3
- `.agents/` directory listing matches:

```
.agents/
├── agents/
│   ├── frontend-developer.md
│   ├── knowledge-keeper.md
│   └── technical-writer.md
├── commands/
│   ├── sync-plans.md
│   └── ultra-think.md
├── memory/
│   ├── MEMORY.md
│   └── *.md (all 40+ memory files)
└── skills/
    ├── executing-plans/SKILL.md
    ├── brainstorming/SKILL.md
    ├── code-reviewer/
    └── ... (all other skill folders)
```

**Manual test _(waiveable)_:**

- [ ] `ls -la .agents/agents .agents/commands .agents/memory .agents/skills` — all present
- [ ] `diff -r .claude/agents .agents/agents` — empty output (no differences)
- [ ] `diff -r .claude/memory .agents/memory` — empty output

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * copy claude tooling into .agents canonical directory"
```

---

### Task 2: Create `ai-docs/` and `ai-work/` canonical directories

**Files:**

- `ai-docs/guidelines/` (create — copy from `.ai/guidelines/`)
- `ai-docs/decisions/` (create — copy from `.ai/decisions/`)
- `ai-docs/diagrams/` (create — copy from `.ai/diagrams/`)
- `ai-docs/lib/` (create — copy from `.ai/lib/`)
- `ai-docs/docs/` (create — copy from `.ai/docs/`, then also copy `.github/instructions/*.instructions.md` into it)
- `ai-docs/copilot-agents/` (create — copy from `.github/agents/`)
- `ai-work/plans/` (create — copy from `.ai/plans/`)
- `ai-work/reviews/` (create — copy from `.ai/reviews/`)
- `ai-work/sessions/` (create — copy from `.ai/sessions/`)
- `ai-work/tickets/` (create — copy from `.ai/tickets/`)
- `ai-work/qa/` (create — copy from `.ai/qa/`)
- `ai-work/research/` (create — copy from `.ai/research/`)

**Acceptance criteria:**

- All `.ai/` content is present in the new locations at equivalent relative paths
- `.github/instructions/*.instructions.md` files are **copied** (not moved yet) into `ai-docs/docs/` — originals remain in `.github/instructions/` until Task 5
- `.github/agents/*.agent.md` files are **copied** into `ai-docs/copilot-agents/` — originals remain until Task 5
- `.ai/README.md` and `.ai/SETUP.md` are copied into `ai-docs/docs/`
- `.ai/examples/` is copied into `ai-docs/` if non-empty; skip if empty
- No files are deleted from `.ai/` or `.github/` yet

**Manual test _(waiveable)_:**

- [ ] `ls ai-docs/guidelines ai-docs/decisions ai-docs/diagrams ai-docs/lib ai-docs/docs ai-docs/copilot-agents` — all exist and contain files
- [ ] `ls ai-work/plans ai-work/reviews ai-work/sessions ai-work/tickets ai-work/qa ai-work/research` — all exist and contain files
- [ ] `diff -r .ai/guidelines ai-docs/guidelines` — empty output
- [ ] `diff -r .ai/plans ai-work/plans` — empty output

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * create ai-docs and ai-work canonical directories"
```

---

### Task 3: Replace `.claude/` real files with per-entry symlinks

**Files:**

- `.claude/agents/*.md` (replace each real file with a per-entry relative symlink → `../../.agents/agents/<filename>`)
- `.claude/commands/*.md` (replace each real file with a per-entry relative symlink → `../../.agents/commands/<filename>`)
- `.claude/memory/*.md` (replace each real file with a per-entry relative symlink → `../../.agents/memory/<filename>`)
- `.claude/skills/<name>/` (replace each real skill directory with a per-entry relative symlink → `../../.agents/skills/<name>`)

**Acceptance criteria:**

- Per-entry pattern (specboot): each individual file/folder inside `.claude/agents/`, `.claude/commands/`, `.claude/memory/`, `.claude/skills/` is a symlink — the parent directories themselves remain real directories
- `ls -la .claude/agents/` shows each `.md` file as a symlink (`l` prefix)
- `readlink .claude/agents/frontend-developer.md` returns `../../.agents/agents/frontend-developer.md` (relative — never absolute)
- `cat .claude/agents/frontend-developer.md` resolves and shows content
- `.claude/CLAUDE.md` and `.claude/settings.local.json` are real files — never touched
- `.claude/pr-description.md` if present is a real file — never touched (external entry)
- Any file in `.claude/` that does NOT have a canonical counterpart in `.agents/` is left untouched (external entries)

**How to create (repeat for each file/dir):**

```bash
# agents — per file
rm .claude/agents/frontend-developer.md
ln -s ../../.agents/agents/frontend-developer.md .claude/agents/frontend-developer.md
# repeat for knowledge-keeper.md, technical-writer.md

# commands — per file
rm .claude/commands/sync-plans.md
ln -s ../../.agents/commands/sync-plans.md .claude/commands/sync-plans.md
# repeat for ultra-think.md

# memory — per file (40+ files — use a loop)
for f in .agents/memory/*.md; do
  name=$(basename "$f")
  rm -f ".claude/memory/$name"
  ln -s "../../.agents/memory/$name" ".claude/memory/$name"
done

# skills — per directory
rm -rf .claude/skills/brainstorming
ln -s ../../.agents/skills/brainstorming .claude/skills/brainstorming
# repeat for each skill folder
```

**Manual test _(waiveable)_:**

- [ ] `ls -la .claude/agents/` — every `.md` file has `l` prefix (symlink)
- [ ] `cat .claude/agents/frontend-developer.md` — content readable
- [ ] Open Claude Code — agents, commands, memory, and skills still discovered without errors
- [ ] Confirm `.claude/settings.local.json` and `.claude/CLAUDE.md` are unmodified real files

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * replace .claude entries with per-entry symlinks to .agents"
```

---

### Task 4: Create `.cursor/` per-entry symlink facade

**Files:**

- `.cursor/` (create — real directory)
- `.cursor/agents/<name>` (create — per-entry symlink for each agent → `../../.agents/agents/<name>`)
- `.cursor/skills/<name>` (create — per-entry symlink for each skill dir → `../../.agents/skills/<name>`)

**Acceptance criteria:**

- `.cursor/` and `.cursor/agents/`, `.cursor/skills/` are real directories
- Each agent file and skill directory inside them is an individual relative symlink
- `readlink .cursor/agents/frontend-developer.md` returns `../../.agents/agents/frontend-developer.md`
- `ls .cursor/agents/` lists the same entries as `.agents/agents/`

**How to create:**

```bash
mkdir -p .cursor/agents .cursor/skills

for f in .agents/agents/*.md; do
  name=$(basename "$f")
  ln -s "../../.agents/agents/$name" ".cursor/agents/$name"
done

for d in .agents/skills/*/; do
  name=$(basename "$d")
  ln -s "../../.agents/skills/$name" ".cursor/skills/$name"
done
```

**Manual test _(waiveable)_:**

- [ ] `ls -la .cursor/agents/` — all entries are symlinks
- [ ] `cat .cursor/agents/frontend-developer.md` — content readable

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * add .cursor per-entry symlink facade to .agents"
```

---

### Task 5: Replace `.github/instructions/` with per-entry symlinks and remove `.github/agents/`

**Files:**

- `.github/instructions/base.instructions.md` (replace with symlink → `../../ai-docs/docs/base.instructions.md`)
- `.github/instructions/documentation.instructions.md` (replace with symlink → `../../ai-docs/docs/documentation.instructions.md`)
- `.github/instructions/frontend.instructions.md` (replace with symlink → `../../ai-docs/docs/frontend.instructions.md`)
- `.github/instructions/security.instructions.md` (replace with symlink → `../../ai-docs/docs/security.instructions.md`)
- `.github/instructions/workflow.instructions.md` (replace with symlink → `../../ai-docs/docs/workflow.instructions.md`)
- `.github/agents/` (remove — content already in `ai-docs/copilot-agents/`)

**Acceptance criteria:**

- All five `.github/instructions/*.instructions.md` files are per-entry relative symlinks
- `readlink .github/instructions/base.instructions.md` returns `../../ai-docs/docs/base.instructions.md`
- Symlink targets exist and are readable
- `.github/agents/` is deleted
- `.github/prompts/`, `.github/workflows/`, and `.github/copilot-instructions.md` are untouched

**How to create:**

```bash
for f in base documentation frontend security workflow; do
  rm ".github/instructions/${f}.instructions.md"
  ln -s "../../ai-docs/docs/${f}.instructions.md" ".github/instructions/${f}.instructions.md"
done
rm -rf .github/agents
```

**Manual test _(waiveable)_:**

- [ ] `ls -la .github/instructions/` — all five files are symlinks
- [ ] `cat .github/instructions/frontend.instructions.md` — content readable
- [ ] `.github/agents/` no longer exists

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * replace .github/instructions with per-entry symlinks to ai-docs/docs"
```

---

### Task 6: Update `.github/copilot-instructions.md`

**Files:**

- `.github/copilot-instructions.md` (modify — slim down to a pointer)

**Acceptance criteria:**

- Retains project name, purpose, and tech stack summary (orientation only)
- All detailed coding standards, naming conventions, and architecture patterns removed — they live in `ai-docs/docs/` and auto-load via `.github/instructions/` symlinks
- Explicitly references `ai-docs/docs/` so a human reader knows where canonical content lives
- File length under 30 lines

**Manual test _(waiveable)_:**

- [ ] Open Copilot chat and ask about the project's commit format — Copilot answers correctly (instructions load via symlinks)

**Sync to `ai` remote:** run the **[Manual Sync Procedure](#manual-sync-procedure-tasks-16)** with:

```bash
msg="chore(workspace): * slim down copilot-instructions.md to a pointer"
```

---

### Task 7: Promote `aisync` into `.agents/scripts/aisync.sh`

**Files:**

- `.agents/scripts/aisync.sh` (create — canonical versioned script, extracted from `~/.functions`)
- `~/.functions` `aisync` (modify — thin wrapper that delegates to `.agents/scripts/aisync.sh`)

**Acceptance criteria:**

- `.agents/scripts/aisync.sh` contains the full `aisync` logic (all fixes from earlier session: `trap`, `git diff --cached --quiet` guard, error handling on `checkout ai-config`, timestamp in commit message, restore after branch switch)
- Script is executable (`chmod +x .agents/scripts/aisync.sh`)
- Script copies from `.agents/`, `ai-docs/`, and `ai-work/` (updated source dirs from Task 10 of original plan — now merged into this task)
- Script calls `sync-symlinks.sh` as its final step after a successful push (added in Task 8)
- `~/.functions` `aisync` becomes a one-liner that resolves the repo root and delegates:

```bash
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

- `source ~/.functions && aisync` from the repo root executes correctly
- The canonical logic lives in `.agents/scripts/aisync.sh` — `~/.functions` has zero business logic

**Manual test:**

- [ ] `source ~/.functions && aisync` — outputs "nothing changed" or pushes successfully
- [ ] `.agents/`, `ai-docs/`, `ai-work/` are intact after running (branch switch does not delete them)
- [ ] `git log ai/main --oneline -3` — remote reflects expected state

**Commit:**

```bash
git commit -m "chore(workspace): * promote aisync into .agents/scripts/aisync.sh"
```

---

### Task 8: Write `sync-symlinks.sh` and the `sync-symlinks` Claude skill

**Files:**

- `.agents/scripts/sync-symlinks.sh` (create — per-entry symlink reconciliation script)
- `.agents/skills/sync-symlinks/SKILL.md` (create — Claude skill that invokes the script)

**Acceptance criteria for `sync-symlinks.sh`:**

The script implements the specboot 5-step state-machine pipeline for each mirror surface:

- **Mirror surfaces managed:**
  - `.claude/agents/` → `.agents/agents/`
  - `.claude/commands/` → `.agents/commands/`
  - `.claude/memory/` → `.agents/memory/`
  - `.claude/skills/` → `.agents/skills/`
  - `.cursor/agents/` → `.agents/agents/`
  - `.cursor/skills/` → `.agents/skills/`
  - `.github/instructions/` → `ai-docs/docs/` (only `*.instructions.md` files)

- **Entry classification (per entry in the mirror dir):**
  - `linked` — valid symlink pointing to an existing canonical entry → no action
  - `broken` — symlink whose target does not exist → remove and recreate
  - `orphan` — symlink pointing to a deleted canonical entry → remove
  - `conflict` — real file/dir sharing a name with a canonical entry → log, skip (never auto-delete real files)
  - `external` — real file/dir with no canonical counterpart → leave completely untouched

- **Actions computed per canonical entry:**
  - `to_add` — exists in canonical, missing in mirror → create relative symlink
  - `to_fix` — exists in mirror as broken symlink → remove and recreate
  - `to_remove` — orphaned symlink in mirror, no canonical counterpart → remove

- **Post-sync verification:** confirm every canonical entry has a valid symlink in each mirror surface; print a summary of actions taken and any conflicts requiring manual review

- Script is executable, accepts an optional repo root argument (defaults to `git rev-parse --show-toplevel`), and produces clear stdout output for each action

**Acceptance criteria for `sync-symlinks` SKILL.md:**

- Skill description explains when to invoke: "when a new agent, skill, command, memory entry, or instruction file is added or removed from a canonical directory and mirror symlinks need updating"
- Skill instructs Claude to: run `bash .agents/scripts/sync-symlinks.sh` from the repo root, read stdout, surface any `conflict` or `to_skip` entries to the user for manual resolution
- Skill is registered in `.agents/skills/` so it appears in Claude's skill list

**Manual test:**

- [ ] Add a dummy file to `.agents/agents/test-agent.md`, run `bash .agents/scripts/sync-symlinks.sh` — file appears as symlinks in `.claude/agents/` and `.cursor/agents/`
- [ ] Remove the dummy file, run the script again — orphaned symlinks are removed from both mirrors
- [ ] Run the script with no changes — output shows "nothing to do" or all entries as `linked`

**Commit:**

```bash
git commit -m "chore(workspace): * add sync-symlinks script and Claude skill"
```

---

### Task 9: Add `sync-symlinks` Copilot prompt

**Files:**

- `.github/prompts/sync-symlinks.prompt.md` (create — Copilot equivalent of the `sync-symlinks` skill)

**Acceptance criteria:**

- Prompt frontmatter follows existing `.github/prompts/` convention (`name`, `description` fields)
- Body instructs Copilot to run `bash .agents/scripts/sync-symlinks.sh` from the repo root
- Surfaces `conflict` entries to the user for manual review
- Consistent in scope and behaviour with the Claude `sync-symlinks` SKILL.md

**Manual test _(waiveable)_:**

- [ ] File exists at `.github/prompts/sync-symlinks.prompt.md`
- [ ] Content is coherent and follows the format of existing prompt files in that directory

**Commit:**

```bash
git commit -m "chore(workspace): * add sync-symlinks Copilot prompt"
```

---

### Task 10: Update `CLAUDE.md` path references

**Files:**

- `.claude/CLAUDE.md` (modify — update all path references)

**Acceptance criteria:**

- All references to `.claude/memory/` updated to `.agents/memory/`
- All references to `.ai/plans/` updated to `ai-work/plans/`
- All references to `.ai/decisions/`, `.ai/guidelines/`, `.ai/sessions/` etc. updated to new locations
- References to `.github/instructions/` updated to `ai-docs/docs/`
- No references to the old `.ai/` root remain
- Memory topic file table links to correct relative paths

**Manual test _(waiveable)_:**

- [ ] Open Claude Code — no broken path warnings on startup
- [ ] `grep -r '\.ai/' .claude/CLAUDE.md` — empty output

**Commit:**

```bash
git commit -m "chore(workspace): * update CLAUDE.md path references to new scaffold layout"
```

---

### Task 11: Remove the old `.ai/` directory

**Files:**

- `.ai/` (remove — all content verified present in `ai-docs/` and `ai-work/`)

**Acceptance criteria:**

- Run final diffs before deleting: `diff -r .ai/guidelines ai-docs/guidelines`, `diff -r .ai/plans ai-work/plans`, etc. — all empty
- `.ai/` directory no longer exists at the repo root
- `.git/info/exclude` entry for `.ai` removed

**Manual test _(waiveable)_:**

- [ ] `ls .ai` — "No such file or directory"
- [ ] `ls ai-docs ai-work` — both present with all expected subdirectories
- [ ] Open Claude Code — no missing path errors

**Commit:**

```bash
git commit -m "chore(workspace): * remove legacy .ai directory after migration"
```

---

### Task 12: Update `.git/info/exclude`

**Files:**

- `.git/info/exclude` (modify)

**Acceptance criteria:**

- `.agents/` added
- `ai-docs/` added
- `ai-work/` added
- `.cursor/` added
- `.ai/` entry removed (directory is gone)
- `.claude/` and `.github/` entries reviewed and retained if present
- `git status` shows none of the new dirs as untracked

**Manual test _(waiveable)_:**

- [ ] `git status` — `.agents/`, `ai-docs/`, `ai-work/`, `.cursor/` do not appear
- [ ] `cat .git/info/exclude` — all four new dirs listed

**Commit:**

```bash
git commit -m "chore(workspace): * update .git/info/exclude for new scaffold directories"
```

---

### Task 13: Update internal cross-references in migrated files

**Files:**

- `ai-docs/copilot-agents/frontend-developer.agent.md` (modify — update path refs)
- `ai-docs/copilot-agents/knowledge-keeper.agent.md` (modify — update path refs)
- `ai-docs/docs/README.md` (modify — update path refs, was `.ai/README.md`)
- Any file in `ai-work/` or `ai-docs/` hardcoding `.ai/`, `.claude/`, or `.github/instructions/` paths

**Acceptance criteria:**

- `.ai/plans/` → `ai-work/plans/`
- `.ai/sessions/` → `ai-work/sessions/`
- `.ai/decisions/` → `ai-docs/decisions/`
- `.ai/guidelines/` → `ai-docs/guidelines/`
- `.github/instructions/` → `ai-docs/docs/`
- `.claude/memory/` → `.agents/memory/`
- Grep confirms no stale refs remain

**Manual test _(waiveable)_:**

- [ ] `grep -r '\.ai/' ai-docs/ ai-work/ .agents/ --include="*.md"` — empty output
- [ ] `grep -r '\.github/instructions' ai-docs/ ai-work/ --include="*.md"` — empty output

**Commit:**

```bash
git commit -m "chore(workspace): * update internal cross-references to new scaffold paths"
```

---

## Phase 2 Tasks (separate milestone — begin only after Phase 1 is complete and verified)

---

### Task 14: Audit memory entries vs. guideline files — produce deduplication map

**Files:**

- Read-only audit — no file changes

**Acceptance criteria:**

- Read all 40+ files in `.agents/memory/`
- Read `ai-docs/guidelines/stencil-best-practices.md`, `ai-docs/guidelines/stencil-unit-testing-patterns.md`, `ai-docs/guidelines/code-practices-&-dev-guidelines.md`
- Produce deduplication map at `ai-work/sessions/YYYY-MM-DD-memory-consolidation-audit.md` with columns:
  - Memory file name
  - Overlap status: `duplicate` / `partial` / `unique`
  - Action: `delete` / `promote then delete` / `keep`
- User reviews and approves the map before Task 15 begins

---

### Task 15: Promote unique memory content into guideline files

**Files:**

- `ai-docs/guidelines/stencil-best-practices.md` (modify)
- `ai-docs/guidelines/stencil-unit-testing-patterns.md` (modify)
- `ai-docs/guidelines/code-practices-&-dev-guidelines.md` (modify)

**Acceptance criteria:**

- All `promote then delete` memory content integrated into the correct guideline section
- No content lost — new sections created where no existing section fits
- Promoted content integrated into narrative, not appended as a raw list

**Commit:**

```bash
git commit -m "chore(workspace): * promote memory entries into guideline files"
```

---

### Task 16: Delete redundant memory entries and update MEMORY.md

**Files:**

- `.agents/memory/*.md` (delete — `duplicate` and `promote then delete` entries)
- `.agents/memory/MEMORY.md` (modify — remove deleted entries; add pointers to guideline sections)

**Acceptance criteria:**

- All `duplicate` and `promote then delete` memory files deleted
- `MEMORY.md` no longer references deleted files
- `MEMORY.md` adds pointer entries for promoted content (e.g. "Stencil async rendering — see `ai-docs/guidelines/stencil-best-practices.md#async-rendering`")
- `unique` memory files untouched

**Commit:**

```bash
git commit -m "chore(workspace): * remove redundant memory entries consolidated into guidelines"
```

---

### Task 17: Finalize `copilot-instructions.md` consolidation

**Files:**

- `.github/copilot-instructions.md` (modify — remove remaining duplicated sections)
- `ai-docs/docs/` files (modify if needed — ensure unique content is present before removing from pointer file)

**Acceptance criteria:**

- `.github/copilot-instructions.md` contains only project orientation and a reference to `ai-docs/docs/`
- All unique content present in the correct `ai-docs/docs/` file
- Copilot answers correctly for commit format, naming conventions, and token usage

**Commit:**

```bash
git commit -m "chore(workspace): * finalize copilot-instructions consolidation"
```

---

## Verification checklist (end of Phase 1)

Run these after Task 13 before declaring Phase 1 complete:

```bash
# Per-entry symlinks resolve in all mirror surfaces
ls -la .claude/agents/ .claude/commands/ .claude/memory/ .claude/skills/
ls -la .cursor/agents/ .cursor/skills/
ls -la .github/instructions/

# Canonical scripts exist and are executable
ls -la .agents/scripts/aisync.sh .agents/scripts/sync-symlinks.sh

# No stale path references
grep -r '\.ai/' ai-docs/ ai-work/ .agents/ .claude/CLAUDE.md --include="*.md"
grep -r '\.github/instructions' ai-docs/ ai-work/ --include="*.md"
grep -r '\.claude/agents\|\.claude/memory\|\.claude/skills' ai-docs/ ai-work/ --include="*.md"

# Old .ai is gone
ls .ai 2>&1 | grep "No such file"

# git status is clean
git status

# aisync still works
source ~/.functions && aisync
```
