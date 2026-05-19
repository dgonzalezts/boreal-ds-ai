# Boreal DS — Code Review Report

**Generated:** 2026-04-22T14:13:07
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:4`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:59`
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - **Note:** Stories and MDX are now present in the diff. This may be a false positive from the script. However, a changeset entry is still missing — this item should be cleared once `[missing-changeset]` is resolved.
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
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/\*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

> _Completed after reading `.claude/memory/MEMORY.md` and the relevant topic files._

### `:host` in light-DOM SCSS — ❌ Bug (unfixed from previous review)

`bds-status.scss` still contains:

```scss
:host {
  display: block;
}
```

Boreal DS uses light DOM exclusively. Per [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/:host), `:host` has no effect outside a shadow boundary — this rule is silently ignored at runtime and `display: block` is never applied.

**Fix:** `bds-status { display: block; }`

- **Memory reference:** `stencil-light-dom-host-vs-class.md`, `project_no_shadow_dom.md`

---

### Test suite is a placeholder — ❌ DoD not met (unfixed from previous review)

The spec file (`__test__/bds-status.spec.tsx`) is unchanged from the previous review cycle. The single test asserts a `<mock:shadow-root>` that can never appear in a light DOM component, and exercises zero real component behavior. DoD requires ≥ 90% statement coverage.

Behaviors not yet tested:

- All five `state` variants render the correct BEM modifier class
- An invalid `state` value falls back to `"neutral"` (prop validation)
- `dot={true}` renders `.bds-status__dot` with `aria-hidden="true"`
- `dot={false}` does not render `.bds-status__dot`
- `role="status"` is applied on the host
- The `icon` named slot renders slotted content
- `componentWillLoad()` calls `checkPropValues()` on initial render

---

### Dead code in `types/enum.ts` and `types/types.ts` — ❌

Two new files were added to the diff but are never imported by any component:

- `types/enum.ts` exports `STATUS_STATES` — an exact structural duplicate of `PROCESS_STATUS` in `packages/boreal-web-components/src/types/states.ts`
- `types/types.ts` exports `StatusState` — a type alias derived from the local `STATUS_STATES`, but the component already imports the equivalent global `Status` type via `IStatus`

The component (`bds-status.tsx`) continues to import `PROCESS_STATUS` from `@/types` and `Status` via `IStatus` from `@/types/states`. Neither local file is imported anywhere.

**Fix:** Either delete both files and use the existing global types exclusively, or migrate the component to use the local enum/type and remove the `@/types` dependency. Do not maintain two parallel type systems for the same value set.

---

### Stories section order — ❌

The documented five-section structure requires `export default meta` to appear **after** the `styles` block, not before it. The current file has:

```ts
} satisfies BorealStoryMeta<StoryArgs>;

export default meta;   // ← appears here

const styles = css`...`; // ← styles should precede export default
```

**Required order (docs instructions):** imports → type definitions → meta → styles → `export default meta` → story exports.

---

### `WithIcon` story has `dot: true` — ⚠️ Verify intent

The `WithIcon` story sets `dot: true`, which causes both the dot indicator and the icon to render simultaneously. If the intent is to demonstrate the icon slot in isolation, `dot` should be `false`. Confirm with design whether combining dot + icon in the same story is intentional or a copy-paste error from the `WithDot` stories.

---

### Missing `PendingWithDot` story — ⚠️ Coverage gap

The `.stories.ts` file covers dot variants for `neutral`, `in-progress`, `complete`, and `cancel` but is missing a `PendingWithDot` story. All five state variants have a corresponding base story — the dot variants should match for completeness and Storybook a11y coverage.

---

### Enum-like prop validation pattern — ✅ No issues found

`state` uses the `validatePropValue` + `@Watch('state')` + `componentWillLoad()` pattern correctly.

---

### Event naming semantics — ✅ Not applicable

No `@Event()` declarations in this component.

---

### Boolean prop prefix — ✅ No issues found

`dot` carries no `is`, `has`, or `show` prefix.

---

### `mouseleave` / `stayOnHover` — ✅ Not applicable

---

### Memory topic files consulted

- `stencil-light-dom-host-vs-class.md`
- `project_no_shadow_dom.md`
- `feedback_prop_validation_pattern.md`
- `component-accessor-naming-conventions.md`
- `feedback_event_naming.md`
- `mouseleave-relatedtarget-vs-target.md`

---

**Result: 25 passed · 7 failed** _(2 static · 5 memory/docs-guided)_

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
