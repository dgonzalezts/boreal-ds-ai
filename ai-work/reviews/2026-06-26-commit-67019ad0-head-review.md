# Boreal DS — Code Review Report

**Generated:** 2026-06-26
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🔴 **[prop-missing-jsdoc]** @Prop() declaration is missing a JSDoc block directly above it. `packages/boreal-web-components/src/components/forms/bds-searchbar/bds-search-bar.tsx:113`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-searchbar/bds-search-bar.tsx:74`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-searchbar/bds-search-bar.tsx:140`
  - _Note: This is a false positive by the static analyzer; `valueChange` is a project-wide exception reserved for Vue `v-model` integration._
- 🟡 **[class-jsdoc-invalid-tags]** Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead. `packages/boreal-web-components/src/components/forms/bds-searchbar/bds-search-bar.tsx`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-searchbar/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-searchbar/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/forms/bds-searchbar/types/index.ts:3`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx:41`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx:71`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/utils/testing/mocks/index.ts:5`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - **Rule:** Storybook/MDX/README updates exist when behavior or APIs change (Universal Section).
  - **Antipattern:** Failing to update the documentation or Storybook configuration along with a new component features leads to outdated API guidelines. The `mode` prop JSDoc does not match the actual `SearchBarMode` types (`"list"` / `"search"`).
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
  - **Rule:** Every `@Prop()` has `readonly` and an adjacent JSDoc block.
  - **Antipattern:** `@Prop()` without a JSDoc block violates `stencil/required-jsdoc`. The `mode` property (line 113) is missing its JSDoc documentation, and `asynch` (line 104) has a copy-paste description unrelated to async loading.
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - **Rule:** `mutable: true` is not used on native form attributes (`disabled`, `checked`, `value`) — use a `@State()` mirror instead.
  - **Antipattern:** Setting `mutable: true` on native attributes like `value` (line 74) can clash with external synchronization and Stencil compilation flow.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - **Rule:** Custom events use the `bds{Action}` prefixed camelCase pattern.
  - **Antipattern:** The linter flagged `valueChange` (line 140), but it is a project-wide exception allowed for Vue `v-model` integration.
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ❌ JSDoc changes preserve custom-elements.json generation accuracy
  - **Rule:** JSDoc changes preserve `custom-elements.json` generation accuracy.
  - **Antipattern:** Placing `@property` and `@method` tags at the class level is ignored by the CEM analyzer, giving a false sense of documentation. Move JSDocs directly to the individual fields/methods.
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/\*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

---

## Memory-Guided Review

### 1. Enum-Like Prop Validation (`mode`)

- **Finding:** While the `variant` prop is correctly validated in `componentWillLoad` using `validatePropValue`, the enum-like `mode` prop is completely missing validation. If an invalid value is passed to `mode`, the component will fail silently.
- **Action:** Implement a `@Watch('mode')` and validation block for `mode` using `SEARCH_BAR_MODE` values.

### 2. Interface File Naming Casing

- **Finding:** The interface file is named `ISearchbar.ts` instead of `ISearchBar.ts` (with a capital `B`). This conflicts with the component casing `BdsSearchBar` and standard monorepo naming conventions.
- **Action:** Rename the file to `ISearchBar.ts`.

### 3. Direct DOM Traversal & Encapsulation

- **Finding:** The getter `bdsInputEl` queries the raw `input` child inside `<bds-text-field>`:
  ```typescript
  private get bdsInputEl(): HTMLInputElement | null {
    return this.bdsFieldEl?.querySelector('input') ?? null;
  }
  ```
  This is a direct dependency on the internal template of `<bds-text-field>`, violating component encapsulation guidelines.
- **Action:** Suggest exposing public method interfaces on `<bds-text-field>` for focus/blur operations instead.

### Memory topic files consulted:

- `ai-docs/guidelines/stencil-best-practices.md`
- `ai-docs/guidelines/code-review-checklist.md`
- `.agents/memory/MEMORY.md`

---

**Result: 22 passed · 5 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
