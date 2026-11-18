# ADR 0023 — Toolbar extension model for bds-text-editor

**Date:** 2026-11-17
**Status:** Proposed (EOA-18739)

---

## Context

The Notion usage guidance describes three toolbar configurations:

| Configuration | Tools |
| --- | --- |
| Minimal | Bold, Italic, Link |
| Extended | Bold, Italic, Underline, Emojis, Fields, Templates |
| Custom | Short URL, Audio Insert, Source Code |

The Figma anatomy has built-in `ButtonGroups`, a `Divider` and a `Slot` "reserved for additional tools or content integrations". The real applications add product-specific tools that the design system cannot know about: Audios, Templates, Sender.

The design system should not push implementation onto consumers, but it cannot build every product tool either. It must also keep the editing engine (ADR 0020) encapsulated, so that it can change without breaking consumers.

---

## Non-Goals

- Does not define the v3 formatting tools (bold, italic and so on). They will join the same `toolbar` list as built-in tools.
- Does not define the visual design of the toolbar. That comes from Figma.

---

## Options Considered

### Option A — Consumers build every tool from slotted content and an exposed engine

Most flexible. However, every app re-implements the emoji picker and the link popover, and the engine becomes public API. Rejected.

### Option B — The component builds every tool, configured only by props

Cannot cover product-specific tools such as Audios or Templates. Rejected.

### Option C — Three layers: built-in tools, data hooks, and a slot with insertion methods

The component fully builds the common tools. Consumers supply data and small behaviour hooks, and add their own tools through a slot. Their tools talk to the editor only through a few public methods. Accepted.

---

## Decision

Adopt **Option C**.

1. **Built-in tools, chosen declaratively.**
   - `toolbar: string` lists tool ids in render order: `emoji`, `link`, `fields`. `|` places a `bds-divider`.
   - The default is `'emoji,link'`, matching Notion's default buttons.
   - Each built-in tool is fully implemented with Boreal components.
   - Unknown ids are ignored with a development warning.
   - The Fields tool hides itself when `fields` is empty.
   - A tool id that is planned but not yet shipped (`emoji` in v1) is accepted and renders nothing. A later release then turns it on without changing the default.
2. **Data and behaviour hooks.**
   - `fields: ITextEditorField[]` (ADR 0021).
   - `linkTransform?: (url) => Promise<string>` for Short URL (v2). Without it, the link tool inserts the URL unchanged.
   - `labels` for every built-in string (ADR 0014).
   - These are the only consumer-supplied behaviours; none of them expose the engine.
3. **Escape hatch for product tools.**
   - `slot="toolbar"` renders consumer controls after the built-in tools.
   - Slotted tools act on the editor only through public methods:
     - `insertText(text)`
     - `insertField(token)`
     - `setFocus()`
     - setting `value` (for templates)
   - `insertText` and `insertField` insert at the preserved cursor, respect the limit (ADR 0022), and return `false` when nothing is inserted.
4. **Encapsulation.** No ProseMirror object, transaction or command is exposed. New editor capabilities reach consumers only as new tool ids, new data hooks or new methods.

---

## Consequences

- **Common cases need no code:** consumers write markup and data for emoji, links and fields.
- **Product tools are thin:** they are plain Boreal buttons or dropdowns in the slot that call one method.
- **The engine can change** (for example, a major ProseMirror upgrade) without breaking consumers, because nothing engine-specific is public.
- **Growth goes through the design system:** a capability that slotted tools cannot express with the existing methods (for example, wrapping the selection) needs a new method or a built-in tool. This trade-off is intended.
- **Reusable pattern:** this layering (declarative built-ins, data hooks, a slot, narrow imperative methods) is the recommended pattern for future composite components with toolbars.
