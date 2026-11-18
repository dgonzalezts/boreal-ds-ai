# ADR 0020 — Editing engine for bds-text-editor: raw ProseMirror

**Date:** 2026-11-17
**Status:** Proposed (EOA-18739)

---

## Context

`bds-text-editor` replaces CKEditor 4 message fields in product apps. CKEditor 4 reached end of life in 2023. The real-application board in Figma shows two products under one name:

- **A plain-text message composer** (most screens). It inserts fields such as `{{1}}`, `[URL_Identify_Senders]` and `DF-Name`, plus emoji and links. Counters read "Characters: 5/160" or "24/1000 equals 1 Msg.".
- **A rich HTML editor** ("Edit header and footer"), with fonts, sizes, tables, images and a Source view.

The component ships in versions. v1 and v2 are the plain-text composer; v3 is the rich editor, still a proposal. The engine must therefore cover plain text now and be able to grow into rich text without being replaced.

Constraints from this codebase:

- **Light DOM.** Components render without shadow DOM, so host-page CSS reaches the editing area and third-party UI.
- **Form association.** The editor is form-associated through `formAssociatedMixin` and `IFormControl<T>`.
- **Boreal UI.** The Figma anatomy builds the toolbar from Boreal parts (`ButtonGroups`, `Divider`, `Slot`), so engine-supplied UI would not match.
- **Shipped to every consumer.** `@pxglobal/boreal-web-components` runtime dependencies reach every app that installs the package. Stencil lazy-loading limits page weight, but not install size or licence obligations.
- **Licence.** A CKEditor licence is available, probably commercial; its type was not confirmed.

Evidence is in `ai-work/research/2026-11-13-bds-text-editor-engine-spike.md`. Bundle sizes were measured locally with esbuild (minified, gzipped, JavaScript only, production `NODE_ENV`), with each entry importing only what the composer needs:

| Engine | gzip |
| --- | --- |
| ProseMirror (model, state, view, history, keymap) | 60 kB |
| Quill 2.0.3 | 58 kB |
| CodeMirror 6 (state, view, commands) | 86 kB |
| Tiptap 3.34 core | 89 kB |
| Lexical 0.53 + plain-text + history | 105 kB |
| notectl core 2.4.2 | 120 kB |
| CKEditor 5 49.1 (minimal: Essentials, Paragraph, Bold/Italic, Link, Mention, Emoji) | 192 kB + 43 kB CSS |
| CKEditor 5 49.1 (HTML-editor feature set) | 255 kB + 43 kB CSS |

---

## Non-Goals

- Does not decide the v3 rich-editor feature set. That needs product confirmation and its own research spike.
- Does not decide the value format or the field model (ADR 0021), counting and limits (ADR 0022), or the toolbar extension model (ADR 0023).

---

## Options Considered

### Option A — CKEditor 5 (licensed)

**For:**
- Most complete feature set (tables, fonts, Source editing, paste from Word, mentions, emoji).
- Mature accessibility and IME handling.
- Commercial support.
- A natural successor to CKEditor 4.

**Against:**
- About 3× ProseMirror's size for the composer, plus about 120 MB installed.
- The licence key cannot be hard-coded in a published DS package, so every consumer would have to supply it.
- The GPL key brings GPL obligations and a "Powered by CKEditor" badge.
- Its toolbar, dropdowns and link balloon do not match Boreal. Using it headless (our toolbar calling `editor.execute()`) discards much of what the licence pays for.
- Upgrades break (v49 removed the Watchdog).
- Content-model lock-in.

Rejected.

### Option B — Raw ProseMirror

**For:**
- MIT licence, the smallest model-based engine measured, and headless.
- A strict, schema-defined document: the composer schema can allow only paragraphs, text and an atomic `field` node, so unsupported content cannot exist.
- Battle-tested selection, IME, undo and paste handling.
- The same engine extends to the v3 rich editor with a larger schema.

**Against:**
- We build and own the toolbar UI and the serialisers.

Accepted.

### Option C — Tiptap 3

ProseMirror with an extension API, at about +30 kB. Its framework bindings (React, Vue) give nothing inside a Stencil component, and its paid features (collaboration, AI) are out of scope. Rejected; revisit only if writing ProseMirror plugins directly proves costly.

### Option D — CodeMirror 6

An excellent plain-text editor: atomic widget decorations for fields, strong accessibility and IME handling, and a string value. It cannot grow into the v3 rich editor, so v3 would need a second engine. Rejected.

### Option E — Quill 2, Lexical, notectl, Trix, Squire, TinyMCE, Editor.js

| Engine | Reason rejected |
| --- | --- |
| Quill 2 | Ships its own toolbar and themes; its schema is less strict. |
| Lexical | Framework-agnostic core, but a React-first ecosystem and heavier. |
| notectl | Young (about 210 stars); its own custom element and toolbar; no fields or emoji. |
| Trix | HTML-only model and its own toolbar. |
| Squire | No document model. |
| TinyMCE | GPL 2+ or commercial since v7, the same licence problem as CKEditor. |
| Editor.js | Block model. |
| Slate, Plate, BlockNote, Remirror | React-only. |

### Option F — Build from scratch on `contenteditable`

- **Plain text with atomic chips:** possible but costly. We would own caret behaviour around non-editable spans (inconsistent across browsers), IME composition, undo, paste normalisation and mobile keyboards.
- **`contenteditable="plaintext-only"`** (all major browsers since Firefox 136, March 2025): cannot reliably hold atomic chips.
- **Rich text:** would mean re-implementing a document model.

Rejected.

---

## Decision

Adopt **Option B**:

- **Packages:** `bds-text-editor` uses raw ProseMirror (`prosemirror-model`, `-state`, `-view`, `-history`, `-keymap`, `-commands`) as runtime dependencies of `@pxglobal/boreal-web-components`.
- **Encapsulation:**
  - ProseMirror owns only the editable area. Every other part of the UI is a Boreal component.
  - Only `bds-text-editor` imports ProseMirror. A single internal adapter module creates and destroys the `EditorView`.
  - Consumers never receive ProseMirror objects through the public API.
- **Versions:** taken under ADR 0019 (`minimumReleaseAge`, no pre-release `prosemirror-view` versions), and pinned to the minor version with tilde ranges (for example `~1.25.13`), so only patch releases install automatically. Minor releases are adopted deliberately through dependency maintenance.

---

## Consequences

- **Bundle:** about 60 kB gzipped, in the `bds-text-editor` lazy chunk only. A plan task verifies that no other component's chunk grows.
- **Ownership:** the schema, serialisers, plugins (limit, paste, placeholder) and toolbar UI are Boreal code under the coverage and mutation gates.
- **Growth:** v3 extends the schema (marks, lists, tables) and adds an HTML serialiser on the same engine. No engine migration.
- **CKEditor:** not used by the design system. Its licence stays available to products that need an editor before v3 ships.
- **Testing:** ProseMirror's state and transactions run without a DOM, so the logic is unit-testable. Whether its view runs in Stencil's mock-doc is checked in the first v1 task. If it does not, specs replace the adapter module with a fake; that pattern may justify its own ADR.
- **Documentation:** fetch current ProseMirror documentation (Context7 or `https://prosemirror.net/docs/ref/`) before writing integration code; never rely on recalled API shapes.
