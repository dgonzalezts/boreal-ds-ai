---
ticket: EOA-18739
component: bds-text-editor
status: validated
---

# bds-text-editor v1 — validated design

All five sections were reviewed and confirmed by the user on 2026-11-13. The evidence and options are in `ai-work/research/2026-11-13-bds-text-editor-engine-spike.md`. A visual version is at https://claude.ai/artifact/1DgCn7PhGQZvTyixsViR6p.

## Decisions

| Topic | Decision |
|---|---|
| Versioning | A versioned component. v1 is the plain-text message composer; the rich HTML editor comes in a later version of the same component. |
| Engine | Raw ProseMirror (`prosemirror-model`, `-state`, `-view`, `-history`, `-keymap`). CKEditor 5 was rejected: about 192 kB + 43 kB CSS gzipped against 60 kB, plus license-key distribution. |
| Output | Plain text. A field serialises to its `token`; paragraphs join with `\n`. |
| Fields | `ITextEditorField = { token, label, length? }`. Each field declares its exact token, with no global syntax. Shown in the editor as an atomic inline chip with `bds-tag` styling (a lightweight span, not the `bds-tag` element). |
| Counter | Characters (graphemes via `Intl.Segmenter`) plus each field's weight (`length` or the token length). A pure function, so SMS segments can be added later without breaking changes. |
| Limit | Hard block, as in `bds-text-field`. Paste is truncated; a field or emoji that does not fit is not inserted. An app-set value over the limit shows the `tooLong` error. |
| Emoji | An in-house `bds-emoji-picker` (Molecule, reusable), with one category per `bds-tab-group` tab and a trimmed `emojibase-data` dataset (en/es) loaded on first open. The Flags tab is hidden when the device cannot render flag emoji (canvas feature test). |
| `bds-flag` SVGs | Kept. Not replaced by emoji, and no follow-up task. |
| Readonly / disabled | Same chips with editing off. Readonly has no border and no toolbar; disabled dims the chips. |

## Part 1 — Components and structure

- `bds-text-editor`: Forms, Organism, form-associated. Built from the label (`renderFieldLabel`), `bds-toolbar` → `bds-button-group` (emoji, link) → Fields (`bds-dropdown` + `bds-list-menu`) → vertical `bds-divider` → `slot="toolbar"`; then the ProseMirror editable; then `renderFieldFooter`.
- `bds-emoji-picker`: Forms, Molecule. Panel only; the host owns the trigger and the `bds-popover`.
- Internal modules: `schema.ts`, `serializer.ts`, `counter.ts`, `plugins.ts` (placeholder, limit, plain-text paste, history, keymap), `field-view.ts`.
- Out of v1: HTML output, formatting marks, SMS counting, Short URL backend calls (apps provide `linkTransform`).

## Part 2 — Public API

- Form props, the same as `bds-text-field`: `name`, `value` (not reflected), `defaultValue`, `required`, `disabled`, `readOnly`, `error`, `errorMessage`, `customValidators`, `validationTiming`.
- Field-part props: `label`, `info`, `helperText`, `placeholder`, `counter`, `charCount` (also the hard limit), `customWidth`.
- Editor props:
  - `toolbar: string = 'emoji,link'`: built-in tools in order, with `|` for a divider.
  - `fields: ITextEditorField[]`: the Fields tool hides itself when empty.
  - `linkTransform?: (url) => Promise<string>`
  - `emojiLocale: 'en' | 'es'`
  - `labels?: TextEditorLabels`: every visible and screen-reader string, merged with `DEFAULT_TEXT_EDITOR_LABELS` (ADR 0014; amended 2026-11-17).
- Events: `valueChange`, `bdsInput`, `bdsChange`, `bdsFocus` and `bdsBlur` (component-level focus only), `bdsValidationChange`.
- Methods: `setFocus()`, `insertText(text)`, `insertField(token)` (both return `false` when nothing is inserted), `checkValidity()`, `reportValidity()`. Slot: `toolbar`.
- `bds-emoji-picker`: `locale`, `labels?: EmojiPickerLabels` (`searchPlaceholder`, `noResults`, `loadError`, `retry`; ADR 0014, amended 2026-11-17); event `bdsEmojiSelect { emoji, label }`; method `setFocus()`.
- The typing area keeps the Figma height and scrolls; there is no auto-grow in v1.

## Part 3 — Data flow

- The document is the single source of truth, and `value` is always the serialised document.
- **Value in:** re-parse only when the incoming value differs from the current serialisation. App-set values skip the undo history and the limit filter. A change to `fields` re-parses the value.
- **Value out:** every document change updates `value`, emits `bdsInput` and `valueChange`, and updates the form value. `bdsChange` fires when focus leaves the component with a changed value.
- **Toolbar:** a shared `insert()` uses the selection preserved while the editor was blurred, checks the limit, dispatches the change, then refocuses the editor.
  - The emoji popover closes after each pick.
  - Link checks the URL with `@braintree/sanitize-url`, then runs the optional `linkTransform` with a loading state.
  - Fields options are disabled individually when they do not fit.
- **Validity:**
  - `valueMissing`: empty after trimming; a chip on its own counts as content.
  - `tooLong`: the count exceeds `charCount`.
  - `customValidators` run on the serialised string.
  - Form reset restores `defaultValue`.
- **Risk:** blocking a change during IME composition. Spike it first; the fallback is to trim at `compositionend`.

## Part 4 — Errors and accessibility

- **Errors:**
  - Validation uses the existing field pattern.
  - An invalid URL shows an inline error.
  - When `linkTransform` fails, the popover stays open and offers to insert the original URL.
  - When emoji data fails to load, the picker shows an error state with a Retry button.
  - Unknown or duplicate tokens produce development-build warnings.
- **Typing area:**
  - `role="textbox"`, `aria-multiline`, `aria-labelledby`, and `aria-describedby` (helper and counter).
  - ARIA state attributes follow the props.
  - Clicking the label focuses the editor; `Tab` leaves the editor.
- **Toolbar:** sits before the typing area in tab order, has named icon buttons, and `Alt+F10` jumps to it. Popovers move focus in, and `Esc` restores the cursor.
- **Chips:** visually hidden "Field:" text, and a visible border in forced-colours mode.
- **Counter:** a polite announcement at 20 characters left and at the limit.
- **Picker:** named tabs, a search result-count live region, and `role="grid"` with roving focus and localised names.

## Part 5 — Testing

1. Pure modules: Jest, table-driven, no DOM.
2. Component specs: `newSpecPage`, ≥ 80% coverage.
3. Stryker: ≥ 90% mutation score on the serializer, counter, limit plugin and emoji search.
4. Browser QA: qa-subagent with Playwright on Chromium, Firefox and WebKit; React and Vue wrappers; a real `<form>` submit; NVDA and VoiceOver by hand.
5. Visual: Storybook and Chromatic, all states in four brand themes.
6. Bundle: inspect the build output.

**First spike:** check whether ProseMirror's view runs on Stencil's mock-doc. If not, put the view behind an adapter that specs can replace with a fake.

## Delivery split (decided 2026-11-13)

| Version | Ticket | Plan | Scope |
|---|---|---|---|
| v1 (4 days, review-ready) | EOA-18739 | `ai-work/plans/EOA-18739-bds-text-editor-v1.md` | Composer core: plain text, Fields, Link, counter and limit, form association, all Figma states, core accessibility, Vue `v-model`, basic docs, coverage ≥ 80% |
| v2 (2 weeks) | TBD | `ai-work/plans/TBD-bds-text-editor-v2.md` | `bds-emoji-picker` and the Emoji tool, `linkTransform`, `Alt+F10`, announcements, forced colours, IME check, full QA matrix, four-theme Chromatic, bundle check, mutation testing ≥ 90% |
| v3 (later, proposal) | TBD — draft `ai-work/tickets/TBD-bds-text-editor-v3.md` | none until scope is confirmed and a research spike concludes | Rich HTML editor |

In v1, `emoji` is already a valid `toolbar` id and the default stays `'emoji,link'`; v1 renders nothing for it, so v2 changes no default.

## Branching

`feature/EOA-18739_text-editor-v1_DG` is stacked on `chore/EOA-20193_dependency-upgrades-followup_DG` (`4774509f`). After EOA-20193 is squash-merged (after the team cut-off and sync pass, EOA-20193 T24), run `git rebase --onto release/current <EOA-20193 tip> feature/EOA-18739_text-editor-v1_DG`. The editor PR stays a draft against the EOA-20193 branch until then.

## Still open (for the plan)

- Verify Figma node `14-34766`, the token values and the four brand themes (the Figma MCP was not authenticated during brainstorming).
- Design sign-off: emoji picker styling (the reference is the production picker), field chip, link popover.
