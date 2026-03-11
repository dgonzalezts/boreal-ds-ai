---
name: plan-frontend-ticket
description: Use this prompt when you have a ticket (Jira or local file) describing a new Boreal DS component or change and you need a ready-to-implement step-by-step frontend plan. Invoke it before touching any code.
---

# Role

You are an expert design system engineer with deep knowledge of Stencil web components, multi-brand theming, SCSS design tokens, Storybook, and the Boreal DS monorepo conventions.

# Ticket ID

$ARGUMENTS

# Goal

Produce a step-by-step implementation plan for the Boreal DS frontend work described in the ticket, covering the full component SDLC: scaffold, props API, SCSS/tokens, unit tests, Storybook stories, MDX documentation, and release preparation.

# Process and Rules

1. Adopt the role defined in `.github/agents/frontend-developer.agent.md`.
2. Analyse the ticket referenced in `$ARGUMENTS`. If the argument is a local file path, read it directly without using an MCP tool.
3. Research the existing codebase to understand the relevant component category, existing patterns, token usage, and test conventions before writing any plan.
4. Apply the best practices from `.github/instructions/base.instructions.md` and `.github/copilot-instructions.md` to ensure the developer can implement the ticket end-to-end autonomously.
5. Do **not** write implementation code — produce only the structured plan in the output format below.
6. If asked to start implementing at any point, ensure the first action is switching to a branch named after the ticket ID (see Step 0 below).

# Output Format

Markdown document saved at `.ai/plans/{ticket-id}-{component_name}.md` following the template below.

The file **must** begin with this frontmatter block before any other content:

```yaml
---
status: pending
---
```

After saving the plan, add a row for it in `.ai/plans/INDEX.md` under the **Pending** section (filename link + one-line description).

---

## Frontend Implementation Plan Template

### 1. Header

```
# Frontend Implementation Plan: [TICKET-ID] [Component/Feature Name]
```

### 2. Overview

Brief description of the component or change and which Boreal DS architectural principles apply (design token system, Stencil shadow DOM, multi-brand theming, two-type documentation pattern).

### 3. Architecture Context

- **Component category**: which sub-folder under `packages/boreal-web-components/src/components/` (e.g. `actions/`, `feedback/`, `display/`)
- **Tag name**: `bds-[name]` in `kebab-case`
- **Affected packages**: list of publishable packages touched (e.g. `boreal-web-components`, `boreal-react`, `boreal-vue`)
- **Storybook story path**: `apps/boreal-docs/src/stories/[category]/`
- **Token layer**: which Usage/Semantic tokens are applicable
- **Brand themes**: confirm all four themes are covered (proximus, masiv, telesign, bics)

### 4. Implementation Steps

#### Step 0: Create Feature Branch

- **Action**: Create and switch to a new feature branch. Verify the branch does not already exist.
- **Branch naming**: `feat/br-[component-name]` (never reuse a general ticket branch for component work)
- **Implementation Steps**:
  1. Ensure you are on the latest `release/current`: `git checkout release/current && git pull origin release/current`
  2. Create the branch: `git checkout -b feat/br-[component-name]`
  3. Verify: `git branch`
- **Notes**: This must be the **first** step before any file changes. Refer to `.github/instructions/workflow.instructions.md` §7 for the branch strategy.

#### Step 1: Scaffold the Component

- **File**: `packages/boreal-web-components/src/components/[category]/bds-[name]/`
- **Action**: Run `pnpm generate:component` from `packages/boreal-web-components` and confirm the generated file set.
- **Generated files**: `bds-[name].tsx`, `bds-[name].scss`, `test/bds-[name].spec.ts`
- **Implementation Steps**: numbered list of what to verify/adjust after generation
- **Notes**: The `@Component` decorator must set `styleUrl`.

#### Step 2: Define the Public API

- **File**: `bds-[name].tsx`
- **Action**: Declare all `@Prop()`, `@Event()`, `@Method()`, and `@Slot()` members
- **Implementation Steps**:
  1. Export all custom union types at the top of the file
  2. Add a JSDoc block to every `@Prop()` with type, default value, and description
  3. Set `bubbles: true, composed: true` on every `@Event()`
  4. Define the `render()` method with slot placeholders
- **Notes**: No `any` types. Prefer explicit union types over `string`.

#### Step 3: Implement SCSS Styles

- **File**: `bds-[name].scss`
- **Action**: Style the component using design tokens exclusively
- **Implementation Steps**:
  1. Import `@use '@telesign/boreal-style-guidelines/stencil' as tokens;`
  2. Map each visual property to the correct Usage/Semantic token variable
  3. Implement BEM class structure (`.bds-[name]`, `.bds-[name]--[modifier]`, `.bds-[name]__[element]`)
  4. Verify all four brand themes render correctly via `data-theme`
- **Notes**: Never hard-code hex values, spacing, or radius. Run `pnpm validate` in `boreal-styleguidelines` to verify token names.

#### Step 4: Write Unit Tests

- **File**: `test/bds-[name].spec.ts`
- **Action**: Cover every prop, event, slot, ARIA attribute, and edge case
- **Implementation Steps**:
  1. Import `newSpecPage` from `@stencil/core/testing`
  2. One `describe` block, one `it` per behaviour
  3. Test each `@Prop()` effect on rendered HTML
  4. Test `@Event()` emissions with `jest.fn()` listeners
  5. Test slot rendering and disabled/error states
  6. Run `pnpm test:spec` in `boreal-web-components` and confirm ≥ 90% coverage
- **Notes**: Test descriptions must read as specifications (e.g. `"renders as disabled when the disabled prop is true"`).

#### Step 5: Generate and Complete Storybook Stories

- **File**: `apps/boreal-docs/src/stories/[category]/bds-[name].stories.ts`
- **Action**: Generate via `pnpm generate:story` then complete all TODOs
- **Implementation Steps**:
  1. Run `pnpm generate:story` from `apps/boreal-docs`
  2. Define `StoryArgs` interface and `BorealStoryMeta` with `satisfies`
  3. Implement the shared `render[ComponentName]` function using Lit `html` tagged template
  4. Add `Default` story plus named variant stories for every significant state
  5. Use `.property=${value}` for property bindings and `?attribute=${bool}` for booleans
- **Notes**: Every story must pass the Storybook a11y addon checks.

#### Step 6: Write MDX Documentation

- **File**: `apps/boreal-docs/src/stories/[category]/bds-[name].mdx`
- **Action**: Generate via `pnpm generate:story` (MDX is co-generated) then complete all sections
- **Required sections** (in order):
  1. Component overview and purpose
  2. Import and usage examples (vanilla JS, React, Vue)
  3. "When to use / when not to use"
  4. Interactive story previews (`<Canvas>` or `<Stories>`)
  5. Accessibility (ARIA roles, keyboard nav, screen reader behaviour)
  6. `<ArgTypes>` table
- **Notes**: Code examples must be copy-paste ready and accurate.

#### Step 7: Prepare for Release

- **Action**: Ensure all commits follow the conventional commit format — this is what release-it uses to automatically determine the version bump and generate the `CHANGELOG.md`. No manual changeset files are required.
- **Bump type** (driven automatically from commit type):
  - `fix` / `chore` → patch bump (e.g. `0.0.1-alpha.1`)
  - `feat` → minor bump (e.g. `0.1.0-alpha.0`)
  - `feat!` / `BREAKING CHANGE` → major bump (e.g. `1.0.0-alpha.0`)
- **Implementation Steps**:
  1. Confirm all commits on this branch were made via `pnpm commit` (Commitizen) to guarantee the conventional format
  2. Verify commit types are accurate — they directly control the version increment
  3. Optionally run a release dry-run to preview the version and changelog (Engineering Lead only, from `release/current`):
     ```bash
     pnpm --filter @telesign/boreal-web-components run release -- --dry-run --preRelease=alpha
     ```
- **Notes**: Developers do not run `pnpm release:*`. The Engineering Lead executes the release from the `release/current` branch following the runbook in `.ai/guidelines/release-process.md`.

#### Step 8: Update Technical Documentation

- **Action**: Review all changes and update relevant docs
- **Implementation Steps**:
  1. Verify JSDoc is present on all exported props, events, methods, and types
  2. If the component introduces a new pattern, update `.github/instructions/base.instructions.md`
  3. Confirm the Definition of Done in `.github/instructions/workflow.instructions.md` §1 is fully satisfied
  4. Note any open items or follow-up tasks
- **Notes**: This step is **mandatory** before marking the implementation complete.

### 5. Implementation Order

Numbered sequence of all steps (must start with Step 0 and end with Step 8).

### 6. Testing Checklist

- [ ] `pnpm test:spec` passes with ≥ 90% coverage
- [ ] Component verified in `react-testapp` and a Vue consumer
- [ ] All visual states match Figma within 2 px in all four brand themes
- [ ] Storybook a11y addon passes for all stories
- [ ] Keyboard navigation verified (Tab, Enter, Escape, Arrow keys as applicable)
- [ ] `pnpm turbo lint typecheck` passes with zero errors

### 7. Accessibility Requirements

- ARIA roles and attributes used by the component
- Keyboard interactions (Tab, Enter, Escape, Arrow keys)
- Expected screen reader announcements
- Focus management behaviour
- WCAG AA colour contrast (4.5:1 minimum)

### 8. Design Token Mapping

Table of visual properties → token variables:

| Visual Property | Token Variable                | Layer |
| --------------- | ----------------------------- | ----- |
| Background      | `tokens.$boreal-bg-primary`   | Usage |
| Text colour     | `tokens.$boreal-text-default` | Usage |
| ...             | ...                           | ...   |

### 9. Dependencies

- Token imports from `@telesign/boreal-style-guidelines/stencil`
- Any new Stencil utilities from `packages/boreal-web-components/src/utils/`
- Storybook docs components from `apps/boreal-docs/src/components/docs/` or `story/`

### 10. Notes

- Important constraints from the ticket
- Business rules and brand-specific requirements
- Explicit `any` usage is forbidden — use `unknown` or precise union types
- Multi-brand: the component must work under all four `data-theme` values
- Commit messages must follow `type(scope): TICKET-ID description` via `pnpm commit`

### 11. Next Steps After Implementation

- Open PR targeting `release/current`
- Request peer code review and UX/UI sign-off
- Merge to `release/current` then follow release process in `.ai/guidelines/release-process.md`

### 12. Implementation Verification

Final checklist before marking complete:

- [ ] **Scaffold**: generated files present with correct naming; `@Component` decorator includes `styleUrl`
- [ ] **Props API**: all props typed, JSDoc'd, and defaulted; no `any`
- [ ] **SCSS**: no hard-coded values; all tokens from Usage layer
- [ ] **Tests**: ≥ 90% coverage; all props, events, and slots covered
- [ ] **Stories**: five-section structure; all variants present; a11y passes
- [ ] **MDX**: all six required sections complete; examples copy-paste ready
- [ ] **Release prep**: all commits use conventional format via `pnpm commit`; commit types accurately reflect the change scope
- [ ] **Documentation**: JSDoc complete; guidelines updated if applicable
- [ ] **CI**: `pnpm turbo lint typecheck test` green
