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

**Design:** [`ai-work/sessions/2026-11-13-bds-text-editor-design.md`](../sessions/2026-11-13-bds-text-editor-design.md) · Research: [`ai-work/research/2026-11-13-bds-text-editor-engine-spike.md`](../research/2026-11-13-bds-text-editor-engine-spike.md) · Next version: [`EOA-21589-bds-text-editor-v2.md`](./EOA-21589-bds-text-editor-v2.md)

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
| T2 Add dependencies and mock-doc check — EOA-21464 (02) | done |
| T3 Editor core modules (types, schema, serializer, counter, plugins, chip view) — EOA-21465 (03) | done |
| T4 Core module unit tests — EOA-21466 (04) | done |
| T5 Component logic: scaffold, value flow, form association — EOA-21467 (05) | done |
| T6 Component render, Fields and Link tools, methods, core accessibility — EOA-21468 (06) | done (`d8aa8bca`) |
| T6a Let `bds-button-group` accept `bds-dropdown` (shared component, own commit before T6) | done (`00322d22`) |
| T7 SCSS — EOA-21469 (07) | done (`14e14297`) |
| T8 Component unit tests — EOA-21470 (08) | done (`407e1696`; fix `f3e4bce5`) |
| T9 Vue v-model, Storybook story and basic MDX — EOA-21471 (09) | done (`ecb46d1c` Vue, `e74d66ca` JSDoc, `248a453f` docs) |
| T10 Review readiness: smoke QA and draft PR — EOA-21472 (10); Definition of Done check — EOA-21474 (11) | done (PR 218 against the EOA-20193 branch; everything pushed, tip `4b0a6064`) |
| T11 Rebase onto `release/current` after EOA-20193 merges (outside the time box). Also: re-sync EOA-20193 with `release/current` first (`bds-button` loading style and `bds-dropdown` padding changes may need spec updates), then check on Chromium, WebKit and Firefox that the standard focus ring on Fields menu items is not clipped (4px padding, 3px ring; also with a scrolling list) | pending |
| T12 Localizable validation messages across form components (follow-up, needs its own ADR) | deferred |
| T13 Fields button display option (`fieldsButton` prop, `labels.fields`) | done (`d8aa8bca`) |
| T14 `bds-button` accessible-name and empty-text fixes (follow-up) | deferred |
| T15 Link popover arrow display (review and fix; follow-up) | deferred |
| T16 Tidy `bds-text-editor.scss` (nesting, `$prefix`, shared mixins), after T8 | done (`75809d54`) |
| T17 Focus on `reportValidity()` and blocked submit (follow-up, shared `useFormField`) | deferred |
| T18 Dropdown menu keys leak to ancestor roving handlers; vertical group conflict (pre-existing, follow-up) | deferred |
| T19 `bds-button-group` ignores children added after load (follow-up) | deferred |
| T20 `bds-toolbar` Tab-stop model: every tool, then one stop after the first arrow key (follow-up) | deferred |

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

**Status:** done (commit `da503440` on 2026-11-18; **mock-doc decision: specs use the real `EditorView`, no fake adapter**; `pnpm install --frozen-lockfile`, `pnpm peers check`, `pnpm build`, `pnpm test` (378 suites, 4967 tests) and `pnpm validate:all` pass; the lockfile is in the commit)
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

**Status:** done (commit `d01a46d0`; reviewed 2026-11-18: eslint 0 problems, `tsc --noEmit` clean, `pnpm build` clean, no inline comments, no JSDoc in type files, no `any`; 13 files under `bds-text-editor/`; `bds-text-editor` variant and validation timing reuse the shared `forms/common` constants)
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
  - Variant: reuse the shared `FIELD_VARIANTS` / `FieldVariant` from `forms/common` and re-export it in `enum.ts` as `TEXT_EDITOR_VARIANTS`, exactly as `bds-text-field` re-exports `TEXT_FIELD_VARIANTS`. No new const object.
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

**Status:** done (commits `a4522997` tests, `384e0571` paste fix)
**Executor:** @testing-subagent
**Files:** `__test__/bds-text-editor.serializer.spec.ts`, `.counter.spec.ts`, `.plugins.spec.ts` (create)

**Unit tests to cover:**

- Dev warnings go through `Logger`, which prints `[BorealDS TextEditor]: <message>` (with a colon) and is not gated to development builds. Assert on that exact prefix.
- **`serializer`** (table-driven): round trips; `{{1}}` vs `{{10}}`; regex metacharacter tokens (`[URL_Identify_Senders]`); unknown tokens; `\r\n`; empty and whitespace input; consecutive empty lines; duplicate-token warning.
- **`counter`:** ASCII, accented characters, skin tones, ZWJ families and flags each counted as 1; fields with and without `length`; paragraph breaks; `graphemeSlice` never splits a grapheme.
- **`plugins`** (`EditorState.apply`, no DOM): limit reject, accept `external`, accept deletion, `max = 0`; paste truncation and pasted tokens becoming chips; placeholder only when empty; undo and redo.
- Coverage-phase only (≥ 80%). Mutation testing is in the v2 plan.
- Result: 231 tests pass; lines 100% on every helper, branches 87.5–100%.
- Ruling: a pasted line that is cut entirely drops its leading paragraph break (`'a\nb\nc'` with max 4 gives `'a\nb'`); empty lines inside the pasted text are kept. Fixed in `plain-paste.ts` with two tests.

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-18739 cover text editor core modules`

### Task 5: Component logic — scaffold, value flow, form association

**Status:** done (QA 6/6 pass in Chromium; real OS/mobile IME, WebKit and Firefox not verified)
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx`, `helpers/editor-adapter.ts` (create)

**Utility discovery:**
- Pattern: `bds-text-field.tsx` (`extends Mixin(formAssociatedMixin)`, `useFormField<string>(this)`, `formAssociated: true`, light DOM).
- Reuse: `runValidators`, `deriveFieldRenderState`, `createId`.
- Team memory `face-composite-child-value-sync-on-non-string-branch`: every commit path syncs the form value.

**Integration research pass:**
- [x] `useFormField` and `formAssociatedMixin` are shared. Use them unchanged; log a task if a gap appears.
- [x] Boundary: `value` set to `null` or `undefined` is treated as `''`; a non-array `fields` is treated as `[]` with a development warning.
- [x] Default/empty: an empty editor serialises to `''`.
- [x] Reactivity: `value`, `fields`, `disabled`, `readOnly`, `charCount` and `labels` are reactive after mount.
- [x] Boundary: `labels` set to `undefined` or `{}` gives the English defaults.

**Acceptance criteria:**

- **Props:**
  - Form: `name`, `value` (mutable, not reflected), `defaultValue`, `required`, `disabled`, `readOnly` (`attribute: 'readonly'`), `error`, `errorMessage`, `customValidators`, `validationTiming = 'blur'`.
  - Field parts: `label`, `info`, `helperText`, `placeholder`, `counter`, `charCount`, `customWidth`.
  - Editor: `toolbar = 'emoji,link'`, `fields = []`, `labels?: TextEditorLabels` (JS property), `variant: TextEditorVariant = 'outline'` (the shared `FieldVariant`; `validatePropValue` in `componentWillLoad` and a `@Watch('variant')`, as in `bds-text-field`).
- **Labels:**
  - A private `mergedLabels` getter returns `{ ...DEFAULT_TEXT_EDITOR_LABELS, ...this.labels }`, the same pattern as `bds-date-picker`.
  - `labels` is reactive: a change re-renders, and the field node views redraw so chip prefixes update.
  - A partial object overrides only the keys it contains.
- **Events:** `valueChange`, `bdsInput`, `bdsChange`, `bdsFocus`, `bdsBlur`, `bdsValidationChange`.
- **Methods:** `setFocus`, `checkValidity`, `reportValidity`. `insertText` and `insertField` are declared here and implemented in T6.
- JSDoc gate applies.
- **Adapter:** `editor-adapter.ts` alone creates and destroys `EditorView`. Specs use the real view (T2 decision, 2026-11-18). `newSpecPage` has no `document.getSelection`, so specs install a `getSelection` stub from a shared helper in `src/utils/testing/mocks/` before the view is created.
- **Plugin options are static:** when `charCount` or `fields` change, call `view.updateState(view.state.reconfigure({ plugins: createTextEditorPlugins(...) }))`. Undo history survives because `history()` keeps its plugin key. On a `labels` change call the chip controller's `refresh()` (`createFieldViewController(() => mergedLabels.fieldPrefix)`).
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
- [x] Given scenario 3 (`charCount=20`), when typing and composing text (including an IME or mobile keyboard) at the limit, then the editor stays in sync with the document (the limit plugin can leave native DOM input momentarily out of sync). Pass: no stuck or duplicated text.
- [x] Given scenario 2 with a chip, when Backspace is pressed after the chip and when the chip is selected, then the whole chip is removed. Pass: both.
- [x] Given scenario 1 empty, when submitted, then it is blocked. After typing, `FormData` holds the text. Pass: both.
- [x] Given scenario 2, when the value is set, then a chip renders and `value` reads `Hello {{1}}`. Pass: round trip.
- [x] Given scenario 3, when the long value is set, then `checkValidity()` is `false`. Pass: `tooLong`.
- [x] Given scenario 1, when the form is reset, then the editor shows `defaultValue`. Pass: reset.

**Commit:** `feat(web-components): EOA-18739 add bds-text-editor value flow and form association`

**Findings logged after T5 (2026-11-19):**
- T6: adapter passes ARIA attributes (`role="textbox"`, label wiring via `view.setProps({ attributes })`); label `htmlFor` targets the editable so label click focuses it. Done in T6.
- T7: keep or replace the `.ProseMirror { white-space: pre-wrap; word-wrap: break-word }` rule in `bds-text-editor.scss`.
- T8: tests for a nullish `fields`, the `formDisabledCallback` path, validator messages with and without `errorMessage`, and an Enter `keydown` on `.ProseMirror` as the typing driver. `ElementInternals.checkValidity` is constant `true` in the shared mock, so assert on `setValidity` calls.

### Task 6: Component render, Fields and Link tools, methods, core accessibility

**Status:** done (`d8aa8bca`; QA pass in Chromium, reduced WebKit pass; real IME, Firefox and Figma conformance not verified)
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx` (modify)

**Utility discovery:**
- Reuse `renderFieldLabel`, `renderFieldFooter` and `deriveFieldRenderState` (unchanged).
- Reuse `hasSlotContent`, `inheritAriaAttributes`, and `UrlSanitizer` (`src/utils/dom/sanitizer/url`).

**Integration research pass:**
- [x] `renderFieldFooter` shows `current/max`. The editor passes its own count; the shared function is unchanged.
- [x] Slot timing: read `.agents/memory/stencil-non-shadow-slot-relocation-timing.md` and use its pattern for the toolbar slot check.
- [x] `bds-text-field` (URL field): open PR 216 (EOA-20929, due to merge by EOW) rewrites its validation timing, reset and `error`/`errorMessage` handling. `error` becomes visual-only and `errorMessage` renders only while `error` is true. Wire the link errors as `error` plus `errorMessage` and re-check against the merged version.
- [x] `bds-popover` outside-click: read `bdsClickOut` before wiring, so a click inside the nested `bds-dropdown` or the link form does not close it.
- [x] `bds-button` re-emits `bdsClick` and stops the native `click` (team memory). Listen to `bdsClick`.
- [x] `bds-dropdown` `bdsChange` carries the option value. Use the field token as the value.

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
  - A tool counts only if it renders something. In v1 `toolbar="emoji"` alone is "no tools", so with no slot content the toolbar is hidden.
  - The default `'emoji,link'` shows only Link in v1.
  - **Dividers:** rendered only between two visible groups, never first, last or doubled. `toolbar=""` plus slot content gives no divider; `"fields,|"` gives no trailing divider; consecutive `|` collapse to one.
  - **Slot detection:** the slot is non-shadow, so check `hasSlotContent` in `componentWillLoad`. Content that arrives after mount is caught by a post-mount check against the settled toolbar wrapper, with the state write deferred to a microtask (team memory `stencil-non-shadow-slot-relocation-timing`).
  - `readOnly` hides slotted app tools too.
- **Variant:** `bds-toolbar` gets `border="all"` for `outline` and `border="bottom"` for `plain`, with `gap="sm"` and `density="comfortable"` in both. The host gets a `--plain` class when `variant` is `plain` and no class for `outline`, the same as `bds-text-field`.
- **Readonly:** no border and no toolbar; chips render. **Disabled:** tools are disabled.
- Host classes `--disabled`, `--readonly`, `--error` and `--focused` follow the `bds-text-field` naming.
- **Shared `insert()`:** uses the preserved `state.selection`, checks the space left, dispatches, then calls `view.focus()`. A non-fitting insert returns `false`.
- **Fields tool:** a `bds-dropdown` labelled "Insert field" listing each field's `label`. Options that don't fit are disabled. Choosing one inserts the chip.
- **Link tool:**
  - A `bds-button` labelled "Insert link" opens a `bds-popover` with a URL `bds-text-field` and an "Insert" `bds-button`.
  - The URL is sanitised. `about:blank` shows "Enter a valid URL".
  - A URL longer than the space left shows "This link is longer than the space left."
  - The URL field's inner `<input>` sits in light DOM inside the host `<form>`. It has no `name`, so it never reaches `FormData`, and `Enter` in it calls `preventDefault()` so it inserts the link and never submits the enclosing form.
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
- [x] Given scenario 1 with the cursor mid-text, when Name is chosen, then a chip is inserted there, the counter rises by 20 and focus returns. Pass: all three.
- [x] Given scenario 1 with 5 characters left, then Name is disabled and Email is enabled. Pass: per-option disabling.
- [x] Given scenario 1, when `javascript:alert(1)` is inserted as a link, then "Enter a valid URL" shows. A valid URL is inserted as text. Pass: both.
- [x] Given scenario 2, when Templates is clicked, then "Hi " is inserted at the cursor. Pass: inserted.
- [x] Given scenario 3, then there is no border and no toolbar, and the chip shows its label. Given scenario 4, the tools are disabled and `Tab` skips the editor. Pass: matches Figma.
- [x] Given DevTools' Accessibility pane, then the editable is a multiline textbox named by the label and described by the helper and counter. Pass: shown.
- [x] Given scenario 1 with `labels = { insertField: 'Insertar campo', invalidUrl: 'Introduce una URL válida' }` set by script, then those two strings show in Spanish and every other string stays English. Pass: partial override works.

**Commit:** `feat(web-components): EOA-18739 render bds-text-editor with fields and link tools`

**Findings after QA (2026-11-19), all fixed in the T6 commit unless noted:**
- Spurious `bdsBlur`, `bdsChange` and `bdsFocus` when a field is inserted or the link popover closes: fixed with a deferred `document.activeElement` recheck when `focusout.relatedTarget` is null. Blur events can arrive one frame late; T8 specs must flush animation frames.
- Label click focused the editable without `bdsFocus`: fixed, it emits one.
- The link popover's Insert button had no accessible name: fixed with its label. The 2 remaining `bds-button` warnings come from playground-only slotted buttons (T14).
- Caret bug reported by the user: with a chip last in the line, ProseMirror adds `img.ProseMirror-separator` hack nodes. The global reset `img { display: block }` made them blocks, so the editor was 48px tall and the caret was on an empty second line or not drawn. Fix: `img.ProseMirror-separator { display: inline; border: none; margin: 0 }` in `bds-text-editor.scss`. Verified in Chromium and WebKit; Firefox not verified.
  - T7: also style `.ProseMirror-selectednode` (selected chip) and `.ProseMirror-hideselection`; re-check caret and editor height with the same cases once the chip is styled.
  - T8: after `insertField` the selection is collapsed right after the chip; value is exactly `{{1}}` with one paragraph; the editor can render `img.ProseMirror-separator` and `.ProseMirror-trailingBreak`.
- Link popover arrow hidden (`hideArrow`), review deferred to T15.

**Rulings logged 2026-11-19:**
- A schemeless URL such as `foo` passes the sanitizer and is inserted. Accepted for v1.
- Dropdown `bdsChange` detail is an object for a non-selectable dropdown; the handler accepts either.
- T8: flush animation frames in specs (focus returns after two frames); test the "link longer than the space left" error.
- Late removal of slotted toolbar content is not detected (observer watches direct children only). Accepted limitation; mention in the PR. **Superseded 2026-11-20:** fixed in `a9194ada` (reported in code review by Laura Cuellar on the "Late slot" playground editor). The observer also watches the `.bds-text-editor__tools` wrapper; the PR no longer lists this as a limitation.
- The toolbar and each group share the accessible name `labels.toolbar`. Accepted for v1.

### Task 6a: `bds-button-group` accepts `bds-dropdown`

**Status:** done (`00322d22`, 7 specs added, 56 pass)
**Executor:** @frontend-subagent, @testing-subagent (specs)
**Files:** `bds-button-group` component, SCSS and spec (modify)

Ruling 2026-11-19 (option A): the Fields `bds-dropdown` stays inside the group. The group stops warning for `bds-dropdown` children and its joined styling reaches the dropdown trigger. Existing stories and specs must not regress.

**Commit:** `feat(web-components): EOA-18739 allow bds-dropdown inside bds-button-group`

### Task 7: SCSS

**Status:** done (`14e14297`; QA pass in Chromium, WebKit and Firefox after two fixes; Safari.app not run)
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-text-editor.scss` (create)

**Utility discovery:** read `forms/_shared/_form-field-shell.scss` and `_form-field-elements.scss` first, and reuse their mixins for border, hover, focus, error and disabled. Write editor-local rules only for the toolbar row, the editable and the chip.

**Figma research pass (complete before writing any SCSS):** pull each row from the `14-34766` variants recorded in T1. A row is done only when it was actually pulled.

- [x] Plain variant — container, toolbar (bottom border only) and every state, using the `3332:85162` to `3332:85467` nodes
- [x] Container — Default, Hover, Focus, Active
- [x] Container — Disabled
- [x] Container — Readonly
- [x] Error = true — Default; Hover and Focus pulled separately
- [x] Error + Focus
- [x] Populated + Default, Populated + Focus
- [x] Toolbar — height, padding, bottom border, top radii, gaps
- [x] Content — padding, typography, placeholder colour, min height, overflow *(padding, typography, placeholder and caret pulled; min height and overflow are not designed, open question 6)*
- [x] Footer — spacing (owned by `renderFieldFooter`; verify only)
- [x] Field chip — default, in Disabled, in Readonly *(design validated 2026-11-17, Part 6 of the design artifact; base on `bds-tag` gray tokens)*
- [x] Dimensions — 448 × 152 and toolbar 41 *(unconfirmed, re-pull)*

**Research results (2026-11-19):** full table with node ids, token names and the CSS variable map in [`ai-work/research/2026-11-19-bds-text-editor-figma-variants.md`](../research/2026-11-19-bds-text-editor-figma-variants.md). Changes to the plan:
- Disabled and Readonly with Error (192 tall) are skeleton placeholders, not designs; 192 = 16 + 4 + 152 + 4 + 16. The editor ignores `error` in those two states (pending confirmation).
- Plain is specified for only 3 of 24 states (Default empty, Default populated, Disabled populated); every other Plain node is a copy of its Outline node.
- Toolbar: `border-bottom` only in both variants (the container border shows around it); height 41 = 32 + 2 × 4 + 1; horizontal padding 12. This replaces the earlier `border="all"` and `density="comfortable"` mapping for `bds-toolbar`, which would add a second line and give 57.
- Hover uses `Box shadow/s` (`$boreal-depth-box-shadow-s`); the shared `bds-hover-shadow` mixin is the smaller `-xs` and must not be used. Focus and Active shadows already exist in the shared tokens.
- The shared shell lacks: hover shadow, active shadow, the toolbar row, the editable box (padding 6 / 12, `$boreal-ui-inverse`, `body/sm`, caret colour), disabled toolbar and editable backgrounds, readonly editable padding, and the footer gap. Container overrides needed: `padding: 0`, a new `min-height`, `align-items: stretch`, `flex-direction: column`.
- Focus ring: the shadows sit on the whole bordered container including the toolbar; toolbar buttons have no designed focus or active styling (`bds-button` owns it).

**Rulings on the research questions (user, 2026-11-19, following the recommendations):**
1. Plain Hover, Focus, Active and Error keep the Default Plain look (no border at rest) plus the ring or error border; the three real Plain frames are the reference. Raise the inconsistent Outline-copy Plain frames with design.
2. `error` is ignored visually in Disabled and Readonly.
3. The counter is danger-coloured with an error whether the editor is empty or populated, like `bds-text-field`; flag the Figma inconsistency to design.
4. Focus keeps the grey border under the ring, as the frames do.
5. The placeholder stays visible until the user types; the frames' caret-for-placeholder swap is not implemented.
6. The editable has a minimum height of 71 (its height inside the 152 frame) and grows with its content up to a `max-height`, then scrolls; the `max-height` value needs design sign-off.
7. The disabled divider uses `ui (components)/default-light`, as in Figma.
8. Disabled empty shows the normal placeholder in the disabled colour, not "-".
9. The Active shadow applies on press inside the editable only, not on toolbar presses.

**Acceptance criteria:**

- Every row is checked off with its value recorded before the first SCSS line is written.
- `var(--boreal-*)` only; no `@use` of the token package.
- Every state × modifier has a rule or a "no difference" note. Modifier blocks override every pseudo-class their base declares.
- Focus uses `:focus-within` on the container. Disabled suppresses the outline.
- **Focus highlight scope (user, 2026-11-19):** the focus ring (`Box shadow/focus`, and `Box shadow/active` while pressed) is drawn around the whole bordered container, toolbar included, as in the Figma Focus and Active frames. The browser outline on `.ProseMirror` is removed. Settle with design whether the ring stays while focus is on a toolbar tool and while the link popover is open; the popover sits outside the container, so `:focus-within` alone would drop the ring there while the host `--focused` class stays on. **Superseded 2026-11-20 (code review):** the container ring shows only while focus is in the editable (host `--editing` class); on a toolbar tool, in the Fields menu or the link form only that element's own ring shows, so two focus indicators never show at once.
- **Editable reset:** `white-space: pre-wrap`, `word-wrap: break-word`, `outline: none` on the editable, `p { margin: 0 }`, and font and colour from tokens. Host-page CSS must not reach it.
- `customWidth` uses the `bds-text-field` mechanism.
- Host styles use the element selector plus the T6 host classes.
- The field chip wraps with the surrounding text and is never truncated (no `text-overflow`, no `max-width` clipping).
- Reuse the shared `forms/_shared/_form-field-shell.scss` `--plain` rule (transparent container border, focus border from `$boreal-stroke-focus`) and verify it against the Plain Figma frames; add only what the toolbar's bottom border needs.
- `plain` removes the container border and keeps only the toolbar's bottom border; every state and modifier is covered for both variants.
- Checked against the **compiled** CSS.

**Manual test _(required — not waveable)_:**

Playground: T6's scenarios plus an error scenario.

- [x] Given each state next to its Figma frame (default theme), then border, background, radius, spacing and typography match. Pass: no visible difference at 100%.
- [x] Given `variant="plain"` next to its Figma frames for Default, Focus, Error and Disabled, then it matches. Pass: no visible difference at 100%.
- [x] Given a page with global `p { margin: 2em; color: red }`, then the editor text is unaffected. Pass: reset holds.
- [x] Given focus on the editable, on a toolbar tool and with the link popover open, then the focus ring wraps the whole container as in Figma and no separate outline shows on the editable. Pass: matches the Focus frame in both variants and in the Error state. (Superseded 2026-11-20: the ring now shows only while focus is in the editable; see the T7 decision.)
- [x] Given an empty editor in each variant, when it is clicked or reached with Tab, then a blinking caret is visible clear of the border (content padding x `spatial/padding/s`, y `spatial/padding/1xs`, from T1). Pass: caret visible. Re-check with the styled chip: after inserting a field at the end of a line, the editor is one line tall and the caret sits after the chip. Reported 2026-11-19: with no padding the caret is not visible on an empty editor.

**Commit:** `style(web-components): EOA-18739 style bds-text-editor`

**Implementation results (2026-11-19):**
- Editable min-height is 69, not 71: the container border is 1px per side in CSS and drawn inside the frame in Figma, so 69 gives the 152 host. Toolbar vertical padding is 3px because the repo's `bds-button` is 34px against Figma's 32; the toolbar is 41.
- Max-height is 10 lines (a token expression, about 212px) and needs design sign-off.
- Toolbar uses `border="bottom"`, `bds-button-group` uses `variant="plain"` and no `size`; new `showError` getter implements ruling 2.
- QA found two browser defects, both fixed: WebKit could not type into an empty editor with a placeholder (`position: absolute` on the placeholder widget; now an inline span) and Firefox never matches `:active` on a contenteditable (a `--pressed` class set from pointer events replaces the `:has(:active)` rule).
- Known, left as is: the Chromium caret after a chip at the end of a line sits 4px inside the pill edge; `display: inline-block` would fix it but breaks the chip-wraps-with-text ruling.
- Raise with design: the Plain frames that are Outline copies, the counter colour in Figma (grey when populated with an error), the max-height, and `--boreal-text-default-darker` (`#595d64` in the repo against `#131316` in Figma).
- Follow-ups: `bds-button` plain-default disabled paints a white background (worked around in the editor); `bds-typography` label and helper render `<p>` and pick up global `p` rules; T8 specs for `showError`, the toolbar and group props, and the `--pressed` state.

### Task 8: Component unit tests

**Status:** done (commits `407e1696` specs, `f3e4bce5` fix; 11 suites, 728 tests; coverage: `bds-text-editor.tsx` 100% lines, 94% branches; failure-mode catalog `ai-work/testing/failure-modes/bds-text-editor.md`, FM-TE-01 to 07 confirmed)
**Executor:** @testing-subagent
**Files:** `__test__/bds-text-editor.basics.spec.ts`, `.form.spec.ts`, `.validation.spec.ts`, `.events.spec.ts`, `.toolbar.spec.ts`, `.a11y.spec.ts` (create)

**Unit tests to cover:**

- **`basics`:** defaults (`variant` is `outline`); an invalid `variant` falls back with a warning; the host class and the toolbar `border` for each variant; rendering order; `toolbar` parsing (order, divider, `emoji` renders nothing, unknown ids warn, Fields hidden when empty); toolbar hidden with no tools or slot content and when readonly (including `toolbar="emoji"` alone, and slotted tools hidden when readonly); divider rules (none leading, trailing, doubled, or with `toolbar=""` plus a slot); slot content added after mount makes the toolbar appear; state classes.
- **`form`:** form value on change; reset → `defaultValue`; `formDisabledCallback`; `null` value treated as `''`.
- **`validation`:** `valueMissing` (a chip alone is content); `tooLong` after an app-set value; custom validators; message precedence; blur validation only on leaving the host.
- **`events`:** `bdsInput` and `valueChange` on edit; `bdsChange` only on leaving with a change; focus events ignore internal moves; no events for app-set values.
- **`toolbar`:** Fields option disabling; insertion position; link sanitising and the too-long path; `Enter` in the URL field inserts and does not submit the enclosing form, and the URL field has no `name`; `insertText` and `insertField` return values (fit, no fit, unknown token, disabled, readonly).
- **`a11y`:** textbox attributes and ids; label click focuses; toolbar name.
- **`labels`** (in `basics` or its own `labels` spec): defaults when unset; a partial override changes only its keys; a reactive change re-renders the toolbar text and the chip prefix.
- Use the real `EditorView` (T2 decision) with the shared `getSelection` stub helper in `src/utils/testing/mocks/`, applied before the view is created. Assert on rendered DOM and on state.
- mock-doc has no `MutationObserver`, `InputEvent` or real focus, so specs drive edits through `view.dispatch`, commands and `keydown` events (not simulated typing), and assert focus with a spy on `view.focus`. Geometry APIs (`coordsAtPos`, `posAtCoords`) are not available.
- Coverage-phase only (≥ 80%). Mutation testing is in the v2 plan.

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-18739 cover bds-text-editor`

**Rulings and fixes during T8 (2026-11-19):**
- `syncLinkAnchor` ignores `null` refs (Stencil nulls refs on unmount), so setting `readOnly` or dropping `link` from `toolbar` after mount no longer throws.
- `aria-invalid` is set only while the editor is editable.
- `valueChange` fires on every value change including app-set values; `bdsInput` and `bdsChange` do not.
- `insertText('')` and non-strings return `false`; a repeated toolbar id renders one tool; `null` at mount reads as `''`, but `undefined` at mount keeps the default `emoji,link` (Stencil treats it as unset).
- A link submitted after the editor stops being editable inserts nothing, shows no error and closes the popover; an app-set value between focus and blur fires `bdsChange` on blur.
- `fields` arriving after the value emits no further `valueChange`.

### Task 9: Vue v-model, Storybook story and basic MDX

**Status:** done (`ecb46d1c` Vue mapping, `e74d66ca` toolbar and fieldsButton JSDoc, `248a453f` story and MDX; `validate:pack:vue` passes, `v-model` verified both ways in Chromium; story and MDX verified in Chromium on Storybook)
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
  - counter rules, including the accepted `Intl.Segmenter` fallback (decided 2026-11-18): Firefox below 125 and Safari below 14.1 count ZWJ emoji families and flags as several characters
  - a Vue `v-model` snippet
- **Fields button (T13) and Plain variant, added 2026-11-19:**
  - A `fieldsButton` select control on the Default story, and a static "Fields button modes" example with `icon`, `text` and `icon-text`.
  - MDX: the visible text comes from `labels.fields` (add it to the key list with its English default); the accessible name is "Insert field" in `icon` mode and the visible text in the other two; the text-only look has no Figma design, so do not present it as a design-system look.
  - A static Plain-variant example.
- Use ternaries with `nothing` in Lit templates. No version labels in consumer text.

**Manual test _(required — not waveable)_:**
- [ ] `pnpm dev:pack:vue`: given `v-model` on `BdsTextEditor`, when typing and when setting the model, then both directions update. Pass: two-way.
- [ ] `pnpm dev:docs` (restart after component changes): given the story and MDX, then they render without console errors and the controls work. Pass: clean.

**Commit:** `feat(vue): EOA-18739 map bds-text-editor v-model` and `docs(docs): EOA-18739 add bds-text-editor story and docs` (two commits)

**Additions after review (2026-11-19):**
- Stories use `toolbar="fields,link"`; the `toolbar` JSDoc and the MDX 'Toolbar' section state that ids render in the order written and slotted tools follow the built-in ones. The component default is still `emoji,link`.
- Every preview has a heading and description; the slot story is `ToolbarSlot` (built-in plus slotted tools, and a slot-only toolbar); `InteractiveFormExample` added with a form-demo wrapper.
- The text-only Fields look is not described as unapproved in the docs (decision 2026-11-19); the PR description should still say it has no Figma design.
- Not verified: the Do and Don't cards come from ADRs 0021 to 0023 and the component, not from the Notion guidance (no source found); the MDX is not Prettier-clean (two existing MDX files are not either); the `bds-button` accessible-name warnings seen in the docs are T14.

### Task 10: Review readiness — smoke QA and draft PR

**Status:** done (smoke QA and gates 2026-11-19; PR 218 opened and described by the user; all commits pushed 2026-11-20, tip `4b0a6064`)
**Executor:** @qa-subagent (smoke QA), main thread (PR)
**Files:** `.claude/pr-description.md` is reserved for EOA-20193. Write this PR's description with the `create-pr` skill into a separate file the user names.

**Acceptance criteria:**

- **Smoke QA in Chromium** on the raw component: T5 scenarios 1 to 3 and T6 scenario 1, including a real `<form>` submit with `checkValidity()`, and `:focus-visible` checks with real `Tab` presses (team memory `playwright-programmatic-focus-not-focus-visible`).
- Any defect is logged as a new task in this plan.
- **Gates:** lint 0 errors, tests green, coverage ≥ 80% for the new files, `pnpm build`, `pnpm validate:all`.
- **PR description note:** `pnpm-lock.yaml` was rewritten in pnpm 12.18's compact format by the T2 commit, so its diff is about 14,000 lines. The only content change is 10 new packages (the six `prosemirror-*` packages plus `orderedmap`, `prosemirror-transform`, `rope-sequence`, `w3c-keyname`). State this in the description.
- **Draft PR:** with the user's confirmation, push and open a draft PR against `chore/EOA-20193_dependency-upgrades-followup_DG`. The description lists what v1 contains and what moves to v2.

**Manual test _(required — not waveable)_:**
- [x] Given the smoke scenarios, then each passes. Pass: no defect, or every defect is logged.
- [x] Given the PR page, then it targets the EOA-20193 branch and lists only EOA-18739 commits. Pass: correct base.

**Commit:** none.

**Gate results (2026-11-19, HEAD `248a453f`):** `pnpm lint` 0 errors (50 warnings, none in `bds-text-editor`); `pnpm test` 389 suites and 5,702 tests pass (T2 baseline: 378 and 4,967); `pnpm build` and `pnpm validate:all` pass; coverage per file for `bds-text-editor` and its helpers is at least 80% (T8).

**Smoke QA (2026-11-19):** all 7 scenarios pass in Chromium; the form, limit, link and focus checks also pass in WebKit and Firefox. No component defect. Observations: `reportValidity()` does not move focus (T17); a long `insertText` is rejected whole while paste truncates (by design); Esc on the Fields menu returns focus to the Fields trigger. Not verified: real IME, Safari.app, WebKit and Firefox for the chip and readonly scenarios, React and Vue wrappers.

**PR (2026-11-19):** opened by the user against `chore/EOA-20193_dependency-upgrades-followup_DG` (the dependencies branch) with the description written from the `create-pr` skill, including the "Bundle size and dependencies" section. Checked with git: the remote branch tip is `248a453f` and lists 14 commits above the EOA-20193 base, all EOA-18739. The base on the PR page was confirmed by the user, not read by me.

**Pushed (2026-11-20):** `c29bc3c0` (bundles), `9587e06a` (dropdown inset focus ring, later reverted: see the T10 decisions), `4b0a6064` `docs(docs): EOA-18739 fix the toolbar divider example` (the MDX example is `toolbar="fields,|,link"`) and `32671e8e` `chore(web-components): EOA-18739 TBD add text editor playground for code review` (the rewritten `src/index.html`). The PR now has 18 commits above the EOA-20193 base.

**Before merging:** `32671e8e` adds the playground to `src/index.html` for code review only, `2963084e` updates its toolbar cases and `0fd57139` its focus ring cases. The squash must not carry any of them: revert the file to the base version (the placeholder playground) and drop the three commits, per the `TBD` flag in their messages.

**Pushed (2026-11-20, later):** `4654410d`, `a9194ada`, `2963084e` (fast-forward, `03d75044..2963084e`). The PR now has 21 commits above the EOA-20193 base.

**Decisions made during T10:**
- Wrapper tree-shaking fixes (PURE annotations and `sideEffects`, from the October review) go in their own branch and PR; not logged as a task here.
- The dropdown inset focus ring (`9587e06a`) was reverted on 2026-11-20. `release/current` removed `--bds-list-menu-padding: 0` from `bds-dropdown` (EOA-18734, `49938347`), so menu rows get the default 4px list padding again and the standard 3px outer ring fits inside the list. Until T11 brings that change in, this branch still has full-bleed rows and the outer ring is clipped in the Fields menu. The PR no longer asks design about an item focus state.
- A manual test plan is being drafted at `ai-work/qa/test-plans/EOA-18739-bds-text-editor-test-plan.md` with the playground in `src/index.html` rewritten to match.

**Toolbar fixes after code review (2026-11-20):**
- `4654410d` `fix(web-components): EOA-18739 keep bds-text-editor toolbar order after runtime updates`. Changing `toolbar` after the first render could render items out of order (for example `fields,link` to `link,|,fields` rendered `divider, fields, link`; `fields,|,link` back to `fields,link` rendered `link, fields`; a tool slotted after mount rendered first). Cause: Stencil's light-DOM slot relocation inserts nodes added next to relocated siblings in the wrong place, in `bds-toolbar` and again inside `bds-button-group`, while the patched `children` still reports the intended order. Not fixed by Stencil 4.45.5 (spiked). Fix: the built-in tools, dividers and toolbar slot render inside one `<div class="bds-text-editor__tools">` (`display: contents`), and each group is keyed `group-${index}-${tools}` so a changed group is rebuilt rather than patched or moved. Side effect: a rebuilt group gets its children at creation, so it also avoids the T19 late-child problem inside the editor.
- `a9194ada` `fix(web-components): EOA-18739 hide the bds-text-editor slot divider when slotted tools are removed`. Supersedes the accepted "late removal" limitation in the T6 rulings.
- Specs: `basics.spec` "toolbar order after updates inside bds-toolbar" (registers `BdsToolbar`) and "slotted toolbar tools removed after mount". `bds-button-group` cannot be registered in these specs: Stencil's mock-doc loops forever when it removes a light-DOM slot host nested in another one (reproduced with a stub that renders only `<slot>`), so group-level order is checked in the browser and by group identity in the specs.
- Playground: `#s7-toolbar` step 3 copy updated, a "Late slot with built-in tools" editor added, and step 6 added for runtime order.
- `b99213b5` `fix(web-components): EOA-18739 show the bds-text-editor focus ring only while typing` (code review: two focus indicators at once). New host class `--editing` while focus is in the editable; the container ring, the pressed shadow and the forced-colours outline follow it. `--focused`, `bdsFocus`, `bdsBlur`, `bdsChange` and blur validation are unchanged. Docs in `aad757a8`. Verified in Chromium, Firefox and WebKit: exactly one indicator in every state (editable, tool, Fields menu item, link URL field), the ring returns after Escape or an insertion; the plain variant shows only the ring while typing.
- **PR description:** remove the late-removal limitation and add the three fixes. If the description says anything about the playground's "Late slot" being a known limitation, drop it.

### Task 11: Rebase onto `release/current` after EOA-20193 merges (outside the time box)

**Status:** pending (blocked until EOA-20193 squash-merges, after its T24 cut-off sync)
**Executor:** main thread (no executor)
**Files:** none expected

**Acceptance criteria:**

- Run `git rebase --onto release/current <EOA-20193 tip at merge> feature/EOA-18739_text-editor-v1_DG`. The tip was `4774509f` on 2026-11-13.
- Re-check the link popover against the merged `bds-text-field` from PR 216 (validation timing, reset, `error`/`errorMessage`): the T6 link-error manual checks and the T8 toolbar specs still pass.
- `pnpm install --frozen-lockfile`, then build, lint, tests and `pnpm validate:all` pass.
- Retarget the PR to `release/current`. Push with `--force-with-lease` only after the user confirms.

**Manual test _(required — not waveable)_:** Pass: `git log release/current..HEAD` lists only EOA-18739 commits, and the gates are green.

**Commit:** none.

---

### Task 12: Localizable validation messages across form components

**Status:** deferred
**Executor:** @knowledge-keeper (ADR), then per-component work in its own plan

Found in T5: `valueMissing` and `tooLong` messages in `bds-text-editor` are English literals, like `bds-text-field`, `bds-color-picker`, `bds-date-picker` and `bds-file-picker`. Consumers localize them today through `errorMessage`, which both validators use as an override (same pattern as `bds-date-picker`).
- Needs an ADR first: placeholder syntax for `tooLong` (`{max}`) and plurals are not covered by ADR 0014.
- Out of scope for this plan; re-scope into its own ticket before this plan is marked done.

### Task 13: Fields button display option

**Status:** done (`d8aa8bca`; option A approved 2026-11-19)
**Executor:** @frontend-subagent, @qa-subagent (manual test)

Use case: the Fields trigger can be text only. `fieldsButton: 'icon' | 'text' | 'icon-text'` (default `'icon'`), visible text from a new `labels.fields` key (default "Fields"). Accessible name: `labels.insertField` in `icon` mode, `labels.fields` (the visible text) in `text` and `icon-text` modes, to satisfy WCAG 2.5.3 Label in Name. No SCSS was added.

**Styling decision (user, 2026-11-19):** the text-only look comes from current use cases and has no Figma design. Style it by our own criteria: a `bds-button` with the visible text in its default slot, the disclosure caret, the same size, color and variant as the sibling tools through `bds-button-group`, design tokens only, no new colors or spacing. Record in the PR that this look is not from Figma. T7 reviews it against both variants.

**Ruling 2026-11-19:** switching `fieldsButton` at runtime back to `icon` leaves the trigger about 8px wider. This is an edge case (only a runtime switch on the same editor). It is not fixed in the editor, because keying the dropdown loses the group's propagated `size`. Fix in `bds-button` under T14: `--is-empty` is only ever turned off from `handleTextSlotChange`, which does not fire when the text is removed.

**Documentation:** the Storybook and MDX additions are listed in T9.

### Task 14: `bds-button` accessible-name and empty-text fixes (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent

- With `experimentalSlotFixes`, `hasSlotContent(this.el)` in `componentWillLoad` is empty for default-slot text, so a text-only `bds-button` warns "No accessible name found".
- `bds-button` does not re-detect removed slot text, so the `--is-empty` class stays off (see the T13 ruling).
- Out of scope for this plan; re-scope into its own ticket before this plan is marked done.

### Task 15: Link popover arrow display (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent, @qa-subagent

The link popover hides its arrow (`floatingOptions={ hideArrow: true }`, decided 2026-11-19). With the arrow on, it points to the right of the Link button instead of its centre: `bds-popover.setArrowPosition` hardcodes `left: 20px` for `top-start` and `bottom-start`, ignoring the trigger-centred `arrowData.x` from floating-ui.
- Option 1 (editor only): `placement="bottom"`. The 320px popover overhangs the small button on both sides.
- Option 2 (shared `bds-popover`): use `arrowData.x` with only a minimum inset from the corner; own commit, specs, stories and QA for every `top-start`/`bottom-start` popover. Recommended.
- `floatingOptions.offset` is a distance only, so it cannot align the arrow.
- Decide with design whether the link popover should show an arrow at all, then re-enable it in the editor (remove `LINK_POPOVER_OPTIONS`) once the arrow is centred.
- Re-scope into its own ticket or complete before this plan is marked done.

### Task 16: Tidy `bds-text-editor.scss`

**Status:** done (`75809d54`; compiled CSS identical for step 1, structural diff only for step 2; 0 computed-style differences in Chromium across 51 states)
**Executor:** @frontend-subagent, @qa-subagent (visual re-check)
**Files:** `bds-text-editor.scss` (modify)

Review prototypes and the compile-and-diff tooling are in the scratchpad `te/` folder (`proto-a.scss`, `proto-b.scss`, `verify.sh`, `baseline.css`).
- **Step 1, identical compiled CSS (verify with an empty diff):** `#{$prefix}` interpolation for every class name (the root tag stays literal); `$interactive` selector variable for the repeated `:not(--disabled):not(--readonly)` chain; `@include bds-focus-ring-active` and `@include bds-hover-shadow` for the matching shadows; flatten `calc(calc())` and share `$editable-padding-block` between `max-height` and the editable padding.
- **Step 2, same effect, different structure:** merge the two plain `border-color: transparent` rules; group the identical disabled overrides (text colour, backgrounds). Re-check the focused, plain, error and disabled states visually.
- **Skip:** `%field-inline-label` reuse (optional, not approved), and everything in the review's Tier 3.
- **Hazards:** keep the rule order `focused`, `pressed`, `plain`, `error`; keep `plain.focused`; keep the `bds-text-editor` tag in every selector (it lifts specificity over the shell); keep `word-wrap: break-word` as the fallback.

**Commit:** `refactor(web-components): EOA-18739 tidy bds-text-editor styles`

### Task 17: Focus on `reportValidity()` and blocked submit (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent

Found in the T10 smoke QA: native `reportValidity()` and a blocked submit flag the editor but leave focus where it was. `bds-text-field` behaves the same way in Chromium, so a fix belongs in the shared `useFormField` and would affect every form component. Out of scope for this plan; re-scope into its own ticket before this plan is marked done.

### Task 18: Dropdown menu keys leak to ancestor roving handlers (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent, @qa-subagent

Found while checking the editor's Fields menu (2026-11-20) and confirmed **pre-existing**: it reproduces identically on the EOA-20193 base (`4774509f`) in Chromium, WebKit and Firefox, because no keyboard code changed on this branch.
- **A.** With a `bds-dropdown` menu open, ArrowLeft, ArrowRight, Home and End close the menu and move focus to a `bds-button-group` or `bds-toolbar` button. It also happens with a dropdown directly in a `bds-toolbar`, with no group. Cause: the container's roving handler is bound on the host in the bubble phase with no check on the event target, and the dropdown does not stop these keys; with focus on a menu item the index lookup fails and focus moves anyway. Proposed fix: bind the menu keys in `bds-dropdown.tsx` and stop propagation for keys whose target is inside the list (the `stopPropagation` option on the dropdown's own bindings is untested).
- **B.** In a vertical `bds-button-group`, ArrowDown and ArrowUp on the dropdown trigger open the menu and the group then moves focus away: the menu ends closed in Chromium and WebKit and open in Firefox. Arrow navigation inside the menu is also taken by the group. Enter, Space and Tab still work. Needs a design decision (for example, the dropdown does not open on Up and Down inside a vertical group).
- Evidence and repro: manual scenarios BG-01 to BG-07 in the temporary playground section of `src/index.html`; the QA findings are in the agent memory notes `bds-button-group-dropdown-keyboard-hijack` and `base-vs-head-worktree-build-pnpm-symlink-hazard`.
- Planned for the next sprint (user, 2026-11-20). Out of scope for this plan; re-scope into its own ticket or complete before this plan is marked done.

### Task 19: `bds-button-group` ignores children added after load (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent

Pre-existing. Validation, prop propagation and roving setup run once in `componentDidLoad`. A `bds-button` or `bds-dropdown` appended later gets no `size`, `color` or `variant` from the group, is an extra Tab stop (no roving `tabindex`), and a late wrapped child gets no warning. Proposed fix: a `MutationObserver` or `slotchange` handler in `bds-button-group.tsx` that re-runs the three steps. The docs describe the prop limitation (button-group MDX, "Group children"). Out of scope for this plan.

### Task 20: `bds-toolbar` Tab-stop model (follow-up)

**Status:** deferred
**Executor:** @frontend-subagent

Found by the test plan (F-02). In `bds-toolbar`, every tool is its own Tab stop until the first arrow key is used; afterwards the toolbar is a single Tab stop at the tool last reached. The editor docs describe the real behaviour (commit `2e13b6d1`). Decide the intended model (a single Tab stop with roving tabindex from the start is the usual toolbar pattern) and fix it in the shared `bds-toolbar`. Out of scope for this plan.

**Findings from the test plan, status 2026-11-20:** F-01 (`\r\n` normalised on every value path) fixed in `a3e13b4d`, specs still owed; F-03 (forced-colours chip border, selected chip and focus outline) fixed in `1d3f6cc1`; F-02 docs wording in `2e13b6d1`, behaviour in T20; F-04 (toolbar divider example) in `4b0a6064`; F-05 is T17.
