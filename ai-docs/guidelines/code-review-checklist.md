# Boreal DS - Monorepo Code Review Checklist

This checklist is a shared baseline for reviewing changes across the Boreal design system monorepo. Use the universal section for every review, then apply the relevant package-specific addenda.

---

## 0. Pre-Review Setup

- [ ] **Scope clarity**: The PR description lists affected packages and user-facing impact.
- [ ] **Branch hygiene**: Work is on a feature branch and scoped to the intended changes.
- [ ] **Compatibility intent**: The author states whether the change is additive, breaking, or behavior-changing.

---

## 1. Universal (Applies to All Changes)

### Code Quality and Architecture

- [ ] **Single responsibility**: The change has a clear purpose with minimal unrelated edits.
- [ ] **Type safety**: No `any` usage without justification and documentation.
- [ ] **Edge cases**: Error paths and invalid inputs are handled explicitly.
- [ ] **Security**: User-provided content is sanitized or safely escaped where applicable.
- [ ] **Performance**: No avoidable re-renders, heavy work on the main thread, or unnecessary bundle growth.

### Testing and Verification

- [ ] **Test coverage**: New logic is covered by tests appropriate to the package.
- [ ] **Regression protection**: Existing tests remain valid and are not weakened.
- [ ] **Async correctness**: Tests wait for async rendering or side effects before assertions.

### Documentation and Developer Experience

- [ ] **Docs updated**: Storybook/MDX/README updates exist when behavior or APIs change.
- [ ] **Changelog or release note impact**: Noted when the change is consumer-facing.
- [ ] **Consistent naming**: Public APIs, events, and props follow established naming conventions.

### Build and Release

- [ ] **Build success**: Relevant `build`, `lint`, and `test` tasks pass in the affected package(s).
- [ ] **Export integrity**: `exports` maps and published artifacts line up with built outputs.

---

## 2. Package-Specific Addenda

Apply the sections below only when the change touches the corresponding package.

### A) `packages/boreal-web-components` (Stencil)

#### Import Order and Barrel Hygiene

- [ ] **Import order**: Framework → `@/services` → `@/mixins` → `@/utils` → local/relative.
- [ ] **Named barrel re-exports**: Barrel files use `export { X } from './X'`, not `export * from './X'`.
- [ ] **No over-exporting**: `@/services` (and other internal barrels) only re-export symbols that belong to that layer's contract.
- [ ] **No cross-component barrels**: No component imports another component through a shared barrel.

#### Component and Prop Discipline

- [ ] **Props are readonly + documented**: Every `@Prop()` has `readonly` and an adjacent JSDoc block.
- [ ] **Boolean prop naming**: No `is`, `has`, or `show` prefix — use descriptive adjectives matching native HTML (`closable` not `showClose`; `header` not `hasHeader`; `error` not `isError`).
- [ ] **Prop validation pattern**: `validatePropValue` + `componentWillLoad()` + stacked `@Watch()` is used for enum-like props.
- [ ] **Mutable props**: `mutable: true` is not used on native form attributes (`disabled`, `checked`, `value`) — use a `@State()` mirror instead. When `mutable: true` is used elsewhere, internal assignment uses a narrow cast, not `as any`.
- [ ] **FACE disabled pattern**: `formDisabledCallback` writes to `@State() private isDisabled`, not to a mutable `@Prop()`.
- [ ] **Interface file naming**: Component interface files are named `IComponent.ts` (e.g. `ITooltip.ts`), never `IBdsComponent.ts`.
- [ ] **Getter accessor naming**: Getter methods do not carry a `get` prefix — `get placement()` not `get getPlacement()`.
- [ ] **No redundant boolean expressions**: `!x || false` must be simplified to `!x`.
- [ ] **No dead Popover API declarations**: No `declare global { interface HTMLElement { showPopover()... } }` blocks — the Popover API is native in TypeScript ≥ 5.2.
- [ ] **No class-level `@internal`**: Component classes do not use `@internal` in JSDoc.
- [ ] **No ignored JSDoc tags**: Avoid `@element` and `@method` at class level; use method-level JSDoc instead.
- [ ] **Use `@file`**: Module JSDoc uses `@file` (not `@fileoverview`).
- [ ] **Type narrowing**: Prefer `instanceof Element` for element-node narrowing instead of `nodeType` checks.

#### DOM and Accessibility

- [ ] **ARIA attribute casing in `setAttribute`**: ARIA attributes passed to `setAttribute` use kebab-case (`aria-describedby`, `aria-haspopup`) — never camelCase (`ariaDescribedBy`).
- [ ] **`mouseleave` stayOnHover uses `relatedTarget`**: Floating element "keep-open" checks use `e.relatedTarget` (pointer destination), not `e.target` (element being left).

#### Events

- [ ] **Event naming**: Custom events use the `bds{Action}` prefixed camelCase pattern.
- [ ] **Event decorator bare**: `@Event()` uses no explicit options (see ADR `ai-docs/decisions/0003-event-options-convention.md`).
- [ ] **No native collisions**: Event names do not reuse native DOM events (`click`, `change`, etc.).

#### FACE (Form-Associated Custom Elements) Components

- [ ] **`@AttachInternals()` placement**: Declared on the component class body, not in mixins.
- [ ] **Method wrappers**: `checkValidity()` and `reportValidity()` are exposed via `@Method()` wrappers.
- [ ] **Constraint validation ownership**: Only `ElementInternals.setValidity()` manages validity. Inner inputs do not carry native constraint attrs.
- [ ] **Focus delegation**: Host is focusable when invalid and delegates focus to the inner input.
- [ ] **Reset/restore hooks**: `formResetCallback` and `formStateRestoreCallback` call `updateValidity()`.
- [ ] **Custom validators**: `customValidators` triggers `updateValidity()` in a `@Watch()` handler.

#### Rendering and Testing Gotchas

- [ ] **Async render assertions**: Tests use `waitForChanges()` before reading reflected DOM state.
- [ ] **Disabled propagation**: `formDisabledCallback` is tested via `<fieldset disabled>`, not `form.disabled`.
- [ ] **Light DOM assumption**: No new usage that assumes Shadow DOM behavior.

#### Build and Output Targets

- [ ] **CEM integrity**: JSDoc changes preserve `custom-elements.json` generation accuracy.
- [ ] **Dist copy behavior**: `postbuild` promotion is intact; validate with a clean `dist/`.
- [ ] **Export map alignment**: `dist/css` and `dist/scss` paths exist and match `package.json` exports.

---

### B) React and Vue Wrappers (`packages/boreal-react`, `packages/boreal-vue`)

- [ ] **Wrapper outputs updated**: Generated outputs or types are rebuilt when web components change.
- [ ] **Internal dependency location**: `@telesign/boreal-web-components` remains in `dependencies` (not `peerDependencies`).
- [ ] **release-it config**: Uses `publishPackageManager: "pnpm"` with `publishArgs`, not `publishCommand`.

#### Vue-Specific

- [ ] **`componentModels` updated**: New form components are registered for `v-model`.
- [ ] **`eventAttr` used when needed**: If `valueChange` emits a primitive, `eventAttr` is configured.

---

### C) Style Guidelines (`packages/boreal-style-guidelines`)

- [ ] **Token generation**: `generate` and `validate` pass after token changes.
- [ ] **Export map sanity**: `dist/css`, `dist/scss`, and token exports match `package.json` exports.
- [ ] **Breaking token changes**: Documented with migration guidance where relevant.

---

### D) Docs and Storybook (`apps/boreal-docs`)

- [ ] **Stories updated**: Component behavior changes are reflected in stories and MDX.
- [ ] **Vite CSS aliasing**: Storybook aliasing remains intact for `@telesign/boreal-web-components/css/*`.
- [ ] **Chromatic workflow**: Uses `dotenv --` and `--storybook-build-dir` (not `--build-script-name`).
- [ ] **Turbo outputs**: `storybook-static/**` is declared when Chromatic uploads are expected.

---

### E) Scripts and Release Pipeline (`scripts-boreal`, root scripts)

- [ ] **Build guarantee**: Pack or validate scripts rely on Turbo `dependsOn`, not ad-hoc builds.
- [ ] **Suffix convention**: Per-framework scripts use `:react`, `:vue`, `:angular` consistently.
- [ ] **Signal handling**: Cleanup handlers use `spawnSync` and `process.once()` for SIGINT/SIGTERM.
- [ ] **Force-kill recovery**: Pipeline docs reference `pnpm install` as the recovery step after SIGKILL.

---

## Checklist Usage

1. Start with the Universal section.
2. Apply the package addenda relevant to the files changed.
3. Record any unchecked items with concrete follow-up actions.

---

## F) Component API Design (`boreal-web-components`)

### Property reflection

- [ ] **Reflect only primitives used for a11y or CSS**: `disabled`, `variant`, `size`, `open`, `selected`, `active`.
- [ ] **Do not reflect**: complex objects/arrays, frequently changing values (`value`, `progress`), or internal implementation state.

### Controlled vs. uncontrolled pattern

- [ ] **Controlled components** emit a change event and do not update the prop themselves — the parent owns the value. Verify the `@Watch()` does not call `this.bdsChange.emit()`.
- [ ] **Uncontrolled components** manage internal `@State()` and may expose a `defaultValue` prop for initial seeding. Confirm there is no external mutation of internal state.

### TypeScript API surface

- [ ] **No `Omit<>` on component props**: each `@Prop()` is declared individually. `Omit<>` breaks Stencil's CEM generation and IDE autocomplete.
- [ ] **No regular enums**: use string union types (`type Variant = 'primary' | 'secondary'`) or `const` enums. Regular enums generate runtime code that cannot be tree-shaken.

---

_This checklist is intentionally framework-agnostic in the Universal section and only calls out framework-specific requirements in the relevant addenda._
