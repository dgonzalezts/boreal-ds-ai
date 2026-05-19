# Sprint 2 Ticket — Storybook Documentation & Decorator System

## 1. Clear and Concise Title
**Deliver Storybook Documentation Patterns, Helper Utilities, and Theme Decorators**

## 2. Detailed Description

### Purpose
Extend the foundation from Sprint 1 by delivering the documentation authoring system, helper utilities, global decorators, and multi-component coverage needed for a production-ready baseline. This sprint ensures contributors can create MDX docs, reuse utilities, and rely on global theming/layout behavior without per-story hacks.

### Specific Details
1. **MDX Template & Button Documentation**
   - Create a canonical `.mdx` template encapsulating Section 5.3 requirements (meta, description, table of contents, installation/usage, framework integration stubs, accessibility, properties, related components).
   - Author `col-button/col-button.mdx` using the template, reusing stories through `<Canvas of={Stories.Default} />` pattern.
   - Integrate Storybook Blocks (`Canvas`, `ArgsTable`, `Controls`, `LinkTo`) and ensure code snippets use the `formatCodeString` utility output.

2. **Helper Utilities & Shared Components**
   - Implement `src/utils/helpers.ts` with `disableControls()`, `enabledControls()`, `wrapContent()` (or equivalent) to reduce per-story duplication.
   - Configure highlight.js (import core, register languages) for syntax highlighting where required.
   - Add any lightweight Lit helper components required for Sprint 2 stories (e.g., layout wrappers) under `src/_storybook/components`.

3. **Decorator & Theme System**
   - Finalize `.storybook/preview.ts` with:
     - Theme decorator that toggles `data-theme` on `<body>` using toolbar selection.
     - Styles decorator honoring the `__sb` parameter for layout control.
     - Docs container that syncs themes in Docs mode.
     - Global backgrounds and story sorting that mirrors Colibri categories.
   - Define `globalTypes` for the available themes (Telesign, Massive, BICS or equivalent) with toolbar metadata.

4. **Multi-Component Coverage**
   - Implement complete story + MDX pairs for three additional components (recommended mix: one form input, one navigation/layout element, one feedback/presentation component).
   - Ensure each component leverages helper utilities, decorators, and MDX template features to validate scalability.
   - Document any component-specific patterns inside PATTERNS/CONTRIBUTING references.

## 3. Acceptance Criteria
- `.mdx` template exists and is documented; Button documentation uses it end-to-end.
- `src/utils/helpers.ts` exports reusable functions and is consumed by at least two components.
- Highlight.js integration works inside stories/docs where needed.
- Theme toolbar toggles update both Docs and Canvas previews without per-story code.
- `__sb` parameters adjust layout (e.g., height/width) for components like headers or overlays.
- Additional components (≥3) have both `.stories.tsx` and `.mdx` files that pass lint/build and follow Section 5.3 patterns.
- PATTERNS/CONTRIBUTING docs are updated with MDX authoring steps and decorator usage guidance.

## 4. Comments and Notes
- Depends on Sprint 1 being complete (configuration, types, utilities, initial component).
- Target effort: full Sprint 2.
- Coordinate with design/docs stakeholders for content validation where needed.
- After this sprint the baseline is production-ready; remaining enhancements (reusable doc components, foundation pages, framework guides) move to the enhancement backlog.

## 5. Links or References
- [Storybook Plan](storybook-plan.md)
- [Sprint 1 Ticket](storybook-sprint-1.md)
- [Code Practices & Dev Guidelines – Section 5.3](docs/code-practices-&-dev-guidelines.md#53)
- Colibri reference (`apps/colibri-docs/src/components/*`) for MDX + story implementations
- [Ticket Definition Rubric](.cursor/rules/ticket-definition.mdc)
