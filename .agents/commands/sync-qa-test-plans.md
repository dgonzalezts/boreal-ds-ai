---
description: Scan all test plan files in ai-work/qa/test-plans/, extract component and date metadata, and rebuild the subfolder INDEX.md.
argument-hint: "[optional: filename | ticket-id (e.g. EOA-10544) | component (e.g. bds-select)]"
---

# Sync QA Test Plans Index

## Purpose

Keep `ai-work/qa/test-plans/INDEX.md` accurate by reading every test plan file, extracting its component name, creation date, and description, and regenerating the index table.

## Input

Optional argument: `$ARGUMENTS`

- **No argument** — full sync: scan all test plan files and rebuild INDEX.md.
- **Filename** (e.g. `EOA-10544-bds-select-test-plan.md`) — display that single plan's metadata; do not modify files.
- **Ticket ID** (e.g. `EOA-10544`) — list all test plans whose filename starts with that ticket ID; do not modify files.
- **Component name** (e.g. `bds-select`) — list all test plans covering that component; do not modify files.

## Instructions

1. **Determine mode** from `$ARGUMENTS`:
   - Empty → full sync mode.
   - Matches a `.md` filename in `ai-work/qa/test-plans/` → single-file display mode.
   - Matches a ticket ID pattern (`EOA-\d+`) → ticket filter mode.
   - Matches a component name → component filter mode.
   - All non-full-sync modes are read-only.

2. **Read all test plan files** (skip `INDEX.md` itself):
   - For each `.md` file in `ai-work/qa/test-plans/`, read at minimum the first 20 lines.
   - Extract the following fields:

   | Field | Where to find it |
   | ----- | ---------------- |
   | **Component** | Inside backticks in the `# Test Plan:` heading (e.g. `` `bds-select` ``); fall back to the filename segment between the ticket ID and `-test-plan` |
   | **Ticket ID** | Leading `EOA-XXXXX` segment of the filename |
   | **Created** | Line matching `Created: YYYY-MM-DD` in the Context section; fall back to `YYYY-MM-DD` in the filename if present |
   | **Description** | First sentence of the Context section prose, truncated to 120 characters |

3. **In full sync mode**:
   a. Present a summary table of every plan with its extracted metadata.
   b. Flag any file where the component or date cannot be extracted and note the specific field that is missing.
   c. Rebuild `INDEX.md` using the verified data — sorted chronologically by `Created` date (oldest first).
   d. Report how many files were processed and whether INDEX.md changed.

4. **In read-only modes** (single-file, ticket, component):
   - Print the matching rows from the index. Make no file changes.

5. **INDEX.md format** — always use this structure:

   ```markdown
   # QA Test Plans Index

   | File | Ticket | Component | Created | Description |
   | ---- | ------ | --------- | ------- | ----------- |
   | [filename](./filename) | EOA-XXXXX | `bds-select` | YYYY-MM-DD | First sentence of context… |
   ```

   - Use a relative markdown link in the `File` column.
   - Component names must be wrapped in backticks.
   - If a field cannot be determined, write `—` in that cell.
   - Omit the `assets/` directory and any non-`.md` files.

6. **Never** rename, move, or delete test plan files. Only write to `INDEX.md`.
