# Memory Consolidation Audit — 2026-06-10

**Purpose:** Cross-reference all 34 `.agents/memory/*.md` files against the three target guideline files to classify overlap and plan Phase 2 Task 15 promotions.

**Guidelines audited:**

- `ai-docs/guidelines/stencil-best-practices.md`
- `ai-docs/guidelines/stencil-unit-testing-patterns.md`
- `ai-docs/guidelines/development-standards.md`

**Overlap statuses:**

- `duplicate` — content substantially already present in a guideline → action: `delete`
- `partial` — unique content exists; guideline has a related section needing targeted addition → action: `promote then delete`
- `unique` — no guideline home; content absorbed by knowledge skill → action: `keep` (deleted in Task 16 after Phase 3)

---

## Deduplication Map

| Memory file                                          | Overlap   | Action              | Target guideline / section                                                                                                                  | Knowledge skill               |
| ---------------------------------------------------- | --------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `component-accessor-naming-conventions.md`           | partial   | promote then delete | `stencil-best-practices.md` → new §"Accessor and Boolean Expression Conventions"                                                            | `stencil-component-knowledge` |
| `component-bds-typography-group-labels.md`           | unique    | keep                | —                                                                                                                                           | `stencil-component-knowledge` |
| `component-interface-content-rule.md`                | partial   | promote then delete | `development-standards.md` §1.4 → new subsection "Component Interface Contract"                                                   | `stencil-component-knowledge` |
| `component-interface-file-naming.md`                 | partial   | promote then delete | `development-standards.md` §1.2 → naming conventions table                                                                        | `stencil-component-knowledge` |
| `chromatic-deployment.md`                            | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `dom-setattribute-aria-kebab-case.md`                | partial   | promote then delete | `stencil-best-practices.md` → new §"DOM API Gotchas"                                                                                        | `stencil-component-knowledge` |
| `feedback_event_options_explicit.md`                 | duplicate | delete              | `development-standards.md` §1.5 line ~1423 covers bubbles/composed for light DOM                                                  | `stencil-component-knowledge` |
| `feedback_prop_validation_pattern.md`                | duplicate | delete              | `development-standards.md` §1.4 "Property Validation" lines 1089–1140 covers full pattern + utility signature                     | `stencil-component-knowledge` |
| `github-actions-windows-debug-technique.md`          | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `mouseleave-relatedtarget-vs-target.md`              | unique    | keep                | —                                                                                                                                           | `stencil-component-knowledge` |
| `mutation-testing-stryker-setup.md`                  | unique    | keep                | —                                                                                                                                           | `testing-knowledge`           |
| `mutation-testing-workflow-decisions.md`             | unique    | keep                | —                                                                                                                                           | `testing-knowledge`           |
| `nodejs-signal-handler-patterns.md`                  | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `release-it-pnpm-publish.md`                         | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `sass-paths-windows-forward-slash.md`                | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `scripts-boreal-pack-pipeline.md`                    | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `stencil-async-rendering-gotchas.md`                 | partial   | promote then delete | `stencil-best-practices.md` §FACE → add formDisabledCallback trigger condition + HTMLButtonElement naming collision                         | `stencil-component-knowledge` |
| `stencil-child-component-props-in-tests.md`          | partial   | promote then delete | `stencil-unit-testing-patterns.md` → new §"Child Component Prop Assertions"                                                                 | `testing-knowledge`           |
| `stencil-composite-light-dom-event-boundary.md`      | partial   | promote then delete | `stencil-best-practices.md` → new §"Composite Light DOM Event Boundary"                                                                     | `stencil-component-knowledge` |
| `stencil-dist-copy-namespace-behavior.md`            | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `stencil-face-attach-internals.md`                   | partial   | promote then delete | `stencil-best-practices.md` §FACE → expand from pointer to full rule                                                                        | `stencil-component-knowledge` |
| `stencil-face-constraint-validation-pattern.md`      | partial   | promote then delete | `stencil-best-practices.md` §FACE → add constraint validation pattern                                                                       | `stencil-component-knowledge` |
| `stencil-face-element-proxy-limits.md`               | partial   | promote then delete | `stencil-best-practices.md` §FACE → expand from pointer to full rule + @Method() fix                                                        | `stencil-component-knowledge` |
| `stencil-face-test-mocks.md`                         | partial   | promote then delete | `stencil-unit-testing-patterns.md` §"Required spec file boilerplate (FACE components)" → add mock file location + exports                   | `testing-knowledge`           |
| `stencil-form-control-interfaces.md`                 | partial   | promote then delete | `development-standards.md` §1.6 → add componentModels registration requirement                                                    | `stencil-component-knowledge` |
| `stencil-light-dom-host-vs-class.md`                 | partial   | promote then delete | `stencil-best-practices.md` §"Style Encapsulation" → add light DOM `:host` rule                                                             | `stencil-component-knowledge` |
| `stencil-prop-patterns.md`                           | partial   | promote then delete | `development-standards.md` §1.4 → add mutable:true Stencil compiler warning; indexed access type ban; constant reference ban      | `stencil-component-knowledge` |
| `stencil-sass-inject-global-paths-constraint.md`     | partial   | promote then delete | `stencil-best-practices.md` §"Global SCSS Utilities" → add @use constraint rules                                                            | `stencil-component-knowledge` |
| `storybook-action-wiring-web-components.md`          | unique    | keep                | —                                                                                                                                           | `documentation-knowledge`     |
| `storybook-source-snippet-non-primitive-props.md`    | unique    | keep                | —                                                                                                                                           | `documentation-knowledge`     |
| `storybook-vite-quirks.md`                           | unique    | keep                | —                                                                                                                                           | `documentation-knowledge`     |
| `test-spec-file-organisation.md`                     | partial   | promote then delete | `stencil-unit-testing-patterns.md` §"Spec file organisation" → inline the slots.spec creation criteria (currently a pointer back to memory) | `testing-knowledge`           |
| `turbo-persistent-interactive-pty-hang.md`           | unique    | keep                | —                                                                                                                                           | `infra-knowledge`             |
| `typescript-popover-api-declare-global-redundant.md` | unique    | keep                | —                                                                                                                                           | `stencil-component-knowledge` |

---

## Summary

| Action                              | Count | Files                                                                 |
| ----------------------------------- | ----- | --------------------------------------------------------------------- |
| `delete` (duplicate)                | 2     | `feedback_event_options_explicit`, `feedback_prop_validation_pattern` |
| `promote then delete`               | 16    | see table above                                                       |
| `keep` (unique → absorbed by skill) | 16    | see table above                                                       |

---

## Task 15 Work Order

Grouped by target guideline to minimise file round-trips.

### `stencil-best-practices.md` (8 promotions)

1. §Style Encapsulation → add "Light DOM: direct tag selectors, not `:host`" (`stencil-light-dom-host-vs-class.md`)
2. §Global SCSS Utilities → add `@use` constraint rules (`stencil-sass-inject-global-paths-constraint.md`)
3. §FACE Components → expand `@AttachInternals()` pointer to full rule (`stencil-face-attach-internals.md`)
4. §FACE Components → expand element proxy pointer to full rule + `@Method()` fix (`stencil-face-element-proxy-limits.md`)
5. §FACE Components → add constraint validation pattern (`stencil-face-constraint-validation-pattern.md`)
6. §FACE Components → add `formDisabledCallback` trigger condition + naming collision gotcha (`stencil-async-rendering-gotchas.md`)
7. New §"Composite Light DOM Event Boundary" (`stencil-composite-light-dom-event-boundary.md`)
8. New §"DOM API Gotchas" (`dom-setattribute-aria-kebab-case.md`)
9. New §"Accessor and Boolean Expression Conventions" (`component-accessor-naming-conventions.md`)

### `stencil-unit-testing-patterns.md` (3 promotions)

1. §Spec file organisation → inline slots.spec creation criteria; remove memory pointer (`test-spec-file-organisation.md`)
2. §Required spec file boilerplate (FACE) → add mock file location and required exports (`stencil-face-test-mocks.md`)
3. New §"Child Component Prop Assertions" (`stencil-child-component-props-in-tests.md`)

### `development-standards.md` (4 promotions)

1. §1.2 Naming conventions → add `IComponent.ts` vs `IBdsComponent.ts` rule (`component-interface-file-naming.md`)
2. §1.4 Properties → add mutable:true Stencil compiler warning; indexed access type ban; constant reference ban (`stencil-prop-patterns.md`)
3. §1.4 Properties → new subsection "Component Interface Contract" (`component-interface-content-rule.md`)
4. §1.6 Output Targets → add componentModels registration requirement for form controls (`stencil-form-control-interfaces.md`)

---

> **Next step:** Review and approve this map, then proceed with Task 15.
