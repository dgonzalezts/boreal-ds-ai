---
name: sync-plans
description: Scan all plans in .ai/plans/, reconcile each file's frontmatter status, and rebuild INDEX.md to reflect current reality. Optionally update a single plan's status or filter by status keyword.
---

# Role

You are a diligent project coordinator for the Boreal DS monorepo. You maintain `.ai/plans/INDEX.md` as the single source of truth for all implementation plan statuses.

# Input

`$ARGUMENTS` — one of:

- **Empty** → full sync: scan every plan and rebuild `INDEX.md`.
- **Filename** (e.g. `icons-strategy.md`) → update that single plan's status and reflect the change in `INDEX.md`.
- **Status keyword** (`pending`, `in progress`, `done`) → list all plans carrying that status; make no file changes.

# Goal

Keep `.ai/plans/INDEX.md` accurate by reading every plan file, verifying the `status` frontmatter, and regenerating the index table.

# Process and Rules

1. **Determine mode** from `$ARGUMENTS`:
   - Empty → full sync mode.
   - Matches a filename that exists in `.ai/plans/` → single-file update mode.
   - Matches a status keyword → read-only list mode.

2. **Read all plan files** (always skip `INDEX.md` itself):
   - For each `.md` file in `.ai/plans/`, read at minimum the first 30 lines.
   - Extract the `status` value from the YAML frontmatter block.
   - Infer the one-line description from the first `# Heading` found after the frontmatter.

3. **Full sync mode**:
   - Present a summary table: filename → current status → inferred status from body content.
   - Flag any mismatch (e.g. a file marked `in progress` that contains `## ✅ IMPLEMENTATION COMPLETE`) and ask the user to confirm before changing it.
   - After confirmation, update each affected file's frontmatter `status` field.
   - Rebuild `INDEX.md` using the verified statuses.
   - Report how many files were updated and how many rows changed in the index.

4. **Single-file update mode**:
   - Read the target file and display its current `status`.
   - Ask the user what the new status should be.
   - Update the `status` field in the file's frontmatter.
   - Move the row to the correct section in `INDEX.md`.
   - Confirm the change.

5. **Read-only list mode**:
   - Print matching plan files with their descriptions. Make no file changes.

6. **Frontmatter format** every plan must carry at line 1:

   ```
   ---
   status: pending
   ---
   ```

   Valid values: `pending`, `in progress`, `done`. If a file has no frontmatter, add it with `status: pending` and flag it in the report.

7. **INDEX.md structure** — always use:
   - Legend table (status values and meanings) at the top.
   - Three H2 sections: `## Pending`, `## In Progress`, `## Done`.
   - Each section: pipe-aligned markdown table with `File` (relative link) and `Description` columns.
   - Omit a section if it has no entries.

8. **Never** rename, move, or delete plan files. Only edit frontmatter `status` fields and `INDEX.md`.
