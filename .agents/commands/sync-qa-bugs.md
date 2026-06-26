---
description: Scan all bug report files in ai-work/qa/bug-reports/, extract severity, priority, status, and component metadata, and rebuild the subfolder INDEX.md.
argument-hint: "[optional: filename | ticket-id (e.g. EOA-10544) | status (open | fixed | closed) | component (e.g. bds-select)]"
---

# Sync QA Bug Reports Index

## Purpose

Keep `ai-work/qa/bug-reports/INDEX.md` accurate by reading every bug report file, extracting its structured metadata fields, and regenerating the index table grouped by status.

## Input

Optional argument: `$ARGUMENTS`

- **No argument** — full sync: scan all bug report files and rebuild INDEX.md.
- **Filename** (e.g. `EOA-10544-bds-select-bug-001.md`) — display that single report's metadata; do not modify files.
- **Ticket ID** (e.g. `EOA-10544`) — list all bug reports whose filename starts with that ticket ID; do not modify files.
- **Status keyword** (`open`, `fixed`, `closed`) — list all reports currently carrying that status; do not modify files.
- **Component name** (e.g. `bds-select`) — list all bug reports for that component; do not modify files.

## Instructions

1. **Determine mode** from `$ARGUMENTS`:
   - Empty → full sync mode.
   - Matches a `.md` filename in `ai-work/qa/bug-reports/` → single-file display mode.
   - Matches a ticket ID pattern (`EOA-\d+`) → ticket filter mode.
   - Matches a status keyword (`open`, `fixed`, `closed`) → status filter mode.
   - Matches a component name → component filter mode.
   - All non-full-sync modes are read-only.

2. **Read all bug report files** (skip `INDEX.md` itself and the `assets/` directory):
   - For each `.md` file in `ai-work/qa/bug-reports/`, read at minimum the first 15 lines.
   - Extract the following fields from the bold key-value block at the top of each file:

   | Field | Source line |
   | ----- | ----------- |
   | **Title** | Text of the `# BUG-…:` heading after the colon, stripped of backticks |
   | **Severity** | `**Severity:** …` |
   | **Priority** | `**Priority:** …` |
   | **Status** | `**Status:** …` — normalise to lowercase (`open`, `fixed`, `closed`) |
   | **Component** | `**Component:** …` — preserve backticks |
   | **Ticket ID** | Leading `EOA-XXXXX` segment of the filename; fall back to `—` |

3. **In full sync mode**:
   a. Present a summary table of every report with its extracted metadata.
   b. Flag any file where `Status` or `Severity` cannot be extracted and note the specific field that is missing.
   c. Rebuild `INDEX.md` using the verified data — three sections grouped by status: **Open → Fixed → Closed**. Within each section, sort by Priority (`P0` first), then by filename.
   d. Report how many files were processed and whether INDEX.md changed.

4. **In read-only modes** (single-file, ticket, status, component):
   - Print the matching rows. Make no file changes.

5. **INDEX.md format** — always use this structure:

   ```markdown
   # QA Bug Reports Index

   ## Open

   | File | Ticket | Component | Severity | Priority | Title |
   | ---- | ------ | --------- | -------- | -------- | ----- |
   | [filename](./filename) | EOA-XXXXX | `bds-select` | High | P1 | Short title… |

   ## Fixed

   | File | Ticket | Component | Severity | Priority | Title |
   | ---- | ------ | --------- | -------- | -------- | ----- |

   ## Closed

   | File | Ticket | Component | Severity | Priority | Title |
   | ---- | ------ | --------- | -------- | -------- | ----- |
   ```

   - Use a relative markdown link in the `File` column.
   - Component names must be wrapped in backticks.
   - Omit a section entirely if it has no entries.
   - Title is truncated to 100 characters; append `…` if cut.
   - If a field cannot be determined, write `—` in that cell.

6. **Never** rename, move, or delete bug report files or their assets. Only write to `INDEX.md`.
