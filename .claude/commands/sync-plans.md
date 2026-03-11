---
description: Scan all plans in .ai/plans/, reconcile each file's frontmatter status, and rebuild INDEX.md to reflect current reality.
argument-hint:
  [optional filename or status filter: pending | in progress | done]
---

# Sync Plans Index

## Purpose

Keep `.ai/plans/INDEX.md` accurate by reading every plan file, verifying the `status` frontmatter, and regenerating the index table. Can also be used to update the status of a single plan.

## Input

Optional argument: `$ARGUMENTS`

- **No argument** — full sync: scan all plans and rebuild INDEX.md.
- **Filename** (e.g. `icons-strategy.md`) — update the status of that single plan and reflect the change in INDEX.md.
- **Status keyword** (`pending`, `in progress`, `done`) — list all plans currently carrying that status; do not modify files.

## Instructions

1. **Determine mode** from `$ARGUMENTS`:
   - Empty → full sync mode.
   - Matches a filename in `.ai/plans/` → single-file update mode.
   - Matches a status keyword → read-only list mode.

2. **Read all plan files** (skip `INDEX.md` itself):
   - For each `.md` file in `.ai/plans/`, read at minimum the first 30 lines.
   - Extract the `status` value from the YAML frontmatter block.
   - Infer the one-line description from the first `# Heading` found after the frontmatter.

3. **In full sync mode**:
   a. Present a summary table of every plan with its current `status`.
   b. For any plan whose body content clearly indicates a different status than its frontmatter (e.g. `## ✅ IMPLEMENTATION COMPLETE` in a file marked `in progress`), flag it and ask the user to confirm before changing it.
   c. After confirmation, update the frontmatter `status` field in each affected file.
   d. Rebuild `INDEX.md` using the verified statuses — three sections (Pending → In Progress → Done), each a markdown table with a relative link and one-line description.
   e. Report how many files were updated and how many rows changed in the index.

4. **In single-file update mode**:
   a. Read the target file and display its current `status`.
   b. Ask the user what the new status should be (`pending`, `in progress`, `done`).
   c. Update the `status` field in the file's frontmatter.
   d. Move the file's row to the correct section in `INDEX.md`.
   e. Confirm the change with the file path and new status.

5. **In read-only list mode**:
   - Print the list of matching plan files with their descriptions. Make no file changes.

6. **Frontmatter format** — every plan must have this block at the very top (line 1):

   ```
   ---
   status: pending
   ---
   ```

   Valid values: `pending`, `in progress`, `done`. If a file has no frontmatter, add it with `status: pending` and flag it in the report.

7. **INDEX.md format** — always use this structure:
   - Legend table at the top (status values and meanings).
   - Three H2 sections: `## Pending`, `## In Progress`, `## Done`.
   - Each section contains a table with columns `File` (relative markdown link) and `Description`.
   - Omit a section entirely if it has no entries.
   - Preserve the user's own formatting style (pipe-aligned tables).

8. **Never** rename, move, or delete plan files. Only edit frontmatter `status` and `INDEX.md`.
