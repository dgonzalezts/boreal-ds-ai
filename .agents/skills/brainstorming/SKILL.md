---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## The Process

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## Output

The output path depends on what the session produced:

| Session type | Output path |
|---|---|
| Validated design / architecture spec | `ai-work/sessions/YYYY-MM-DD-{slug}-design.md` |
| Research spike (tech comparison, API analysis, approach evaluation) | `ai-work/research/YYYY-MM-DD-{slug}.md` |

**Research spike structure:** **Goal** — **Options evaluated** — **Findings** — **Recommendation** — **Open questions**. Use this format whenever the session's primary output is an evaluation rather than a design decision. Invoke `knowledge-keeper` after writing the spike if any findings should be promoted to team memory or an ADR.

## After the Design

**Documentation:**

- Write the validated design to `ai-work/sessions/YYYY-MM-DD-{slug}-design.md`
- Use writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation (if continuing):**

- Ask: "Ready to set up for implementation?"
- Use using-git-worktrees skill if available to create isolated workspace
- Use writing-plans skill if available to create detailed implementation plan

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
