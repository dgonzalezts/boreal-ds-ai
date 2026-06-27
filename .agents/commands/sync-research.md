---
description: Scan all research files in ai-work/research/, extract ticket, component, and status metadata, and rebuild the subfolder INDEX.md.
argument-hint: "[optional: filename | ticket-id (e.g. EOA-13695) | status (exploring | concluded | promoted) | component (e.g. bds-select)]"
---

# Sync Research Index

## Purpose

Keep `ai-work/research/INDEX.md` accurate by reading every research file, extracting its frontmatter fields and title, and regenerating the index table grouped by status.

## Input

Optional argument: `$ARGUMENTS`

- **No argument** — full sync: scan all research files and rebuild INDEX.md.
- **Filename** (e.g. `2026-05-28-bds-select-multiselect-extension.md`) — display that single file's metadata; do not modify files.
- **Ticket ID** (e.g. `EOA-13695`) — list all research files whose `ticket` field matches; do not modify files.
- **Status keyword** (`exploring`, `concluded`, `promoted`) — list all files carrying that status; do not modify files.
- **Component name** (e.g. `bds-select`) — list all research files whose `component` field matches; do not modify files.

## Instructions

1. **Determine mode** from `$ARGUMENTS`:
   - Empty → full sync mode.
   - Matches a `.md` filename in `ai-work/research/` → single-file display mode.
   - Matches a ticket ID pattern (`EOA-\d+` or `AI-\d+`) → ticket filter mode.
   - Matches a status keyword (`exploring`, `concluded`, `promoted`) → status filter mode.
   - Matches a component name → component filter mode.
   - All non-full-sync modes are read-only.

2. **Read all research files** (skip `INDEX.md` itself):
   - For each `.md` file in `ai-work/research/`, read at minimum the first 15 lines.
   - Extract the following fields:

   | Field | Where to find it |
   | ----- | ---------------- |
   | **Date** | Leading `YYYY-MM-DD` segment of the filename |
   | **Ticket** | `ticket:` in frontmatter; `—` if absent or not present |
   | **Component** | `component:` in frontmatter; `—` if line is omitted |
   | **Status** | `status:` in frontmatter; flag as missing if absent |
   | **Title** | First `# Heading` found after the frontmatter block |

3. **In full sync mode**:
   a. Present a summary table of every file with its extracted metadata.
   b. Flag any file where `status` cannot be extracted — it is missing required frontmatter.
   c. Rebuild `INDEX.md` using the verified data — three sections grouped by status: **Exploring → Concluded → Promoted**. Within each section, sort by date descending (newest first).
   d. Report how many files were processed and whether INDEX.md changed.

4. **In read-only modes** (single-file, ticket, status, component):
   - Print the matching rows. Make no file changes.

5. **INDEX.md format** — always use this structure:

   ```markdown
   # Research Index

   ## Exploring

   | File | Date | Ticket | Component | Title |
   | ---- | ---- | ------ | --------- | ----- |
   | [filename](./filename) | YYYY-MM-DD | EOA-XXXXX | `bds-select` | Research title… |

   ## Concluded

   | File | Date | Ticket | Component | Title |
   | ---- | ---- | ------ | --------- | ----- |

   ## Promoted

   | File | Date | Ticket | Component | Title |
   | ---- | ---- | ------ | --------- | ----- |
   ```

   - Use a relative markdown link in the `File` column.
   - Component names must be wrapped in backticks; use `—` when no component applies.
   - Omit a section entirely if it has no entries.
   - Title is truncated to 100 characters; append `…` if cut.
   - If `status` is missing, place the file in a `## Missing Frontmatter` section and flag it.

6. **Never** rename, move, or delete research files. Only write to `INDEX.md`.
