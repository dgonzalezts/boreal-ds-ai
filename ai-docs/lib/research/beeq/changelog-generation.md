# How Changelog Generation Works in BEEQ

The whole pipeline is built around **Conventional Commits + Nx Release**, with commit-message linting enforced at commit time via Husky/commitlint. No changesets, semantic-release, or standard-version — it's Nx's native release feature.

## 1. Underlying Technologies

| Layer | Tool | Purpose |
|---|---|---|
| Commit message linting | `@commitlint/cli` + `@commitlint/config-conventional` (`.commitlintrc.ts`) | Enforces Conventional Commits format on every commit |
| Git hook enforcement | `husky` (`.husky/commit-msg`, `.husky/pre-commit`) | Runs commitlint on `commit-msg`, plus branch-name/staged-file lint on `pre-commit` |
| Branch naming | `.husky/branch-name.sh` | Forces branch prefixes (`feat/`, `fix/`, `chore/`, etc.) to mirror commit types |
| Version bump + changelog generation | **Nx Release** (`nx release`, config in `nx.json`) | Parses conventional commits since last tag, computes semver bump, generates changelog entries, tags, commits |
| Changelog commit parsing | `conventional-changelog-conventionalcommits` / `conventional-changelog-angular` (transitive deps pulled in by Nx release + commitlint config) | Underlying parser that groups commits by `type(scope): subject` |
| Publishing | GitHub Actions (`publish.yml`) + `nx release publish` | Publishes packages to npm once a GitHub Release is published |
| GitHub Release creation | Nx release's `createRelease: "github"` option | Nx opens/updates a GitHub Release with the same changelog content |

## 2. Generation Process (end to end)

1. **Author writes a commit** following `<type>[optional scope]: <subject>` (e.g. `fix(Select): prevent tag removal on backspace...`).
2. **`commit-msg` hook** runs `commitlint --edit`, validating against the allowed `type-enum` in `.commitlintrc.ts` (`feat, fix, test, docs, style, chore, perf, refactor, revert, ci, build, wip, release`) and a 500-char body line limit. Invalid messages are rejected before the commit is created.
3. **PR merge**: CONTRIBUTING.md instructs that PR titles must also follow the same convention and PRs are **squash-merged**, so each PR becomes exactly one conventional commit on `main` — this is what keeps the generated changelog clean (one bullet per PR/feature, not per WIP commit).
4. **Release time** (run manually/by a maintainer, since there's no dedicated CI "release" workflow, only `publish.yml` reacting to `release: published`): `nx release` is invoked. Nx:
   - Scans commits since the last `vX.Y.Z` tag (`releaseTagPattern: "v{version}"`) across `projects: ["packages/*"]`.
   - Uses `conventionalCommits: true` under `release.version` to determine the semver bump per commit type (e.g. `fix`, `docs`, `style`, `chore`, `perf`, `refactor`, `revert`, `test` are all mapped to `semverBump: "patch"`; `feat` implicitly bumps minor; `!`/`BREAKING CHANGE:` footers bump major).
   - Groups matching commits into named changelog sections via the `conventionalCommits.types` map in `nx.json`, e.g.:
     - `feat` → "Features ⚡️"
     - `fix` → "Bug Fixes 🐞"
     - `docs` → "Documentation 📚"
     - `chore` → "Chore ⚙️"
     - `revert` → "Revert 🔄"
     - `release` commits are **excluded** (`"release": false`) so the release-bump commit itself never pollutes the log.
   - Renders a `workspaceChangelog` (single root `CHANGELOG.md`, not per-package) with `renderOptions`:
     - `authors: true` + `applyUsernameToAuthors: true` → produces the "❤️ Thank You" section with GitHub usernames.
     - `commitReferences: true` → links each entry to its commit SHA or PR number.
     - `versionTitleDate: true` → stamps each version heading with the release date.
   - Prepends the new section to `CHANGELOG.md`.
5. **Git tagging & commit**: per `release.git`, Nx stages the changelog + version bumps, commits with message `release: {version} [skip ci]`, and creates the git tag — the `[skip ci]` avoids re-triggering CI on the release commit itself.
6. **GitHub Release**: `createRelease: "github"` makes Nx open a GitHub Release using the same rendered changelog content.
7. **Publish workflow** (`.github/workflows/publish.yml`) triggers on `release: published`, builds all packages, then runs `pnpm exec nx release publish --parallel=5` to push to npm with provenance (`NPM_CONFIG_PROVENANCE: true`), and deploys Storybook to GitHub Pages.

## 3. Best Practices Implemented

- **Single source of truth for history**: commit message *is* the changelog line — no separate manual changelog editing, eliminating drift between code history and release notes.
- **Enforcement at the earliest point (shift-left)**: commitlint runs client-side via Husky before the commit even lands, not just in CI — bad messages never make it into history.
- **Branch name ↔ commit type consistency**: `branch-name.sh` mirrors the same type vocabulary as commitlint, reinforcing the taxonomy across the whole workflow (branch → commits → PR title → changelog section).
- **Squash-merge policy**: keeps `main`'s history to one meaningful conventional commit per PR, so the auto-generated changelog stays readable instead of listing every "wip", "fix typo" commit.
- **Semantic Versioning automation**: bump is derived, not manually chosen, removing human error/inconsistency in version numbers.
- **Scoped commits** (`type(scope): subject`, e.g. `fix(Select): ...`) — although no `scope-enum` is enforced, using component names as scopes makes generated entries immediately actionable/searchable (readers know which component changed without opening the PR).
- **Breaking change / deprecation footers** (`BREAKING CHANGE:`, `DEPRECATED:`) are explicitly documented in CONTRIBUTING.md, ensuring major bumps and migration notes are captured verbatim in the changelog, not just inferred from a `!`.
- **Attribution baked into release notes**: `authors`/`applyUsernameToAuthors` credits contributors automatically, and `commitReferences` gives traceability back to the exact commit/PR.
- **CI-noise prevention**: `release: {version} [skip ci]` commit message prevents infinite/pointless CI runs off the bot's own release commit.
- **Decoupling versioning from publishing**: `nx release` (version+changelog) is a separate, deliberate step from `nx release publish` (npm push), which only runs in CI when a GitHub Release is actually published — reducing risk of accidental publishes.

## 4. Other Key Aspects

- **Nx workspace-wide changelog, not per-package**: even though `projects: ["packages/*"]` targets multiple publishable packages (core `beeq`, framework wrappers, Tailwind package, etc.), only a `workspaceChangelog` is configured — there's one root `CHANGELOG.md` aggregating all packages rather than one file per package, simplifying consumer-facing history.
- **No dedicated "release" GitHub Action**: unlike many repos with a bot-driven release PR (e.g., Release Please, Changesets bot), BEEQ's release step (`nx release`) appears to be run manually/locally by a maintainer with push+tag rights, and only the *publish* step is automated via `publish.yml`, triggered by the `release: published` GitHub event.
- **Tight coupling to Stencil/Nx monorepo structure**: because BEEQ is an Nx monorepo (Stencil core + Angular/React/Vue wrappers), Nx Release's multi-project awareness (`nx-release-publish` target with `packageRoot: "dist/{projectName}"`) lets a single conventional-commit-driven release cut versions/changelogs and publish all framework-specific packages together consistently.
- **`versionPrefix: "^"`**: internal cross-package dependency ranges get updated with a caret automatically during release version bumps.
