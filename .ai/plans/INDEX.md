# Plans Index

All plan files in this folder carry a YAML frontmatter block with a `status` field:

| Value         | Meaning                            |
| ------------- | ---------------------------------- |
| `pending`     | Not yet started                    |
| `in progress` | Work has begun but is not complete |
| `done`        | Fully implemented and verified     |

---

## Pending

| File                                                                   | Description                                                                                                                    |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [generator-extension-strategy.md](generator-extension-strategy.md)     | Extend the Plop generator to scaffold Stencil components in `boreal-web-components` and stories in `boreal-docs` cross-package |
| [storybook-chromatic-deployment.md](storybook-chromatic-deployment.md) | Publish the Storybook to Chromatic for team access without a local dev environment                                             |

---

## In Progress

| File                                                                 | Description                                                                                                                    |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [EOA-10099-form-foundation.md](EOA-10099-form-foundation.md)         | Shared FACE-based form foundation (form association, props, validation) required before any form components can be implemented |
| [icons-strategy.md](icons-strategy.md)                               | Phased icon library rollout — icon font + S3 CDN for alpha, component wrappers for beta                                        |
| [integrated-monorepo-migration.md](integrated-monorepo-migration.md) | pnpm workspaces + Turborepo + root-level git hooks + release-it migration                                                      |
| [welcome-page-content-plan.md](welcome-page-content-plan.md)         | Welcome page content and styling for the `boreal-docs` Storybook                                                               |

---

## Done

| File                                                                 | Description                                                                                       |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [automated-changelog-&-release.md](automated-changelog-&-release.md) | Replace manual Changesets with release-it + `@release-it/conventional-changelog`                  |
| [code-snippetformatter.md](code-snippetformatter.md)                 | Replace `prettierFormatter` with `formatHtmlSource` in `apps/boreal-docs/src/utils/formatters.ts` |
| [first-alpha-release.md](first-alpha-release.md)                     | Step-by-step runbook for the first `0.1.0-alpha.0` publish to npm                                 |
| [plop-implementation-plan.md](plop-implementation-plan.md)           | Plop.js generator for scaffolding `.stories.ts` + `.mdx` files in `apps/boreal-docs`              |
| [root-level-hooks-migration.md](root-level-hooks-migration.md)       | Move git hooks from `packages/boreal-web-components/.husky/` to the monorepo root                 |
| [shared-storybook-components.md](shared-storybook-components.md)     | Shared React `docs/` and Lit `story/` components used in MDX and story files                      |
| [storybook-plan.md](storybook-plan.md)                               | Baseline Storybook architecture — stories, MDX, theme-aware previews, token integration           |
