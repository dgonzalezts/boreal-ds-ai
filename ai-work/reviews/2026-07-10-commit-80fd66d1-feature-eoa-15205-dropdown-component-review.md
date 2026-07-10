# Boreal DS — Code Review Report

**Generated:** 2026-07-10T08:41:00
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/actions/bds-dropdown/bds-dropdown.tsx:35`
  - **Manual review verdict: FALSE POSITIVE.** `bds-dropdown` does not declare `formAssociated: true` and has no `@AttachInternals()` — it is not a FACE component, so the `disabled`-specific `mutable: true` warning (rule from `stencil-prop-patterns.md`, confirmed in `.agents/memory/MEMORY.md` 2026-03-13 entry: _"`mutable: true` with narrow cast remains valid for non-FACE props"_) does not apply. This rule is scoped to native constraint attrs like `disabled`/`checked` on FACE controls, not a generic `value` prop on a non-form component.
  - Checklist rule: "Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`" — antipattern doc: _"`mutable: true` on `disabled`: Stencil warns and creates two writers on the same reflected attribute... Use `@State() private isDisabled` instead."_ Applies only when the component is form-associated.
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-dropdown/bds-dropdown.tsx:41`
  - **Manual review verdict: FALSE POSITIVE, but flags a real architectural gap (see Memory-Guided Review below).** `valueChange` is not a generic DOM custom event — it is the reserved convention name from `IFormValueEmitter<T>` (`packages/boreal-web-components/src/mixins/form-associated.mixin.ts:86-92`), used by `@stencil/vue-output-target`'s `componentModels` config to auto-generate Vue `v-model` bindings. Every other component using this exact event name (`bds-text-field`, `bds-radio-group`, `bds-slider`, `bds-checkbox`, `bds-toggle`) is exempt from the `bds{Action}` prefix rule for this one reserved name. The `event-name-format` checker rule doesn't know about this carve-out.
  - Checklist rule: "Custom events use the `bds{Action}` prefix pattern" — `valueChange` is a documented exception tied to the `IFormControl<T>` 2-way-binding contract, not a violation.
- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:31`
  - **Out of scope for this PR.** `git diff` confirms line 31 is untouched by this branch — the only change to `bds-list-menu-item.tsx` is the new `handleBlur` handler and its `onBlur` wiring. This is pre-existing debt in a file the PR happens to touch, not something introduced here.
- 🔴 **[event-name-format]** @Event() name 'readonly' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:67`
  - **Out of scope for this PR** — same reasoning as above; the checker scans the whole file, not just the diff hunk, and line 67 predates this branch. Likely a checker false positive matching the word `readonly` near an unrelated `@Event()` — worth a look independently of this PR, but not a blocker here.
- 🟡 **[import-order]** Internal alias import order violation (×3). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:3-5`
  - **Out of scope for this PR** — pre-existing import order in a file not touched at those lines by this branch.
- 🔵 **[missing-stories]** Component TSX files changed but no Storybook stories found in the diff.
  - **Real gap.** `bds-dropdown` has no `.stories.ts` in this PR — confirmed by directory listing (`test/`, `bds-dropdown.tsx`, `bds-dropdown.scss`, no stories file). Should be added before merge per project convention (`documentation-subagent` / `documentation-knowledge` skill).
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  - **Real gap.** Confirmed — no changeset file in the diff for a net-new public component.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ✅ JSDoc changes preserve custom-elements.json generation accuracy
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ✅ Getter accessors carry no redundant `get` prefix

## Manual Findings (not caught by static checks)

- 🔴 **Stray zero-byte file committed:** `packages/boreal-web-components/src/components/actions/bds-dropdown/types/IDropdown` (no extension) sits next to the real `IDropdown.ts` and is empty. It's an accidental artifact (likely an editor `touch`/rename slip) and should be deleted before merge — it serves no purpose and will confuse anyone browsing the `types/` folder.
- 🟠 **Architectural gap — `value`/`valueChange` mimics the `IFormControl<T>` contract without implementing it.** `bds-dropdown` declares `@Prop({ mutable: true }) value` and `@Event() valueChange` — exactly the shape `IFormValueEmitter<T>` expects (`form-associated.mixin.ts:86-92`) — but the component is not `formAssociated: true`, doesn't extend `formAssociatedMixin`, has no `@AttachInternals()`, and has no `name`/`disabled`/`required` props. A dropdown/select is a canonical form control, and every sibling in `actions/` that owns a `value` (e.g. `bds-toggle`) implements the full `IFormControl<T>` contract. Worth confirming with the author/ticket (EOA-15205) whether FACE integration is intentionally deferred to a follow-up ticket — if not called out explicitly, this reads as a half-finished contract that will be a breaking change to retrofit once consumers depend on the current non-form behavior.
- 🟡 **Redundant event emission on selection.** `listenListBdsChange` (`bds-dropdown.tsx:130-145`) emits `bdsChange` unconditionally, then — only when `selectable` — also sets `this.value` and emits `valueChange` with the _same_ `eventDetail`. Consumers using two-way binding will receive the identical payload twice (once as `bdsChange`, once as `valueChange`). Confirm this duplication is intentional (bdsChange for general listeners, valueChange for v-model) rather than leftover from iterating on the selection logic.
- 🟡 **Self-referential `@Watch('value')`.** `watchValue` (`bds-dropdown.tsx:47-52`) reassigns `this.value = newValue` inside the watcher for `value` itself, after already checking `newValue !== oldValue`. Since Stencil calls the watcher after the prop is already set to `newValue`, this reassignment is a no-op — `this.value` already equals `newValue` when the watcher runs. Harmless today, but reassigning a prop inside its own watcher is a pattern that invites infinite-loop bugs if the equality check is ever loosened. Consider dropping the reassignment and keeping only `this.loadValue()`.
- 🔴 **Thin test coverage for a stateful component — UPDATED, verified against companion branch `feature/EOA-15205_dropdown-testing`.** The original single-smoke-test file (`test/bds-dropdown.spec.tsx`) has been superseded on a sibling branch, `origin/feature/EOA-15205_dropdown-testing`, which renames it to `__test__/bds-dropdown.spec.ts` and adds four new spec files (`bds-dropdown-keyboard.spec.ts`, `bds-dropdown.ay11.spec.ts`, `bds-dropdown.basics.spec.ts`, `bds-dropdown.events.spec.ts` — 17 tests total, all passing) plus a 3-line tweak to `bds-dropdown.tsx` itself (`this.el as HTMLElement` cast, a `!this.selectable` guard added to `loadValue()`, and `role="presentation"` on the child `bds-popover`). This closes some of the originally-named gaps but **not all of them**, and overall coverage still misses the project's ≥90% gate on every metric. Verified by running `pnpm test:coverage` against a worktree of that branch:

    | Metric | Result | Gate |
    |---|---|---|
    | Statements | 81.42% (57/70) | ❌ below 90% |
    | Branches | 60.37% (32/53) | ❌ below 90% |
    | Functions | 78.94% (15/19) | ❌ below 90% |
    | Lines | 87.3% (55/63) | ❌ below 90% |

  Jest's own project-wide threshold already fails this run (branches 80% gate, functions gate) — this is below even the repo's baseline, not just the stricter 90% quality-gate bar.

  Gap-by-gap verdict (cross-checked against lcov hit counts, not just reading the specs):
  - ✅ `selectable`/`multiSelect` branching — covered (`basics`, `ay11`, `events`, and the multi-select case in `keyboard` spec).
  - ⚠️ `value` watcher (`@Watch('value')`) — only incidentally hit via *initial* `value="2"` HTML attributes in three specs; no test changes `value` post-render, so the watcher's actual "old !== new" branch is never taken (`BRDA:49,...,0,0`).
  - ✅ Keyboard-driven popover opening (ArrowUp/ArrowDown) — covered, including negative cases (Enter/Tab don't open).
  - ❌ `disconnectedCallback` listener cleanup — **still untested.** `FNDA:0` for the function; no spec removes the element from the DOM.
  - ❌ `handlePopoverClose` active-item reset — **still untested.** `FNDA:0` for the function; no spec dispatches `bdsClose` on the popover child.
  - Two coverage gaps not named in the original finding: the `bdsButton`/`bdsList`/`bdsPopover` getters' `this.el !== null` else-branch is never exercised, and the `requestAnimationFrame` focus-return callback on line 138 never runs inside a test's `waitForChanges()`.

  One test-quality note: the four `keyboard` spec cases that stub `openPopover`/`closePopover` via `Object.defineProperty` on the real `bds-popover` child prove only that the dropdown *calls the right method name* — a rename or internal-mechanism change in `bds-popover` wouldn't be caught. Not broken, just an implementation-detail coupling likely to surface as a surviving mutant if/when mutation testing (phase 2, not run here) is done.

  **Action needed before merge:** the testing branch should be merged into this one (or the two reconciled), and `disconnectedCallback` / `handlePopoverClose` / the `value`-watcher change-path each need a dedicated test before the coverage gate can pass.

## Memory-Guided Review

### Component conventions (`.agents/memory` + user auto-memory)

- **`feedback_custom_events_naming.md`** (bds + action only, no component name): `bdsChange` complies. `valueChange` is a deliberate, documented exception (see false-positive note above) — not a violation, but confirms the naming rule was correctly checked rather than blindly applied.
- **`stencil-form-control-interfaces.md` / ADR-0002 (`IFormControl<T>` composite interface)**: applies to any component that "owns a `value` prop" per the mixin's own doc comment. `bds-dropdown` owns `value` but does not implement the interface — see Manual Finding above. **Correction (validation pass):** a second agent checked `forms/bds-select/bds-select.tsx` — a directly analogous trigger+listbox pattern with its own mutable `value` — and confirmed it *also* has zero FACE code (no `Mixin`, no `AttachInternals`, no `formAssociated`). So the codebase already has an established, if inconsistent, split: listbox/menu-driven value pickers (`bds-select`, and now `bds-dropdown`) skip FACE, while primitive input controls (`bds-toggle`, `bds-text-field`, `bds-checkbox`, `bds-radio-group`, `bds-slider`) implement it. This softens the finding from "PR-specific oversight" to "consistent with an existing codebase pattern that may itself be worth revisiting" — still worth flagging to the author, but not evidence this PR uniquely dropped the ball.
- **`component-accessor-naming-conventions.md`** (no `get` prefix on getters, `!x \|\| false` redundant): `bdsButton`, `bdsList`, `bdsPopover` getters are correctly named with no `get` prefix. No redundant `|| false` patterns found. No issues.
- **`component-bds-typography-group-labels.md`**: not applicable — `bds-dropdown` renders no label/helperText.
- **`feedback_boolean_prop_naming.md`** (no `is`/`has`/`show` prefix): `selectable` and `multiSelect` both comply. No issues.
- **`mouseleave-relatedtarget-vs-target.md`**: not applicable — no `mouseleave` handler in this component.
- **`dom-setattribute-aria-kebab-case.md`**: `loadAria()` calls `updateElementAttr(button, 'aria-controls', this.listId)` — kebab-case, compliant. No issues.
- **`feedback_dev_server_restart.md`**: process note only, not a code defect — flagging for the reviewer's own manual verification step, not the PR author.

### Styles (`bds-dropdown.scss`)

- **CORRECTION (previous pass was wrong):** an earlier version of this review claimed `bds-popover` "ships no SCSS file at all," used as justification that `bds-dropdown.scss`'s 3 lines were complete. That claim was based on searching the wrong directory (`actions/bds-popover/` instead of `overlays/bds-popover/`) and was false — `overlays/bds-popover/bds-popover.scss` exists and is 120 lines (fixed `--popover-width: 320px` default, border-radius, box-shadow, placement-based arrow positioning). Caught on a validation pass by a second agent given the same task; correcting here rather than leaving the earlier verdict standing.
- 🟡 **Real gap: `bds-dropdown` never sets a `width` on its `bds-popover`, unlike its closest analogue.** `bds-dropdown.tsx:174` renders `<bds-popover managed={false} placement="bottom-start" id={this.listId}>` with no `width` prop, so it silently falls back to `bds-popover`'s fixed `320px` default regardless of the trigger's size. `bds-select.tsx:791` — a directly comparable trigger+listbox pattern in the same codebase — explicitly renders `<bds-popover width="full" managed={true}>` so the popover matches the trigger width. This may be an intentional design choice (menu-style dropdown vs. full-width form select), but it wasn't called out anywhere in the PR, and a fixed 320px popover attached to an arbitrarily-sized trigger (button, icon, custom slot content) is a plausible visual bug for any trigger narrower or much wider than 320px. Worth an explicit confirmation with the author/design spec rather than assuming it's deliberate.
- `bds-dropdown.scss` itself has no hardcoded colors/spacing/radii to check against the `var(--boreal-*)` token rule, and no `@use` of the token package (would double-inject per `stencil-sass-inject-global-paths-constraint.md`) — those two checks still pass. The file's minimalism is fine in principle for a slot-based wrapper; the issue is the missing `width` prop on the child `bds-popover`, not the SCSS file itself.
- 🔴 **`:host` selector is dead CSS — Boreal DS uses light DOM.** `bds-dropdown.scss:1` uses `:host { display: block; }`, but `:host` is a shadow-DOM-only pseudo-class per spec (MDN) and has **no effect** outside a shadow boundary. `bds-dropdown.tsx` never sets `shadow: true` (uses the project-wide light DOM default), so this rule never matches anything — the intended `display: block` is silently dropped, and `<bds-dropdown>` falls back to the browser's default `display: inline` for unknown elements. This is a documented, previously-corrected mistake in this exact codebase: see `.agents/memory/MEMORY.md`'s 2026-04-17 "Major correction" entry, which fixed the same wrong assumption project-wide and settled on direct tag-name selectors instead (`bds-button { }`, `bds-checkbox { }`, `bds-grid { }` all confirmed as the live pattern). **Fix:** `:host { display: block; }` → `bds-dropdown { display: block; }`. Caught only after the user directly asked about this selector — missed on both the initial pass and the subagent validation pass, which focused on token/`@use` checks rather than the selector itself.

### Memory topic files consulted

- `.agents/memory/MEMORY.md` (index)
- `.agents/memory/stencil-form-control-interfaces.md` (referenced via MEMORY.md; interface confirmed directly in `form-associated.mixin.ts`)
- User auto-memory: `feedback_custom_events_naming.md`
- `.claude/skills/code-reviewer/references/common_antipatterns.md`
- `packages/boreal-web-components/src/mixins/form-associated.mixin.ts` (primary source, not memory, but required to verify the `valueChange`/`IFormControl<T>` claim)

---

**Result: 20 passed · 4 failed (2 of the 4 automated fails are false positives on manual review; 2 are pre-existing debt outside this PR's diff — see annotations above). 5 additional manual findings identified, one escalated to blocking after verifying the companion `feature/EOA-15205_dropdown-testing` branch's actual test run: coverage remains below the project's 90% gate (81.42% statements / 60.37% branches / 78.94% functions) and two named behaviors — `disconnectedCallback` cleanup and `handlePopoverClose` active-item reset — are still completely untested.**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
