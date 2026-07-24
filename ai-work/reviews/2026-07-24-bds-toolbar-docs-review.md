# Boreal DS — Code Review Report

**Generated:** 2026-07-24T11:29:50  
**Base ref:** `a0c517c4~1`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[missing-tests]** Component TSX files changed but no test files found in the diff.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ❌ New logic is covered by tests
  - Checklist rule (Universal → Testing and Verification): "New logic is covered by tests appropriate to the package."
  - Automated finding: `bds-toolbar.tsx` (arrow-function-to-method-syntax refactor on `containerClass`) and `bds-drawer-header.tsx` (1-line change) are touched in this diff slice with no corresponding spec file changes. Per `common_antipatterns.md` § "Rendering and Testing Antipatterns," untested component-code edits risk silent regressions. In this case the risk is low — the `bds-toolbar.tsx` change is a pure syntax refactor (arrow property → class method, same return value) already exercised by the existing `bds-toolbar.a11y/basics/variants.spec.ts` suite — but the automated rule cannot distinguish a behavior-preserving refactor from a real logic change, so it correctly flags for human confirmation.
- ❌ Storybook/MDX/README updated when behavior or APIs change
  - **False positive** — the script maps both `missing-stories` and `missing-changeset` findings to this same checklist row (`review_report_generator.py:97-98`). Only `missing-changeset` fired here; no `missing-stories` finding exists. This diff adds 413 lines of MDX and 729 lines of stories for `bds-toolbar` — docs were unambiguously updated. The ❌ is a tool limitation (over-broad rule-to-checklist mapping), not a real gap. See "Changelog or release note impact" below for the one legitimate open item this row is conflating.
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
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

Read `.claude/memory/MEMORY.md` and evaluated every topic file for applicability to the changed files (`bds-toolbar.mdx`, `bds-toolbar.stories.ts`, `bds-toolbar.tsx`, `IToolbar.ts`).

### Storybook action wiring (`storybook-action-wiring-web-components.md`)

No issues found. `bds-toolbar` and `bds-toolbar-item` emit no custom events, so the four-level action-wiring pattern (type declaration, argTypes, args, template binding) does not apply to this story set — nothing to wire.

### Storybook source snippet override for non-primitive props (`storybook-source-snippet-non-primitive-props.md`)

No issues found. `bds-toolbar.stories.ts` uses only attribute bindings (`align="${args.align}"`, `gap="${args.gap}"`, etc.) for primitive string/boolean props — no `.prop=${...}` Lit property bindings on arrays or objects appear anywhere in the file, so the "Show code" snippet override is not required here.

### Mouseleave relatedTarget vs. target (`mouseleave-relatedtarget-vs-target.md`)

Not applicable — `bds-toolbar` has no `mouseleave` handler or hover-based floating behavior.

### Popover API dead `declare global` blocks (`typescript-popover-api-declare-global-redundant.md`)

Not applicable — no Popover API usage in the changed files. Also independently confirmed clean by the automated `declare-global-popover` rule (section A checklist, ✅).

### Group-label typography pattern (`component-bds-typography-group-labels.md`)

Not applicable — `bds-toolbar` is a layout primitive with no `label`/`helperText` group-rendering responsibility (its `label` prop only sets `aria-label`, not a rendered typography element).

### Cross-reference: prior subagent-validated review

This session already ran an independent manual review of `bds-toolbar.mdx`/`bds-toolbar.stories.ts`, cross-validated in parallel by the frontend-subagent, testing-subagent, and documentation-subagent. That pass found defects this script's static rules cannot detect (they operate on `.tsx`/`.ts` syntax patterns, not documentation content or cross-file ARIA-forwarding behavior):

1. **High** — `aria-pressed` set on `<bds-button>` in the `TextFormattingBar`/`RichContentEditorToolbar` stories is never forwarded to the inner native `<button>` by `bds-button.tsx`'s `render()` — the ARIA APG toggle-button pattern the docs present is inert for screen readers. (Confirmed independently by two subagents; `bds-card.tsx` already implements the correct `inheritAttributes(this.el, ['aria-pressed'])` pattern that `bds-button` lacks.)
2. **High** — The `label` prop (`bds-toolbar.tsx:70`, used in 7+ stories and discussed in the MDX Accessibility section) has no `argTypes` entry in `bds-toolbar.stories.ts`, so it is silently absent from the auto-generated Properties table.
3. **Medium** — Orphaned dead JSDoc comment at `bds-toolbar.stories.ts:327-330` describing a non-existent "Editor toolbar" story (confirmed via `git blame` as refactor debris from commit `a0c517c4`).
4. **Medium** — Story declaration order in `bds-toolbar.stories.ts` doesn't track the MDX's narrative walkthrough, splitting the Positioning section into three separate clusters in the file.
5. **Low** — Unused imports: `nothing` (from `lit`) and `LinkTo` (from `@storybook/addon-links/react`).
6. **Low** — The MDX's "unpredictable results" wording for combining `sticky`+`fixed` or `align`+sub-components overstates what is actually deterministic (if undesirable) CSS-cascade behavior.
7. **Test-coverage gap** — The MDX's full roving-tabindex keyboard model (Tab/Arrow/Home/End/Enter/Space) has zero test coverage at the `bds-toolbar` level; only the generic shared `KeyboardController` utility is tested against a plain div/button fixture, not `bds-toolbar` itself.

### Memory topic files consulted

- `storybook-action-wiring-web-components.md`
- `storybook-source-snippet-non-primitive-props.md`
- `mouseleave-relatedtarget-vs-target.md`
- `typescript-popover-api-declare-global-redundant.md`
- `component-bds-typography-group-labels.md`

---

**Result: 25 passed · 2 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_