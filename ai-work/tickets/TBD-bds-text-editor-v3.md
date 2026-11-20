# TBD — bds-text-editor v3

**Ticket:** TBD (draft, not in Jira; rename this file with the ID once created)
**Status:** Proposal — scope to be confirmed with product before planning
**Goal:** Extend `bds-text-editor` into a rich HTML editor that can replace the CKEditor 4 "HTML Editor" screens (for example, "Edit header and footer").

> **Proposal.** The scope below is inferred from the CKEditor 4 toolbars in the Figma real-application board. Nobody has agreed to it yet. Confirm with product which tools are needed before research and planning start.

## Jira fields (copy when creating)

- **Summary:** Implement Text Editor v3: rich text and HTML output
- **Type:** Story
- **Links:** follows the v2 ticket (`EOA-21589-bds-text-editor-v2.md`)

## Proposed scope

**In (to confirm):**

- An HTML output mode alongside the existing plain-text mode. Plain text stays the default, so existing consumers are unaffected.
- Text formatting: bold, italic, underline, strikethrough, clear formatting.
- Block formatting: paragraph and heading formats, bulleted and numbered lists, indent and outdent, alignment, horizontal line.
- Font family, font size, text colour and background colour.
- Links as real anchors (edit and remove), building on the v1 Link tool.
- Tables and images.
- Source view (edit the HTML directly).
- Fields working inside rich content, with the same token behaviour as v1.
- Pasted HTML cleaned and reduced to the supported formatting, using `dompurify` (already a dependency).
- Toolbar buttons that show their on/off state, which requires `aria-pressed` support in `bds-button`.

**Possibly (to decide):**

- WhatsApp-style formatting (`*bold*`, `_italic_`, `~strike~`) as a plain-text option for messaging channels.
- Paste from Word with formatting kept.
- A full-screen mode.

**Out:**

- Real-time collaboration and comments.
- SMS segment counting (separate decision).

## Acceptance Criteria (draft)

- [ ] Product has confirmed the tool list.
- [ ] HTML output contains only the formatting the configured tools allow; pasted content is cleaned to match.
- [ ] Switching between Source view and the editor keeps the content.
- [ ] Toolbar buttons show the formatting active at the cursor, to both sighted and screen-reader users.
- [ ] Plain-text consumers from v1 and v2 see no change.
- [ ] Matches the signed-off design in all four brand themes, with the project's coverage and mutation gates met.

## Dependencies

- v2 merged.
- Figma designs for the rich toolbar, the table and image tools, and Source view (none exist yet).
- A research spike before planning: which ProseMirror packages to add (lists, tables, history of marks), how much of the CKEditor 4 toolbar to reproduce, bundle cost, and HTML paste cleaning.

## Notes

- No implementation plan exists yet. It is written after product confirms the scope and the research spike concludes.
- Background: `ai-work/research/2026-11-13-bds-text-editor-engine-spike.md` (ProseMirror was chosen partly because the same engine can grow into this version).
