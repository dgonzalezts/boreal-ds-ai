# Plans Index

All plan files in this folder carry a YAML frontmatter block with a `status` field:

| Value         | Meaning                            |
| ------------- | ---------------------------------- |
| `pending`     | Not yet started                    |
| `in progress` | Work has begun but is not complete |
| `done`        | Fully implemented and verified     |

---

## Pending

| File                                                               | Description                                                                                                                    |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| [EOA-10533-bds-radio-button.md](EOA-10533-bds-radio-button.md)     | `bds-radio-button` (leaf component) and extension of `bds-radio-group` to support `type="radiobutton"`                         |
| [generator-extension-strategy.md](generator-extension-strategy.md) | Extend the Plop generator to scaffold Stencil components in `boreal-web-components` and stories in `boreal-docs` cross-package |

---

## In Progress

| File                                                                         | Description                                                                                                       |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| [EOA-12342-bds-checkbox-button.md](EOA-12342-bds-checkbox-button.md)         | `bds-checkbox-button` leaf — Tasks 1–9 done; stories + MDX need updates once `bds-checkbox-group` wrapper lands  |
| [alpha-release-vue-react-storybook.md](alpha-release-vue-react-storybook.md) | Vue first publish, React re-publish, and Storybook deploy to Chromatic                                            |
| [icons-strategy.md](icons-strategy.md)                                       | Phased icon library rollout — icon font + S3 CDN for alpha, component wrappers for beta                           |
| [integrated-monorepo-migration.md](integrated-monorepo-migration.md)         | pnpm workspaces + Turborepo + root-level git hooks + release-it migration. Missing watch mode on styleguidelines. |
| [token-synchronization-and-cleanup.md](token-synchronization-and-cleanup.md) | Standardize tokens with Figma (sync, sort, clean $extensions) — Phase 1 baseline infrastructure done              |

---

## Done

| File                                                                             | Description                                                                                                                                |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [EOA-12334-bds-radio-and-radio-group.md](EOA-12334-bds-radio-and-radio-group.md) | `bds-radio` (FACE) + `bds-radio-group` (orchestrator) compound component — 3 visual variants, 9 tasks                                      |
| [EOA-12029_grid_foundational_system.md](EOA-12029_grid_foundational_system.md)   | Foundational 12-column grid system — `bds-grid` + `bds-grid-item` with 5 responsive breakpoints                                            |
| [EOA-10057-bds-text-field.md](EOA-10057-bds-text-field.md)                       | Full implementation of `bds-text-field` — Tasks 1–6 done (types, TSX, SCSS, Vue v-model, 79 unit tests); Task 7 (Storybook docs) remaining |
| [EOA-10099-form-foundation.md](EOA-10099-form-foundation.md)                     | Shared FACE-based form foundation (form association, props, validation) required before any form components can be implemented             |
| [first-alpha-release.md](first-alpha-release.md)                                 | Step-by-step runbook for the first `0.1.0-alpha.0` publish to npm — Steps 9–11 (Vue) remaining                                             |
| [welcome-page-content-plan.md](welcome-page-content-plan.md)                     | Welcome page content and styling for the `boreal-docs` Storybook                                                                           |
| [automated-changelog-&-release.md](automated-changelog-&-release.md)             | Replace manual Changesets with release-it + `@release-it/conventional-changelog`                                                           |
| [code-snippetformatter.md](code-snippetformatter.md)                             | Replace `prettierFormatter` with `formatHtmlSource` in `apps/boreal-docs/src/utils/formatters.ts`                                          |
| [integrate-vue-testapp.md](integrate-vue-testapp.md)                             | Port vue-testapp scaffold, wire validate:pack:vue pipeline, extend first-alpha-release for Vue                                             |
| [plop-implementation-plan.md](plop-implementation-plan.md)                       | Plop.js generator for scaffolding `.stories.ts` + `.mdx` files in `apps/boreal-docs`                                                       |
| [root-level-hooks-migration.md](root-level-hooks-migration.md)                   | Move git hooks from `packages/boreal-web-components/.husky/` to the monorepo root                                                          |
| [shared-storybook-components.md](shared-storybook-components.md)                 | Shared React `docs/` and Lit `story/` components used in MDX and story files                                                               |
| [storybook-chromatic-deployment.md](storybook-chromatic-deployment.md)           | Publish the Storybook to Chromatic for team access without a local dev environment                                                         |
| [storybook-plan.md](storybook-plan.md)                                           | Baseline Storybook architecture — stories, MDX, theme-aware previews, token integration                                                    |
