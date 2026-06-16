---
name: sync-knowledge
description: "End-of-session knowledge governance. Scans per-subagent memory directories (.claude/agent-memory/<name>/MEMORY.md) for cross-cutting discoveries and promotes them to the team store (.agents/memory/) via knowledge-keeper. Run at the end of any multi-subagent session. Also produces a session summary in ai-work/sessions/."
---

# Sync Knowledge

## When to Invoke

- End of any session where specialist subagents (frontend, testing, documentation, release) ran and may have written to their per-scope memories
- When the user says "save what we learned", "capture the session", or "sync knowledge"
- After a debugging session that surfaced non-obvious constraints
- After completing a plan where multiple subagents contributed

---

## Step 1 — Scan Per-Subagent Memories

For each of the four worker subagents, check whether `.claude/agent-memory/<name>/MEMORY.md` exists:

| Subagent | Memory path |
|---|---|
| frontend-subagent | `.claude/agent-memory/frontend-subagent/MEMORY.md` |
| testing-subagent | `.claude/agent-memory/testing-subagent/MEMORY.md` |
| documentation-subagent | `.claude/agent-memory/documentation-subagent/MEMORY.md` |
| release-subagent | `.claude/agent-memory/release-subagent/MEMORY.md` |

For each file that exists, read its contents and identify entries that are:
- **Cross-cutting** — relevant to more than one subagent or to a human developer
- **Not already present** in `.agents/memory/MEMORY.md`

Entries that are purely scope-specific (e.g. a file path only the frontend subagent will ever need) stay where they are.

---

## Step 2 — Classify

For each candidate entry, determine the right promotion target using knowledge-keeper's classification table:

| Signal | Target artifact |
|---|---|
| Non-obvious codebase or environment constraint | Memory entry in `.agents/memory/` |
| Decision with trade-offs and rejected alternatives | ADR in `ai-docs/decisions/` |
| Gap or error in an existing guideline | Guideline update |
| Evaluation of options, no decision yet | Research spike in `ai-work/research/` |

---

## Step 3 — Promote via `knowledge-keeper`

Invoke the `knowledge-keeper` agent with the classified list. Pass each candidate entry with:
- The original text from the per-subagent memory
- The target artifact type
- The subagent it came from

Knowledge-keeper writes the artifacts. This skill does not write to `.agents/memory/` directly.

---

## Step 4 — Session Summary

Write a session summary to `ai-work/sessions/YYYY-MM-DD-{slug}.md` covering:

- **What was built** — components, features, or fixes completed
- **Subagents that ran** — which specialist agents participated
- **Promoted to team memory** — list of entries moved to `.agents/memory/` or ADRs written
- **Open questions** — unresolved items needing a follow-up session

---

## Step 5 — Report

Return a summary to the user of:
- How many entries were scanned across the four memory files
- How many were promoted and to which artifact type
- Where each artifact was written

Then prompt the user to run `aisync . "docs(agents): sync session knowledge"` to push the updated scaffold to the `ai` remote.

---

## What This Skill Does Not Do

- Write directly to `.agents/memory/` — that is `knowledge-keeper`'s responsibility
- Modify per-subagent memory files — leave them as-is after scanning
- Promote entries that are already in the team store — check `.agents/memory/MEMORY.md` first
