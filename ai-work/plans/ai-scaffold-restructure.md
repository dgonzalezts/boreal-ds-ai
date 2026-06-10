# AI Scaffold Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Restructure the AI scaffold from three ad-hoc folders (`.ai/`, `.claude/`, `.github/`) into three semantically clean canonical directories (`.agents/`, `ai-docs/`, `ai-work/`), with `.claude/`, `.cursor/`, and `.github/instructions/` as per-entry symlink facades, `aisync` promoted into a versioned shell script inside `.agents/`, and a `sync-symlinks` skill for on-demand symlink repair.

**Architecture:** `.agents/` is the canonical SSoT for all AI tooling (agents, skills, commands, memory, scripts). `ai-docs/` is the canonical SSoT for persisting knowledge (guidelines, decisions, diagrams, instructions). `ai-work/` holds all temporary work artifacts (plans, reviews, sessions, tickets, qa, research). Mirror directories (`.claude/`, `.cursor/`, `.github/instructions/`) contain **per-entry relative symlinks** pointing into the canonical dirs — following the specboot pattern where each agent/skill/instruction file gets its own symlink, so unmanaged entries in mirror dirs are never touched. A `sync-symlinks` skill drives symlink repair on demand. A Phase 2 consolidation pass deduplicates memory entries against guideline files. A Phase 3 build introduces a specialist subagent architecture with four domain knowledge skills, four specialist subagent files, Node.js version management hooks, and a `create-component` SDLC entry point skill.

**Tech Stack:** bash (symlinks via `ln -s`, shell scripts), zsh shell functions (`~/.functions` as thin wrapper), git (`ai-config` branch, `ai` remote), Claude Code skills (SKILL.md)

---

## Progress

| Task                 | Status         | Notes                                                                                                                                 |
| -------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Tasks 1–13 (Phase 1) | ✅ Complete    | Canonical dirs, symlinks, aisync, sync-symlinks, CLAUDE.md                                                                            |
| Task 14              | ✅ Complete    | Audit written to `ai-work/sessions/2026-06-10-memory-consolidation-audit.md`                                                          |
| Task 15              | ✅ Complete    | 16 memory entries promoted into 3 guideline files (9 → stencil-best-practices, 3 → stencil-unit-testing-patterns, 4 → code-practices) |
| Task 16              | ⏳ Deferred    | Delete redundant memory files + update MEMORY.md — do after Phase 3                                                                   |
| Task 17              | ⏳ Deferred    | Finalize copilot-instructions consolidation — do after Phase 3                                                                        |
| Task 18              | ⏳ Not started | Create `with-node.sh` + `check-node-version.sh`                                                                                       |
| Tasks 19–22          | ⏳ Not started | Create 4 knowledge skills                                                                                                             |
| Tasks 23–26          | ⏳ Not started | Create 4 specialist subagent files                                                                                                    |
| Task 27              | ⏳ Not started | Repurpose `frontend-developer.md` as coordinator                                                                                      |
| Task 28              | ⏳ Not started | Update `writing-plans` + `executing-plans` skills                                                                                     |
| Task 29              | ⏳ Not started | Create `create-component` SDLC entry-point skill                                                                                      |
| Task 30              | ⏳ Not started | Run `sync-symlinks` to propagate new agents/skills into mirror dirs                                                                   |

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

### Phase 3 — Subagents Architecture (separate milestone, do not begin until Phase 1 is complete and verified)

| File                                                  | Notes                                                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `.agents/scripts/with-node.sh`                        | New — wraps commands with fnm Node.js activation; used in subagent system prompts                  |
| `.agents/scripts/check-node-version.sh`               | New — `PreToolUse` hook; warns when `pnpm`/`node` run without `with-node.sh` wrapper               |
| `.agents/skills/stencil-component-knowledge/SKILL.md` | New — domain knowledge skill for Stencil implementation; absorbs FACE + component API memory files |
| `.agents/skills/testing-knowledge/SKILL.md`           | New — domain knowledge skill for unit testing; absorbs testing memory files                        |
| `.agents/skills/documentation-knowledge/SKILL.md`     | New — domain knowledge skill for Storybook and MDX; absorbs storybook memory files                 |
| `.agents/skills/infra-knowledge/SKILL.md`             | New — domain knowledge skill for CI/release/build; absorbs infra memory files                      |
| `.agents/skills/create-component/SKILL.md`            | New — SDLC entry point; sequences brainstorming → writing-plans → executing-plans                  |
| `.agents/skills/writing-plans/SKILL.md`               | Modify — add `Executor` field to task template and executor mapping table                          |
| `.agents/skills/executing-plans/SKILL.md`             | Modify — replace `superpowers:subagent-driven-development` with local subagent dispatch protocol   |
| `.agents/agents/frontend-subagent.md`                 | New — specialist subagent for component implementation                                             |
| `.agents/agents/testing-subagent.md`                  | New — specialist subagent for unit tests; loads `testing-knowledge` + `mutations-testing` skills   |
| `.agents/agents/documentation-subagent.md`            | New — specialist subagent for Storybook stories and MDX docs                                       |
| `.agents/agents/release-subagent.md`                  | New — specialist subagent for CI/release/build/wrapper validation workflows                        |
| `.agents/agents/frontend-developer.md`                | Modify — repurpose as coordinator; document delegation rules; remove raw implementation detail     |

---

## Manual Sync Procedure (Tasks 1–6)

Until Task 7 updates `aisync` to include `.agents/`, `ai-docs/`, and `ai-work/`, run this single script to commit **and** push to the `ai` remote. Replace the `msg` value, then paste the whole block into one terminal run.

Uses a **git worktree** so the working directory is never touched — no branch switching, no snapshot/restore step, no risk of wiping local files.

```bash
(
  msg="update internal cross-references to canonical dir paths"

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

---

## Phase 3 Tasks (separate milestone — begin only after Phase 1 is complete and verified)

---

### Task 18: Create Node.js version management scripts

**Files:**

- `.agents/scripts/with-node.sh` (create)
- `.agents/scripts/check-node-version.sh` (create)

**Acceptance criteria:**

`with-node.sh`:

- Activates fnm and runs `fnm use` before exec-ing the given command
- Executable (`chmod +x`)
- Handles fnm not on PATH silently — does not abort the wrapped command
- Resolves repo root via `git rev-parse --show-toplevel` to locate `.node-version`
- Usage: `.agents/scripts/with-node.sh pnpm test`

`check-node-version.sh`:

- Used as a `PreToolUse` hook on `Bash` tool calls in subagent definitions
- Reads and discards JSON from stdin (required by Claude Code hook protocol)
- If the command contains `pnpm`, `npm`, or `node` without `.agents/scripts/with-node.sh` prefix, prints a one-line warning to stderr
- Always exits 0 — warn-only, never blocks execution
- Executable

**Manual test:**

- [ ] `.agents/scripts/with-node.sh node --version` — outputs `v22.x.x`
- [ ] `.agents/scripts/with-node.sh pnpm --version` — outputs `11.x.x`
- [ ] `echo '{"tool_input":{"command":"pnpm test"}}' | bash .agents/scripts/check-node-version.sh` — warning printed to stderr; exit code 0

**Commit:**

```bash
git commit -m "chore(workspace): * add Node.js version management scripts for subagent hooks"
```

---

### Task 19: Create domain knowledge skills

**Files:**

- `.agents/skills/stencil-component-knowledge/SKILL.md` (create)
- `.agents/skills/testing-knowledge/SKILL.md` (create)
- `.agents/skills/documentation-knowledge/SKILL.md` (create)
- `.agents/skills/infra-knowledge/SKILL.md` (create)

**Acceptance criteria:**

Each skill has YAML frontmatter (`name`, `description`) and a markdown body. The body consolidates content from the listed memory files — include the substance inline; reference the memory file path for material better read in full.

**`stencil-component-knowledge`:**

- `name: stencil-component-knowledge`
- `description:` "Domain knowledge for implementing Stencil web components in Boreal DS. Covers FACE (Form-Associated Custom Elements), component API conventions, props, events, slots, SCSS tokens, and light DOM patterns. Load proactively when implementing or reviewing Stencil components."
- Consolidates from: `stencil-face-attach-internals.md`, `stencil-face-element-proxy-limits.md`, `stencil-face-constraint-validation-pattern.md`, `stencil-async-rendering-gotchas.md`, `feedback_prop_validation_pattern.md`, `component-interface-file-naming.md`, `component-interface-content-rule.md`, `component-accessor-naming-conventions.md`, `feedback_event_options_explicit.md`, `component-bds-typography-group-labels.md`, `stencil-composite-light-dom-event-boundary.md`, `stencil-form-control-interfaces.md`
- References (do not duplicate): `ai-docs/guidelines/stencil-best-practices.md`, `ai-docs/guidelines/code-practices-&-dev-guidelines.md`, `ai-docs/docs/frontend.instructions.md`

**`testing-knowledge`:**

- `name: testing-knowledge`
- `description:` "Domain knowledge for writing unit tests for Stencil components in Boreal DS. Covers spec file organisation, FACE test mocks, child component props in tests, and the two-phase test quality gate (conventional coverage + mutation testing). Load proactively when writing or reviewing unit tests."
- Consolidates from: `test-spec-file-organisation.md`, `stencil-face-test-mocks.md`, `stencil-child-component-props-in-tests.md`, `mutation-testing-stryker-setup.md`, `mutation-testing-workflow-decisions.md`
- References: `ai-docs/guidelines/stencil-unit-testing-patterns.md`
- Must include a **Mutation Testing** section documenting the two-phase gate:
  1. Conventional unit tests pass ≥ 90% statement coverage — required before proceeding
  2. Invoke the `mutations-testing` skill; scope Stryker to the current component by following the reuse pattern in `packages/boreal-web-components/MUTATION_TESTING.md` (update `testMatch` and `mutate` paths, rename config, run, review surviving mutants, clean up — do not commit Stryker artefacts or `package.json` changes)
  3. Mutation score ≥ 90% — required before marking the testing task complete; score < 90% requires additional tests targeting surviving mutants before proceeding
- The `mutations-testing` skill is the executor for mutation runs — reference it by name, do not duplicate its content

**`documentation-knowledge`:**

- `name: documentation-knowledge`
- `description:` "Domain knowledge for writing Storybook stories and MDX documentation for Boreal DS components. Covers action wiring, source snippets for non-primitive props, and Vite build quirks. Load proactively when writing stories, MDX docs, or JSDoc."
- Consolidates from: `storybook-action-wiring-web-components.md`, `storybook-source-snippet-non-primitive-props.md`, `storybook-vite-quirks.md`
- References: `ai-docs/guidelines/storybook-patterns.md`, `ai-docs/guidelines/jsdoc-template.md`, `ai-docs/docs/documentation.instructions.md`

**`infra-knowledge`:**

- `name: infra-knowledge`
- `description:` "Domain knowledge for CI/CD, Turborepo pipelines, release workflows, build tooling, and framework wrapper validation in Boreal DS. Covers Turbo pty hang, Stencil dist copy, SCSS paths, scripts-boreal pipeline, release-it, Chromatic deployment, GitHub Actions debugging, and the validate:pack consumer simulation workflow. Load proactively for build, CI, release, or wrapper validation tasks."
- Consolidates from: `turbo-persistent-interactive-pty-hang.md`, `stencil-dist-copy-namespace-behavior.md`, `stencil-sass-inject-global-paths-constraint.md`, `sass-paths-windows-forward-slash.md`, `scripts-boreal-pack-pipeline.md`, `release-it-pnpm-publish.md`, `chromatic-deployment.md`, `github-actions-windows-debug-technique.md`, `nodejs-signal-handler-patterns.md`
- References: `ai-docs/guidelines/release-process.md`, `ai-docs/guidelines/scripts-boreal.md`, `ai-docs/guidelines/cicd-dependency-installation.md`
- Must include a **Wrapper Validation** section documenting the per-component consumer simulation workflow:
  - **Interactive validation** (`pnpm dev:pack:react`): add the new component to `examples/react-testapp/src/App.tsx` (import from `@telesign/boreal-react`; render with all key prop combinations — default state, all variants, disabled state, event binding, slot usage); run `pnpm dev:pack:react` from the monorepo root; verify in browser under all four brand themes (`data-theme` values: `connect`, `engage`, `protect`, `proximus`)
  - **Vue validation** (`pnpm dev:pack:vue` once available): add the same component to `examples/vue-testapp/src/App.vue` (import from `@telesign/boreal-vue`; verify `v-model` binding when applicable)
  - **CI validation**: run `pnpm validate:pack:react && pnpm validate:pack:vue` — both must succeed (exit 0) before the task is complete; these commands pack built artefacts into `.tgz` files, install them in the example apps, and run `pnpm build` to confirm the published package is consumable
  - **Cleanup**: remove test component usage from `App.tsx` and `App.vue` before committing — example apps are blank playgrounds, not persistent demos; `package.json` and `pnpm-lock.yaml` are auto-restored on pipeline exit but verify with `git status` before committing
  - Pipeline mechanics: `scripts-boreal/README.md` is the authoritative reference; do not duplicate its content

**Manual test _(waiveable)_:**

- [ ] `ls .agents/skills/{stencil-component-knowledge,testing-knowledge,documentation-knowledge,infra-knowledge}/SKILL.md` — all four exist
- [ ] Each SKILL.md has valid YAML frontmatter with `name` and `description`
- [ ] `bash .agents/scripts/sync-symlinks.sh` — four new skill symlinks appear in `.claude/skills/` and `.cursor/skills/`

**Commit:**

```bash
git commit -m "chore(workspace): * add domain knowledge skills for specialist subagents"
```

---

### Task 20: Create specialist subagent files

**Files:**

- `.agents/agents/frontend-subagent.md` (create)
- `.agents/agents/testing-subagent.md` (create)
- `.agents/agents/documentation-subagent.md` (create)
- `.agents/agents/release-subagent.md` (create)

**Acceptance criteria:**

All four files share the same structural pattern.

Required frontmatter fields in each:

- `name` — matches filename without `.md`
- `description` — one sentence with "Use proactively" phrasing (enables automatic Claude delegation)
- `model: claude-sonnet-4-5`
- `color` — unique per subagent (see table below)
- `skills` — list with one domain knowledge skill name
- `memory: project` — persistent memory stored at `.claude/agent-memory/<name>/`, versioned with the repo
- `hooks` — `PreToolUse` on `Bash` pointing to `.agents/scripts/check-node-version.sh`:
  ```yaml
  hooks:
    PreToolUse:
      - matcher: "Bash"
        hooks:
          - type: command
            command: ".agents/scripts/check-node-version.sh"
  ```

Required body sections in each:

- **Node.js Environment** — instructs the agent to prefix all `pnpm`, `npm`, and `node` commands with `.agents/scripts/with-node.sh`
- **Memory Management** — read agent memory before starting work; update memory after completing with new patterns, file paths, or architectural decisions discovered

Per-subagent configuration:

| Subagent                 | color  | skills                                   | description                                                                                                                                                                                                         |
| ------------------------ | ------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `frontend-subagent`      | green  | `[stencil-component-knowledge]`          | "Implements Stencil web components in Boreal DS — props, SCSS tokens, render(), lifecycle hooks, FACE, and JSDoc. Use proactively for any component implementation task."                                           |
| `testing-subagent`       | blue   | `[testing-knowledge, mutations-testing]` | "Writes and fixes unit tests for Stencil components in Boreal DS, enforces the two-phase quality gate (≥ 90% coverage then ≥ 90% mutation score). Use proactively when unit tests are needed, failing, or missing." |
| `documentation-subagent` | purple | `[documentation-knowledge]`              | "Creates Storybook stories (.stories.ts) and MDX documentation for Boreal DS components. Use proactively after component implementation."                                                                           |
| `release-subagent`       | orange | `[infra-knowledge]`                      | "Handles Boreal DS release workflows — Turborepo pipelines, CI scripts, framework wrapper validation (validate:pack), and package publishing. Use proactively for build, CI, release, or wrapper validation tasks." |

**Manual test _(waiveable)_:**

- [ ] `ls .agents/agents/{frontend,testing,documentation,release}-subagent.md` — all four exist
- [ ] Spot-check frontmatter: `head -20 .agents/agents/frontend-subagent.md` — `memory`, `skills`, `hooks` all present
- [ ] `bash .agents/scripts/sync-symlinks.sh` — four new symlinks in `.claude/agents/` and `.cursor/agents/`

**Commit:**

```bash
git commit -m "chore(workspace): * add specialist subagent files for component SDLC"
```

---

### Task 21: Repurpose frontend-developer.md as SDLC coordinator

**Files:**

- `.agents/agents/frontend-developer.md` (modify)

**Acceptance criteria:**

Frontmatter:

- `tools` field set to `Read, Write, Edit, Bash, Glob, Grep, Agent(frontend-subagent, testing-subagent, documentation-subagent, release-subagent)` — the `Agent()` whitelist only takes effect when this agent runs as the main thread via `claude --agent frontend-developer`; in all other invocations it serves as documentation
- `skills` field removed or cleared — raw implementation knowledge now lives in the specialist knowledge skills

Body rewritten to contain exactly:

- **Delegation rules** — table mapping task type to the correct subagent (same executor mapping table as in `writing-plans`)
- **Agent() restriction note** — subagents cannot spawn further subagents per Claude Code design; delegation via `Agent()` only works when `frontend-developer` is the main agent thread; in normal use the main conversation thread orchestrates
- **SDLC workflow** — full sequence: brainstorming → writing-plans → executing-plans; reference the `create-component` skill for end-to-end component creation
- No raw implementation details (component scaffold patterns, SCSS token usage, FACE patterns) — that knowledge belongs to `stencil-component-knowledge` loaded by `@frontend-subagent`

**Manual test _(waiveable)_:**

- [ ] `cat .agents/agents/frontend-developer.md` — body is delegation rules + workflow description; no raw implementation instructions
- [ ] `.claude/agents/frontend-developer.md` symlink still resolves (`cat` shows same content)

**Commit:**

```bash
git commit -m "chore(workspace): * repurpose frontend-developer agent as SDLC coordinator"
```

---

### Task 22: Update writing-plans and executing-plans skills

**Files:**

- `.agents/skills/writing-plans/SKILL.md` (modify)
- `.agents/skills/executing-plans/SKILL.md` (modify)

**Acceptance criteria for `writing-plans/SKILL.md`:**

Add an **Executor Mapping** table to the skill body immediately before the "Task Structure" section:

| Task type                                                        | Executor                  |
| ---------------------------------------------------------------- | ------------------------- |
| Type interfaces, scaffold, lifecycle, render(), JSDoc, SCSS      | `@frontend-subagent`      |
| Unit tests (all spec files)                                      | `@testing-subagent`       |
| Storybook story, MDX documentation                               | `@documentation-subagent` |
| Framework output targets, build scripts, CI fixes, release steps | `@release-subagent`       |
| Utility/config tasks with no component code                      | main thread (no executor) |

Add a mandatory `**Executor:**` field to the task template in "Task Structure", immediately after the `### Task N:` heading and before `**Files:**`:

```markdown
### Task N: [Deliverable Layer Name]

**Executor:** @frontend-subagent
**Files:** ...
```

The skill `description` must mention that plans must include `Executor` fields so `executing-plans` can dispatch correctly.

**Acceptance criteria for `executing-plans/SKILL.md`:**

Step 2 ("Execute Tasks") replaces the `superpowers:subagent-driven-development` reference with the local dispatch protocol:

1. Read the `**Executor:**` field on the current task
2. If `@<subagent>` is declared: compose a dispatch message containing task title, files, acceptance criteria, unit tests, manual test checklist, and commit message; invoke `@<subagent>: <message>`
3. If no executor declared: execute the task directly on the main thread
4. Wait for subagent output; review it against acceptance criteria; mark task done only when acceptance criteria are met

The "Integration" section at the bottom removes the `superpowers:` prefix from all skill references and uses local skill names only.

**Manual test _(waiveable)_:**

- [ ] `grep 'Executor Mapping' .agents/skills/writing-plans/SKILL.md` — match found
- [ ] `grep 'Executor' .agents/skills/writing-plans/SKILL.md` — appears in both the mapping table and the task template
- [ ] `grep 'superpowers' .agents/skills/executing-plans/SKILL.md` — no matches

**Commit:**

```bash
git commit -m "chore(workspace): * add Executor field to writing-plans; add subagent dispatch to executing-plans"
```

---

### Task 23: Create create-component skill

**Files:**

- `.agents/skills/create-component/SKILL.md` (create)

**Acceptance criteria:**

- `name: create-component`
- `description:` "Entry point for the full Boreal DS component SDLC. Sequences brainstorming → writing-plans → executing-plans for new component creation. Use when the user says 'create X component', 'implement bds-X', 'build a new Y', or provides a Figma design and asks what to do next. Do not use for bug fixes, token-only changes, or documentation-only updates — route those directly to the relevant subagent."

Body sections (in order):

**When to invoke** — clear trigger phrases; explicit cases where a direct subagent invocation is preferred over the full three-phase sequence (e.g. "only tests needed → invoke @testing-subagent directly")

**Phase 1 — Brainstorming** — invoke the `brainstorming` skill; output is shared understanding of scope, component classification (Atom/Molecule/Organism), public API surface (props, events, slots, CSS parts), Figma coverage confirmation, and accessibility requirements; does not produce a plan file

**Phase 2 — Writing the plan** — invoke the `writing-plans` skill; save to `ai-work/plans/<ticket-id>-<component-name>.md`; plan must include `Executor` fields on every task using the executor mapping table; confirm filename with the user before saving

**Phase 3 — Executing the plan** — invoke the `executing-plans` skill; it reads the saved plan and dispatches each task to the declared `@<executor>` subagent; review each task output before proceeding to the next

**Partial workflow** — three shortcut paths:

- Plan already exists → skip to Phase 3 only
- Only documentation needed → invoke `@documentation-subagent` directly
- Only tests needed → invoke `@testing-subagent` directly

The skill body must not duplicate content from `writing-plans` or `executing-plans` — reference them by name.

**Manual test _(waiveable)_:**

- [ ] `ls .agents/skills/create-component/SKILL.md` — exists
- [ ] Valid YAML frontmatter with `name` and `description`
- [ ] `bash .agents/scripts/sync-symlinks.sh` — appears as symlink in `.claude/skills/` and `.cursor/skills/`

**Commit:**

```bash
git commit -m "chore(workspace): * add create-component SDLC entry point skill"
```

---

### Task 24: Run sync-symlinks for all Phase 3 additions

**Files:**

- `.claude/agents/` (modify — new symlinks added by script)
- `.claude/skills/` (modify — new symlinks added by script)
- `.cursor/agents/` (modify — new symlinks added by script)
- `.cursor/skills/` (modify — new symlinks added by script)

**Acceptance criteria:**

- `bash .agents/scripts/sync-symlinks.sh` runs without errors from repo root
- All 4 new subagent files appear as valid symlinks in `.claude/agents/` and `.cursor/agents/`
- All 5 new skill directories (`stencil-component-knowledge`, `testing-knowledge`, `documentation-knowledge`, `infra-knowledge`, `create-component`) appear as valid symlinks in `.claude/skills/` and `.cursor/skills/`
- No `conflict` or broken entries in script output
- All existing symlinks (including `frontend-developer.md` and all pre-existing skills) remain valid and unchanged

**Manual test:**

- [ ] `ls -la .claude/agents/ | grep subagent` — four entries
- [ ] `ls -la .claude/skills/ | grep -E 'knowledge|create-component'` — five entries
- [ ] `cat .claude/agents/frontend-subagent.md` — content readable
- [ ] Open Claude Code — all 4 new subagents discoverable via `@` mention

**Commit:**

```bash
git commit -m "chore(workspace): * sync symlinks for Phase 3 subagent architecture additions"
```

---

## Verification checklist (end of Phase 3)

Run these after Task 24 before declaring Phase 3 complete:

```bash
# All specialist subagents exist
ls -la .agents/agents/{frontend,testing,documentation,release}-subagent.md

# All knowledge skills and create-component exist
ls -la .agents/skills/{stencil-component-knowledge,testing-knowledge,documentation-knowledge,infra-knowledge,create-component}/SKILL.md

# Node.js scripts exist and are executable
ls -la .agents/scripts/with-node.sh .agents/scripts/check-node-version.sh

# Subagents are symlinked in mirror surfaces
ls -la .claude/agents/ | grep subagent
ls -la .cursor/agents/ | grep subagent

# Knowledge skills are symlinked in mirror surfaces
ls -la .claude/skills/ | grep -E 'knowledge|create-component'
ls -la .cursor/skills/ | grep -E 'knowledge|create-component'

# frontend-developer is now a coordinator (delegation rules present, no raw impl detail)
grep 'Executor\|delegation\|SDLC' .agents/agents/frontend-developer.md

# writing-plans has Executor mapping table
grep 'Executor Mapping' .agents/skills/writing-plans/SKILL.md

# executing-plans has no superpowers references
grep 'superpowers' .agents/skills/executing-plans/SKILL.md || echo "clean"

# Spot-check: subagent content readable through symlink
cat .claude/agents/frontend-subagent.md | head -15
```
