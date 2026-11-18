---
ticket: EOA-18739
component: bds-text-editor
status: promoted
---

# bds-text-editor — editing engine spike

## Goal

Decide how `bds-text-editor` gets its editing engine: CKEditor 5 (license available), another third-party engine, or a from-scratch implementation. The answer must cover the real-application scenarios in Figma, sit inside the Boreal anatomy (label, toolbar of `ButtonGroups` + `Divider` + `Slot`, content, helper text, char counter), and work in web components, React and Vue.

## Inputs reviewed

- Figma anatomy, properties and main node `14:34766` (file `rtiE5zGA4aoOuxIQMgfD6h`). The Figma MCP is not authenticated in this session, so the token values below come from screenshots only.
- Notion usage, content, behaviour and use-case tables.
- Figma "real applications" board.

### What the design specifies

| Area | Spec |
|---|---|
| Size | 448 × 152 default; toolbar height 41 |
| Content | bg `ui/default`, border `stroke/default-dark` `stroke/xs`, radius `radius/xs` |
| Toolbar | bg `ui/default`, bottom border `stroke/xs`, top radii `radius/xs` |
| Toolbar parts | `ButtonGroups` (default buttons: emoji dropdown + link), vertical `Divider`, `Slot` |
| Visibility toggles | Buttons, Divider, Slot, Char Counter, Helper Text, Toolbar, Footer, Header |
| States | Default, Hover, Focus, Active, Disabled, Readonly (toolbar hidden, plain text), Error, Populated |
| Toolbar presets (Notion) | Minimal (B/I/Link), Extended (B/I/U/Emoji/Fields/Templates), Custom (Short URL, Audio, Source) |

### What the real applications use

The Figma board shows two different products under one name:

1. **Message composer** (most screens). Fields/variables dropdown that inserts tokens (`{{1}}`, `[URL_Identify_Senders]`, `DF-Name`), emoji picker, link/short URL, audios, templates, sender. Some have WhatsApp-style B / I / S / `</>`. Counter labels such as "Characters: 5/160" and "24/1000 equals 1 Msg." show the output is mostly **plain text or channel markup (SMS, WhatsApp)**, not HTML.
2. **HTML editor** ("Edit header and footer", "HTML Editor"). Full CKEditor 4 toolbar: Format, Font, Size, colours, alignment, lists, indent, tables, image, HR, clear formatting, Source view, Fields. The DOM inspector in the screenshot shows `cke_editor4`, so these screens **currently run CKEditor 4**, which reached end of life in 2023.

## Constraints from this codebase

- **Light DOM.** Components do not use shadow DOM. `contenteditable` and the Selection API work without shadow-root workarounds, but host-page CSS reaches the editable content. The content area needs a scoped reset.
- **FACE.** Form controls extend `formAssociatedMixin` and implement `IFormControl<T>`. The editor must sync its value on every commit path; see the memory entry `face-composite-child-value-sync-on-non-string-branch`.
- **Shared field parts.** `forms/common/renderFieldParts.tsx` already renders the label, helper text, error state and counter (`counter` + `charCount`, as in `bds-text-field`). The editor should reuse them.
- **Distribution.** The `@pxglobal/boreal-web-components` dependencies ship to every consumer. Stencil lazy-loads per component, which limits the runtime cost but not install size or licensing obligations.
- **Already a dependency:** `dompurify`, for paste and HTML sanitisation.

## Options evaluated

### A. CKEditor 5 (licensed)

- **Pros:** Most complete feature set: tables, fonts, Source editing, paste-from-Word, mentions (usable for Fields), emoji, link UI. Covers the HTML-editor scenario immediately. Mature accessibility and IME handling. Commercial support. Runs inside open shadow roots since v49 (Oct 2026), which matters little here because we use light DOM. A natural migration from the CKEditor 4 screens.
- **Cons:** Large bundle. **The license key is a distribution problem:** it cannot be hard-coded in a DS package, so consumers must pass it in. With the GPL key, the editor shows a "Powered by CKEditor" badge and GPL obligations apply. Its UI (toolbar, dropdowns, link balloon) does not match Boreal. Using it headless, with our own toolbar calling `editor.execute()` and observing command state, works but discards much of what we pay for. Upgrades bring breaking changes (v49 removed the Watchdog). Vendor lock-in on the content model.
- **Fit:** Excellent for the HTML editor. Overkill and heavy for the message composer.

### B. Headless ProseMirror engine (Tiptap core or raw ProseMirror), Boreal UI

- **Pros:** MIT core. Headless, so the toolbar, emoji picker and link popover are Boreal components (`bds-button-group`, `bds-divider`, `bds-popover`, `bds-dropdown`). Schema-driven: we can define a **minimal schema** for the composer (paragraphs, text, `field` atom node, optional marks) so unsupported formatting cannot exist. Fields are first-class atom nodes with clean serialisation to `{{name}}`. Battle-tested selection, IME, undo and paste handling. Framework-agnostic, so it fits Stencil and the React/Vue wrappers. Custom serialisers can output plain text, WhatsApp markup or HTML.
- **Cons:** We build and own the UI and serialisers. A full HTML editor (tables, fonts, Source view) is a large build on top. Tiptap's paid features (collaboration, AI) are irrelevant here.
- **Fit:** Strong for the message composer and minimal/extended presets. Medium for the HTML editor.

### C. Quill 2

- **Pros:** BSD, simple drop-in, Delta format, embeds (Blots) can model fields.
- **Cons:** Ships its own toolbar and themes. Its schema is less strict than ProseMirror's. History of selection issues outside light DOM. Slower ecosystem momentum. No advantage over B for our headless needs.

### D. notectl

- **Pros:** MIT, a native web component, transaction/immutable-state architecture, one dependency (`dompurify`, which we already ship), HTML and JSON output, about 76 kB gzipped core.
- **Cons:** Young and small (about 210 stars). Ships its own toolbar and custom element, so it nests a foreign custom element and styling system inside ours. No documented fields/mentions, emoji or Source view. Bus-factor risk for a DS dependency.
- **Use:** Architecture inspiration only.

### E. Inspiration only

- **shadcn-editor:** Lexical + React + shadcn. React-only, not integrable into Stencil. Its UX (slash menu, floating toolbar, mentions) is useful reference.
- **wysiwyg-e:** Lit, BSD, about 14 commits and 1 star. Not viable.
- **Lexical:** Framework-agnostic core, but its ecosystem and plugins are React-first. No clear win over B for us.

### F. From scratch (`contenteditable`)

- **Composer-only scope** (plain text + atomic field tokens + emoji insertion, no marks): technically viable but deceptively costly. We would have to handle caret behaviour around non-editable token spans (browser-inconsistent, especially in Firefox and Safari), IME composition, our own undo stack, paste normalisation, mobile keyboards and screen-reader announcements for tokens. `document.execCommand` is deprecated and unsuitable as a foundation.
- **Any formatting scope:** not viable. It would mean re-implementing a document model, which is what B already provides.
- **Verdict:** Only defensible if the composer stays plain-text forever and adding a dependency is forbidden. Even then, B's minimal schema is less code to own.

## Preliminary recommendation

**Build `bds-text-editor` on a headless ProseMirror engine (option B) with Boreal-rendered UI. Treat the full HTML-editor scenario as a separate decision, potentially a CKEditor 5 integration (option A) or a later extended preset.**

Why:

1. It covers most real use cases (message composer, comments, form rich inputs) with a strict schema, first-class fields and pixel-faithful Boreal UI.
2. It avoids pushing a license key and a heavy commercial bundle onto every DS consumer.
3. CKEditor stays available, so the HTML editor does not block v1.

## Proposed API sketch (to validate)

- Tag `bds-text-editor`, category **Forms**, classification **Organism**.
- FACE form control (`name`, `value`, `defaultValue`, `required`, `disabled`, `readonly`, `error`, `errorMessage`, `customValidators`, `validationTiming`).
- Field parts reused: `label`, `info`, `helperText`, `placeholder`, `counter`, `charCount`.
- `toolbar`: preset (`'minimal' | 'extended' | 'none'`) or explicit item list; `slot="toolbar-end"` for custom tools (Fields, Templates, Audios).
- `format`: `'text' | 'html'` (and possibly `'whatsapp'` markup), which drives `value` serialisation.
- `fields`: list of insertable tokens. `@Method() insertText()` / `insertField()` so slotted tools can insert content.
- Events: `bdsInput`, `bdsChange`, `bdsFocus`, `bdsBlur`, `bdsValidationChange`, `valueChange`.

## Decisions from round 1 (2026-11-13)

| # | Decision |
|---|---|
| 1 | Versioned component. v1 is the plain-text message composer; the rich HTML editor comes in a later version of the same component. |
| 2 | Consumers need **plain text**. |
| 3 | The counter **includes the length of fields**. |
| 4 | CKEditor license type is unknown (probably commercial). If it adds a lot to the bundle, explore an alternative. |
| 5 | There are no designs for the emoji picker or link popover. The component should own its features and avoid pushing implementation onto consumers. |
| 6 | v1 counts characters, but the design must leave room for SMS segments. |
| 7 | Ticket: EOA-18739. |

## Measured bundle cost

Measured with esbuild, minified and gzipped, JS only, production `NODE_ENV`. Each entry imports only what that scenario needs. Treat the numbers as a relative comparison.

| Engine | Entry | gzip |
|---|---|---|
| Squire 2.4.11 | core | 18 kB |
| Trix 2.1.19 | core | 51 kB |
| Quill 2.0.3 | core | 58 kB |
| **ProseMirror** (model/state/view/history/keymap) | plain composer | **60 kB** |
| CodeMirror 6 (state/view/commands) | plain composer | 86 kB |
| Tiptap 3.34 core | core | 89 kB |
| Lexical 0.53 + plain-text + history | plain composer | 105 kB |
| notectl core 2.4.2 | core | 120 kB |
| Tiptap 3.34 + StarterKit | rich | 121 kB |
| **CKEditor 5 49.1** (Essentials, Paragraph, B/I, Link, Mention, Emoji) | minimal | **192 kB + 43 kB CSS** |
| CKEditor 5 49.1 (HTML-editor feature set) | full | 255 kB + 43 kB CSS |

Install footprint: CKEditor 5 is about 120 MB in `node_modules` (`ckeditor5` plus `@ckeditor/*`).

CKEditor costs about three times as much as ProseMirror for the minimal composer, and the license key still has to be distributed somehow. Following decision 4, **CKEditor 5 is out for v1.**

## Effect of plain-text output on scope

- **Content model:** paragraphs + text + `field` atom. No marks, no HTML serialiser, and no output sanitisation. Paste becomes text extraction.
- **Toolbar actions become insertions:** emoji inserts a Unicode character, link inserts URL text, a field inserts a token. WhatsApp-style B/I/S/`</>` (seen in the "Message bubble" screen) can wrap the selection with `*`, `_`, `~` or a backtick fence, and the output stays plain text.
- **Serialiser:** a field serialises to its token (for example `{{name}}`), and paragraphs join with `\n`. Parsing the incoming `value` works in reverse: tokens matching the configured `fields` become atoms.
- **Effort:** roughly half that of a rich editor. Plain text also makes CodeMirror 6 and a from-scratch build technically viable for v1.
- **Versioning risk:** if v1 uses a plain-text-only engine (CodeMirror, plaintext-only `contenteditable`), v2 (rich HTML) needs a different engine. ProseMirror covers both with the same engine and a larger schema.

## Additional options (beyond the user's list)

| Option | License | Verdict |
|---|---|---|
| **ProseMirror (raw)** | MIT | Leanest model-based engine. Strict schema, atom nodes for fields, and grows into rich text for v2. **Preferred.** |
| **CodeMirror 6** | MIT | Excellent plain-text editor: atomic widget decorations for fields, strong accessibility and input-method handling, value is a string. Cannot grow into the v2 rich editor. A strong alternative only if v2 might use a different engine. |
| **Tiptap 3** | MIT core | ProseMirror plus extension ergonomics, at about +30 kB. Its React/Vue bindings are irrelevant because we wrap it in Stencil. Revisit if extension authoring becomes painful. |
| **Lexical (vanilla)** | MIT | Works without React, but the ecosystem is React-first and it is heavier than ProseMirror. |
| **Trix** | MIT | A native web component with its own toolbar and an HTML-only document model. Poor fit for custom fields and Boreal UI. |
| **Squire** | MIT | Tiny HTML `contenteditable` wrapper (Fastmail) with no schema. Fields and plain-text guarantees would be hand-rolled. |
| **TinyMCE** | GPL 2+ / commercial since v7 | Same licensing problem as CKEditor. |
| **Editor.js** | Apache 2.0 | Block-based JSON. Wrong model for an inline composer. |
| Slate, Plate, BlockNote, Remirror, Milkdown | various | React-only or Markdown-centric. Not integrable. |
| **From scratch:** `contenteditable="plaintext-only"` | — | Baseline since Firefox 136 (Mar 2025). Viable only if fields are plain text highlighted with the CSS Custom Highlight API, which makes them non-atomic (they can be partially deleted). Atomic chips inside `plaintext-only` are unreliable. |

## Feature model (built-in features, consumer supplies data)

Three layers, from most to least built-in:

1. **Built-in tools** enabled declaratively: `toolbar="fields,link,|,emoji"` or an array property. Order sets render order and `|` places a `bds-divider`. Each tool is fully implemented by the component.
2. **Data and behaviour hooks:** `fields: ITextEditorField[]` (`{ value, label, length? }`), and an optional async `linkTransform(url) => Promise<string>` property for Short URL. When absent, the link tool inserts the URL unchanged.
3. **Escape hatch:** `slot="toolbar"` for product-specific tools (Audios, Templates, Sender) plus public methods: `insertText()`, `insertField()`, `setValue()`, `setFocus()`. Slotted tools never touch the engine directly.

| Tool | Proposed version | Design needed |
|---|---|---|
| Fields | v1 | No: reuses `bds-dropdown` / `bds-list-menu`. |
| Link | v1 | Small: `bds-popover` + `bds-text-field` + confirm button. |
| Emoji | v1 if a picker design exists, otherwise v1.1 | **Yes**: picker panel. Also needs an emoji dataset (full set about 30–50 kB; lazy-load it or use a curated subset). |
| Slot + methods | v1 | No. |
| WhatsApp-style marks | later | Small: toggle buttons. |

## Counter strategy and SMS segments

- **v1:** `counter` + `charCount`, consistent with `bds-text-field`. Count = text length + each field's `length` (or its token length when `length` is not set).
- **Extensible:** internally, the counter is a pure function `(segments) => { current, max, label? }`. SMS segments become a second built-in strategy (`counterMode="sms"`), non-breaking.
- **What SMS segments involve:**
  - Detect the GSM-7 alphabet. Extension-table characters (`€ [ ] { } ^ ~ | \`) count as 2.
  - Any character outside GSM-7 (emoji, `á`, `ó`, `ú`, and others) switches the **whole** message to UCS-2.
  - Segment limits: 160 per single segment and 153 per concatenated segment for GSM-7; 70 and 67 for UCS-2. Emoji outside the Basic Multilingual Plane take 2 UCS-2 units.
  - Fields have unknown runtime length, so the count is approximate. This matches the "approx. when replacement field used" copy in Figma.
  - Effort: one pure utility (about 100 lines) plus an exhaustive table-driven spec, and a design for the "N/1000 · 1 SMS" footer label.

## Decision: raw ProseMirror (2026-11-13)

The user chose raw ProseMirror. The engine owns only the editable area. Every other part of the component is Boreal.

### Questions the engine settles

| Topic | How ProseMirror settles it | Still open |
|---|---|---|
| Plain text vs HTML | Schema + serialiser. v1 serialises to a string; v2 adds marks and `DOMSerializer` on the same engine. | — |
| Character count | Derived from the document: `textBetween` with a field atom's `leafText` returning its `length`. A hard limit is possible with `filterTransaction`. | Hard block vs error state (product decision) |
| Fields | Inline `atom` node rendered as a chip. Incoming `value` is parsed by a token regex. | Default token syntax, chip visuals |
| Link (plain text) | `insertText(url)` at the selection, optionally after an async `linkTransform`. | Popover layout (small design) |
| Emoji insertion | `insertText(char)` | **Picker UI and dataset are not engine concerns** |
| Paste | `clipboardTextParser` / `transformPastedHTML` reduce everything to text and fields. | — |
| Undo/redo, input methods for non-Latin scripts, selection | `prosemirror-history`, `prosemirror-keymap`, view internals | — |
| Placeholder | Decoration when the document is empty | — |
| Readonly / disabled | `editable: () => false`; readonly renders without a border, as in Figma | — |
| SMS segments | Independent of the engine: a pure counter function | Footer label design |

### Alignment with existing Boreal components

| Anatomy part | Boreal implementation | Gap |
|---|---|---|
| Label | `renderFieldLabel` → `bds-typography variant="label"` (required, info tooltip) | Its `htmlFor` renders `<label for>`, which cannot target a `contenteditable`. Use `aria-labelledby` on the editable (`role="textbox"`, `aria-multiline="true"`) and focus the editor when the label is clicked. |
| Helper text / error / counter | `renderFieldFooter` | The counter text is hard-coded `current/max`. SMS needs an optional label override later. |
| Toolbar | `bds-toolbar` (`role="toolbar"`, focus handling) | Check the height-41 / bottom-border look against Figma, or style the container in the editor SCSS. |
| Button groups | `bds-button-group` (switches to `role="group"` inside a toolbar) | — |
| Divider | `bds-divider orientation="vertical"` | — |
| Icon buttons | `bds-button` with `slot="icon"` + `label`; `disclosure` adds the chevron (emoji ▾) | No pressed/toggle state (`aria-pressed`). Not needed for v1 insertion tools; needed for later formatting marks. |
| Fields menu | `bds-dropdown` (`slot="trigger"` + `slot="list"`) + `bds-list-menu` | — |
| Link popover | `bds-popover` + `bds-text-field` + `bds-button` | Small design |
| Emoji picker | `bds-popover` + button grid | Needs a design, grid keyboard navigation and a dataset |
| Slot | `slot="toolbar"` | — |
| Form behaviour | `formAssociatedMixin` + `IFormControl<string>` | — |

### Integration gotchas to plan for

- **Focus spans toolbar, popovers and editor.** `bdsBlur` and blur-timed validation must ignore `focusout` events whose `relatedTarget` is still inside the host. Otherwise opening the Fields menu triggers "required" errors.
- **Selection survives toolbar clicks.** Clicking a toolbar button blurs the editor but keeps `state.selection`. Dispatch against it, then call `view.focus()`.
- **Light DOM.** Ship the essential ProseMirror CSS (`white-space: pre-wrap`, etc.) in the component SCSS and scope a reset on the editable, so host-page styles do not restyle content.
- **Bundle scope.** Stencil lazy-loading keeps ProseMirror in the `bds-text-editor` chunk. Verify that the `dist-custom-elements` and React/Vue wrapper builds tree-shake it out of other components.
- Fetch current ProseMirror docs (Context7) before writing the schema, plugins and view setup.

## Emoji picker (2026-11-13)

**Reference UI.** A screenshot of the current production campaign editor (Subject field): an emoji button with ▾, a popover with category tabs (People, Nature, Food, Activity, Travel, Objects, Symbols, Flags), a "Search emoji…" input, sectioned headings ("People") and a scrollable grid of about 7 columns. This is the existing app's picker, not a Boreal Figma design, so Boreal styling still needs design confirmation.

**ProseMirror's role.** It only inserts the emoji (`insertText`, undoable). Typed, pasted and OS-picker emoji, including multi-character sequences (flags, skin tones, ZWJ families), need no extra code. ProseMirror has no picker, dataset or search.

### Measured cost (gzip)

| Package | License | Size | Notes |
|---|---|---|---|
| `emoji-picker-element` 1.29.1 | Apache-2.0 | 13.7 kB JS | Ready-made shadow-DOM picker: tabs, search, skin tones, recently used. Fetches its data from a CDN into IndexedDB by default. |
| `emojibase-data` 18.0.0 `en/compact.json` | MIT | 83 kB | 1,958 emoji with labels, tags and groups; includes skin variations |
| `emojibase-data` 18.0.0 `es/compact.json` | MIT | 77 kB | Spanish labels and keywords for search |
| `unicode-emoji-json` 0.9.0 `data-by-group.json` | MIT | 32 kB | English only, grouped |

A build-time trimmed dataset (group, label, keywords and version; no skin variants) should land around 20–35 kB gzipped. This is an estimate, not measured.

### Options

1. **`bds-emoji-picker` built in-house (recommended).** Built from `bds-tab-group`, `bds-search-bar`/`bds-text-field` and `bds-popover`, with `@tanstack/virtual-core` (already a dependency) for the grid. Uses a trimmed `emojibase-data` JSON loaded with a dynamic import on first open. It matches Boreal pixel for pixel and is reusable (chat reactions, comments).
2. **`emoji-picker-element`.** Fastest to ship and small, but it has its own look, themed only through CSS variables, its own shadow DOM and CDN data by default. It would be a foreign UI inside a Boreal component.

**Decision:** build `bds-emoji-picker` in-house (option 1).

### Composition from existing Boreal components

| Picker part | Boreal implementation | Notes |
|---|---|---|
| Trigger (😀 ▾) | `bds-button` with `slot="icon"` + `disclosure` | Already part of the editor toolbar |
| Floating panel | `bds-popover` | Placement, outside click, `Esc` |
| Category tabs | `bds-tab-group` + `bds-tab` (`slot="icon"`) + `bds-tab-content` | `bds-tab` has no `ariaLabel` prop; icon-only tabs need `aria-label` on the host, which works because the host carries `role="tab"`. Tabs switch panels; they do not scroll to a section. |
| Search | `bds-search-bar` (`mode="search"`, `clearable`) or `bds-text-field` with a search icon | `bds-search-bar` has a built-in polite `role="status"` live region and a debounced input event |
| Section heading ("People") | `bds-typography` | — |
| Emoji grid | **Native `<button>` cells + component SCSS with `var(--boreal-*)` tokens** | Not `bds-button`: hundreds of nested custom elements are too heavy. Follow `bds-calendar-grid` for `role="grid"` and arrow-key navigation. |
| Empty search state | `bds-typography` | — |
| Long lists | `utils/dom/virtualWindow` (`@tanstack/virtual-core`), only if needed | One category per tab panel caps the DOM at about 270 cells (Flags), so virtualisation is probably unnecessary. |

**New SCSS needed:** the grid layout, cell size, hover/focus/selected states and panel sizing. Everything else is existing components.

**Decision:** one category per tab (`bds-tab-group` panels). Search results replace the panel content. No virtualisation.

### Flags: emoji dataset vs `bds-flag` SVGs

The picker's Flags tab uses the emoji dataset: the output is Unicode text, so it must be. **The `bds-flag` SVGs should not be replaced with emoji, and no follow-up removal task is needed.**

| Reason | Detail |
|---|---|
| Windows | Windows has no flag emoji glyphs and shows regional letters ("CO"). `bds-flag` / `bds-select` country pickers would break for Windows users, who are common in the target apps; the production screenshot is Windows. |
| Coverage | `constants/flags/4x3` has 271 SVGs, including flags with no Unicode emoji: `es-ct`, `es-ga`, `es-pv`, `sh-ac`, `sh-hl`, `sh-ta`, `gb-nir`, `arab`, `asean`, `cefta`, `eac`. |
| Visual consistency | Emoji flags look different on every OS (waving on Apple, flat elsewhere) and do not support `bds-flag`'s `shape` (circle/rectangle) cleanly. |
| Cost | Already lazy: `generatedFlags.ts` dynamic-imports one SVG per flag on demand. The 2.7 MB is repository size, not page weight. |

The two serve different purposes: `bds-flag` is an *image of a country*; a flag emoji is *a character in a message*, rendered by the recipient's device.

**Decision:** hide the Flags tab when the device cannot render flag emoji. Detect this with a feature test (draw a flag emoji on a canvas and check that it renders as one glyph), not by user-agent sniffing.

### Gotchas

- **Windows** has no flag emoji glyphs (it shows the regional letters, such as "CO"). Hide the Flags category on Windows or render flag images.
- **Unsupported newer emoji** render as empty boxes on older OS versions. Filter the list by emoji version or detect support with a canvas test.
- **Grid accessibility:** `role="grid"` with arrow-key navigation, search results announced through a live region, `Esc` closes the picker and returns focus to the editor at the saved selection.
- **Counter:** 😀 is 1 grapheme but 2 UTF-16 units. Characters mode should count graphemes with `Intl.Segmenter`; SMS mode counts UCS-2 units.
- **Localisation:** search keywords follow the dataset locale (en/es available in `emojibase-data`).

## Decision: limit behaviour (2026-11-13)

**Hard block, consistent with `bds-text-field`** (which passes `effectiveMaxLength` to the native `maxLength`):

- Typing past `charCount` is blocked (`filterTransaction`).
- Paste is truncated to the remaining space.
- A field or emoji that does not fit is not inserted, and its toolbar trigger is disabled while it cannot fit.
- A programmatic `value` that exceeds the limit shows the error state (`tooLong`), which covers the Notion "Text exceeds the character limit" case.

## Decision: field tokens (2026-11-13)

**Each field declares its exact serialised token:** `ITextEditorField = { token: string; label: string; length?: number }`.

- The chip shows `label`, and the value contains `token`.
- Parsing an incoming `value` turns exact occurrences of the configured tokens back into field atoms (longest token first, so overlapping tokens resolve correctly).
- Tokens must be unique. Duplicates produce a dev-mode console warning.
- No global syntax or regex setting. Covers `{{1}}`, `[URL_Identify_Senders]` and `DF-Name`.
- Counter weight: `length` when set, otherwise the token's length.

## Decision: field chip visuals (2026-11-13)

Inside the text area, an inserted field renders as a **lightweight inline `<span>` chip** (a ProseMirror node view, `contenteditable="false"`) showing `label`. It is styled with the same `var(--boreal-*)` tokens as `bds-tag` (gray background, radius, small text) and sized to fit the line height.

- It does **not** use the `bds-tag` element, which would bring a focusable close button, line-height jumps and per-chip custom-element cost.
- It is atomic: one Backspace deletes the whole chip.
- Accessible name: "Field: {label}".
- Pending a quick design review.

The Fields *dropdown* (`bds-dropdown` + `bds-list-menu`) needs no new design.

**Readonly / disabled:** the same chip node view with `editable: () => false`. Readonly has no border and no toolbar (as in Figma). Disabled dims the chips.

## Open questions

1. ~~Engine~~ — **raw ProseMirror** (decided).
2. Emoji picker: request a design, or ship v1 without emoji?
3. Counter limit: hard-block typing at `charCount`, or allow overflow with an error state (as `bds-text-field` does)?
4. Field token syntax: one fixed syntax (`{{name}}`) or configurable per consumer (`[NAME]`, `{{1}}`)?
5. Field chip visual design in the editable area.
6. Readonly state: render plain text (as Figma shows) with field tokens resolved to labels?
7. Verify all four brand themes once the Figma MCP is authenticated.
