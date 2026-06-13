# Memory Consolidation Audit — 2026-05-19

**Plan reference:** `ai-work/plans/ai-scaffold-restructure.md` — Task 14

**Scope:** Classify all 35 `.agents/memory/*.md` topic files against the three guideline files, identify inaccuracies in both memory and guideline content (codebase verified), and flag which sections of `development-standards.md` contain unique content not yet in other canonical files.

> **Constraint:** `development-standards.md` is frozen until Confluence is updated. It may contain inaccurate content — do not treat it as a source of truth in either direction.

---

## Part 1 — Guideline File Accuracy (codebase-verified)

Before any promotion, these inaccuracies must be fixed first.

### `ai-docs/guidelines/stencil-best-practices.md`

| Section | Inaccuracy | Evidence | Fix needed |
|---------|-----------|----------|------------|
| "FACE Components: `formAssociated: true` with `scoped: true`" | States `scoped: true` is "the canonical pattern" for all FACE components. **Codebase has NO `scoped: true` anywhere.** | `grep -rn "scoped: true" src/components` returns no results; all 6 FACE components use bare `@Component` with no encapsulation option | Replace `scoped: true` recommendation with verified pattern (bare light DOM, as in `project_no_shadow_dom.md`) |

### `ai-docs/guidelines/development-standards.md` (frozen)

| Section | Status | Notes |
|---------|--------|-------|
| §1.1 Component Architecture & Inheritance | **INACCURATE** | Describes aspirational "Base Layer / Form Layer / Selectable Layer" inheritance model. The actual pattern is `extends Mixin(formAssociatedMixin)` / `extends Mixin(anchoredMixin)` etc. No base layer classes exist. Do NOT promote to other files. |
| §1.2 Component Naming Conventions | PARTIALLY ACCURATE | Boolean prop rules ✅ (verified). Event naming ✅ (verified). Code examples have generic naming (`my-change`, `my-button`) and don't use `bds` prefix — illustrative only, not templates. |
| §1.3 Component Code Organization | UNVERIFIED | The 15-section member ordering exists as a pattern but was never verified against the codebase systematically. Section comments using `=====` dividers are NOT used in actual components. |
| §1.4 Properties & Attributes | PARTIALLY ACCURATE | Prop reflection strategy ✅. `validatePropValue` pattern ✅. `@Watch` + `componentWillLoad` ✅. |
| §1.5 Custom Events | ACCURATE (post-fix) | Event naming ✅. Bubbling/composition now correct after today's fix. `valueChange` for v-model ✅. |
| §1.6 Output Targets | ACCURATE | New section, verified against `vue-output-target.ts`. |
| §2 Linting | ACCURATE (post-fix) | Verified against `eslint.config.ts`. |
| §3 TypeScript | ACCURATE (post-fix) | Verified against `tsconfig.json`. |
| §4 Testing | PARTIALLY ACCURATE | AAA pattern ✅. Unit test boilerplate ✅. `shadowRoot.querySelector` fixed ✅. Storybook/Chromatic sections are aspirational/untested. |
| §5 Documentation | UNVERIFIED | Storybook story structure is detailed but not systematically verified against `apps/boreal-docs`. |
| §6–8 Git/PR/CI | ACCURATE | Populated from Confluence; matches team workflow. |

---

## Part 2 — Memory File Classification

### Column definitions
- **Overlap status:** `duplicate` = fully covered in a guideline; `partial` = some content covered, some unique; `unique` = not covered anywhere
- **Action:** `delete` = covered by guidelines; `promote → delete` = move unique parts to guideline first, then delete; `keep` = no guideline covers this

| Memory file | Overlaps with | Overlap status | Action | Notes |
|-------------|--------------|---------------|--------|-------|
| `stencil-face-attach-internals.md` | `stencil-best-practices.md` (FACE section, line 290 — rule mentioned) | partial | **keep** | SBP only states the rule. Memory has the full failure mode: `this.internals === undefined` at runtime, silent TypeScript pass. Valuable detail not in SBP. |
| `stencil-face-element-proxy-limits.md` | — | unique | **keep** | `@Method()` wrapper pattern for `checkValidity`/`reportValidity`. Not covered anywhere else. |
| `stencil-face-constraint-validation-pattern.md` | — | unique | **keep** | Doubled validation events, `tabIndex`, `onFocus` delegation. Not covered anywhere. |
| `stencil-async-rendering-gotchas.md` | — | unique | **keep** | Async DOM reflection, `formDisabledCallback` trigger conditions, `HTMLButtonElement.prototype.checkValidity` naming collision, `page.setContent()` test pattern. Not covered anywhere. |
| `stencil-face-test-mocks.md` | `stencil-unit-testing-patterns.md` (FACE boilerplate section) | partial | **keep** | SUTP has the import boilerplate. Memory adds: mock file location (`src/utils/testing/mocks/`), `attachInternals()` + `suppressConsoleError()` API, why `?.` can't prevent mock-doc `console.error`. Distinct enough to keep. |
| `stencil-child-component-props-in-tests.md` | — | unique | **keep** | JSX props as JS properties vs HTML attributes in `newSpecPage`. Not covered anywhere. |
| `stencil-prop-patterns.md` | `stencil-best-practices.md` (`@Prop()` section covers type inference and defaults) | partial | **keep** | SBP covers prop defaults and naming. Memory adds: ESLint enforcement (`stencil/props-must-be-readonly` and `stencil/required-jsdoc` are errors, not warnings), `disabled` @State mirror pattern, `instanceof Element` TypeScript narrowing, `@internal` class-level JSDoc exclusion from CEM. All distinct from SBP. |
| `feedback_prop_validation_pattern.md` | — | unique | **keep** | `validatePropValue` + `componentWillLoad()` + stacked `@Watch()`. Not in SBP. |
| `component-interface-file-naming.md` | — | unique | **keep** | `IComponent.ts` not `IBdsComponent.ts`. Not in SBP. |
| `component-interface-content-rule.md` | — | unique | **keep** | Interface contains only consumer-settable `@Prop()` — no `@Event()`, no group props, no `@State()` mirrors. Not covered anywhere. |
| `component-accessor-naming-conventions.md` | — | unique | **keep** | No `get` prefix on getters; `!x \|\| false` is always `!x`. Not covered anywhere. |
| `feedback_event_naming.md` | `stencil-best-practices.md` ("Custom event naming" section — covers the `bds{Action}` rule) | partial | **promote → delete** | SBP covers the rule. Memory adds the failure modes for native event names (type contract, duplicate dispatch, framework binding conflicts). Promote failure modes into SBP's event naming section, then delete. |
| `feedback_event_options_explicit.md` | `stencil-best-practices.md` (Bubbling & Composition section — now in guidelines after today's update) | partial | **keep** | SBP now has the rule and rationale. Memory adds: BEEQ/Aqua DS reference counts (88/80 bare `@Event()`), ADR 0003 pointer. Retaining as supporting reference with ADR link. |
| `component-bds-typography-group-labels.md` | — | unique | **keep** | Group components render `label` via `<bds-typography variant="label">` and `helperText` via `<bds-typography variant="helper">`. Pattern-specific, not in SBP. |
| **`stencil-vdom-listener-pattern.md`** | `stencil-best-practices.md` ("Event Listener Placement" section — full decision table, vDOM pattern, `@Listen` usage, `addEventListener` warning) | **duplicate** | **delete** | SBP is more complete. Memory adds nothing beyond what SBP already covers. |
| **`scss-global-injected-utilities.md`** | `stencil-best-practices.md` ("Global SCSS Utilities" section — `_commons.scss`, `_interactions.scss`, full symbol table, examples) | **duplicate** | **delete** | SBP is more complete and includes the hover block consolidation pattern. Memory adds nothing. |
| `project_no_shadow_dom.md` | `stencil-best-practices.md` (encapsulation table covers `shadow: true` / `scoped: true` / neither) | partial | **promote → delete** | Memory is the **correction** to SBP's erroneous `scoped: true` prescription. It also lists light DOM implications (`composed` irrelevant, `:host` doesn't work, BEEQ adapation note). Promote corrections into SBP FACE section (fix the `scoped: true` error), then delete memory file. |
| `stencil-light-dom-host-vs-class.md` | `stencil-best-practices.md` (table row: `querySelector` works in scoped/neither) | partial | **keep** | Memory is more explicit: `:host` requires shadow boundary (MDN citation), correct pattern is direct tag selector (`bds-button { ... }`). SBP table entry is implicit. Distinct enough to keep. |
| `stencil-form-control-interfaces.md` | — | unique | **keep** | `IFormControl<T>` composite interface, `IFormAssociatedCallbacks`, `IFormValueEmitter<T>`, `componentModels` three-field config. Not covered anywhere. |
| `stencil-dist-copy-namespace-behavior.md` | — | unique | **keep** | Stencil namespace subfolder placement, `postbuild.js` promotion step. Infrastructure-specific. |
| `dom-setattribute-aria-kebab-case.md` | — | unique | **keep** | `setAttribute` requires kebab-case ARIA. Not covered anywhere. |
| `mouseleave-relatedtarget-vs-target.md` | — | unique | **keep** | `e.relatedTarget` vs `e.target` in `mouseleave`. Unfixed bug in `bds-tooltip`. Not covered anywhere. |
| `typescript-popover-api-declare-global-redundant.md` | — | unique | **keep** | `declare global` Popover API dead code since TS 5.2. Not covered anywhere. |
| `turbo-persistent-interactive-pty-hang.md` | — | unique | **keep** | `persistent: true` PTY deadlock. Infrastructure-specific. |
| `sass-paths-windows-forward-slash.md` | — | unique | **keep** | Sass backslash path issue. Windows/CI-specific. |
| `github-actions-windows-debug-technique.md` | — | unique | **keep** | `workflow_dispatch` debug pattern. CI-specific. |
| `nodejs-signal-handler-patterns.md` | — | unique | **keep** | `spawnSync` for SIGINT/SIGTERM cleanup. Script-specific. |
| **`stencil-unit-testing-root-pattern.md`** | `stencil-unit-testing-patterns.md` ("Root element access", "Querying child elements", "QuerySelectorAll", "assertExists usage") | **duplicate** | **delete** | SUTP is the canonical reference. Every pattern in this memory file is already in SUTP with examples. |
| `test-spec-file-organisation.md` | — | unique | **keep** | Five spec file types (`a11y`, `basics`, `variants`, `events`, `slots`), criteria for `slots.spec.ts`. Not in SUTP. |
| `mutation-testing-stryker-setup.md` | — | unique | **keep** | Stryker constraints and test patterns. Tooling-specific. |
| `mutation-testing-workflow-decisions.md` | — | unique | **keep** | Local-only strategy, per-component config, 100% score bar. Tooling-specific. |
| `scripts-boreal-pack-pipeline.md` | — | unique | **keep** | `publish.js` + Turborepo `dependsOn` pipeline. Infrastructure-specific. |
| `release-it-pnpm-publish.md` | — | unique | **keep** | `publishCommand` silently ignored, correct `publishPackageManager` field. Release-specific. |
| `chromatic-deployment.md` | — | unique | **keep** | pnpm `.env` loading, Turborepo output caching, two-actor model. Deployment-specific. |
| `storybook-vite-quirks.md` | — | unique | **keep** | Vite glob export limitation, esm-es5 warning suppression. Dev-tooling-specific. |

---

## Part 3 — Summary of Actions

### Delete (Task 16)

| File | Reason |
|------|--------|
| `stencil-vdom-listener-pattern.md` | Fully covered by `stencil-best-practices.md` |
| `scss-global-injected-utilities.md` | Fully covered by `stencil-best-practices.md` |
| `stencil-unit-testing-root-pattern.md` | Fully covered by `stencil-unit-testing-patterns.md` |

### Promote then delete (Task 15 → Task 16)

| File | Promote to | What to promote |
|------|-----------|----------------|
| `feedback_event_naming.md` | `stencil-best-practices.md` | Three failure modes for native event names (type contract, duplicate dispatch, framework binding conflict) |
| `project_no_shadow_dom.md` | `stencil-best-practices.md` | (1) Fix the FACE section — remove `scoped: true` prescription, replace with bare light DOM; (2) Add light DOM implications list: `composed` irrelevant, `:host` doesn't work, BEEQ adaptation note |

### Keep (no action)

All other 30 files — their content is unique or provides meaningful depth beyond what the guidelines cover.

---

## Part 4 — `stencil-best-practices.md` Corrections Required Before Task 15

Before promoting anything INTO `stencil-best-practices.md`, these errors in that file must be fixed:

1. **FACE section prescribes `scoped: true`** — codebase uses bare light DOM for all FACE components. The entire `scoped: true` code block in the FACE section is wrong. Replace with verified bare pattern (no `shadow`, no `scoped`).

2. **"When to use `scoped: true`" section** — describes a valid architectural choice but the bullet "For all form-associated components" is not the current practice. Soften to "when full stylesheet isolation is needed and shadow DOM is not appropriate" rather than coupling to FACE.

These corrections are a prerequisite for Task 15 — fixing these first ensures promoted content lands in accurate context.

---

## Part 5 — Unique Content in `development-standards.md` Not Covered Elsewhere

These sections contain verified content that does not exist in memory files or other guideline files. They should be promoted to the correct canonical location in Task 15, **only after codebase verification**:

| Section | Verified? | Promote to | Notes |
|---------|-----------|------------|-------|
| §1.3 Member Ordering (15-section standard) | ✅ | `stencil-best-practices.md` | Promote the ordering standard itself. Exclude the `// ===...===` section divider comments from the code example — they are not used in actual components and should not be prescribed. |
| §1.4 `validatePropValue` pattern details | ✅ | Already in `feedback_prop_validation_pattern.md` | No promotion needed |
| §4.1 AAA test pattern | ✅ | `stencil-unit-testing-patterns.md` | Not currently in SUTP; add as a section |
| §4.2 Unit test structure (describe/it, beforeAll, etc.) | ✅ | `stencil-unit-testing-patterns.md` | Partial overlap; supplement SUTP |
| §5 Storybook story structure + MDX patterns | ✅ VERIFIED | `ai-docs/guidelines/storybook-patterns.md` | Created 2026-05-19. Verified against `bds-button`, `bds-text-field`, `bds-banner` stories. Corrected wrong type names, import paths, and file extension from frozen guidelines. |

---

*Status: ready for user review. No files were modified during this audit.*
