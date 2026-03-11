---
status: done
---

# Storybook Baseline Implementation Plan

## 1. Context & Goals

- Build a production-ready Storybook baseline for the new component library using the Colibri implementation as reference.
- Ensure every component can ship with type-safe stories, high-quality MDX documentation, theme-aware previews, and reusable utilities.
- Avoid future refactors by establishing the complete architecture upfront—no MVP shortcuts.

## 2. References

- [Code Practices & Dev Guidelines – Section 5.3](docs/code-practices-&-dev-guidelines.md#53)
- Existing Storybook implementation in `apps/colibri-docs`
- Ticket definition rubric in `.cursor/rules/ticket-definition.mdc`

## 3. Guiding Principles

1. **Separation of concerns**: Stories (`.stories.tsx`) handle interactive narratives; MDX files handle documentation.
2. **Manual documentation**: Use curated `.mdx` files instead of `autodocs` for clarity and flexibility.
3. **Framework-agnostic rendering**: Use Lit`s `html` template literal (no Stencil bindings).
4. **Type safety first**: Custom `ColibriStoryMeta`/`ColibriStory` types plus module declarations.
5. **Consistent argTypes**: Categorize controls (`Core`, `State`, `Validation`, `Accessibility`, `Events`, `Storybook Controls`).
6. **Theming & layout decorators**: Theme toolbar and `__sb` layout styles are global responsibilities.
7. **Reusable utilities**: `formatCodeString`, helper decorators, and boolean attribute lists live in `src/utils`.
8. **Design documentation parity**: Foundation (tokens, colors, typography) published under `src/_storybook` alongside components.

## 4. Architecture Overview

| Layer                   | Components                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| **Tooling & Build**     | Storybook 8.6.7, `@storybook/web-components-vite`, Vite builder                                        |
| **Config**              | `.storybook/main.ts`, `preview.ts`, `manager.ts`, `theme.ts`, static assets, global CSS                |
| **Types & Utilities**   | `src/types/storybook.ts`, `src/custom.d.ts`, utilities (`formatters.ts`, `helpers.ts`, `constants.ts`) |
| **Reusable Primitives** | `src/_storybook/components` (React MDX helpers + Lit demo components)                                  |
| **Documentation**       | `src/_storybook` MDX pages (welcome, frameworks, foundation)                                           |
| **Components**          | `src/components/<component>/<component>.stories.tsx` + `.mdx`                                          |

## 5. Workstreams & Tasks

### 5.1 Foundation (Sprint 1)

1. **Project & Storybook setup**: Install dependencies, configure `package.json` scripts, define path aliases, enable remark-gfm, configure static directories.
2. **Type system**: Implement `ColibriStoryMeta`, `ColibriStory`, `StoryArgs`, `Styles`, module declarations, and `tsconfig` paths.
3. **Utilities**: Implement `formatCodeString`, `removeStyles`, `BOOLEAN_ATTRIBUTES`, central exports.
4. **Story template**: Document canonical `.stories.tsx` structure, deliver Button example with multiple variants, create PATTERNS guide.

### 5.2 Core Documentation & Decorators (Sprint 2)

5. **MDX template & Button doc**: Build full `.mdx` pattern (meta, ToC, usage, component preview, accessibility, properties).
6. **Helper utilities**: `disableControls`, `enabledControls`, layout wrappers, highlight.js setup, shared render helpers.
7. **Decorator system**: Theme toolbar, layout decorator using `__sb`, docs container enforcing `data-theme`, global backgrounds, story sorting.
8. **Component coverage**: Document at least 3 additional components (form, navigation, feedback) to validate patterns.

### 5.3 Enhancements & Expansion (Post Sprint 2)

9. **Reusable documentation components**: Build Callout, Card, Container (React) plus FormDemo, CodeBlock, LayoutDemo (Lit).
10. **Design foundation & framework guides**: Publish colors/typography/spacing/theming MDX pages, create React/Vue/Angular integration guides, add related component references.
11. **Advanced patterns**: Hidden stories, FormDemo wrappers, LinkTo navigation, dynamic code snippets, responsive layouts, device viewport presets.
12. **Quality gates**: Chromatic integration, lint rules (`eslint-plugin-storybook`), accessibility checklist documentation, authoring checklist automation.

## 6. Deliverables & Success Criteria

- Storybook runs via `npm run dev` and `npm run build` without errors.
- At least four components demonstrate the full story + MDX pipeline.
- Theme switching, layout decorators, and code formatting work consistently.
- Documentation contributors can follow PATTERNS/CONTRIBUTING guides without mentor support.
- Reusable utilities prevent duplication (helper import usage tracked across >50% of stories).

## 7. Risks & Mitigations

| Risk                 | Impact                           | Mitigation                                                 |
| -------------------- | -------------------------------- | ---------------------------------------------------------- |
| Skipping type system | Refactor every story             | Implement types before any story merges                    |
| Incomplete utilities | Inconsistent docs output         | Ship `formatCodeString` + helpers before copying templates |
| Late decorator setup | Per-story hacks for layout/theme | Build decorators in Sprint 2 before scaling components     |
| Documentation drift  | Hard-to-follow contributions     | Maintain single PATTERNS + CONTRIBUTING sources of truth   |

## 8. Timeline Snapshot

- **Sprint 1**: Foundation tasks (config, types, utilities, story template, first component)
- **Sprint 2**: Documentation patterns, helper utilities, decorator system, multi-component coverage
- **Post Sprint 2**: Reusable doc components, design foundation, framework guides, advanced patterns, quality gates

## 9. Definition of Done

- Developers can scaffold a new component story + doc using templates in under 30 minutes.
- Storybook surfaces accurate code snippets, controls, and theming without manual tweaks.
- Documentation structure mirrors the Colibri reference and passes internal reviews.
- All planned files live under `.ai` root and align with ticket definition standards.
