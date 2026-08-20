# Boreal DS — Code Review Report

**Generated:** 2026-08-20T12:53:28  
**Base ref:** `release/current`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Internal alias import order violation: expected @/services → @/mixins → @/utils. `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:2`
  - Checklist A → Import Order and Barrel Hygiene: "Import order: Framework → `@/services` → `@/mixins` → `@/utils` → local/relative."
  - Antipattern: "Wrong import order: Framework imports must come first, then internal aliases (`@/services`, `@/mixins`, `@/utils`) ordered by abstraction layer, then local/relative imports." Line 2 imports `@/types` before `@/utils` on line 2 is fine in isolation, but combined with line 3's Stencil framework import landing *after* the alias imports, the file violates the framework-first ordering.
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:3`
  - Checklist A → Import Order and Barrel Hygiene (same rule as above).
  - Antipattern: same "Wrong import order" entry — `@stencil/core` (framework) must be the first import, but it is on line 3, after the `@/types` and `@/utils` alias imports on lines 1–2.
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-progress-bar/bds-progress-bar/bds-progress-bar.tsx:67`
  - Checklist A → Component and Prop Discipline: "Getter accessor naming: Getter methods do not carry a `get` prefix — `get placement()` not `get getPlacement()`."
  - Antipattern: "`get` prefix on getter accessors: Writing `get getPlacement()` is redundant — the `get` keyword already marks it as an accessor. Use `get placement()` instead." Applies directly to `private get getClassMap()` at line 67 — should be `get classMap()`.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Design-Fidelity Findings (Figma vs. Implementation)

- 🔴 **[missing-feature] Action buttons entirely absent.** The Figma spec (`Actions Buttons` toggle group with independently switchable `Refresh`, `Trash`, and `Close` buttons rendered next to the progress item) has no corresponding implementation. `bds-progress-bar.tsx` exposes no `@Prop()`, slot, or sub-component for actions of any kind — only `icon`, `label`, `meta`, `status`, and `helperText` slots exist (lines 16–20, rendered at lines 88, 95, 97, 100, 111). There is no `progress-bar__actions` region in the markup or SCSS (`bds-progress-bar.scss` has no `__actions` block), and neither `IProgressBar.ts` nor `types.ts`/`enum.ts` declare anything action-related. Consumers currently have no supported way to render refresh/delete/close controls on the component — they would have to smuggle them into an unrelated slot (e.g. `status` or `icon`), which is not what the design intends per-button-toggle composition.
- 🟢 **[test-coverage — RESOLVED on sibling branch, NOT YET on this branch]** Real tests exist on `feature/EOA-15918_progress-bar-component-test` (commit `af11bab0`), a **sibling** branch that shares parent commit `0d1dc082` with the reviewed `feature/EOA-15918_progress-bar-component-docs` branch — confirmed via `git merge-base --is-ancestor` in both directions (neither branch contains the other's commits). The test branch replaces the old 12-line smoke test (`test/bds-progress-bar.spec.tsx`) with a proper split suite under `__test__/`: `bds-progress-bar.basics.spec.ts` (151 lines — renders all 5 slots with real content assertions, negative `value` clamps to 0%, `value` > `max` clamps to 100% of a custom `max`, invalid `status` attribute falls back to `progress-bar--info`, `disabled` toggles the `--disabled` class, and all four `status` variants apply their modifier class) and `bds-progress-bar.a11y.spec.ts` (asserts `role`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-live`). The sibling meta-item/meta-row tests were similarly upgraded (`bds-progress-bar-meta-item.spec.ts` now also asserts label/content rendering; `bds-progress-bar-meta-row.basics.spec.ts` now asserts slotted meta-item rendering). All 4 progress-bar spec files pass: `pnpm --filter @telesign/boreal-web-components test` → `Test Suites: 237 passed, 237 total`, `Tests: 2524 passed, 2524 total`, run 2026-08-20 against the test branch. **However, as of this review, `feature/EOA-15918_progress-bar-component-docs` (the branch actually under review) still only has the old one-line smoke test** — these tests have not been merged/cherry-picked into it. The Universal checklist item "New logic is covered by tests" is corrected from ✅ to ❌ **for this branch specifically**; it will resolve automatically once the test branch is merged into this one (or vice versa) before the PR ships. Confirmed independently by the testing subagent (smoke-test-only finding) and re-verified against the sibling branch afterward.
- 🔴 **[missing-feature] HelperText has no `state` (Default/Error) variant.** The Figma spec shows the helper-text region toggled between `Default` and `Error` (red text), independent of the bar's `status`. The current implementation hardcodes the helper text color in SCSS: `.progress-bar__status-bar-helper-text` (`bds-progress-bar.scss:138-144`) sets a single fixed `color: $boreal-text-default-light` with no modifier class or state-driven variation, and `bds-progress-bar.tsx` has no `helperTextState` (or similarly named) `@Prop()`, no enum for it, and no conditional class applied to the helper-text wrapper. The only color variation implemented is the whole-bar `status` prop (`success`/`error`/`paused`/`info`, `bds-progress-bar.tsx:33`), which is a different axis from the design's independent helper-text state toggle — setting `status="error"` does not change `[slot='helperText']` color today, since the `bds-progress-bar-variant` mixin only touches `.progress-bar__left-side__trailing` (status slot text) and the bar fill, not `-helper-text`.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ❌ New logic is covered by tests _(❌ for this branch; tests exist and pass on sibling branch `feature/EOA-15918_progress-bar-component-test`, not yet merged here — see finding above)_
- ✅ Tests use `waitForChanges()` before DOM assertions
- ⚠️ Storybook/MDX/README updated when behavior or APIs change — see note below
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ✅ Every @Prop() has `readonly` and an adjacent JSDoc block
- ✅ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ✅ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
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
- ❌ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

**Note on the "Storybook/MDX/README updated" item (⚠️, not a clean ❌):** the documentation subagent independently verified that `bds-progress-bar.stories.ts` / `bds-progress-bar.mdx` fully and correctly document everything actually implemented today — all 4 props, all 5 slots, correct `argTypes`, correct `status` control options, ARIA section matches the real attributes. The docs are **not stale**; they simply (correctly) don't document the two unimplemented Figma features, since documenting a feature that doesn't exist would be worse. The original ❌ conflated "docs are out of sync with the code" with "the code is missing designed functionality" — those are different problems, and only the latter applies here. One genuine, minor doc nit found: `bds-progress-bar.mdx:101` refers to the slot as `helper-text` (kebab-case) in prose, but the actual slot attribute is `helperText` (camelCase) per `bds-progress-bar.tsx:19,111` and `bds-progress-bar.stories.ts:112` — a one-line copy fix, not a blocking issue.

**Note:** even the upgraded test suite on the sibling branch has, correctly, no coverage for action buttons or helperText `state` — those features don't exist in the code, so nothing to test yet. One small gap worth closing when tests do land here: `bds-progress-bar.a11y.spec.ts` only asserts `aria-valuemax` against the default `max="100"` fixture; there's no case with a custom `max` (e.g. `max="25"`) confirming `aria-valuemax` reflects it independently of `value`.

## Suggested Fix Direction (from frontend-subagent review, non-blocking guidance)

- **Action buttons**: follow the existing `bds-progress-bar-meta-item`/`bds-progress-bar-meta-row` sub-component convention already used in this directory — introduce a dedicated `bds-progress-bar-actions` sub-component with independent boolean `@Prop()`s per button (`refresh`, `trash`, `close` — no `show`/`has` prefix) rather than a single freeform slot, since the design calls for independently toggleable buttons. This would be the component's first use of `@Event()` emitters (e.g. `bdsRefresh`, `bdsTrash`, `bdsClose`).
- **HelperText state**: add `readonly helperTextState: 'default' | 'error' = 'default'` as a new prop with its own enum (mirroring `PROGRESS_BAR_STATUS`'s pattern in `enum.ts`), its own `validatePropValue` + `@Watch()` + `componentWillLoad()` call (do not reuse the existing `status` watcher — the two must vary independently per Figma), and a `progress-bar--helper-error` modifier class applied via the (renamed) `classMap` getter, with a new SCSS rule scoped to `&--helper-error .progress-bar__status-bar-helper-text { color: $boreal-text-danger-base; }`, decoupled from the `bds-progress-bar-variant` mixin.

## Memory-Guided Review

> _This section is completed by the agent after reading `.claude/memory/MEMORY.md` and the relevant topic files. The script leaves this placeholder intentionally._

### `mouseleave` handlers (relatedTarget vs. target)
No issues found — `bds-progress-bar.tsx` has no `mouseleave` listeners; not applicable to this component.

### Enum-like props (`validatePropValue` + `componentWillLoad()` + stacked `@Watch()`)
No issues found. `status: ProgressBarStatus` is validated correctly: `@Watch('status') checkPropValue()` (line 44) calls `validatePropValue` against `PROGRESS_BAR_STATUS` values with an `INFO` fallback, and `componentWillLoad()` invokes it once on initial load (line 59). This matches the pattern in `feedback_prop_validation_pattern.md`.

### FACE `disabled` (`@State` mirror + `@Watch` + `formDisabledCallback`)
Not applicable — `bds-progress-bar` is not form-associated (no `formAssociated: true`, no `@AttachInternals()`). `disabled` here is a plain, non-reflected-native-constraint boolean prop, so the FACE mirror pattern from `stencil-prop-patterns.md` doesn't apply.

### Form control composite interface (`IFormControl<T>`)
Not applicable — this is a feedback/display component, not a form control.

### Light DOM (no `shadow: true` / `::part()`)
No issues found. `@Component` config only sets `tag` and `styleUrl` (lines 22–25); no `shadow: true`, no `::part()` usage anywhere in the file, consistent with `project_no_shadow_dom.md`.

### Event naming semantics (`bds{Component}{Action}` mid-word component noun)
Not applicable — the component declares no `@Event()` emitters at all.

### Component convention cross-checks (`feedback_boolean_prop_naming.md`, `component-accessor-naming-conventions.md`)
- `disabled` (line 36) follows the required boolean-prop naming — no `is`/`has`/`show` prefix. No issue.
- `get getClassMap()` (line 67) duplicates the `getter-get-prefix` static finding above; per `component-accessor-naming-conventions.md` this should be `get classMap()`. Same underlying issue, surfaced independently by memory as a known repo-wide convention rather than a one-off linter rule.

### Dev-server hot-reload caveat (`feedback_dev_server_restart.md`)
Not a code defect, but relevant for whoever validates this PR manually: Stencil changes to `bds-progress-bar.tsx`/`.scss` do not hot-reload in Storybook — `pnpm dev:docs` must be restarted from the monorepo root after edits, including any fix for the action-buttons/helperText-state gaps found above.

**Memory topic files consulted:**
- `mouseleave-relatedtarget-vs-target.md`
- `feedback_boolean_prop_naming.md`
- `component-accessor-naming-conventions.md`
- `stencil-sass-inject-global-paths-constraint.md` (checked — `bds-progress-bar.scss` starts directly with mixin/selectors, no `@use`, compliant)
- `feedback_dev_server_restart.md`
- `feedback_no_why_comments_tightened.md` (checked — file has zero inline `//` comments, only JSDoc; compliant)

---

**Result: 24 passed · 2 failed (test coverage on this branch, getter prefix) · 1 warning (docs — see note)**
_(Checklist row "New logic is covered by tests" corrected from ✅ to ❌ during subagent validation — real, passing tests exist on sibling branch `feature/EOA-15918_progress-bar-component-test` but are not present on `feature/EOA-15918_progress-bar-component-docs`, the branch this report reviews; this failure clears once the two branches are merged. "Storybook/MDX/README updated" downgraded from ❌ to ⚠️ — see notes above. Plus 2 design-fidelity gaps (action buttons, helperText state) and 2 import-order findings tracked separately above, outside the pass/fail checklist count.)_

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_