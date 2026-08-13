---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Note:** This skill dispatches tasks to specialist subagents based on the `**Executor:**` field declared in each plan task. Ensure the plan was created with the `writing-plans` skill so all tasks have executor fields.

## The Process

### Step 1: Load and Review Plan

1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Tasks

For each task:

1. Mark as in_progress
2. Read the `**Executor:**` field on the task
3. If `@<subagent>` is declared: compose a dispatch message containing the task title, files, acceptance criteria, unit tests, manual test checklist, and commit message; invoke `@<subagent>: <message>`
   - **When dispatching to `@qa-subagent` specifically**, also state this task's position among the plan's manual-QA tasks — e.g. "this is the only/last manual-QA task in this plan" or "N more manual-QA tasks remain after this one." The subagent has no visibility into the plan beyond what it's told and uses this to decide whether to tear down dev servers (web components/React/Vue) at the end of the task or leave them running for the next dispatch. Omitting this causes it to default to full teardown, which is safe but forces a redundant rebuild on the next QA task.
4. If no executor declared: execute the task directly on the main thread
5. Wait for subagent output; review it against acceptance criteria
6. Run the task's manual test checklist yourself (or confirm with your human partner it was run) — manual tests are required, not waiveable; a failing or skipped manual test is a blocker, not a pass
7. Mark as completed only when acceptance criteria are met AND the manual test checklist passes

### Step 3: Complete Development

After all tasks complete and verified:

- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use `finishing-a-development-branch`
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**

- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**

- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember

- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**

- **using-git-worktrees** — REQUIRED: Set up isolated workspace before starting
- **writing-plans** — Creates the plan this skill executes; produces tasks with `**Executor:**` fields
- **finishing-a-development-branch** — Complete development after all tasks
