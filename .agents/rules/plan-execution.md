# Plan Execution Strategy

Apply these rules whenever executing a plan from `ai-work/plans/` or any multi-step task.

## Before Starting

Check the plan's frontmatter `status`:

- `pending` — safe to start; update to `in progress` and update `ai-work/plans/INDEX.md` before writing any code.
- `in progress` — confirm with the user before resuming.
- `done` — do not re-execute; inform the user the plan is already complete.

## 1. Establish a TODO list first

Create a concrete ordered task list before writing any code.

- Each task = one discrete, testable unit of work from the plan.
- Include a manual testing task after each implementation step.
- Include a confirmation task whenever a design decision has multiple valid approaches.
- Do not begin until the list is visible and confirmed.

## 2. One task at a time

- Mark a task in-progress before starting; mark completed only when fully verified.
- Never start the next task until the current one is done and validated.
- If a task reveals unexpected complexity, create a new task to track the blocker.
- Prefer small, focused commits per task over one large commit at the end.

## 3. Confirm before continuing

After completing each task, pause and ask the user to confirm before moving to the next one.
Do not proceed automatically through multiple tasks — sequential validation prevents compounding errors.

## 4. Manual test after each task

Every completed task requires a minimal, explicit test scoped to what was just built:

- **Steps**: list the exact steps to run (e.g. "Run `pnpm dev` in `apps/boreal-docs`, open the browser, verify X renders without console errors").
- **Pass/fail criteria**: state what a passing result looks like.
- Manual tests are required, not waiveable. Do not mark a task complete until the test has actually been run and passes — a skipped, deferred, or unwaived-but-unrun test blocks completion the same as a failing one.

## 5. Read before writing

Never propose or apply changes to a file that has not been read in the current session.

## 6. Surface assumptions early

State any assumption explicitly and confirm with the user before acting on it.

## 7. Keep scope tight

Only implement what the current task describes. Do not refactor surrounding code or add features outside task scope. Log observations as new tasks instead.
