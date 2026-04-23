# Boreal DS — Code Review Report

**Generated:** 2026-04-22T13:53:26
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:3`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:4`
- 🟡 **[getter-get-prefix]** Getter accessor has a redundant `get` prefix in its name. The `get` keyword already communicates accessor semantics — rename to the value it returns (e.g. `get placement()` not `get getPlacement()`). `packages/boreal-web-components/src/components/feedback/bds-status/bds-status.tsx:59`
- 🔵 **[missing-stories]** Component TSX files changed but no Storybook stories found in the diff.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - **Standard:** Every component PR must include a corresponding `.stories.ts` file and an `.mdx` documentation file. Both are required before a PR can be merged.
  - **Antipattern:** Shipping a new component without Storybook documentation prevents consumers from discovering its API and violates the Definition of Done.
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
  - **Standard:** Getter accessors must not carry a `get` prefix. Use `classMap`, not `getClassMap`. The `get` keyword already communicates accessor semantics — the redundancy shows up at every call site as `this.getClassMap`.
  - **Antipattern:** `get getClassMap()` — the `get` prefix is redundant and misleading. Rename to `get classMap()` and update the render method to use `this.classMap`.
  - **Reference:** `component-accessor-naming-conventions.md`

## Memory-Guided Review

> _Completed after reading `.claude/memory/MEMORY.md` and the relevant topic files._

### `:host` used in light-DOM SCSS — ❌ Bug

`bds-status.scss` contains:

```scss
:host {
  display: block;
}
```

Boreal DS uses light DOM exclusively (`shadow: true` is never set in `@Component` decorators). Per [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/:host), the `:host` pseudo-class **only works inside a shadow DOM boundary — it has no effect in light DOM**. This rule is silently ignored at runtime, meaning the intended `display: block` is never applied.

**Fix:** Replace `:host { display: block; }` with `bds-status { display: block; }` to follow the verified codebase pattern.

- **Memory reference:** `stencil-light-dom-host-vs-class.md`, `project_no_shadow_dom.md`

---

### Test suite is a placeholder — ❌ Does not meet DoD

The spec file (`__test__/bds-status.spec.tsx`) contains a single test that does not verify any real component behavior:

```tsx
expect(page.root).toEqualHtml(`
  <bds-status>
    <mock:shadow-root>
      <slot></slot>
    </mock:shadow-root>
  </bds-status>
`);
```

This snapshot is wrong on two counts:

1. **Shadow root expectation on a light DOM component.** `bds-status` uses light DOM — there is no shadow root. The `<mock:shadow-root>` wrapper will never appear. The correct snapshot must reflect the `<Host>` output including the class map, `role="status"`, and any rendered children.
2. **Trivial coverage.** None of the following behaviors are exercised:
   - `state` prop validation (valid values, invalid fallback to `"neutral"`)
   - `dot` prop rendering the `.bds-status__dot` element
   - `icon` slot rendering
   - Class map modifiers (e.g. `bds-status--pending`)
   - Initial `componentWillLoad()` validation

The DoD requires ≥ 90% statement coverage. This test file contributes near-zero coverage.

---

### Enum-like prop validation pattern — ✅ No issues found

`state` uses the `validatePropValue` + stacked `@Watch('state')` + `componentWillLoad()` pattern correctly. The single-enum prop only needs one `@Watch` decorator, which is appropriate.

---

### Event naming semantics — ✅ No issues found

No `@Event()` declarations in this component.

---

### Boolean prop prefix — ✅ No issues found

`dot` is a boolean prop. It carries no `is`, `has`, or `show` prefix. Correct.

---

### `mouseleave` / `stayOnHover` — ✅ Not applicable

No overlay or hover-triggered floating behavior in this component.

---

### Memory topic files consulted

- `stencil-light-dom-host-vs-class.md`
- `project_no_shadow_dom.md`
- `feedback_prop_validation_pattern.md`
- `component-accessor-naming-conventions.md`
- `feedback_event_naming.md`
- `mouseleave-relatedtarget-vs-target.md`

---

**Result: 22 passed · 4 failed** _(2 static · 2 memory-guided)_

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
