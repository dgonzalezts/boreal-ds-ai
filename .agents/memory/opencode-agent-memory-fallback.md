# OpenCode Has No Per-Agent Auto-Injected Memory

## The Gap

Claude Code's `memory: project` frontmatter directive gives a subagent its own scoped memory directory (`.claude/agent-memory/<name>/MEMORY.md`), auto-created on first write and auto-injected — the first 200 lines land in context on every invocation with zero effort from the agent or the user.

OpenCode has no equivalent capability. There is no per-agent auto-injected memory, scoped or otherwise, in OpenCode's agent model as of v1.18.22. This is a genuine capability loss when running the same subagents (`frontend-subagent`, `testing-subagent`, `documentation-subagent`, `qa-subagent`, `release-subagent`) under OpenCode instead of Claude Code — not a config translation gap that can be papered over.

## The Fallback Convention

Every OpenCode-generated agent file (`.opencode/agent/*.md`, produced by `.agents/scripts/generate-opencode-agents.py` from the canonical `.agents/agents/*.md`) carries an appended note pointing the agent at `.agents/memory/` — this repo's team-wide, manually-read memory store — and instructing it to:

1. Read the relevant topic files under `.agents/memory/` at the start of a task (starting from `.agents/memory/MEMORY.md`'s index).
2. Append new non-obvious learnings to the appropriate topic file at the end of a task, the same way `.claude/agent-memory/<name>/MEMORY.md` would have accumulated them under Claude Code.

## The Ergonomic Cost

This is explicitly a downgrade, not parity:

- No automatic injection — the agent must remember to read and must be told to, every time, rather than it simply arriving in context.
- No per-agent scoping — everything routes through the shared team store (`.agents/memory/`), which is coarser-grained than Claude Code's per-subagent directories.
- Easy to silently regress — if a future edit to the canonical `.agents/agents/*.md` files or the generator drops the appended note, an OpenCode session loses this behavior with no error, just quieter agents.

Do not treat this fallback as equivalent to Claude Code's behavior in any writeup, plan, or future memory entry — it is a mitigation for a missing capability, not a substitute for it.

## Source

AI-005 (OpenCode facade plan), Task 7. Confirmed no built-in alternative exists via live OpenCode session testing and OpenCode's own agent documentation.
