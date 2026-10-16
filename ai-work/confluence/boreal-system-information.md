# Boreal Component Library - System Information

**Last reviewed:** 2026-10-16

**Status of this page:** Living document, first draft. Anything not confirmed is marked "To be confirmed" (TBC); work in progress is marked "WIP". Version numbers and dependency ranges change with every release: treat the repository (`package.json`, git tags) and npm as the source of truth, and update this page whenever the "Last reviewed" date is refreshed.

# 1. Overview

## 1.1 Purpose

Boreal is the Proximus Global component library (design system). It ships framework-agnostic web components built with Stencil, design tokens with multi-brand themes (Proximus, Engage, Protect, Connect), and thin wrappers for React and Vue 3.

## 1.2 Status

Alpha, on plain `0.x` versions (see the package inventory in section 4 for the latest published versions). While below `1.0`, breaking changes bump the minor version. Alpha is a stated status, not a version suffix or dist-tag. Graduation to `1.0.0` is a deliberate release decided by the maintainers.

## 1.3 Owners

| Role | Name |
| --- | --- |
| Engineering Manager | `<Name>` - To be confirmed |
| Tech lead / release owner | `<Name>` - To be confirmed |
| Core team members | `<Name> - <Role>` (see section 19) |

## 1.4 Links

| Resource | Link |
| --- | --- |
| Source repository (Bitbucket Server) | https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds |
| Storybook (hosted on Chromatic) | Branch URL for `release/current`; canonical link To be confirmed (the package READMEs contain two different Chromatic hashes) |
| npm packages | `@pxglobal/boreal-*` on npmjs.com |
| Publishing & deployment guide (Confluence) | SENG 1692827661 |
| CI/CD Pipeline Strategy (Confluence) | SENG 1303773297 |
| ADR-0011 release tooling (Confluence) | SENG 2097872958 |
| Release procedure | `RELEASING.md` at the repository root (wins over any Confluence page) |

This page links to those pages instead of repeating them.

# 2. General information

| Item | Value |
| --- | --- |
| Name | Boreal DS (`boreal-ds` monorepo; root `package.json` is private) |
| Repository | Bitbucket Server, project `DEV`, repo `boreal-ds`; default branch `release/current` |
| Monorepo tooling | pnpm workspaces + Turborepo 2 |
| Components | Stencil 4, Sass, TypeScript 5 |
| Wrappers | `@stencil/react-output-target`, `@stencil/vue-output-target` |
| Documentation | Storybook 10 (`@storybook/web-components-vite`), Chromatic |
| Release tooling | release-it 21 with `@release-it/conventional-changelog` |
| Commit tooling | commitizen, commitlint, husky, lint-staged |
| Node.js | 22.23.3 (`.node-version` and `.nvmrc`; `engines.node >=22`) |
| pnpm | 11.28.2 (`packageManager` field; `engines.pnpm >=11`; activated by Corepack) |
| Jira project | EOA (ticket IDs such as `EOA-10057`) |

## 2.1 License

**To be confirmed with Legal.** The packages declare different licenses today:

| Package | `license` in `package.json` |
| --- | --- |
| `@pxglobal/boreal-web-components` | MIT (README badge also says MIT) |
| `@pxglobal/boreal-style-guidelines` | ISC |
| `@pxglobal/boreal-react` | ISC |
| `@pxglobal/boreal-vue` | none declared |

# 3. Usage / Consumption

Consumers can use the library in three ways. Install without a tag (`npm install @pxglobal/<package>`); use the caret range (for example `^0.14.0`) to receive fixes without breaking changes, because breaking changes bump the minor version. For step-by-step setup per environment, see the "Framework Integration" guide in Storybook (linked from the Storybook welcome page).

| Environment | Install | Notes |
| --- | --- | --- |
| Raw web components (any framework or none) | `npm install @pxglobal/boreal-web-components` | Import the stylesheet in the app entry (`@pxglobal/boreal-web-components/dist/boreal-web-components/boreal-web-components.css`, per the package README); set `data-theme` on `<body>` (`proximus`, `engage`, `protect`, `connect`). Component registration steps: see the package README and the Framework Integration guide. |
| React | `npm install @pxglobal/boreal-react` | Import `@pxglobal/boreal-react/css/boreal.css`. Web components are installed automatically as a dependency. |
| Vue 3 | `npm install @pxglobal/boreal-vue` | Web components are installed automatically as a dependency. Registration details: see the package README and Framework Integration guide. |

The icon font is loaded from a stylesheet URL referenced in the package READMEs; hosting of static assets is outside the scope of this page.

## 3.1 Peer dependencies

The wrapper packages declare **no `peerDependencies`**. React and Vue appear only as devDependencies (see section 7). The supported consumer versions of React and Vue are therefore To be confirmed.

# 4. Packages inventory

The "Latest on npm" column is a live badge, so it never goes stale. To check by hand: `npm view <package> version`. Private workspaces are never published and carry no badge.

| Name | Path | Latest on npm | Purpose | Published |
| --- | --- | --- | --- | --- |
| `@pxglobal/boreal-style-guidelines` | `packages/boreal-style-guidelines` | ![npm](https://img.shields.io/npm/v/@pxglobal/boreal-style-guidelines) | Design tokens, generated CSS/SCSS and Stencil SCSS | Yes (npm, public) |
| `@pxglobal/boreal-web-components` | `packages/boreal-web-components` | ![npm](https://img.shields.io/npm/v/@pxglobal/boreal-web-components) | Stencil web components, custom-elements manifest | Yes |
| `@pxglobal/boreal-react` | `packages/boreal-react` | ![npm](https://img.shields.io/npm/v/@pxglobal/boreal-react) | React wrapper generated from web components | Yes |
| `@pxglobal/boreal-vue` | `packages/boreal-vue` | ![npm](https://img.shields.io/npm/v/@pxglobal/boreal-vue) | Vue 3 wrapper generated from web components | Yes |
| `@pxglobal/boreal-docs` | `apps/boreal-docs` | private | Storybook documentation site | No (deployed to Chromatic) |
| `scripts-boreal` | `scripts-boreal` | private | `validate:pack` / `dev:pack` tooling, changelog link script | No |
| `react-testapp` | `examples/react-testapp` | private | React test app for pack validation | No |
| `vue-testapp` | `examples/vue-testapp` | private | Vue test app for pack validation | No |

Packages can have different versions: a package is only released when it, or a package it is built from, has a releasable change (section 12). Release tags follow the format `@pxglobal/<package>@<version>` (`git tag | grep pxglobal`).

Older `@telesign/boreal-*` packages (up to `0.1.0-alpha.N`) are deprecated and point to the new names.

# 5. Architecture diagram

![Boreal architecture](diagrams/boreal-architecture.drawio)

- The dependency direction is `boreal-style-guidelines` -> `boreal-web-components` -> `boreal-react` and `boreal-vue`. The wrappers depend on web components through `workspace:*`; web components use style-guidelines as a devDependency and copy its CSS/SCSS into its own `dist`.
- The React and Vue wrapper sources are generated by Stencil output targets configured in `stencil.config.ts`.
- `apps/boreal-docs` (Storybook) serves the built web components and token CSS.
- `examples/*` are private test apps; `scripts-boreal` packs the wrappers and installs them into the test apps to validate the real tarballs (`validate:pack`).
- Turborepo orders builds (`dependsOn: ^build`); Stencil compiles components; release-it releases packages.
- Outputs: npm (`@pxglobal`, today), an internal registry (section 8) and Chromatic (Storybook).

# 6. Design token flow

![Boreal token flow](diagrams/boreal-token-flow.drawio)

1. **Design source:** tokens are defined in Figma and exported with the native Figma "Export" feature.
2. **Manual adaptation:** the exported JSON is adapted by hand to the format the generators expect. There is no automated Figma sync.
3. **Sources in the repository** (`packages/boreal-style-guidelines`): `src/tokens/primitives/primitives.json`, `src/tokens/theme/{proximus,engage,protect,connect}.json` and `src/tokens/usage/colors-themes.json`.
4. **Build:** `pnpm build` runs `clean`, then `generate` (`tsx src/generators/generate.ts`), then `validate` (`tsx src/generators/validate.ts`).
5. **Outputs:** the custom TypeScript generators (`src/generators/*.ts`) write `dist/css` (`boreal.css`, `global.css`, `theme-*.css`), `dist/scss` (variables and maps) and `dist/stencil/_index.scss`. CSS custom properties use the `--boreal-` prefix.
6. **Consumption:** Stencil injects `dist/stencil/_index.scss` into every component stylesheet and copies `dist/css` and `dist/scss` into its own `dist`. Components consume `var(--boreal-*)` only. Consumers import the CSS and select a brand with the `data-theme` attribute.

# 7. Supported environments

| Area | Support | Source |
| --- | --- | --- |
| Chrome / Edge | >= 79 | Stencil v4 browser policy |
| Firefox | >= 70 | Stencil v4 browser policy |
| Safari | >= 14 | Stencil v4 browser policy |
| Internet Explorer, legacy Edge | Not supported | Stencil v4 browser policy |
| React | Built and tested against React 19 (devDependency). Supported consumer range: To be confirmed (no peerDependencies) | `boreal-react` package.json |
| Vue | Built against Vue 3.5 (devDependency). Supported consumer range: To be confirmed | `boreal-vue` package.json |
| Node.js (development) | 22.23.3 pinned; `>=22` | `.node-version`, root `package.json` |
| pnpm | 11.28.2 pinned; `>=11` | root `package.json` |
| OS for releases | macOS / Linux only (Windows: use WSL2 or CI) | CONTRIBUTING.md |

The browser table follows Stencil's published policy; the repository has no project-level browser matrix.

# 8. Hosting & distribution

| Artifact | Where | Status |
| --- | --- | --- |
| npm packages | Public npm registry, scope `@pxglobal` (`access: public`) | Live today. Releases are manual (section 12). |
| Internal registry | AWS CodeArtifact | Confirmed as the internal sharing registry. Domain and repository are tracked in ITOPS-72203. Technical details (URLs, accounts, access, origin controls) are To be confirmed. WIP. |
| Public npm long term | Public npm | To be confirmed once a stable version exists (promotion to `1.x`). |
| Storybook | Chromatic, deployed manually with `pnpm deploy:docs`; the `release/current` branch URL is stable across deploys | Live. Deployment is manual. |

`pnpm deploy:docs` builds `@pxglobal/boreal-docs` and its dependencies, then runs `chromatic` using the `CHROMATIC_PROJECT_TOKEN` loaded from a local `.env` through `dotenv-cli`. See the Publishing & Deployment Guide (SENG 1692827661) for the account and credential handling.

# 9. Configuration files

| File | Location | Purpose |
| --- | --- | --- |
| `package.json` | root | Workspace scripts, `packageManager` pin, engines, dev tooling |
| `pnpm-workspace.yaml` | root | Workspaces (`packages/*`, `apps/*`, `examples/*`, `scripts-boreal`) and `allowBuilds` (`@parcel/watcher`, `esbuild`, `puppeteer`) |
| `turbo.json` | root | Task graph: `build`, `test`, `test:coverage`, `lint`, `dev`, `release`, `validate:pack:*` |
| `tsconfig.json` | root and per package | TypeScript settings; `tsconfig.build.json` for web-components |
| `.node-version`, `.nvmrc` | root | Node 22.23.3 |
| `stencil.config.ts` | `packages/boreal-web-components` | Output targets (www, dist, dist-custom-elements, custom elements manifest, React, Vue), Sass plugin, `buildEs5: 'prod'` |
| `testing.config.ts` | `packages/boreal-web-components` | Jest settings, coverage threshold 80% |
| `.release-it.json` (x4) | each of the four published packages | Tag format `@pxglobal/<pkg>@<version>`, `requireBranch: release/current`, push with `--follow-tags`, conventional-changelog with `preMajor`, path scoping, hooks |
| `commitlint.config.js`, `commitlint-custom-rules.js` | root | Commit message rules and allowed scopes |
| `.husky/` | root | Git hooks: commitlint, lint-staged, Stencil spec tests |
| `.lintstagedrc.js` | root | Staged-file lint and format |
| `.storybook/` (`main.ts`, `preview.ts`, `manager.ts`, `theme.ts`) | `apps/boreal-docs` | Storybook config and addons |
| `scripts-boreal/` | root | Pack validation scripts and `link-changelog-heading.js` |
| `.env`, `.env.example` | root | Local secrets such as the Chromatic token (never committed; do not copy values into docs) |

# 10. Local development

Run `eval "$(fnm env)" && fnm use` (or enable `fnm --use-on-cd`) in each terminal session. Always install from the workspace root.

| Task | Command |
| --- | --- |
| Select Node version | `fnm use` |
| Enable pnpm | `corepack enable pnpm` |
| Install | `pnpm install` (CI: `pnpm install --frozen-lockfile`) |
| Storybook (builds styles and components first) | `pnpm dev:docs` (served on port 6006) |
| Components dev server | `pnpm dev:components` |
| Build everything | `pnpm build` |
| Tests | `pnpm test` |
| Coverage | `pnpm --filter @pxglobal/boreal-web-components test:coverage` (root `test:coverage` is not defined; the task exists in `turbo.json`) |
| Lint / format check | `pnpm lint`, `pnpm format:check` |
| Guided commit | `pnpm commit` |
| Pack validation | `pnpm validate:pack:react`, `pnpm validate:pack:vue`, `pnpm validate:all` (`validate:pack:angular` also exists) |
| Local pack for manual testing | `pnpm dev:pack:react`, `pnpm dev:pack:vue` |
| Generate a component or story | `pnpm generate:component`, `pnpm generate:story` |

# 11. CI/CD pipelines

## 11.1 Today

There is **no automated pipeline**. Releases are manual, run from a maintainer machine on macOS or Linux (section 12). Local git hooks (husky) run commitlint, lint-staged and the Stencil spec tests. The strategy and target design live in the CI/CD Pipeline Strategy page (SENG 1303773297).

## 11.2 Target: Jenkins (WIP)

![Jenkins pipeline WIP](diagrams/boreal-jenkins-pipeline-wip.drawio)

**Status: WIP. No `Jenkinsfile` exists in the repository yet.** Agreed direction with DevOps:

- One Jenkins job with several stages ("gates"): quality, lint, tests, build and release, aligned with other company pipelines. The final stage list is To be confirmed.
- Package versions published to the internal registry are the same as the npm versions (no prerelease scheme).
- Storybook deployment stays manual (`pnpm deploy:docs`).

Ticket mapping (the order and final scope are To be confirmed):

| Ticket | Scope |
| --- | --- |
| ITOPS-63109 | Code quality stage |
| ITOPS-63110 | Build components stage |
| ITOPS-63111 | Build Storybook stage |
| ITOPS-72071 | CI quality gate (blocked by 63109/63110/63111) |
| ITOPS-72203 | Provision the internal registry |
| ITOPS-72204 | Jenkins job publishing to the internal registry |
| ITOPS-72205 | Jenkins job publishing to npm; whether it is still planned or deferred is To be confirmed |
| ITOPS-63144 | Manual release and Storybook deploy job; relation to 72205 To be confirmed |

Release trigger and cadence, git credentials for the job, push rights to `release/current` and consumer access are To be confirmed.

# 12. Release & versioning process

![Release flow](diagrams/boreal-release-flow.drawio)

The authoritative procedure is `RELEASING.md` at the repository root; the Confluence Publishing & Deployment Guide (SENG 1692827661) mirrors it.

## 12.1 Rules

- **Trunk:** `release/current` is the single permanent branch. Work branches are `type/TICKET-ID_short-description` and merge back by pull request, squash only.
- **PR titles:** the squashed PR title is the commit that drives the version bump and the changelog, so it must be a Conventional Commit: `type(scope): TICKET-ID description` (or `* ` instead of a ticket). Allowed scopes are enforced by commitlint.
- **Version bumps (`preMajor: true`):** `feat`, `fix`, `perf`, `revert` give a patch; a breaking change (`!` in the title) gives a minor; nothing moves the library to `1.0` by itself. `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `test` never release on their own.
- **Batching:** each package takes one bump from all its commits since its last tag; the highest level wins. A package with nothing releasable is skipped.
- **Path scoping:** a package is released when it, or a package it is built from, has a releasable commit (web-components includes style-guidelines; React and Vue include web-components).
- **Tags:** `@pxglobal/<package>@<version>`, annotated, pushed with `--follow-tags`.
- **Changelogs:** only two exist: `packages/boreal-web-components/CHANGELOG.md` (components, tokens and wrapper changes) and `packages/boreal-style-guidelines/CHANGELOG.md`. React and Vue have none (`infile: false`).
- **Bitbucket Server compare links:** disabled (`linkCompare: false`); `scripts-boreal/bin/link-changelog-heading.js` links the newest heading instead.

## 12.2 Commands

| Command | Effect |
| --- | --- |
| `pnpm release:styles` | Releases style-guidelines |
| `pnpm release:wc-stack` | Web components, then React and Vue |
| `pnpm release:all` | All four packages in dependency order (style-guidelines, web-components, react, vue), one at a time |
| `pnpm release:publish` | `release:all`, then `deploy:docs` |
| `pnpm release:wc`, `release:react`, `release:vue` | One package each |

React and Vue run `pnpm -w run validate:pack:<framework>` as a `prerelease` hook, so a wrapper is only published after its real packed tarball installs and builds in the test app. Publishing uses `pnpm publish` for the wrappers (`publishPackageManager: pnpm`).

## 12.3 Publish authentication and notes

- Authentication: an interactive `npm login` with 2FA (each publish may be held for a browser approval), or a granular token scoped to `@pxglobal` with bypass 2FA. npm is expected to restrict bypass-2FA tokens for direct publishing in the future (credential type To be decided with DevOps).
- release-it does not wait for npm's staged approval; approve in dependency order and verify afterwards.
- Release scripts were verified on macOS only.
- The first release created `0.0.0-stage` placeholder versions on npm; they are never `latest`.
- Once publishing to the internal registry is live, the npm-specific checks and the staged-publish approval in `RELEASING.md` will change (WIP).

## 12.4 Deprecation of `@telesign`

`@telesign/boreal-*` (up to `0.1.0-alpha.N`) are deprecated with a message pointing to the `@pxglobal` names. `@pxglobal` starts at `0.14.0`.

# 13. Build & CI logs / where to look

There is no central log platform.

| What | Where |
| --- | --- |
| Local and manual builds | Terminal output of Turborepo (`pnpm build`); Turbo cache in `.turbo/` |
| Test and coverage output | `packages/boreal-web-components/coverage/` and jest-junit report |
| Release output | release-it terminal output on the maintainer machine; the git tags and release commits on `release/current` |
| Published versions | `npm view @pxglobal/boreal-web-components version dist-tags` |
| Storybook / visual review | Chromatic build log (link printed by `pnpm deploy:docs`) |
| Jenkins | WIP; no job exists yet. Log location To be confirmed |

# 14. Testing & quality gates

| Area | Tooling and gate |
| --- | --- |
| Web components unit tests | Stencil + Jest (`stencil test --spec`), run by the pre-commit hook |
| Coverage | Threshold in `testing.config.ts`: 80% (branches, functions, lines, statements) |
| Mutation testing | Stryker, run locally per component (configs are never pushed); target >= 90% mutation score |
| Style-guidelines tests | vitest (`vitest run`, `test:coverage`) |
| `scripts-boreal` tests | vitest |
| React / Vue wrappers | No tests (`echo 'No tests configured'`) |
| Accessibility checks | Storybook `@storybook/addon-a11y` |
| Component tests in Storybook | `@storybook/addon-vitest` (Playwright browser mode) |
| Visual regression | Chromatic (`@chromatic-com/storybook`, `chromatic --exit-zero-on-changes`) at manual deploy; PR-level Chromatic is a later phase (ITOPS-63136) |
| Pack validation | `pnpm validate:pack:*` installs the packed wrappers into the test apps |
| Lint / format | ESLint 9, Prettier, run via Turbo |
| Commit rules | commitlint via husky |

# 15. Accessibility

What exists today:

- `@storybook/addon-a11y` is enabled in Storybook.
- Components are expected to support keyboard navigation, focus management, screen reader behavior and WCAG AA contrast (4.5:1 normal text, 3:1 large text).
- Each component's accessibility behavior (roving tabindex, focus rings, ARIA roles) is documented in its Storybook page.

Formal WCAG conformance target (for example WCAG 2.1 or 2.2 AA) for the library: To be confirmed. No accessibility conformance report exists yet.

# 16. Dependencies & maintenance

## 16.1 Key dependencies

Declared ranges in `package.json`; the file is the source of truth and these values can drift between reviews.

| Dependency | Version range | Used in |
| --- | --- | --- |
| `@stencil/core` | ^4.27.1 | web-components |
| `@stencil/sass` | ^3.2.3 | web-components |
| `@stencil/react-output-target` | ^1.3.2 (web-components), ^1.2.0 (react) | wrappers |
| `@stencil/vue-output-target` | ^0.11.8 (web-components), ^0.13.1 (vue) | wrappers |
| `typescript` | ^5.9.3 (style-guidelines ^5.8.2) | all |
| `date-fns`, `@date-fns/tz` | ^4.4.0, ^1.5.0 | web-components runtime |
| `@floating-ui/dom`, `@tanstack/virtual-core` | ^1.7.5, ^3.17.1 | web-components runtime |
| `dompurify`, `@braintree/sanitize-url` | ^3.4.8, ^7.1.2 | web-components runtime |
| `jest` | ^29.7.0 | tests |
| `vitest` | ^4.0 | style-guidelines, storybook, scripts |
| `storybook` | ^10.1.11 | docs |
| `turbo` | ^2.8.7 | root |
| `release-it` | ^21.1.0 | root |
| `husky`, `commitlint` | ^9.1.7, ^21.2.3 | root |

## 16.2 pnpm safeguards

`pnpm-workspace.yaml` uses `allowBuilds` so that only `@parcel/watcher`, `esbuild` and `puppeteer` may run install scripts; any new dependency with an install script is blocked until added. No `minimumReleaseAge` setting exists in the repository files, so pnpm's built-in default applies (1440 minutes, or 1 day, per the pnpm supply-chain documentation). Raising it, for example to one week, is a follow-up in the dependency policy.

## 16.3 Policy

The dependency maintenance policy is documented in the ADR "Dependency maintenance policy" (status: proposed). In short, it defines how and when outdated and vulnerable dependencies are reviewed and upgraded; refer to the ADR for the rules rather than this page. Confluence link: To be confirmed.

# 17. Contribution guide

Summary of `CONTRIBUTING.md` (the repository file wins):

- **Workflow:** Bitbucket Server pull requests, Jira tickets (project EOA), trunk-based on `release/current`.
- **Branches:** `type/TICKET-ID_short-description`, for example `feature/EOA-10057_add-text-field`. Types: `feature/`, `fix/` or `bugfix/`, `docs/`, `chore/`. Keep PRs small and short-lived.
- **Commits and PR titles:** `type(scope): TICKET-ID description`; use `pnpm commit`. Allowed scopes: `react`, `vue`, `web-components`, `styles`, `docs`, `examples`, `scripts`, `workspace`, `ci`, `deps`, `release`, `multiple`. Use `chore`, `ci`, `build`, `test` or `docs` for changes consumers cannot observe, because a `feat`/`fix` touching a package folder triggers its release.
- **Breaking changes:** put `!` in the PR title.
- **Pull requests:** all checks (lint, tests, build) pass; new or modified components have unit tests that meet the 80% coverage threshold; bug fixes include a reproducing test.
- **Component rules:** tag prefix `bds-`; styles use `var(--boreal-*)` tokens only; no `any`.

# 18. Troubleshooting / runbooks

`RELEASING.md` has the release failure table.

| Symptom | Cause and fix |
| --- | --- |
| `pnpm dev` / `dev:components` hangs with no output (headless, CI or Windows cold daemon) | Turbo `persistent: true` implies an interactive PTY. Fixed with `"interactive": false` on the `dev` task; `dev:docs` and `dev:components` bypass Turbo |
| CSS/SCSS missing at `dist/css` or `dist/scss` | Stencil places `copy` targets under `dist/<namespace>/`; `scripts/postbuild.js` promotes them to `dist/` |
| npm `E403`, `E404` on publish, `SELF_SIGNED_CERT_IN_CHAIN` on a teammate machine | Account needs real 2FA or a `@pxglobal`-scoped bypass token installed in `~/.npmrc`; behind the company proxy set `NODE_EXTRA_CA_CERTS` to the company root certificate; never disable TLS verification |
| Version not installable after release-it finishes | npm holds the publish for approval; release-it does not wait; approve in dependency order, deprecate `0.0.0-stage` placeholders |
| Breaking change not detected after squash | The `!` must be in the PR title; a footer inside Bitbucket's indented squash list is ignored. Wrap `@handles` in backticks in titles |
| Changelog compare link returns HTTP 400 | Bitbucket Server rejects encoded slashes; compare links are off and the heading is linked by script |
| Chromatic deploy cannot find the token | pnpm does not load `.env`; the script uses `dotenv --` |
| Package published but push failed | See the failure table in `RELEASING.md` |
| New worktree fails to build web-components | Style-guidelines `dist` is missing; build it first |

# 19. Support & ownership

There is no official support channel yet. A shared alias or Teams channel is pending: **To be defined**. Until then the Storybook welcome page tells users to contact their Boreal component library point of contact.

| Role | Person |
| --- | --- |
| Core team member | `<Name> - <Role>` |
| Core team member | `<Name> - <Role>` |
| Team lead / escalation | `<Name> - Team Lead` |
| Backup publisher (single named `@pxglobal` npm org member with 2FA) | `<Name>` - To be confirmed |

- **Intake:** Jira project EOA (ticket per bug or request); the `CONTRIBUTING.md` "Report a Bug" section describes the format.
- **Escalation path:** reporter -> core team member -> team lead.
- **On-call and SLA:** none while the library is alpha.
- **Failed or half-finished release:** where to report it is To be confirmed.
- Stakeholders of the release process are listed in the Publishing & Deployment Guide (SENG 1692827661).

# 20. Related documentation & references

| Document | Location |
| --- | --- |
| Release procedure | `RELEASING.md` |
| Contribution rules | `CONTRIBUTING.md` |
| Setup, prerequisites, scripts | `README.md` |
| Pack validation tool | `scripts-boreal/README.md` |
| Publishing & deployment guide | Confluence SENG 1692827661 |
| CI/CD Pipeline Strategy | Confluence SENG 1303773297 |
| ADR-0011 release tooling | Confluence SENG 2097872958 |
| Dependency maintenance policy | ADR "Dependency maintenance policy"; Confluence link To be confirmed |
