# Boreal DS — Code Review Report

**Generated:** 2026-04-22T16:37:00
**Base ref:** `release/current`
**Repository:** `.`
**Scope note:** Testing, documentation, and styling are explicitly out of scope for this review pass.

## Affected Packages

- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

> ⚠️ **Scanner false positive note:** The two `[event-name-format]` errors reporting `readonly` as the event name are false positives. The regex extracted the `readonly` modifier on `@Event({ ... }) readonly bds…` lines instead of the actual event name. The real events are `bdsListChange` and `bdsListMenuItemClick` — see the Memory-Guided Review for the real naming analysis on those.

- 🔴 **[event-name-format] FALSE POSITIVE** — Scanner misread `readonly` keyword as event name. Actual event `bdsListChange` is `bds{Action}` compliant, but see Memory-Guided Review for a real naming issue. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-host/bds-list-menu-host.tsx:41`
- 🟡 **[class-jsdoc-invalid-tags]** Component class JSDoc uses `@element` or `@method` tags — ignored by the CEM analyzer. Use method-level JSDoc instead. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-host/bds-list-menu-host.tsx`
  - **Standard:** Do not place `@element` or `@method` in a component class JSDoc. These tags are ignored by the CEM analyzer and give a false sense of documentation. Move `@method` documentation to the `@Method()` member directly.
  - **Antipattern:** `@element` and `@method` in class JSDoc creates invisible dead documentation — CEM never reads it, so the output JSON omits these details entirely.
- 🔴 **[prop-missing-jsdoc] LIKELY FALSE POSITIVE** — All `@Prop()` declarations in the file carry JSDoc blocks. This may be a line-counting artifact from the `@Element()` JSDoc at a nearby line. Verify manually: every `@Prop()` must have a `/** … */` block immediately above it with no blank line in between. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:64`
  - **Standard:** Every `@Prop()` must be `readonly` and have a JSDoc block directly above it — required for `custom-elements.json` generation accuracy.
  - **Antipattern:** Missing JSDoc on `@Prop()` silently degrades `custom-elements.json` output and breaks wrapper generation for React and Vue.
- 🔴 **[event-name-format] FALSE POSITIVE** — Scanner misread `readonly` keyword as event name. Actual event `bdsListMenuItemClick` embeds the component noun `ListMenuItem` — see Memory-Guided Review for the real violation. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:97`
- 🟡 **[import-order]** `@/types` appears before `@/mixins` (line 3 — internal alias order must be: `@/services → @/mixins → @/utils`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:3`
  - **Standard:** Internal aliases must follow `@/services → @/mixins → @/utils` layering. Dependencies flow downward — each group only imports from groups above it.
  - **Antipattern:** Mixing import groups makes it impossible to read coupling direction from the file header.
- 🟡 **[import-order]** `@/utils/helpers/validateProps` appears before `@/mixins` (line 4 — `@/utils` must come after `@/mixins`). `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:4`
- 🟡 **[import-order]** `@/utils` (KEYBOARD) appears on line 9 after local/relative imports — all internal aliases must come before local imports. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:9`
- 🟡 **[getter-get-prefix]** `get getClassMap()` — the `get` keyword already communicates accessor semantics; rename to `get classMap()`. `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu-item/bds-list-menu-item.tsx:145`
  - **Standard:** Getter accessors must not carry a `get` prefix. Use `classMap`, not `getClassMap`; `linkAttributes`, not `getLinkAttributes`.
  - **Antipattern:** `get getClassMap()` is a redundant double-`get` — callers read `this.getClassMap` which looks like a method call, not a property access, misleading readers about whether it has side effects.
- 🟡 **[barrel-wildcard-export]** `export * from '...'` in `mixins/index.ts` (6 entries), `types/index.ts` (7 entries), `utils/index.ts` (7 entries), `utils/menu/index.ts` (1 entry) — pre-existing across the package, not introduced in this branch.
  - **Standard:** Use named re-exports (`export { X } from './X'`) to keep module edges visible to the bundler and enable tree-shaking.
  - **Antipattern:** Wildcard re-exports prevent Rollup from eliminating unused exports and can force the entire module graph into the consumer bundle.
- 🟡 **[import-order]** `links.mixin.ts` and `menu-behavior.mixin.ts` also have import order violations — pre-existing in the mixins.
- ~~🟡 **[missing-tests]**~~ — _Out of scope for this review pass (testing WIP)._
- ~~🔵 **[missing-stories]**~~ — _Out of scope for this review pass (docs WIP)._
- ~~🔵 **[missing-changeset]**~~ — _Out of scope for this review pass._

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ~~❌ New logic is covered by tests~~ — _Out of scope_
- ✅ Tests use `waitForChanges()` before DOM assertions
- ~~❌ Storybook/MDX/README updated when behavior or APIs change~~ — _Out of scope_
- ❌ Public APIs, events, and props follow naming conventions
  - `bdsListMenuItemClick` embeds the component noun — see Memory-Guided Review.
  - `get getClassMap()` and `get getLinkAttributes()` carry redundant `get` prefixes.

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
  - **Standard:** Every `@Prop()` must be `readonly` and carry a JSDoc block immediately above it (no blank line separator).
  - **Antipattern:** Missing JSDoc breaks `custom-elements.json` prop entries and degrades React/Vue wrapper output.
- ✅ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ❌ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
  - `bds-list-menu-item` has `@Watch('variant')` calling `validatePropValue` but **no `componentWillLoad()` invocation**. Initial attribute values set via HTML markup are never validated. See Memory-Guided Review.
  - **Standard:** All three parts are required together — `@Watch` alone only fires on runtime changes after mount.
  - **Antipattern:** Omitting `componentWillLoad()` silently accepts invalid initial prop values and passes them to the render cycle.
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - `bdsListMenuItemClick` embeds the component noun `ListMenuItem`. Must be `bdsClick` or a better action verb (e.g. `bdsSelect`). See Memory-Guided Review.
  - **Standard:** Event names follow `bds{Action}` — no component noun in the middle. `bdsClose`, not `bdsBannerClose`.
  - **Antipattern:** Embedding the component name creates collisions and verbosity in framework bindings (`onBdsListMenuItemClick` vs `onBdsClick`).
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ✅ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
- ❌ JSDoc changes preserve custom-elements.json generation accuracy
  - The class-level JSDoc in both components uses `@attr`, `@property`, and `@method` tags that duplicate prop-level JSDoc and are not read by the CEM analyzer — this creates divergent documentation.
  - **Standard:** Class-level JSDoc should carry `@summary`, `@slot`, and `@event` tags only. Prop documentation lives on the `@Prop()` member JSDoc.
  - **Antipattern:** `@method` in class JSDoc is silently ignored by the CEM, so method descriptions never appear in `custom-elements.json`.
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ❌ Getter accessors carry no redundant `get` prefix
  - `get getClassMap()` in `bds-list-menu-item.tsx` → rename to `get classMap()`.
  - `get getLinkAttributes()` in `links.mixin.ts` → rename to `get linkAttributes()`.
  - **Standard:** Use `classMap`, not `getClassMap`; `linkAttributes`, not `getLinkAttributes`.
  - **Antipattern:** `get getX()` is doubly redundant — the `get` keyword already marks it as an accessor.

## Memory-Guided Review

### 1. Event naming — `bdsListMenuItemClick` embeds a component noun

**Topic file:** `feedback_event_naming.md`
**Verdict:** ❌ Violation found

`bdsListMenuItemClick` embeds the component noun `ListMenuItem` in the middle of the name. The convention (`bds{Action}`) forbids this. All events must express only the action, not the source component.

| Current                | Required                  | Framework binding (current) | Framework binding (fixed)    |
| ---------------------- | ------------------------- | --------------------------- | ---------------------------- |
| `bdsListMenuItemClick` | `bdsClick` or `bdsSelect` | `onBdsListMenuItemClick`    | `onBdsClick` / `onBdsSelect` |

`bdsListChange` in `bds-list-menu-host` is compliant — `List` here is the action domain, not the component name. No change needed there.

---

### 2. `componentWillLoad()` missing from `bds-list-menu-item`

**Topic file:** `feedback_prop_validation_pattern.md`
**Verdict:** ❌ Real bug — not caught by automated checker

The component uses `@Watch('variant')` → `validatePropValue(...)` but has **no `componentWillLoad()` that calls `checkPropsVariant()`**. `@Watch` only fires on prop changes that occur after the component mounts. An invalid `variant` value set via an HTML attribute (e.g. `<bds-list-menu-item variant="invalid">`) will pass through silently on first render and never be reset to the fallback.

Required fix:

```tsx
componentWillLoad(): void {
  this.checkPropsVariant();
}
```

---

### 3. Explicit `@Event()` options violate the bare-decorator convention

**Topic file:** `feedback_event_options_explicit.md`
**Verdict:** ❌ Convention violation

Both `bds-list-menu-host` and `bds-list-menu-item` use `@Event({ bubbles: true, composed: true })`. The project convention is bare `@Event()` with no options. `composed` is irrelevant in light DOM; `bubbles` is only needed for event delegation, which Boreal DS does not use.

```tsx
// Current — wrong
@Event({ bubbles: true, composed: true }) readonly bdsListMenuItemClick!: EventEmitter<IListMenuItemEvent>;

// Required — correct
@Event() readonly bdsListMenuItemClick!: EventEmitter<IListMenuItemEvent>;
```

---

### 4. Light DOM — no violations

**Topic file:** `project_no_shadow_dom.md`
No `shadow: true` or `::part()` usage detected. Both components correctly use light DOM.

---

### 5. `mouseleave` handler — not applicable

**Topic file:** `mouseleave-relatedtarget-vs-target.md`
No `mouseleave` event handling in this component set. No issues.

---

### 6. Enum-like prop validation pattern — partial pass

**Topic file:** `feedback_prop_validation_pattern.md`
The automated checker passed this item (it detected `validatePropValue` + `@Watch`), but as noted above in finding #2, `componentWillLoad()` is absent. This is a false ✅ from the script — the manual review overrides it to ❌.

---

### Memory topic files consulted

- `feedback_event_naming.md`
- `feedback_prop_validation_pattern.md`
- `feedback_event_options_explicit.md`
- `project_no_shadow_dom.md`
- `component-accessor-naming-conventions.md`

---

## Summary of Required Changes

| #   | Severity      | File                                                | Fix                                                                                                     |
| --- | ------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1   | 🔴 Must fix   | `bds-list-menu-item.tsx`                            | Rename `bdsListMenuItemClick` → `bdsClick` (or `bdsSelect`)                                             |
| 2   | 🔴 Must fix   | `bds-list-menu-item.tsx`                            | Add `componentWillLoad()` that calls `this.checkPropsVariant()`                                         |
| 3   | 🔴 Must fix   | `bds-list-menu-item.tsx` & `bds-list-menu-host.tsx` | Remove explicit `{ bubbles: true, composed: true }` from `@Event()`                                     |
| 4   | 🟡 Should fix | `bds-list-menu-item.tsx`                            | Fix import order: `@/mixins` → `@/utils` → local; move `KEYBOARD` import before local imports           |
| 5   | 🟡 Should fix | `bds-list-menu-item.tsx`                            | Rename `get getClassMap()` → `get classMap()`                                                           |
| 6   | 🟡 Should fix | `links.mixin.ts`                                    | Rename `get getLinkAttributes()` → `get linkAttributes()`                                               |
| 7   | 🟡 Should fix | `bds-list-menu-host.tsx`                            | Remove `@method` from class-level JSDoc; move to method-level JSDoc                                     |
| 8   | 🟡 Verify     | `bds-list-menu-item.tsx`                            | Confirm `prop-missing-jsdoc` at line 64 is a false positive — no blank line between JSDoc and `@Prop()` |

---

**Result: 15 passed · 6 failed (2 scanner false positives; 4 real failures; testing/docs/styling out of scope)**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py) — enriched manually_
