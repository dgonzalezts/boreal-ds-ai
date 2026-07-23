---
name: feedback_claude_md_no_internal_jsdoc
description: .claude/CLAUDE.md's "JSDoc on exported public API only" rule overrides jsdoc-template.md's silence on internal-method JSDoc — strip all /** */ from non-public members, even valuable rationale comments
metadata:
  type: feedback
---

`ai-docs/guidelines/jsdoc-template.md` only mandates/forbids JSDoc for `@Prop()`, `@Event()`, `@Method()`, and the class-level block (description + `@slot`). It is silent on private/internal methods, render helpers, `@State()`, and `@Element()` — the CEM analyzer ignores those entirely, so there's no compiler-driven reason to add or remove JSDoc there.

But `.claude/CLAUDE.md` (project-level, marked as overriding default behavior) has a stricter, unconditional rule: *"No inline comments: no `//` or `/* */` explaining what code does. JSDoc on exported public API only."* When the user directs this rule to be applied literally, it wins over jsdoc-template.md's silence — **every** `/** */` block on a non-public member gets removed, including:

- `@State()` one-line descriptions
- `@Element()` ref comments
- Private/internal method and getter JSDoc, however long or valuable-looking (design-rationale blocks explaining *why*, not just *what*, still count — the rule has no length or "value" exception)
- Render-helper (`render*()`) JSDoc

**Why:** the user gave this instruction directly to the subagent on 2026-07-23 (bds-table.tsx had ~150 lines of detailed rationale JSDoc on private virtualization/pin-offset internals, several of which map 1:1 to bug-fix rationale already captured in `.claude/agent-memory/frontend-subagent/`). Note: when this same tension was first flagged mid-task, the coordinating session had NOT yet authorized the strip — the actual authorization came via a separate, direct instruction from the user straight to this subagent, a channel the coordinating session had no visibility into. That caused a legitimate mix-up (the coordinating session reverted the change, thinking it was unauthorized, before the user clarified). Takeaway for future sessions: if a user instructs a subagent directly rather than through the coordinator, the subagent's own report back should say so explicitly ("per your direct instruction to me") rather than just "confirmed by the user" — the coordinator has no way to distinguish that from an agent's own inference otherwise.

**How to apply:** On any future Boreal DS Stencil component task — not just bds-table — treat `@Prop()`/`@Event()`/`@Method()`/class-level-`@slot` as the *only* members allowed inline `/** */` documentation, but only once this direction is actually confirmed for the task at hand (this is a real interpretive choice about CLAUDE.md, not an automatic default — don't apply it unprompted). Flag it if you spot rationale JSDoc worth preserving before deleting (e.g. it may belong in a commit message, an ADR, or `.claude/agent-memory/`/`.agents/memory/` instead of inline source) — but do not leave it in the `.tsx` file once confirmed. Removing comments does not change runtime behavior — no test suite re-verification beyond a normal lint/tsc/test pass is needed for this class of edit alone.

This is a real, non-obvious tension between two guideline docs (jsdoc-template.md's silence vs. CLAUDE.md's blanket rule) that will recur on every future component task — worth promoting to `.agents/memory/` via `knowledge-keeper` so other subagents don't rediscover it independently.
