---
name: create-component
description: Entry point for the full Boreal DS component SDLC. Sequences brainstorming → writing-plans → executing-plans for new component creation. Use when the user says "create X component", "implement bds-X", "build a new Y", or provides a Figma design and asks what to do next. Do not use for bug fixes, token-only changes, or documentation-only updates — route those directly to the relevant subagent.
---

# Create Component

## When to Invoke

**Use this skill when the user:**

- Says "create X component", "implement bds-X", "build a new Y", "I need a new component"
- Provides a Figma design and asks what to do next
- Asks to add a new component to the design system from scratch

**Skip to a subagent directly when:**

- Only tests are needed → invoke `@testing-subagent` directly
- Only documentation is needed → invoke `@documentation-subagent` directly
- Only a bug fix is needed → invoke `@frontend-subagent` directly with the issue
- A plan already exists → skip to Phase 3 only

---

## Phase 1 — Brainstorming

Load and follow the `brainstorming` skill.

Output of this phase:

- Shared understanding of scope and component classification (Atom / Molecule / Organism)
- Public API surface defined: props (with types and defaults), events, slots, CSS parts
- Figma coverage confirmed: all states, variants, slots, and all four brand themes present
- Accessibility requirements identified: ARIA roles, keyboard interactions, screen reader behaviour
- Component category selected (one of the 12 official categories in `apps/boreal-docs/plopfile.js`)

This phase does not produce a plan file. It produces shared understanding that feeds Phase 2.

---

## Phase 2 — Writing the Plan

Load and follow the `writing-plans` skill.

Save the plan to `ai-work/plans/<ticket-id>-<component-name>.md`. Confirm the filename with the user before saving.

**Every task in the plan must include an `**Executor:**` field** using the executor mapping table from `writing-plans`. Do not produce a plan without executor fields — `executing-plans` uses them to dispatch.

---

## Phase 3 — Executing the Plan

Load and follow the `executing-plans` skill.

It reads the saved plan and dispatches each task to its declared `@<executor>` subagent. Review each task output against its acceptance criteria before proceeding to the next task.

---

## Phase 4 — Knowledge Capture (optional)

After the component is implemented and reviewed, invoke the `knowledge-keeper` agent to persist what was learned. Pass it a summary of:
- Any non-obvious Stencil patterns or FACE constraints encountered
- API decisions made (prop naming, event shape, slot structure) and the rationale
- Test setup quirks specific to this component type
- Anything that would save the next person 30+ minutes

Knowledge-keeper will classify the findings and write them to the appropriate artifact (ADR, memory entry, or guideline update). Per-subagent memory in `.claude/agent-memory/<name>/` captures session-level detail; this phase promotes cross-cutting findings to the team store at `.agents/memory/`.

---

## Partial Workflow Shortcuts

| Situation                     | Action                                    |
| ----------------------------- | ----------------------------------------- |
| Plan already exists           | Skip to Phase 3 only                      |
| Only documentation needed     | Invoke `@documentation-subagent` directly |
| Only tests needed             | Invoke `@testing-subagent` directly       |
| Only implementation (no plan) | Invoke `@frontend-subagent` directly      |

---

Do not duplicate content from `brainstorming`, `writing-plans`, or `executing-plans` — reference them by name and load them when needed.
