---
ticket: EOA-18739
component: bds-text-editor
status: in progress
created: 2026-11-13
---

# bds-text-editor v1 (composer core) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Deliver a review-ready `bds-text-editor` in 4 days: a form-associated plain-text composer with field chips, links and a hard character limit.

**Ticket brief:** [`ai-work/tickets/EOA-18739-bds-text-editor.md`](../tickets/EOA-18739-bds-text-editor.md)

**Design:** [`ai-work/sessions/2026-11-13-bds-text-editor-design.md`](../sessions/2026-11-13-bds-text-editor-design.md) · Research: [`ai-work/research/2026-11-13-bds-text-editor-engine-spike.md`](../research/2026-11-13-bds-text-editor-engine-spike.md) · Next version: [`TBD-bds-text-editor-v2.md`](./TBD-bds-text-editor-v2.md)

**Decisions (Confluence, SENG › Text Editor ADRs):** ADR-0017 engine, ADR-0018 value contract and field tokens, ADR-0019 counting and limits, ADR-0020 toolbar extension model, ADR-0008 localizable copy. Local copies: `ai-docs/decisions/0020`–`0023` and `0014` (local numbering differs).

**Architecture:**
- **Editing core.** Raw ProseMirror owns only the editable area. Its schema is document → paragraph → text | `field` atom.
- **Pure helpers.** Plain-TypeScript modules (schema, serializer, counter, plugins) hold the logic and are tested without a DOM.
- **Composition.** The Stencil component composes `renderFieldLabel`, a toolbar (`bds-toolbar` or editor-local per T1) with `bds-button-group`, `bds-dropdown` + `bds-list-menu`, `bds-divider`, `bds-popover`, and `renderFieldFooter`.

**Tech Stack:** Stencil 4.45 (light DOM, `formAssociatedMixin`), `prosemirror-model` ~1.25.13, `prosemirror-state` ~1.4.4, `prosemirror-view` ~1.42.9, `prosemirror-history` ~1.5.1, `prosemirror-keymap` ~1.2.3, `prosemirror-commands` ~1.7.2 (tilde = minor-version pinning; fetched 2026-11-13, re-verify in T2), Jest via `stencil test --spec`, Storybook.

**Time box:** 4 days to review-ready (T1–T10). T11 runs after EOA-20193 merges and is outside the time box.

**Branch:** `feature/EOA-18739_text-editor-v1_DG`, stacked on `chore/EOA-20193_dependency-upgrades-followup_DG` at `4774509f`. The PR is a draft against that branch until T11.

**Working rules for every task:**
- Run `fnm use` before Node or pnpm commands.
- Fetch ProseMirror docs with Context7 before writing integration code. If Context7 is unavailable (it failed to connect on 2026-11-17), fetch the official reference at `https://prosemirror.net/docs/ref/` instead, and never rely on recalled API shapes.
- Localizable copy follows ADR 0014: every visible or screen-reader string comes from `labels`, never a literal.
- No inline comments. JSDoc goes on the public API only, never on type files.
- `var(--boreal-*)` tokens only.
- Never commit `src/index.html`. Keep each task's QA scenario in it as a visible `.section`.
- No ticket IDs in test files. No version labels in consumer-facing text.
- Commit only after the user confirms the exact message. No `Co-Authored-By` trailer.

**JSDoc gate (applies to every task that declares a `@Prop`, `@Event` or `@Method`):** JSDoc is 1–2 sentences and consumer-facing only: what it does, or what the consumer sees or receives. Never internal implementation details. It matches the worked examples in `ai-docs/guidelines/jsdoc-template.md`.

---

## Files to create / modify

Paths are relative to `packages/boreal-web-components/` unless they start with `apps/`.

| File | Notes |
| --- | --- |
| `package.json`, root `pnpm-lock.yaml` | Modify — ProseMirror dependencies (T2) |
| `src/components/forms/bds-text-editor/types/ITextEditor.ts`, `types.ts`, `enum.ts`, `index.ts` | New — T3 |
| `src/components/forms/bds-text-editor/utils/constants.ts` | New — `DEFAULT_TEXT_EDITOR_LABELS` (T3), following `bds-date-picker/utils/constants.ts` |
| `src/components/forms/bds-text-editor/helpers/schema.ts`, `serializer.ts`, `counter.ts`, `field-view.ts` | New — T3 |
| `src/components/forms/bds-text-editor/helpers/plugins/limit.ts`, `plain-paste.ts`, `placeholder.ts`, `index.ts` | New — T3 |
| `src/components/forms/bds-text-editor/helpers/editor-adapter.ts` | New — the only module that creates an `EditorView` (T5) |
| `src/components/forms/bds-text-editor/bds-text-editor.tsx` | New — T5, T6 |
| `src/components/forms/bds-text-editor/bds-text-editor.scss` | New — T7 |
| `src/components/forms/bds-text-editor/__test__/*.spec.ts` | New — T4, T8 |
| `targets/vue-output-target.ts` | Modify — `v-model` mapping (T9) |
| `apps/boreal-docs/src/stories/forms/bds-text-editor/bds-text-editor.stories.ts`, `.mdx` | New — T9 |
| `src/index.html` | Playground only, never committed |

---

## Progress

| Task | Status |
| --- | --- |
| T1 Figma research and sign-off request (no Jira sub-task) | done |
| T2 Add dependencies and mock-doc check — EOA-21464 (02) | pending |
| T3 Editor core modules (types, schema, serializer, counter, plugins, chip view) — EOA-21465 (03) | pending |
| T4 Core module unit tests — EOA-21466 (04) | pending |
| T5 Component logic: scaffold, value flow, form association — EOA-21467 (05) | pending |
| T6 Component render, Fields and Link tools, methods, core accessibility — EOA-21468 (06) | pending |
| T7 SCSS — EOA-21469 (07) | pending |
| T8 Component unit tests — EOA-21470 (08) | pending |
| T9 Vue v-model, Storybook story and basic MDX — EOA-21471 (09) | pending |
| T10 Review readiness: smoke QA and draft PR — EOA-21472 (10); Definition of Done check — EOA-21474 (11) | pending |
| T11 Rebase onto `release/current` after EOA-20193 merges (outside the time box) | pending |

---

### Task 1: Figma research and sign-off request

**Status:** done (sign-off request sent by the user on 2026-11-17; chip and popover designs validated by design on 2026-11-17; 10 of 48 variants pulled; the other 38 are pulled in T7's research pass)
**Executor:** main thread (no executor)
**Files:** this plan (values recorded under T7)
**Time:** about 2 hours. Requires the Figma MCP; load `figma:figma-design-to-code` before `get_design_context`.

**Acceptance criteria:**

- Pull node `14-34766` (file `rtiE5zGA4aoOuxIQMgfD6h`) and record:
  - variant properties
  - state variants (Default, Hover, Focus, Active, Disabled, Readonly, Error, Populated)
  - token names for background, border, border weight and radius
  - sizes: 448 × 152 and toolbar 41 *(unconfirmed, re-pull)*
- Decide whether `bds-toolbar` matches the toolbar region or the editor styles its own toolbar row. Record the decision.
- Record which brand themes exist. v1 verifies the default theme; the other three are a v2 Chromatic check.
- Draft a sign-off request for the field chip and the link popover for the user to send. *(Sent by the user on 2026-11-17.)*

**Manual test _(required — not waveable)_:** Non-visual task. Pass: values recorded with their source node IDs; sign-off request delivered.

**Commit:** none (plan-only).

#### T1 findings (recorded 2026-11-17)

**Source:** file `rtiE5zGA4aoOuxIQMgfD6h`, frame `TextEditor` node `14:34765` (the user-supplied node; the plan's `14:34766` is its first child, Default / Outline). Boreal token names below are the Figma variable names; the matching `--boreal-*` custom properties are confirmed in T7, not assumed here.

**Variant properties (node `14:34765`, 48 variants):** `State` = Default, Hover, Focus, Active, Disabled, Readonly; `State Error` = False, True; `Populated` = False, True; `Variant` = **Outline, Plain**. Boolean layer toggles: `header`, `toolbar`, `buttons`, `divider`, `slot`, `footer`, `helperText`, `charCounter`.

**Decision (2026-11-17): add a `variant` prop in v1.** The plan had none, but Figma has two variants. Default is `outline`, pending the design answer in the sign-off request. Outline: 1px border around the container and around the toolbar. Plain: no container border, toolbar has a bottom border only. Node IDs: Outline Default `14:34766`, Plain Default `3332:85162`; every Plain node is the Outline ID's counterpart in the `3332:85162`–`3332:85467` range.

**Pulled so far (Outline unless stated):**

| State | Node | Container | Toolbar | Content area | Other |
| --- | --- | --- | --- | --- | --- |
| Default, empty | `14:34766` | bg `ui (components)/default-base`, border `stroke/xs` `stroke/default-light`, radius `radius/xs` | bg `ui (components)/inverse`, border `stroke/xs` `stroke/default-light`, h 41, padding `spatial/padding/s`, gap `spatial/gap/s`, top radii `radius/xs` | bg `ui (components)/inverse`, padding x `spatial/padding/s`, y `spatial/padding/1xs`, placeholder `text/default-light` body/sm | label `text/default-darker` supporting/label/xs; helper and counter `text/default-light` body/xs; container gap `spatial/gap/2xs` |
| Default, empty, Plain | `3332:85162` | no border, radius `radius/xs` | border-bottom only (`stroke/xs`; other sides `stroke/none`) | same as Outline | same |
| Default, populated | `14:34781` | as Default | as Default | text `text/default-darker` body/sm | |
| Hover | `14:34796` | adds shadow `Box shadow/s` (0 `depth/y/s` `depth/blur/s` `depth/color/base`) | as Default | as Default | |
| Focus | `14:34826` | adds `Box shadow/focus` (spread `depth/spread/xs` `depth/state/focus/inner-color`, then `depth/spread/m` `depth/state/focus/outer-color`) | as Default | caret text `text/default-darker` | |
| Active | `14:34856` | focus shadow plus inner shadow `Box shadow/active` | as Default | as Focus | |
| Disabled | `14:35056` | as Default | bg `ui (components)/default-lighter`; divider line `ui (components)/default-light`; buttons use full `radius/xs` each (not a joined group) | bg `ui (components)/default-lighter`, placeholder text is `-` in `text/disabled` | label `text/disabled`; helper and counter unchanged |
| Readonly | `14:34886` | **no border, no background, no toolbar**; radius `radius/xs`; height 122 (empty) | none | padding y `spacing/1xs` only (no x padding), text `text/default-darker` | |
| Error, Default | `14:34916` | border `stroke/danger-base` | as Default | as Default | helper and counter `text/danger-base` |
| Error, Focus | `14:34976` | `stroke/danger-base` border plus focus shadow | as Default | as Focus | helper and counter `text/danger-base` |

**Not yet pulled (left for T7's research pass):** Hover and Active with Error, Disabled with Error (192 tall), Readonly with Error (192 tall), Readonly populated (72 tall), and the populated Hover, Focus, Active and Disabled variants. Plain counterparts of the states above.

**Sizes:** default frame 448 × 152 (confirmed). Toolbar height 41 (confirmed). Readonly 122 empty and 72 populated; Disabled/Readonly with Error 192 (the extra 40 is not yet explained and likely an error message row; confirm in T7).

**Toolbar contents (Figma):** a joined button group (emoji with disclosure chevron, then link; each 32 high, padding x `spatial/padding/1xs`, y `spatial/padding/2xs`, icons 16), a vertical divider (18 high, 1 wide, colour `ui (components)/default-lighter`), then a slot placeholder ("Guide zone", dashed `stroke/default-light`). In v1 emoji renders nothing, so the group shows only what `toolbar` lists.

**Footer:** helper text and counter in one row, gap `spatial/gap/s`, counter right aligned, reads `0/0`.

**Toolbar decision:** use `bds-toolbar` for the toolbar row. It already supplies `role="toolbar"`, an `aria-label` (fed from `labels.toolbar`), roving arrow-key navigation, and these map onto the Figma values: `gap="sm"` (12 = `spatial/gap/s`), `density="comfortable"` (padding 12 = `spatial/padding/s`), `border="all"` for Outline and `border="bottom"` for Plain. The editor adds only editor-local rules on a class: background `ui (components)/inverse`, height 41, top radii, and the disabled background. Consequences to confirm in T6: (1) roving tabindex makes the toolbar one Tab stop, which matches "toolbar first, then the editable"; (2) `bds-toolbar` builds its item list lazily from non-disabled buttons, so a disabled toolbar has no focusable items, which matches the "Tab skips the tools" check; (3) a button inside `bds-popover` content must not be picked up by the toolbar's selector, so the link form needs to render outside the `bds-toolbar` element or be verified.

**Brand themes:** four exist in `packages/boreal-style-guidelines/src/tokens/theme/`: `connect`, `engage`, `protect`, `proximus`. The playground default is `data-theme="engage"`. v1 verifies `engage`; the other three are the v2 Chromatic check.

**Field chip and link popover:** neither exists in this Figma frame. Design validated both looks on 2026-11-17 (Part 6 of the design artifact). The chip is based on the gray `bds-tag` tokens, wraps with the text and is never truncated.

**Sign-off request (draft, for you to send to design):**

> Hi, we're building `bds-text-editor` and need two designs before we can finish styling. They are not in the TextEditor frame (`14:34765`).
>
> 1. **Field chip:** the inline chip that represents an inserted field such as `{{1}}`. Please give default, hover, selected (the cursor or a selection is on it), Disabled and Readonly states. We plan to base it on the gray `bds-tag` tokens unless you say otherwise.
> 2. **Link popover:** the panel that opens from the toolbar's link button. It holds a URL field, an Insert button and the two error messages ("Enter a valid URL" and "This link is longer than the space left.").
>
> Also: the frame has an Outline and a Plain variant, and the plan only covered one. Which should be the default, and should consumers be able to switch?
>
> Please reply with the node links when ready.
>
> Proposed designs for both parts are in Part 6 of the design artifact: https://claude.ai/artifact/1DgCn7PhGQZvTyixsViR6p

**Link scope (decided 2026-11-17):** link only. The popover has one URL field and an Insert button, and the URL is inserted as plain text. No display text and no placeholder option; dynamic URLs come from the Fields tool.


### Task 2: Add dependencies and mock-doc check

**Status:** pending
**Executor:** main thread (dependencies), @testing-subagent (mock-doc check)
**Files:** `package.json`, `pnpm-lock.yaml`; the check uses a throwaway spec that is not committed

**Acceptance criteria:**

- **Dependencies:**
  - Re-fetch `https://registry.npmjs.org/<pkg>/latest` for the six ProseMirror packages. Respect `minimumReleaseAge` and never take a `prosemirror-view` beta.
  - Add them as runtime `dependencies` with pnpm 12, each **pinned to its minor version with a tilde range** (for example `~1.25.13`), decided 2026-11-17. Check `package.json` after installing, because pnpm writes `^` by default.
  - `pnpm install --frozen-lockfile` and `pnpm peers check` pass.
  - The lockfile is in the commit (`git show HEAD:pnpm-lock.yaml`).
  - `pnpm validate:all` passes after committing.
- **Mock-doc check (about 2 hours):** in a throwaway spec, create an `EditorView` inside `newSpecPage`, dispatch `insertText`, and read the DOM.
  - **Decision recorded in this status line:** either specs use the real view, or `editor-adapter.ts` is replaced with a fake (`jest.mock`) in component specs.
  - The IME check moves to v2.

**Manual test _(required — not waveable)_:** Non-visual task. Pass: `pnpm build` and `pnpm test` succeed, and the mock-doc decision is recorded.

**Commit:** `build(deps): EOA-18739 add prosemirror`

### Task 3: Editor core modules

**Status:** pending
**Executor:** @frontend-subagent
**Files:** `types/*`, `utils/constants.ts`, `helpers/schema.ts`, `helpers/serializer.ts`, `helpers/counter.ts`, `helpers/plugins/*`, `helpers/field-view.ts` (create)

**Utility discovery:**
- **Searched:** `src/types/form.ts` (`IFormValidator`), `src/utils/form/field-form-association.ts` (`ValidationChangePayload`), `src/mixins/form-associated.mixin.ts` (`IFormControl<T>`), and `bds-text-field/types/` as the sibling pattern.
- **Reuse:** those types.
- **New:** only editor-specific types and ProseMirror modules. Nothing equivalent exists in the codebase.

**Acceptance criteria:**

- **Types:**
  - `ITextEditorField = { token: string; label: string; length?: number }`.
  - `TEXT_EDITOR_TOOL = { EMOJI: 'emoji', LINK: 'link', FIELDS: 'fields', DIVIDER: '|' }` with a derived union.
  - `TEXT_EDITOR_VARIANT = { OUTLINE: 'outline', PLAIN: 'plain' }` in `enum.ts` with a derived union, following the const-object pattern.
  - Event detail types matching `bds-text-field`.
  - `ITextEditor` lists the v1 props only (no `emojiLocale` or `linkTransform`; v2 adds them), including `labels?: TextEditorLabels`.
  - No JSDoc in type files.
- **Localizable copy (ADR 0014, two or more strings → one bundled `labels` object):**
  - `TextEditorLabels` is an all-optional object type. Its v1 keys cover every visible or screen-reader string: `toolbar` ("Text editor tools"), `insertField` ("Insert field"), `insertLink` ("Insert link"), `linkUrl` (the URL field label, "Link URL"), `insertLinkConfirm` ("Insert"), `invalidUrl` ("Enter a valid URL"), `linkTooLong` ("This link is longer than the space left."), `fieldPrefix` ("Field: ").
  - `DEFAULT_TEXT_EDITOR_LABELS: Required<TextEditorLabels>` in `utils/constants.ts` holds the English defaults, matching `DEFAULT_DATE_PICKER_LABELS`.
  - Final key names follow `DatePickerLabels`' naming style. Any string added later in this plan gets a key here, never a hard-coded literal.
  - No string with a number or plural form in v1. The field chip's prefix is the only string the node view uses.
- **Schema:** `doc` → `paragraph+`; `paragraph` → `(text | field)*`. `field` is an inline, selectable atom with attrs `token` and `label`, and `leafText` returns the token. No marks.
- **Serializer:**
  - `serialize(doc)`: paragraphs joined with `\n`, fields replaced by their tokens.
  - `parse(text, fields, schema)`: split on `\n`, normalise `\r\n`, match the **longest token first**, leave unknown tokens as text. Empty input gives one empty paragraph.
  - Duplicate tokens: the first definition wins, with a development warning (`[BorealDS TextEditor] …`).
  - Round trip holds for every input.
- **Counter:**
  - `countCharacters(doc, fields)` counts graphemes with `Intl.Segmenter`, adds each field's `length` (or its token's grapheme count), and counts each paragraph break as 1.
  - `graphemeSlice(text, max)` returns at most `max` whole graphemes.
  - Shaped as a strategy function, with no SMS code.
- **Plugins:**
  - Limit: rejects user transactions over `max`; lets through transactions with the meta `external: true` and any that lower the count; `max <= 0` means no limit.
  - Plain paste: reduces pasted content to text, turns configured tokens into chips, truncates with `graphemeSlice`.
  - Placeholder: an `aria-hidden` decoration while the document is empty.
  - History and keymap: `history()`, undo and redo keys, `baseKeymap`; `Tab` is not bound.
- **Field view:** `<span class="bds-text-editor__field" contenteditable="false">` containing visually hidden prefix text (the `fieldPrefix` label, passed in by the component) and the label. Backspace removes the whole chip.

**Manual test _(required — not waveable)_:** Non-visual task, validated by T4. Pass: lint and build are clean.

**Commit:** `feat(web-components): EOA-18739 add text editor core modules`

### Task 4: Core module unit tests

**Status:** pending
**Executor:** @testing-subagent
**Files:** `__test__/bds-text-editor.serializer.spec.ts`, `.counter.spec.ts`, `.plugins.spec.ts` (create)

**Unit tests to cover:**

- **`serializer`** (table-driven): round trips; `{{1}}` vs `{{10}}`; regex metacharacter tokens (`[URL_Identify_Senders]`); unknown tokens; `\r\n`; empty and whitespace input; consecutive empty lines; duplicate-token warning.
- **`counter`:** ASCII, accented characters, skin tones, ZWJ families and flags each counted as 1; fields with and without `length`; paragraph breaks; `graphemeSlice` never splits a grapheme.
- **`plugins`** (`EditorState.apply`, no DOM): limit reject, accept `external`, accept deletion, `max = 0`; paste truncation and pasted tokens becoming chips; placeholder only when empty; undo and redo.
- Coverage-phase only (≥ 80%). Mutation testing is in the v2 plan.

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-18739 cover text editor core modules`

### Task 5: Component logic — scaffold, value flow, form association

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx`, `helpers/editor-adapter.ts` (create)

**Utility discovery:**
- Pattern: `bds-text-field.tsx` (`extends Mixin(formAssociatedMixin)`, `useFormField<string>(this)`, `formAssociated: true`, light DOM).
- Reuse: `runValidators`, `deriveFieldRenderState`, `createId`.
- Team memory `face-composite-child-value-sync-on-non-string-branch`: every commit path syncs the form value.

**Integration research pass:**
- [ ] `useFormField` and `formAssociatedMixin` are shared. Use them unchanged; log a task if a gap appears.
- [ ] Boundary: `value` set to `null` or `undefined` is treated as `''`; a non-array `fields` is treated as `[]` with a development warning.
- [ ] Default/empty: an empty editor serialises to `''`.
- [ ] Reactivity: `value`, `fields`, `disabled`, `readOnly`, `charCount` and `labels` are reactive after mount.
- [ ] Boundary: `labels` set to `undefined` or `{}` gives the English defaults.

**Acceptance criteria:**

- **Props:**
  - Form: `name`, `value` (mutable, not reflected), `defaultValue`, `required`, `disabled`, `readOnly` (`attribute: 'readonly'`), `error`, `errorMessage`, `customValidators`, `validationTiming = 'blur'`.
  - Field parts: `label`, `info`, `helperText`, `placeholder`, `counter`, `charCount`, `customWidth`.
  - Editor: `toolbar = 'emoji,link'`, `fields = []`, `labels?: TextEditorLabels` (JS property), `variant = 'outline'` (reflected; `validatePropValue` in `componentWillLoad`).
- **Labels:**
  - A private `mergedLabels` getter returns `{ ...DEFAULT_TEXT_EDITOR_LABELS, ...this.labels }`, the same pattern as `bds-date-picker`.
  - `labels` is reactive: a change re-renders, and the field node views redraw so chip prefixes update.
  - A partial object overrides only the keys it contains.
- **Events:** `valueChange`, `bdsInput`, `bdsChange`, `bdsFocus`, `bdsBlur`, `bdsValidationChange`.
- **Methods:** `setFocus`, `checkValidity`, `reportValidity`. `insertText` and `insertField` are declared here and implemented in T6.
- JSDoc gate applies.
- **Adapter:** `editor-adapter.ts` alone creates and destroys `EditorView`. Specs use it per the T2 decision.
- **Mount:** build the state from `parse(value || defaultValue, fields)` with T3's plugins; `editable` follows `disabled` and `readOnly`.
- **Value out:** a change sets `value = serialize(doc)`, emits `bdsInput` and `valueChange`, and updates the form value and validity. A guard flag stops the `@Watch` from re-parsing the editor's own update.
- **Value in:** `@Watch('value')` re-parses only when the value differs, using a transaction with `external: true` and `addToHistory: false`. `@Watch('fields')` re-parses the current value.
- **Validity:** `valueMissing` (trimmed and empty; a chip on its own is content), `tooLong`, then `customValidators`. Messages go through `deriveFieldRenderState`.
- **Focus:** `bdsFocus`, `bdsBlur`, `bdsChange` and blur-timed validation fire only when focus enters or leaves the **host**, judged by `focusout.relatedTarget`.
- **Form callbacks:** `formResetCallback` restores `defaultValue`; `formDisabledCallback` behaves like `disabled`.

**Manual test _(required — not waveable)_:**

Playground scenarios (minimal render: label + editable is enough until T6):
- Scenario 1: inside a `<form>` with `required` and a submit button that logs `FormData` and `checkValidity()`.
- Scenario 2: `fields` set by script, and a button that sets `Hello {{1}}`.
- Scenario 3: `charCount=20`, and a button that sets a 30-character value.

Run `pnpm dev:components`:
- [ ] Given scenario 1 empty, when submitted, then it is blocked. After typing, `FormData` holds the text. Pass: both.
- [ ] Given scenario 2, when the value is set, then a chip renders and `value` reads `Hello {{1}}`. Pass: round trip.
- [ ] Given scenario 3, when the long value is set, then `checkValidity()` is `false`. Pass: `tooLong`.
- [ ] Given scenario 1, when the form is reset, then the editor shows `defaultValue`. Pass: reset.

**Commit:** `feat(web-components): EOA-18739 add bds-text-editor value flow and form association`

### Task 6: Component render, Fields and Link tools, methods, core accessibility

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx` (modify)

**Utility discovery:**
- Reuse `renderFieldLabel`, `renderFieldFooter` and `deriveFieldRenderState` (unchanged).
- Reuse `hasSlotContent`, `inheritAriaAttributes`, and `UrlSanitizer` (`src/utils/dom/sanitizer/url`).

**Integration research pass:**
- [ ] `renderFieldFooter` shows `current/max`. The editor passes its own count; the shared function is unchanged.
- [ ] `bds-popover` outside-click: read `bdsClickOut` before wiring, so a click inside the nested `bds-dropdown` or the link form does not close it.
- [ ] `bds-button` re-emits `bdsClick` and stops the native `click` (team memory). Listen to `bdsClick`.
- [ ] `bds-dropdown` `bdsChange` carries the option value. Use the field token as the value.

**Acceptance criteria:**

- **Render order:**
  1. Label.
  2. Toolbar, containing the built-in tools in `toolbar` order inside `bds-button-group`, a vertical `bds-divider` for each `|` and before the slot, and `<slot name="toolbar">`.
  3. The editable.
  4. `renderFieldFooter` with the T3 count.
- **Toolbar parsing:**
  - Split on `,` and trim.
  - `emoji` is a valid id that renders nothing in v1, with no warning.
  - Unknown ids are ignored with a development warning.
  - `fields` is dropped when `fields` is empty.
- **Toolbar visibility:** not rendered when it has no tools and no slot content, and never when `readOnly`.
- **Variant:** `bds-toolbar` gets `border="all"` for `outline` and `border="bottom"` for `plain`, with `gap="sm"` and `density="comfortable"` in both. The host gets a `--outline` or `--plain` class.
- **Readonly:** no border and no toolbar; chips render. **Disabled:** tools are disabled.
- Host classes `--disabled`, `--readonly`, `--error` and `--focused` follow the `bds-text-field` naming.
- **Shared `insert()`:** uses the preserved `state.selection`, checks the space left, dispatches, then calls `view.focus()`. A non-fitting insert returns `false`.
- **Fields tool:** a `bds-dropdown` labelled "Insert field" listing each field's `label`. Options that don't fit are disabled. Choosing one inserts the chip.
- **Link tool:**
  - A `bds-button` labelled "Insert link" opens a `bds-popover` with a URL `bds-text-field` and an "Insert" `bds-button`.
  - The URL is sanitised. `about:blank` shows "Enter a valid URL".
  - A URL longer than the space left shows "This link is longer than the space left."
  - The Insert button is disabled while the URL field is empty (decided 2026-11-17); errors show only for a non-empty URL and clear when the user edits it.
  - On success, the URL is inserted as text and the popover closes.
  - `Esc` closes the popover and restores the cursor.
- **Methods:**
  - `insertText(text)` inserts plain text.
  - `insertField(token)` returns `false` for an unknown token, with a development warning.
  - Both return `false` when disabled or readonly.
- **Core accessibility:**
  - The editable has `role="textbox"`, `aria-multiline="true"`, `aria-labelledby` (label id), `aria-describedby` (helper and counter ids), and `aria-required`, `aria-invalid`, `aria-readonly`, `aria-disabled` and `aria-placeholder`.
  - Clicking the label focuses the editable.
  - The toolbar has the accessible name "Text editor tools".
  - Tab order is toolbar first, then the editable. `Tab` leaves the editable.
- **Copy:** every visible and screen-reader string above (button labels, toolbar name, the URL field label, the Insert button, both link errors, the chip prefix) comes from `mergedLabels`. No English literal in the render code (ADR 0014).
- JSDoc gate applies to `insertText` and `insertField`.

**Manual test _(required — not waveable)_:**

Playground scenarios:
- Scenario 1: `toolbar="fields,link"`, three fields (`{{1}}` Name length 20, `[URL_Identify_Senders]` Identify senders, `DF-Email` Email), `counter`, `charCount=60`.
- Scenario 2: `toolbar=""` with a slotted "Templates" `bds-button` that calls `insertText('Hi ')`.
- Scenario 3: `readonly` with a value containing a token.
- Scenario 4: `disabled`.

Run `pnpm dev:components`:
- [ ] Given scenario 1 with the cursor mid-text, when Name is chosen, then a chip is inserted there, the counter rises by 20 and focus returns. Pass: all three.
- [ ] Given scenario 1 with 5 characters left, then Name is disabled and Email is enabled. Pass: per-option disabling.
- [ ] Given scenario 1, when `javascript:alert(1)` is inserted as a link, then "Enter a valid URL" shows. A valid URL is inserted as text. Pass: both.
- [ ] Given scenario 2, when Templates is clicked, then "Hi " is inserted at the cursor. Pass: inserted.
- [ ] Given scenario 3, then there is no border and no toolbar, and the chip shows its label. Given scenario 4, the tools are disabled and `Tab` skips the editor. Pass: matches Figma.
- [ ] Given DevTools' Accessibility pane, then the editable is a multiline textbox named by the label and described by the helper and counter. Pass: shown.
- [ ] Given scenario 1 with `labels = { insertField: 'Insertar campo', invalidUrl: 'Introduce una URL válida' }` set by script, then those two strings show in Spanish and every other string stays English. Pass: partial override works.

**Commit:** `feat(web-components): EOA-18739 render bds-text-editor with fields and link tools`

### Task 7: SCSS

**Status:** pending
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-text-editor.scss` (create)

**Utility discovery:** read `forms/_shared/_form-field-shell.scss` and `_form-field-elements.scss` first, and reuse their mixins for border, hover, focus, error and disabled. Write editor-local rules only for the toolbar row, the editable and the chip.

**Figma research pass (complete before writing any SCSS):** pull each row from the `14-34766` variants recorded in T1. A row is done only when it was actually pulled.

- [ ] Plain variant — container, toolbar (bottom border only) and every state, using the `3332:85162` to `3332:85467` nodes
- [ ] Container — Default, Hover, Focus, Active
- [ ] Container — Disabled
- [ ] Container — Readonly
- [ ] Error = true — Default; Hover and Focus pulled separately
- [ ] Error + Focus
- [ ] Populated + Default, Populated + Focus
- [ ] Toolbar — height, padding, bottom border, top radii, gaps
- [ ] Content — padding, typography, placeholder colour, min height, overflow
- [ ] Footer — spacing (owned by `renderFieldFooter`; verify only)
- [ ] Field chip — default, in Disabled, in Readonly *(design validated 2026-11-17, Part 6 of the design artifact; base on `bds-tag` gray tokens)*
- [ ] Dimensions — 448 × 152 and toolbar 41 *(unconfirmed, re-pull)*

**Acceptance criteria:**

- Every row is checked off with its value recorded before the first SCSS line is written.
- `var(--boreal-*)` only; no `@use` of the token package.
- Every state × modifier has a rule or a "no difference" note. Modifier blocks override every pseudo-class their base declares.
- Focus uses `:focus-within` on the container. Disabled suppresses the outline.
- **Editable reset:** `white-space: pre-wrap`, `word-wrap: break-word`, `outline: none` on the editable, `p { margin: 0 }`, and font and colour from tokens. Host-page CSS must not reach it.
- `customWidth` uses the `bds-text-field` mechanism.
- Host styles use the element selector plus the T6 host classes.
- The field chip wraps with the surrounding text and is never truncated (no `text-overflow`, no `max-width` clipping).
- `plain` removes the container border and keeps only the toolbar's bottom border; every state and modifier is covered for both variants.
- Checked against the **compiled** CSS.

**Manual test _(required — not waveable)_:**

Playground: T6's scenarios plus an error scenario.

- [ ] Given each state next to its Figma frame (default theme), then border, background, radius, spacing and typography match. Pass: no visible difference at 100%.
- [ ] Given `variant="plain"` next to its Figma frames for Default, Focus, Error and Disabled, then it matches. Pass: no visible difference at 100%.
- [ ] Given a page with global `p { margin: 2em; color: red }`, then the editor text is unaffected. Pass: reset holds.

**Commit:** `style(web-components): EOA-18739 style bds-text-editor`

### Task 8: Component unit tests

**Status:** pending
**Executor:** @testing-subagent
**Files:** `__test__/bds-text-editor.basics.spec.ts`, `.form.spec.ts`, `.validation.spec.ts`, `.events.spec.ts`, `.toolbar.spec.ts`, `.a11y.spec.ts` (create)

**Unit tests to cover:**

- **`basics`:** defaults (`variant` is `outline`); an invalid `variant` falls back with a warning; the host class and the toolbar `border` for each variant; rendering order; `toolbar` parsing (order, divider, `emoji` renders nothing, unknown ids warn, Fields hidden when empty); toolbar hidden with no tools or slot content and when readonly; state classes.
- **`form`:** form value on change; reset → `defaultValue`; `formDisabledCallback`; `null` value treated as `''`.
- **`validation`:** `valueMissing` (a chip alone is content); `tooLong` after an app-set value; custom validators; message precedence; blur validation only on leaving the host.
- **`events`:** `bdsInput` and `valueChange` on edit; `bdsChange` only on leaving with a change; focus events ignore internal moves; no events for app-set values.
- **`toolbar`:** Fields option disabling; insertion position; link sanitising and the too-long path; `insertText` and `insertField` return values (fit, no fit, unknown token, disabled, readonly).
- **`a11y`:** textbox attributes and ids; label click focuses; toolbar name.
- **`labels`** (in `basics` or its own `labels` spec): defaults when unset; a partial override changes only its keys; a reactive change re-renders the toolbar text and the chip prefix.
- Use the T2 decision (real view or mocked adapter). Assert on rendered DOM.
- Coverage-phase only (≥ 80%). Mutation testing is in the v2 plan.

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-18739 cover bds-text-editor`

### Task 9: Vue v-model, Storybook story and basic MDX

**Status:** pending
**Executor:** @release-subagent (Vue mapping), @documentation-subagent (story and MDX)
**Files:** `targets/vue-output-target.ts` (modify); `apps/boreal-docs/src/stories/forms/bds-text-editor/bds-text-editor.stories.ts`, `.mdx` (create)

**Integration research pass:**
- [ ] Read the current `componentModels` (EOA-20193 moved `bds-toggle` to its own entry). Add `bds-text-editor` to the `valueChange` → `value` entry only.

**Acceptance criteria:**

- **Vue:** `bds-text-editor` is in the `value` model. `pnpm validate:pack:vue` passes.
- **Story:** load `documentation-knowledge` and scaffold with plop under `forms`. The story has a Default with controls, plus static examples for Readonly, Disabled, Error, With fields, Custom slot tool, and Counter and limit.
- **MDX:**
  - Usage (the Notion Minimal and Custom toolbar guidance, Do and Don't)
  - `fields` and the `toolbar` slot with `insertText` and `insertField`, as a `<script>` example (team memory `storybook-js-property-bindings-invisible-in-source-panel`)
  - `labels`: the key list with English defaults, and a partial Spanish override as a `<script>` example
  - value format
  - counter rules
  - a Vue `v-model` snippet
- Use ternaries with `nothing` in Lit templates. No version labels in consumer text.

**Manual test _(required — not waveable)_:**
- [ ] `pnpm dev:pack:vue`: given `v-model` on `BdsTextEditor`, when typing and when setting the model, then both directions update. Pass: two-way.
- [ ] `pnpm dev:docs` (restart after component changes): given the story and MDX, then they render without console errors and the controls work. Pass: clean.

**Commit:** `feat(vue): EOA-18739 map bds-text-editor v-model` and `docs(docs): EOA-18739 add bds-text-editor story and docs` (two commits)

### Task 10: Review readiness — smoke QA and draft PR

**Status:** pending
**Executor:** @qa-subagent (smoke QA), main thread (PR)
**Files:** `.claude/pr-description.md` is reserved for EOA-20193. Write this PR's description with the `create-pr` skill into a separate file the user names.

**Acceptance criteria:**

- **Smoke QA in Chromium** on the raw component: T5 scenarios 1 to 3 and T6 scenario 1, including a real `<form>` submit with `checkValidity()`, and `:focus-visible` checks with real `Tab` presses (team memory `playwright-programmatic-focus-not-focus-visible`).
- Any defect is logged as a new task in this plan.
- **Gates:** lint 0 errors, tests green, coverage ≥ 80% for the new files, `pnpm build`, `pnpm validate:all`.
- **Draft PR:** with the user's confirmation, push and open a draft PR against `chore/EOA-20193_dependency-upgrades-followup_DG`. The description lists what v1 contains and what moves to v2.

**Manual test _(required — not waveable)_:**
- [ ] Given the smoke scenarios, then each passes. Pass: no defect, or every defect is logged.
- [ ] Given the PR page, then it targets the EOA-20193 branch and lists only EOA-18739 commits. Pass: correct base.

**Commit:** none.

### Task 11: Rebase onto `release/current` after EOA-20193 merges (outside the time box)

**Status:** pending (blocked until EOA-20193 squash-merges, after its T24 cut-off sync)
**Executor:** main thread (no executor)
**Files:** none expected

**Acceptance criteria:**

- Run `git rebase --onto release/current <EOA-20193 tip at merge> feature/EOA-18739_text-editor-v1_DG`. The tip was `4774509f` on 2026-11-13.
- `pnpm install --frozen-lockfile`, then build, lint, tests and `pnpm validate:all` pass.
- Retarget the PR to `release/current`. Push with `--force-with-lease` only after the user confirms.

**Manual test _(required — not waveable)_:** Pass: `git log release/current..HEAD` lists only EOA-18739 commits, and the gates are green.

**Commit:** none.
