---
status: done
---

# Automated Changelog & Release Plan

**Branch:** `feature/EOA-XXXX_automated_changelog`
**Ticket:** TBD — update XXXX in all commit messages

---

## Context

Replace the manual Changesets workflow with:

- **release-it** (`19.2.4`) + **@release-it/conventional-changelog** (`10.0.5`) — automated releases from conventional commit history
- **@wc-toolkit/changelog** (`1.0.2`) — component API breaking-change detection via Custom Elements Manifest

**Decisions confirmed:**

- Changesets fully removed (no fallback)
- Per-package `.release-it.json` configs (not workspaces plugin)
- No CI integration in this phase (local execution only)
- Bitbucket on-prem → `github.release: false`

---

## Publishable Packages & Release Order

| Package                       | workspace dep                  | Release sequence           |
| ----------------------------- | ------------------------------ | -------------------------- |
| `@boreal-ds/style-guidelines` | none                           | 1st — independent          |
| `@boreal-ds/web-components`   | none                           | 2nd — independent          |
| `@boreal-ds/react`            | `workspace:*` → web-components | 3rd — after web-components |
| `@boreal-ds/vue`              | `workspace:*` → web-components | 4th — after web-components |

WC-Toolkit applies **only** to `@boreal-ds/web-components` (Stencil components define the API surface tracked by CEM).

---

## Affected Files

| File                                                           | Action                                                                | Phase |
| -------------------------------------------------------------- | --------------------------------------------------------------------- | ----- |
| `/package.json`                                                | Remove changeset scripts + dep; add `release:styles/wc/react/vue/all` | 1     |
| `/.changeset/config.json`                                      | Delete                                                                | 1     |
| `packages/boreal-web-components/.release-it.json`              | Create                                                                | 1     |
| `packages/boreal-web-components/package.json`                  | Add `release` + `check:cem` scripts; update `files` array             | 1, 2  |
| `packages/boreal-react/.release-it.json`                       | Create                                                                | 1     |
| `packages/boreal-react/package.json`                           | Add `release` script                                                  | 1     |
| `packages/boreal-vue/.release-it.json`                         | Create                                                                | 1     |
| `packages/boreal-vue/package.json`                             | Add `release` script                                                  | 1     |
| `packages/boreal-styleguidelines/.release-it.json`             | Create                                                                | 1     |
| `packages/boreal-styleguidelines/package.json`                 | Add `release` script                                                  | 1     |
| `packages/boreal-web-components/CHANGELOG.md`                  | Create (stub)                                                         | 1     |
| `packages/boreal-react/CHANGELOG.md`                           | Create (stub)                                                         | 1     |
| `packages/boreal-vue/CHANGELOG.md`                             | Create (stub)                                                         | 1     |
| `packages/boreal-web-components/stencil.config.ts`             | Add `docs-custom-elements-manifest` output target                     | 2     |
| `turbo.json`                                                   | Add `custom-elements.json` to build outputs                           | 2     |
| `packages/boreal-web-components/scripts/check-cem-changes.mjs` | Create                                                                | 2     |

---

## Phase 1 — release-it (replaces Changesets)

### Task 1 — Remove Changesets

1. Delete `/.changeset/config.json`
2. In root `package.json`:
   - Remove scripts: `changeset`, `version-packages`, `release`
   - Remove `@changesets/cli` from `devDependencies`
3. Run `pnpm install` to update lockfile
4. Commit: `chore(release): EOA-XXXX remove changesets in favor of release-it`

---

### Task 2 — Install release-it at workspace root

Always fetch latest versions before installing (CLAUDE.md rule):

```
https://registry.npmjs.org/release-it/latest
https://registry.npmjs.org/@release-it/conventional-changelog/latest
```

Install:

```bash
pnpm add -D -w release-it@latest @release-it/conventional-changelog@latest
```

Add to root `package.json` scripts:

```json
"release:styles": "pnpm --filter @boreal-ds/style-guidelines run release",
"release:wc": "pnpm --filter @boreal-ds/web-components run release",
"release:react": "pnpm --filter @boreal-ds/react run release",
"release:vue": "pnpm --filter @boreal-ds/vue run release",
"release:all": "pnpm run release:styles && pnpm run release:wc && pnpm run release:react && pnpm run release:vue"
```

Note: `release:all` releases in dependency order. `styles` and `wc` have no workspace deps and could run in parallel, but sequential ordering avoids race conditions in git operations.

Commit: `chore(release): EOA-XXXX install release-it and conventional-changelog plugin`

---

### Task 3 — Configure release-it for @boreal-ds/web-components

Create `packages/boreal-web-components/.release-it.json`:

```json
{
  "git": {
    "tagName": "@boreal-ds/web-components@${version}",
    "tagAnnotation": "Release @boreal-ds/web-components v${version}",
    "commitMessage": "chore(release): * release @boreal-ds/web-components v${version}",
    "requireBranch": "release/current",
    "requireCleanWorkingDir": true,
    "push": true,
    "pushRepo": "origin"
  },
  "npm": {
    "publish": true,
    "publishPath": "."
  },
  "github": {
    "release": false
  },
  "hooks": {
    "before:init": "turbo run build --filter=@boreal-ds/web-components",
    "after:release": "echo 'Released @boreal-ds/web-components@${version}'"
  },
  "plugins": {
    "@release-it/conventional-changelog": {
      "preset": "conventionalcommits",
      "infile": "CHANGELOG.md",
      "header": "# Changelog",
      "parserOpts": {
        "headerPattern": "^(\\w*)(?:\\(([\\w\\$\\.\\-\\*\\s]*)\\))?\\:\\s?(?:[A-Z0-9]+-\\d+\\s|\\*\\s)?(.*)$",
        "headerCorrespondence": ["type", "scope", "subject"]
      }
    }
  }
}
```

**Key notes:**

- `commitMessage` uses `* ` prefix — the non-ticket format accepted by the project's `ticket-format` commitlint rule
- `headerPattern` strips ticket IDs (`EOA-9606`) from subjects before they appear in the changelog
- `requireBranch: "release/current"` blocks release-it from running on other branches
- `github.release: false` prevents any GitHub API calls

Add to `packages/boreal-web-components/package.json` scripts:

```json
"release": "release-it"
```

Smoke test: `pnpm --filter @boreal-ds/web-components run release -- --dry-run`
Expected: version prompt appears, changelog preview shown, no files written.

Commit: `chore(release): EOA-XXXX add release-it config for web-components`

---

### Task 4 — Configure release-it for @boreal-ds/react

Create `packages/boreal-react/.release-it.json`:

```json
{
  "git": {
    "tagName": "@boreal-ds/react@${version}",
    "tagAnnotation": "Release @boreal-ds/react v${version}",
    "commitMessage": "chore(release): * release @boreal-ds/react v${version}",
    "requireBranch": "release/current",
    "requireCleanWorkingDir": true,
    "push": true,
    "pushRepo": "origin"
  },
  "npm": {
    "publish": true,
    "publishPath": "."
  },
  "github": {
    "release": false
  },
  "hooks": {
    "before:init": "turbo run build --filter=@boreal-ds/react...",
    "after:release": "echo 'Released @boreal-ds/react@${version}'"
  },
  "plugins": {
    "@release-it/conventional-changelog": {
      "preset": "conventionalcommits",
      "infile": "CHANGELOG.md",
      "header": "# Changelog",
      "parserOpts": {
        "headerPattern": "^(\\w*)(?:\\(([\\w\\$\\.\\-\\*\\s]*)\\))?\\:\\s?(?:[A-Z0-9]+-\\d+\\s|\\*\\s)?(.*)$",
        "headerCorrespondence": ["type", "scope", "subject"]
      }
    }
  }
}
```

**Key note:** `before:init` uses `--filter=@boreal-ds/react...` (trailing `...`) — Turborepo syntax for "this package AND all its dependencies". Guarantees `web-components` builds first.

Add `"release": "release-it"` to `packages/boreal-react/package.json` scripts.

Smoke test: `pnpm --filter @boreal-ds/react run release -- --dry-run`

Commit: `chore(release): EOA-XXXX add release-it config for react package`

---

### Task 4b — Configure release-it for @boreal-ds/vue

Create `packages/boreal-vue/.release-it.json`:

```json
{
  "git": {
    "tagName": "@boreal-ds/vue@${version}",
    "tagAnnotation": "Release @boreal-ds/vue v${version}",
    "commitMessage": "chore(release): * release @boreal-ds/vue v${version}",
    "requireBranch": "release/current",
    "requireCleanWorkingDir": true,
    "push": true,
    "pushRepo": "origin"
  },
  "npm": {
    "publish": true,
    "publishPath": "."
  },
  "github": {
    "release": false
  },
  "hooks": {
    "before:init": "turbo run build --filter=@boreal-ds/vue...",
    "after:release": "echo 'Released @boreal-ds/vue@${version}'"
  },
  "plugins": {
    "@release-it/conventional-changelog": {
      "preset": "conventionalcommits",
      "infile": "CHANGELOG.md",
      "header": "# Changelog",
      "parserOpts": {
        "headerPattern": "^(\\w*)(?:\\(([\\w\\$\\.\\-\\*\\s]*)\\))?\\:\\s?(?:[A-Z0-9]+-\\d+\\s|\\*\\s)?(.*)$",
        "headerCorrespondence": ["type", "scope", "subject"]
      }
    }
  }
}
```

Add `"release": "release-it"` to `packages/boreal-vue/package.json` scripts.

---

### Task 4c — Configure release-it for @boreal-ds/style-guidelines

Create `packages/boreal-styleguidelines/.release-it.json`:

```json
{
  "git": {
    "tagName": "@boreal-ds/style-guidelines@${version}",
    "tagAnnotation": "Release @boreal-ds/style-guidelines v${version}",
    "commitMessage": "chore(release): * release @boreal-ds/style-guidelines v${version}",
    "requireBranch": "release/current",
    "requireCleanWorkingDir": true,
    "push": true,
    "pushRepo": "origin"
  },
  "npm": {
    "publish": true,
    "publishPath": "."
  },
  "github": {
    "release": false
  },
  "hooks": {
    "before:init": "turbo run build --filter=@boreal-ds/style-guidelines",
    "after:release": "echo 'Released @boreal-ds/style-guidelines@${version}'"
  },
  "plugins": {
    "@release-it/conventional-changelog": {
      "preset": "conventionalcommits",
      "infile": "CHANGELOG.md",
      "header": "# Changelog",
      "parserOpts": {
        "headerPattern": "^(\\w*)(?:\\(([\\w\\$\\.\\-\\*\\s]*)\\))?\\:\\s?(?:[A-Z0-9]+-\\d+\\s|\\*\\s)?(.*)$",
        "headerCorrespondence": ["type", "scope", "subject"]
      }
    }
  }
}
```

**Note:** `boreal-styleguidelines` already has a `CHANGELOG.md` at version `0.0.2`. Do NOT create a stub — release-it will prepend to the existing file.

Add `"release": "release-it"` to `packages/boreal-styleguidelines/package.json` scripts.

Commit both (4b + 4c): `chore(release): EOA-XXXX add release-it config for vue and style-guidelines`

---

### Task 5 — Create CHANGELOG.md stubs

Only for packages that do not already have a `CHANGELOG.md`. Check first:

```bash
ls packages/boreal-web-components/CHANGELOG.md packages/boreal-react/CHANGELOG.md packages/boreal-vue/CHANGELOG.md 2>&1
```

Create stubs for any that are missing:

`packages/boreal-web-components/CHANGELOG.md`:

```markdown
# Changelog

All notable changes to `@boreal-ds/web-components` are documented in this file.
```

`packages/boreal-react/CHANGELOG.md`:

```markdown
# Changelog

All notable changes to `@boreal-ds/react` are documented in this file.
```

`packages/boreal-vue/CHANGELOG.md`:

```markdown
# Changelog

All notable changes to `@boreal-ds/vue` are documented in this file.
```

(`boreal-styleguidelines` already has a `CHANGELOG.md` at v0.0.2 — skip it.)

Commit: `chore(release): EOA-XXXX add initial CHANGELOG stubs for publishable packages`

---

### Phase 1 Verification

```bash
pnpm --filter @boreal-ds/style-guidelines run release -- --dry-run
pnpm --filter @boreal-ds/web-components run release -- --dry-run
pnpm --filter @boreal-ds/react run release -- --dry-run
pnpm --filter @boreal-ds/vue run release -- --dry-run
```

**Pass criteria:** All 4 pass — no errors; correct tag format per package (e.g. `@boreal-ds/web-components@X.Y.Z`); changelog generated from conventional commit history; no commits/tags/publishes created.

---

## Phase 2 — WC-Toolkit Changelog

**Prerequisite:** Phase 1 complete and verified.

**Architecture note:** Stencil v4.42.1 natively supports `type: 'docs-custom-elements-manifest'` as an output target — no external CEM analyzer needed.

---

### Task 6 — Add CEM output target to Stencil config

In `packages/boreal-web-components/stencil.config.ts`, add to `outputTargets` after `dist-custom-elements`:

```typescript
{
  type: 'docs-custom-elements-manifest',
  file: 'custom-elements.json',
},
```

Verify after build:

```bash
pnpm --filter @boreal-ds/web-components run build
cat packages/boreal-web-components/custom-elements.json
```

Expected: standard CEM JSON with `schemaVersion`, `modules[]`, component `declarations`.

Update `turbo.json` build task `outputs`:

```json
"outputs": ["dist/**", "loader/**", "components-build/**", ".stencil/**", "custom-elements.json"]
```

Commit: `feat(web-components): EOA-XXXX add docs-custom-elements-manifest Stencil output target`

---

### Task 7 — Install @wc-toolkit/changelog

Fetch current version: `https://registry.npmjs.org/@wc-toolkit/changelog/latest`

```bash
pnpm add -D -w @wc-toolkit/changelog@latest
```

Commit: `chore(deps): EOA-XXXX install @wc-toolkit/changelog`

---

### Task 8 — Create CEM comparison script

Create `packages/boreal-web-components/scripts/check-cem-changes.mjs`:

```js
import { CemChangelog } from "@wc-toolkit/changelog";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

async function getPublishedCem(packageName, version) {
  const url = `https://unpkg.com/${packageName}@${version}/custom-elements.json`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      console.log(
        `No published CEM at ${url} (status ${response.status}) — skipping comparison.`,
      );
      return null;
    }
    return await response.json();
  } catch {
    console.log("Could not fetch published CEM — skipping comparison.");
    return null;
  }
}

async function main() {
  const pkg = JSON.parse(
    await readFile(join(__dirname, "..", "package.json"), "utf8"),
  );

  let localCem;
  try {
    localCem = JSON.parse(
      await readFile(join(__dirname, "..", "custom-elements.json"), "utf8"),
    );
  } catch {
    console.error(
      "ERROR: custom-elements.json not found. Run `pnpm build` first.",
    );
    process.exit(1);
  }

  const publishedCem = await getPublishedCem(pkg.name, pkg.version);
  if (!publishedCem) {
    console.log("\n--- CEM Comparison skipped (no prior published CEM) ---\n");
    return;
  }

  const detector = new CemChangelog();
  const { changelog, rawData } = detector.compareManifests(
    publishedCem,
    localCem,
  );

  console.log("\n=== WC-Toolkit: Component API Change Report ===\n");

  if (rawData?.breaking?.length > 0) {
    console.log(
      '⚠️  BREAKING CHANGES — select "major" for the version bump:\n',
    );
    console.log(changelog);
  } else if (rawData?.features?.length > 0) {
    console.log("✨ New features detected (no breaking changes):\n");
    console.log(changelog);
  } else {
    console.log("✅ No component API changes detected.");
  }

  console.log("\n=== End of Change Report ===\n");
}

main().catch((err) => {
  console.error("CEM comparison failed:", err.message);
  process.exit(0);
});
```

**Design:** Always exits `0` (network failure never blocks a release). Exits `1` only if `custom-elements.json` is missing.

Add to `packages/boreal-web-components/package.json` scripts:

```json
"check:cem": "node scripts/check-cem-changes.mjs"
```

Test: `pnpm --filter @boreal-ds/web-components run check:cem`
Expected (first run, v0.0.1 unpublished): `--- CEM Comparison skipped ---`

Commit: `feat(web-components): EOA-XXXX add CEM comparison script for breaking change detection`

---

### Task 9 — Wire CEM check into release-it hook + update files array

Update `before:init` in `packages/boreal-web-components/.release-it.json`:

```json
"before:init": "turbo run build --filter=@boreal-ds/web-components && node scripts/check-cem-changes.mjs"
```

Add `custom-elements.json` to `packages/boreal-web-components/package.json` `files` array:

```json
"files": ["dist/", "loader/", "components-build/", "custom-elements.json"]
```

Full dry-run:

```bash
pnpm --filter @boreal-ds/web-components run release -- --dry-run
```

Expected: build → CEM report → version prompt → no actual changes.

Commit: `feat(web-components): EOA-XXXX wire CEM detection into release-it hook`

---

## Phase 2 Verification

After publishing the first real release to npm:

```bash
# Make a breaking API change (e.g. remove a @Prop from my-component), rebuild, then:
pnpm --filter @boreal-ds/web-components run check:cem
# Expected: "⚠️ BREAKING CHANGES DETECTED — select major"

pnpm run release:wc -- --dry-run
# Expected: CEM report printed before version prompt
```

---

## Commit Format Note

All release-it auto-commits use `* ` (non-ticket prefix), which passes the project's `ticket-format` commitlint rule:

```
chore(release): * release @boreal-ds/web-components v1.0.0
```
