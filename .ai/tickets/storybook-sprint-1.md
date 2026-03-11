# Sprint 1 Ticket — Storybook Foundation Infrastructure

## 1. Clear and Concise Title
**Implement Storybook Foundation Infrastructure for Component Library**

## 2. Detailed Description

### Purpose
Establish the foundational Storybook infrastructure required to document any component in a consistent, type-safe, and theme-aware way. This sprint delivers the core configuration, type system, utilities, and canonical story template needed before scaling to additional components or documentation work. Completing these tasks upfront prevents high-cost refactors later.

### Specific Details
1. **Project & Storybook Setup**
   - Install Storybook 8.6.7 with `@storybook/web-components-vite` and `@storybook/builder-vite`.
   - Configure `.storybook/main.ts` with story globs, static directories, remark-gfm, and essential addons (`essentials`, `a11y`, `actions`, `docs`, `links`).
   - Configure Vite aliases (`@/` → `src`, `@root/` → project root) for both Vite and TypeScript.
   - Add preview head assets (global styles) and build-specific asset handling.
   - Define `package.json` scripts: `dev`, `build`, `lint`, `lint:fix`.

2. **Type System Foundation**
   - Create `src/types/storybook.ts` with `ColibriStoryMeta<T>`, `ColibriStory<T>`, `StoryArgs`, `Styles`, and `StylesOptions` types.
   - Add `src/custom.d.ts` to support image/CSS imports and align with story code usage.
   - Update `tsconfig.json` with alias paths matching Vite configuration and include `.mdx` files.

3. **Critical Utilities**
   - Implement `src/utils/formatters.ts` with `formatHtmlSource()` function that:
     - Adds comprehensive Prettier options (printWidth, tabWidth, htmlWhitespaceSensitivity, bracketSameLine, singleAttributePerLine)
     - Cleans empty attribute values using regex (no manual BOOLEAN_ATTRIBUTES list)
     - Removes style tags via `removeStyleTags()`
     - Uses Phase 1 approach (no Lit binding handling unless needed)
   - Export utilities via `src/utils/index.ts` for concise imports in stories.

4. **Story Template Pattern**
   - Document canonical `.stories.tsx` structure aligned with Section 5.3 (imports, meta, argTypes, args, render functions, story exports).
   - Build `col-button/col-button.stories.tsx` implementing the full pattern (StoryArgs type, meta configuration, argTypes categories, render function, ≥3 variants).
   - Produce `PATTERNS.md` (or similar doc) summarizing how to author compliant stories.

## 3. Acceptance Criteria
- Storybook starts (`npm run dev`) and builds (`npm run build`) successfully.
- `.storybook/main.ts` includes configured addons, remark-gfm, static directories, and path aliases.
- `ColibriStoryMeta`/`ColibriStory` types provide IntelliSense and enforce type safety across the example story.
- Utilities transform docs source output correctly (boolean attributes, indentation, style stripping).
- Button story renders, exposes working controls, and demonstrates at least Default/AllVariants/Interactive stories.
- PATTERNS documentation exists and references the Button example.

## 4. Comments and Notes
- Complete these tasks sequentially—each depends on the previous step.
- No external teams required; all work is internal to the Storybook project.
- Estimated effort: ~5 developer days (entire Sprint 1 focus).
- Skipping any item introduces critical technical debt (type refactors, inconsistent docs, broken builds).

## 5. Links or References
- [Storybook Plan](storybook-plan.md)
- [Code Practices & Dev Guidelines – Section 5.3](docs/code-practices-&-dev-guidelines.md#53)
- [Ticket Definition Rubric](.cursor/rules/ticket-definition.mdc)
- Colibri reference implementation: `apps/colibri-docs` (configuration, utilities, stories)
