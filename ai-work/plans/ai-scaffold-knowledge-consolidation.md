# AI Scaffold — Knowledge Base Consolidation

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Close the gaps in the AI scaffold's knowledge flow so every session enters with full context, produces durable artifacts, and promotes discoveries upstream. The structural scaffold (directories, symlinks, subagent files) is handled by `ai-scaffold-restructure.md`. This plan owns the knowledge layer: memory architecture, guideline–skill wiring, duplicate content, and governance commands.

**Scope:**
- Phase 0 — Bootstrap automation (worktree AI file restore)
- Phase 1 — Memory architecture clarification (three-tier model, worker subagent instructions)
- Phase 2 — Knowledge base consolidation (code-review dedup, stencil-best-practices dedup, dev-standards wiring)
- Phase 3 — `ai-work` folder governance (`research/`, `tickets/` writers)
- Phase 4 — `knowledge-keeper` repair and skill wiring
- Phase 5 — `/sync-knowledge` governance skill

**Prerequisites:** `ai-scaffold-restructure.md` Phase 1 complete (canonical dirs and symlinks exist).

---

## Three-Tier Memory Model (reference throughout)

| Tier | Location | Scope | Created by | Read by |
|---|---|---|---|---|
| **User auto-memory** | `~/.claude/projects/…/memory/` | User, cross-project | Claude Code auto-memory | Claude Code on every session load |
| **Per-subagent memory** | `.claude/agent-memory/<name>/` | Project, per-subagent | Claude Code via `memory: project` frontmatter (lazily on first write) | That subagent, on every invocation (CC auto-loads `MEMORY.md`) |
| **Team curated memory** | `.agents/memory/` | Project, shared | `knowledge-keeper` only | All agents (must be explicitly instructed to read `MEMORY.md`) |

---

## Progress

| Task | Status | Notes |
|---|---|---|
| Task 1 — bootstrap.sh | ✅ Done | |
| Task 2 — Memory Management sections in worker subagents | ✅ Done | |
| Task 3 — Three-tier memory ADR | ⏳ Not started | |
| Task 4 — Consolidate code-review checklists | ⏳ Not started | |
| Task 5 — Stencil-best-practices vs dev-standards dedup | ⏳ Not started | |
| Task 6 — Wire dev-standards into knowledge skills | ⏳ Not started | |
| Task 7 — ai-work/research/ writer | ⏳ Not started | |
| Task 8 — ai-work/tickets/ governance | ⏳ Not started | |
| Task 9 — Fix knowledge-keeper tools | ⏳ Not started | |
| Task 10 — Wire knowledge-keeper into finishing-a-development-branch | ⏳ Not started | |
| Task 11 — Wire knowledge-keeper into create-component | ⏳ Not started | |
| Task 12 — /sync-knowledge skill | ⏳ Not started | |

---

## Phase 0 — Bootstrap Automation

### Task 1: Write `bootstrap.sh`

**Context:** `SETUP.md` documents a 5-step manual setup. Step 3 (restore AI files from `ai-config`) must be repeated for every new git worktree. Currently the user has to remember and re-run it manually. A `bootstrap.sh` makes this idempotent and self-contained.

**Files:**
- `.agents/scripts/bootstrap.sh` (create)
- `.agents/SETUP.md` (modify — replace manual step commands with `bootstrap.sh` invocation)

**Acceptance criteria for `bootstrap.sh`:**

The script is idempotent and organised into three scopes, run in order:

**Scope 1 — Machine** (runs once per developer machine; skips if already done):
- Detects whether the `aisync` shell function exists in `~/.functions` (grep for `function aisync`); if missing, appends the thin-wrapper block from `SETUP.md §5`
- Detects whether `~/.functions` is sourced by `~/.zshrc` or `~/.bashrc`; if not, prints a reminder (does not auto-modify shell config)
- Scope guard: skip if `type aisync 2>/dev/null` succeeds

**Scope 2 — Repository** (runs once per clone; skips if already done):
- Adds the `ai` remote (`git remote add ai https://github.com/dgonzalezts/boreal-ds-ai.git`) if not present (`git remote | grep -q '^ai$'`)
- Writes the `git aiboot` alias to `.git/config` so any worktree in this clone can run `git aiboot` instead of the full script path:
  ```
  [alias]
    aiboot = "!bash \"$(git rev-parse --git-common-dir)/../.agents/scripts/bootstrap.sh\""
  ```
  Note: `--git-common-dir` resolves to the main repo's `.git/` even from a worktree, so the alias always finds `bootstrap.sh` regardless of which worktree it is run from.
- Updates `.git/info/exclude` with all scaffold dirs (`.agents/`, `ai-docs/`, `ai-work/`, `.claude/`, `.cursor/`, `.github/`) if not already present
- Scope guard: skip each step individually if already done

**Scope 3 — Worktree** (runs per worktree; always executes the restore if needed):
- Checks whether `.agents/` exists in the current directory
- If missing: fetches `ai` remote (`git fetch ai`) and runs the three-command restore from `SETUP.md §3`:
  ```bash
  git checkout ai/main -- .agents ai-docs ai-work .claude .cursor .github
  git rm --cached -r .agents ai-docs ai-work .claude .cursor .github
  ```
- If present: prints "AI scaffold already present — skipping restore"
- After restore: runs `bash .agents/scripts/sync-symlinks.sh` to repair any broken symlinks

**Additional requirements:**
- Executable (`chmod +x .agents/scripts/bootstrap.sh`)
- Clear stdout per scope: `[machine] …`, `[repo] …`, `[worktree] …` prefixes
- Safe to run multiple times without side effects
- Works from any directory inside the repo (uses `git rev-parse --show-toplevel`)

**`SETUP.md` changes:**
- Steps 2–5 collapse to: "Run `.agents/scripts/bootstrap.sh` from inside the repo root. For subsequent worktrees: `git aiboot`."
- Keep Step 1 (clone) as-is — bootstrap cannot clone the repo it lives in
- Keep the "Daily workflow" and "Amending" sections unchanged

**Manual test:**
- [ ] Delete `.agents/` from a test worktree; run `git aiboot` — scaffold restored, symlinks repaired, no errors
- [ ] Run `git aiboot` again immediately — all three scopes report "already done" or skip cleanly
- [ ] `type aisync` in a new shell tab — resolves correctly after sourcing `~/.functions`

---

## Phase 1 — Memory Architecture Clarification

### Task 2: Fix "Memory Management" sections in worker subagents

**Context:** All four worker subagents (`frontend-subagent`, `testing-subagent`, `documentation-subagent`, `release-subagent`) have a "Memory Management" section that says "read your agent memory at `.claude/agent-memory/<name>/`". This is technically correct but misleading — it implies the subagent manually manages that directory. In reality, Claude Code handles it automatically via `memory: project` in the frontmatter: the directory is created lazily on first write, and the first 200 lines of its `MEMORY.md` are injected into the subagent's context at every invocation.

The sections also say nothing about the team memory store at `.agents/memory/MEMORY.md`, which carries cross-cutting constraints that every subagent should consult.

**Files:**
- `.agents/agents/frontend-subagent.md` (modify)
- `.agents/agents/testing-subagent.md` (modify)
- `.agents/agents/documentation-subagent.md` (modify)
- `.agents/agents/release-subagent.md` (modify)

**Acceptance criteria:** Replace the existing `## Memory Management` section in each subagent with the following block, substituting `<name>` for the actual subagent name:

```markdown
## Memory Management

This subagent has two memory sources:

**1. Per-scope memory (auto-managed by Claude Code)**
The `memory: project` frontmatter directive instructs Claude Code to manage a memory directory at `.claude/agent-memory/<name>/`. This directory is created automatically on first write. At every invocation, Claude Code injects the first 200 lines of `.claude/agent-memory/<name>/MEMORY.md` into your context — you do not need to read it manually.

Use this memory to accumulate scope-specific learnings: component file paths, Stencil quirks, test helper locations, build command patterns. Update `MEMORY.md` after completing a task if you discovered something non-obvious.

**2. Team memory (read explicitly)**
Before starting any task, read the team memory index at `.agents/memory/MEMORY.md`. This is the shared, curated store of cross-cutting constraints, verified patterns, and non-obvious facts that apply across all agents. It is not auto-loaded — you must read it.

**Promotion rule:** if a per-scope discovery is non-obvious and would benefit any other agent or team member (not just this subagent's next session), it belongs in `.agents/memory/`, not only here. Mention it in your response so the user can invoke `knowledge-keeper` to promote it.
```

**Manual test:**
- [ ] `grep -A 20 "## Memory Management" .agents/agents/frontend-subagent.md` — new block present
- [ ] `grep "agent-memory" .agents/agents/frontend-subagent.md` — returns the `.claude/agent-memory/frontend-subagent/` line in context (not a phantom instruction)
- [ ] `grep "\.agents/memory/MEMORY.md" .agents/agents/frontend-subagent.md` — match found

---

### Task 3: Write a three-tier memory architecture ADR

**Context:** The three-tier model (user auto-memory / per-subagent `memory: project` / team curated `.agents/memory/`) was designed across multiple sessions and has never been documented as a decision. Future contributors (human or AI) will re-litigate it without this record.

**Files:**
- `ai-docs/decisions/` — find the next available ADR number by listing existing files
- `ai-work/sessions/2026-06-12-memory-architecture.md` (create — session summary for this decision)

**Acceptance criteria for the ADR:**

- **Title:** `Use a three-tier memory architecture for AI scaffold knowledge`
- **Status:** `Accepted`
- **Context section:** explains why a single flat memory was insufficient (team vs user scope, per-subagent vs cross-cutting, auto-managed vs curated)
- **Options considered:**
  1. MCP knowledge graph server (`@modelcontextprotocol/servers/memory`) — rejected: opaque JSONL, not git-diff-friendly, requires running server, overkill for ~20 topic files
  2. Single flat `.agents/memory/` — rejected: conflates user-scoped preferences with team knowledge; can't capture per-subagent session learnings cheaply
  3. Three-tier model (chosen) — with the tier table from this plan's reference section
- **Decision:** three-tier model as documented
- **Consequences:**
  - Each tier has a single writer (CC auto-memory / the subagent itself / knowledge-keeper)
  - `knowledge-keeper` is the promotion mechanism between tier 2 and tier 3
  - `.claude/agent-memory/` dirs are lazily created by CC — absence does not indicate misconfiguration
  - `aisync.sh` syncs `.claude/` (which includes `agent-memory/`) to the `ai` remote, making tier-2 memory team-visible

**Manual test:**
- [ ] ADR file exists at `ai-docs/decisions/NNNN-three-tier-memory-architecture.md`
- [ ] Session summary exists at `ai-work/sessions/2026-06-12-memory-architecture.md`

---

## Phase 2 — Knowledge Base Consolidation

### Task 4: Consolidate code-review checklists to one canonical source

**Context:** Three copies of the code-review checklist exist:
1. `ai-docs/guidelines/code-review-checklist.md`
2. `ai-docs/guidelines/code_review_checklist.md` (underscore variant — likely identical or near-identical)
3. `.agents/skills/code-reviewer/references/coding_standards.md` (157-line parallel summary)

**Files:**
- `ai-docs/guidelines/code-review-checklist.md` (modify — canonical; merge unique content from the other two)
- `ai-docs/guidelines/code_review_checklist.md` (delete — after content merge)
- `.agents/skills/code-reviewer/references/coding_standards.md` (modify — replace body with one-line pointer to canonical checklist; keep the file so the skill's `references/` directory structure is preserved)
- `.agents/skills/code-reviewer/SKILL.md` (verify — confirm it references the correct path after changes)

**Acceptance criteria:**
- Read all three files; identify unique content in each
- Merge unique content into `ai-docs/guidelines/code-review-checklist.md` without duplicating
- Rename `code_review_checklist.md` to a redirect stub: one line pointing to the canonical file, or delete it if no other file references it by that name (grep first)
- `coding_standards.md` body becomes: "See the canonical checklist at [`ai-docs/guidelines/code-review-checklist.md`](../../../../ai-docs/guidelines/code-review-checklist.md)." (preserve the file for skill path stability)
- `grep -r "code_review_checklist" .agents/ ai-docs/ ai-work/` — only matches the stub itself or references that now point to the canonical file

**Manual test:**
- [ ] One canonical checklist exists and contains all non-duplicate content from the three originals
- [ ] `coding_standards.md` is a one-line pointer, not a 157-line parallel copy
- [ ] Code-reviewer skill still loads without errors

---

### Task 5: Audit and dedup `stencil-best-practices.md` vs `development-standards.md §1`

**Context:** `ai-docs/guidelines/stencil-best-practices.md` (736 lines) duplicates 6 sections from `development-standards.md §1`: naming conventions, member ordering, mixin architecture, `IComponent.ts` contract, `IFormControl<T>`, and FACE. The canonical rule should live in one place; the other file should delegate.

**Files:**
- Read-only audit — no file changes in this task; produces a dedup map only

**Acceptance criteria:**
- Read both files in full
- Produce `ai-work/sessions/2026-06-12-stencil-bestpractices-dedup.md` with a table:

| Section | In `stencil-best-practices.md` | In `development-standards.md` | Unique content? | Action |
|---|---|---|---|---|
| … | lines X–Y | lines A–B | yes/no | keep in best-practices / delegate to dev-standards / merge |

- User reviews and approves the map before any edits are made (this task ends here)

---

### Task 6: Wire `development-standards.md` into knowledge skills

**Context:** The four domain knowledge skills (`stencil-component-knowledge`, `testing-knowledge`, `documentation-knowledge`, `infra-knowledge`) do not reference `development-standards.md`. A subagent loading these skills has no pointer to the project's primary rules document.

**Files:**
- `.agents/skills/stencil-component-knowledge/SKILL.md` (modify)
- `.agents/skills/testing-knowledge/SKILL.md` (modify)
- `.agents/skills/documentation-knowledge/SKILL.md` (modify)
- `.agents/skills/infra-knowledge/SKILL.md` (modify)

**Acceptance criteria:**

Add a `## Primary Reference` section at the top of each skill body (immediately after the frontmatter), before any existing sections:

```markdown
## Primary Reference

[`ai-docs/guidelines/development-standards.md`](../../../../ai-docs/guidelines/development-standards.md) is the project's primary rules document. Read the sections relevant to your task before starting. This skill provides scope-specific patterns and gotchas that complement — not replace — those rules.
```

For `stencil-component-knowledge` specifically, also add a pointer to `ai-docs/guidelines/stencil-best-practices.md` in the same section.

**Directional rule (applies to future edits):**
- **Procedures and patterns** (how to implement X step by step) → live in the knowledge skill
- **Rules, rationale, and constraints** (you must / you must not, and why) → live in `development-standards.md`

**Manual test:**
- [ ] `grep "Primary Reference" .agents/skills/stencil-component-knowledge/SKILL.md` — match found
- [ ] `grep "development-standards" .agents/skills/testing-knowledge/SKILL.md` — match found

---

## Phase 3 — `ai-work` Folder Governance

### Task 7: Give `ai-work/research/` a writer

**Context:** `ai-work/research/` contains 12 spike and analysis documents but no skill produces output there. Files were written ad hoc. Without a writer, new research goes wherever the current session saves it.

**Files:**
- `.agents/skills/brainstorming/SKILL.md` (modify — add research spike output path)

**Acceptance criteria:**
- Add a `## Output` section to the brainstorming skill that says: when a session produces a standalone research spike (technology comparison, API analysis, approach evaluation), save the output to `ai-work/research/YYYY-MM-DD-{slug}.md`
- Add the same output path note to `.agents/agents/knowledge-keeper.md`'s "Artifact Types" section (a new "Research Spike" type), with structure: **Goal**, **Options evaluated**, **Findings**, **Recommendation**, **Open questions**
- The research spike type sits between "Session Summary" and "Plan Document" in knowledge-keeper's classification table

**Manual test:**
- [ ] `grep "ai-work/research" .agents/skills/brainstorming/SKILL.md` — match found
- [ ] `grep "Research Spike" .agents/agents/knowledge-keeper.md` — match found

---

### Task 8: Give `ai-work/tickets/` a writer via `start-ticket` skill

**Context:** `ai-work/tickets/` contains 5 ticket brief documents but no skill produces output there. Ticket briefs are structured work summaries (scope, acceptance criteria, dependencies) written before a plan.

**Files:**
- `.agents/skills/writing-plans/SKILL.md` (modify — add ticket brief as a pre-plan step)

**Acceptance criteria:**
- Add a `## Pre-Plan: Ticket Brief` section to `writing-plans/SKILL.md` that describes: when a Jira ticket ID is provided, first write a ticket brief to `ai-work/tickets/<TICKET-ID>-{slug}.md` before producing the plan file
- Ticket brief structure: **Ticket**, **Goal**, **Scope** (in/out), **Acceptance criteria**, **Dependencies**, **Open questions**
- The plan file (in `ai-work/plans/`) then links to the ticket brief in its preamble
- If no ticket ID is provided, skip the ticket brief step

**Manual test:**
- [ ] `grep "ai-work/tickets" .agents/skills/writing-plans/SKILL.md` — match found
- [ ] Existing plan files are unaffected (no retrospective changes required)

---

## Phase 4 — `knowledge-keeper` Repair and Wiring

### Task 9: Fix `knowledge-keeper` tool declarations

**Context:** `knowledge-keeper.md` line 4 declares `mcp_memory_read_graph` and `mcp_memory_add_observations` in its `tools` field. No MCP server for this is configured in the project. `mcp_memory_read_graph` is not referenced anywhere in the agent body. `mcp_memory_add_observations` is referenced in Phase 5 as "optionally also persist… skip if unavailable" — it is treated as supplemental already.

Having non-existent tools in the `tools` field causes silent failures and pollutes the agent's tool list.

**Files:**
- `.agents/agents/knowledge-keeper.md` (modify)

**Acceptance criteria:**
- Remove `mcp_memory_read_graph` from the `tools` frontmatter field — it is not used anywhere in the workflow
- Remove `mcp_memory_add_observations` from the `tools` frontmatter field — the workflow already works without it; removing it from tools prevents silent failures while the body already handles its absence gracefully ("skip if unavailable")
- In the Phase 5 body, update the `mcp_memory_add_observations` reference: change "Optionally also persist memory entries using `mcp_memory_add_observations` (Claude Code only — skip if unavailable)" to "The user-scoped Claude Code auto-memory (`~/.claude/projects/…/memory/`) is managed separately by Claude Code's built-in memory system — no action required from this agent."
- Final `tools` line: `tools: Read, Write, Edit, Glob, Grep`

**Manual test:**
- [ ] `head -5 .agents/agents/knowledge-keeper.md` — `tools:` line contains no `mcp_` entries
- [ ] `grep "mcp_memory" .agents/agents/knowledge-keeper.md` — no matches

---

### Task 10: Wire `knowledge-keeper` into `finishing-a-development-branch`

**Context:** `finishing-a-development-branch` is the skill that closes out a development session. It is the natural trigger point for capturing what was learned. Currently no knowledge persistence step exists there.

**Files:**
- `.agents/skills/finishing-a-development-branch/SKILL.md` (read first, then modify)

**Acceptance criteria:**
- Read the skill in full before making any changes
- Add a final step to the skill's workflow (after PR creation, before sign-off):

```markdown
### Final step — Capture session learnings

Before closing the session, consider whether any of the following occurred:
- A non-obvious constraint was discovered (environment, build, API, test infrastructure)
- A decision was made with trade-offs that another contributor might re-litigate
- A recurring gotcha was encountered that isn't documented anywhere

If yes to any: invoke the `knowledge-keeper` agent to persist the finding. Pass a brief description of what was discovered and where; knowledge-keeper will classify and write the correct artifact type. This step is optional but strongly encouraged — undocumented discoveries are the primary source of repeated debugging sessions.
```

- Do not add mandatory steps — this is advisory, not blocking

**Manual test:**
- [ ] `grep "knowledge-keeper" .agents/skills/finishing-a-development-branch/SKILL.md` — match found
- [ ] The existing skill workflow is otherwise unchanged

---

### Task 11: Wire `knowledge-keeper` into `create-component`

**Context:** `create-component` is the SDLC entry point for new components. By the time it completes (three phases: brainstorming → plan → execution), significant implementation decisions have been made. These should be captured.

**Files:**
- `.agents/skills/create-component/SKILL.md` (read first, then modify)

**Acceptance criteria:**
- Read the skill in full before making any changes
- Add a `## Phase 4 — Knowledge Capture (optional)` section after Phase 3:

```markdown
## Phase 4 — Knowledge Capture (optional)

After the component is implemented and reviewed, invoke the `knowledge-keeper` agent to persist what was learned. Pass it a summary of:
- Any non-obvious Stencil patterns or FACE constraints encountered
- API decisions made (prop naming, event shape, slot structure) and the rationale
- Test setup quirks specific to this component type
- Anything that would save the next person 30+ minutes

Knowledge-keeper will classify the findings and write them to the appropriate artifact (ADR, memory entry, or guideline update). Per-subagent memory in `.claude/agent-memory/<name>/` captures session-level detail; this phase promotes cross-cutting findings to the team store.
```

**Manual test:**
- [ ] `grep "Phase 4" .agents/skills/create-component/SKILL.md` — match found
- [ ] `grep "knowledge-keeper" .agents/skills/create-component/SKILL.md` — match found

---

## Phase 5 — `/sync-knowledge` Governance Skill

### Task 12: Create the `sync-knowledge` skill

**Context:** Per-subagent memories accumulate in `.claude/agent-memory/<name>/MEMORY.md` over time. Some of those entries are cross-cutting — they would benefit all agents and team members, not just the originating subagent. Currently no mechanism exists to promote them to `.agents/memory/`. The `sync-knowledge` skill provides an on-demand governance command for this.

**Files:**
- `.agents/skills/sync-knowledge/SKILL.md` (create)

**Acceptance criteria:**

Frontmatter:
```yaml
name: sync-knowledge
description: "End-of-session knowledge governance. Scans per-subagent memory directories (.claude/agent-memory/<name>/MEMORY.md) for cross-cutting discoveries and promotes them to the team store (.agents/memory/) via knowledge-keeper. Run at the end of any multi-subagent session. Also produces a session summary in ai-work/sessions/."
```

Body sections:

**When to invoke:**
- End of any session where specialist subagents (frontend, testing, documentation, release) ran and may have written to their per-scope memories
- When the user asks "save what we learned" or "capture the session"
- After a debugging session that surfaced non-obvious constraints

**Step 1 — Scan per-subagent memories:**
For each of the four worker subagents, check whether `.claude/agent-memory/<name>/MEMORY.md` exists. If it does, read its contents and identify entries that are:
- Cross-cutting: relevant to more than one subagent or to a human developer
- Not already present in `.agents/memory/MEMORY.md`

**Step 2 — Classify:**
For each candidate entry, determine the right promotion target using knowledge-keeper's classification table:
- Non-obvious codebase constraint → `.agents/memory/` entry
- Decision with trade-offs → ADR in `ai-docs/decisions/`
- Gap in an existing guideline → guideline update

**Step 3 — Promote via knowledge-keeper:**
Invoke the `knowledge-keeper` agent with the classified list. knowledge-keeper writes the artifacts; this skill does not write to `.agents/memory/` directly.

**Step 4 — Session summary:**
Write a session summary to `ai-work/sessions/YYYY-MM-DD-{slug}.md` covering: what was built, which subagents ran, what was promoted to team memory, and any open questions.

**Step 5 — Report:**
Return a summary of what was promoted and where it was written. The user can then run `aisync` to push everything to the `ai` remote.

**Manual test:**
- [ ] `ls .agents/skills/sync-knowledge/SKILL.md` — exists
- [ ] Valid YAML frontmatter with `name` and `description`
- [ ] `bash .agents/scripts/sync-symlinks.sh` — appears as symlink in `.claude/skills/` and `.cursor/skills/`

---

## Verification Checklist (end of all phases)

```bash
# Phase 0
bash .agents/scripts/bootstrap.sh    # runs clean, all scopes pass or skip
git aiboot                           # alias resolves (from any worktree)

# Phase 1
grep "\.agents/memory/MEMORY.md" .agents/agents/frontend-subagent.md
grep "mcp_memory" .agents/agents/knowledge-keeper.md || echo "clean"

# Phase 2
ls ai-docs/decisions/ | grep "three-tier-memory"
grep "Primary Reference" .agents/skills/stencil-component-knowledge/SKILL.md
grep "ai-work/research" .agents/skills/brainstorming/SKILL.md

# Phase 3
ls .agents/skills/sync-knowledge/SKILL.md

# Phase 4
grep "knowledge-keeper" .agents/skills/create-component/SKILL.md
grep "knowledge-keeper" .agents/skills/finishing-a-development-branch/SKILL.md

# Symlinks up to date
bash .agents/scripts/sync-symlinks.sh
ls -la .claude/skills/ | grep sync-knowledge
```
