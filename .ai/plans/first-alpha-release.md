---
status: in progress
---

# First Alpha Release — Boreal DS

**Branch required:** `release/current`
**Packages:** `@telesign/boreal-style-guidelines`, `@telesign/boreal-web-components`, `@telesign/boreal-react`, `@telesign/boreal-vue`
**npm dist-tag:** `alpha` (configured in all `.release-it.json` files)

---

## Key Concepts Before You Start

### `"tag": "alpha"` vs `"preRelease": "alpha"` — different things

|                                 | Controls                                | Where configured                                |
| ------------------------------- | --------------------------------------- | ----------------------------------------------- |
| `"tag": "alpha"` in `npm` block | npm dist-tag (`--tag alpha` on publish) | `.release-it.json`                              |
| `"preRelease": "alpha"` in root | Version number suffix (`-alpha.N`)      | `.release-it.json` (added during first release) |

Both are now in `.release-it.json` for all packages. **No CLI flags are required for subsequent alpha releases** — `pnpm release:styles`, `pnpm release:wc`, `pnpm release:react`, `pnpm release:vue` work from the workspace root without extra arguments.

### What the version number means

```
  0   .   1   .   0   -  alpha  .   0
  │       │       │            │   └── pre-release iteration counter (resets on base bump)
  │       │       └────────────────── PATCH
  │       └────────────────────────── MINOR
  └────────────────────────────────── MAJOR (0 = not yet stable)
```

Counter progression example:

```
0.1.0-alpha.0   ← first alpha
0.1.0-alpha.1   ← fix commit; base stays, counter increments
0.2.0-alpha.0   ← feat commit; minor bumps, counter resets to 0
```

### `--increment=minor` is only needed for the very first release of each package

The full git history contains `BREAKING CHANGE` footers from infrastructure/scaffolding commits. With no existing tag as baseline, release-it scans all commits and inflates the bump to **major**. `--increment=minor` overrides this to produce `0.1.0-alpha.0`.

**This flag does not forward through nested pnpm calls.** For first releases, always run `npx release-it` directly from inside the package directory — not via the root `pnpm release:*` scripts.

Once a tag exists, all subsequent releases auto-calculate from that tag as the baseline and `--increment=minor` is never needed again.

### `latest` dist-tag on first publish — expected and unavoidable

npm always sets `latest` on a package's first publish, regardless of `--tag alpha`. The registry returns `400 Bad Request` if you try to remove it with `npm dist-tag rm`. This is a registry invariant: every package must have a `latest` tag.

**Impact is acceptable:**

- The version number `0.1.0-alpha.0` communicates pre-release status via semver
- Semver range resolution (`^0.1.0`) will not match `0.1.0-alpha.0` in consumer projects
- `latest` will naturally move to the first stable release

### Stashing pending `.release-it.json` changes

The `"preRelease": "alpha"` field was added to all `.release-it.json` files during this session. `requireCleanWorkingDir: true` will block releases while these are uncommitted. **Stash them before each release, pop after:**

```bash
git stash          # before release
# ... run release ...
git stash pop      # after release completes
```

Commit all `.release-it.json` changes together after the full release sequence.

### Why `pnpm release:all` cannot be used here

The root `release:*` sub-scripts do not append `--`, so any flag passed via `pnpm release:all -- --flag` is **not forwarded** to the inner `pnpm run release` calls. Each package must be released individually. This is documented as a pre-CI gap; it will be fixed when the CI/CD pipeline is implemented.

---

## Pre-conditions (must pass before any package is released)

### Step 1 — npm authentication

```bash
npm login --registry=https://registry.npmjs.org
```

Verify access to the `@telesign` scope:

```bash
npm whoami
npm access list packages @telesign
```

Expected: your username appears; `@telesign/boreal-web-components` (and siblings) are listed with publish access.

If using a token instead of interactive login:

```bash
echo "//registry.npmjs.org/:_authToken=<your-token>" >> ~/.npmrc
npm whoami  # must return your username
```

---

### Step 2 — Merge this feature branch to `release/current`

All `.release-it.json` configs enforce `requireBranch: "release/current"`. Release-it will reject any run from any other branch.

Create a PR from `feature/EOA-10230_implement_deployment_publishing_DG` → `release/current` and merge it (or merge directly per team workflow), then:

```bash
git checkout release/current
git pull origin release/current
```

---

### Step 3 — Verify clean state

```bash
pnpm install          # regenerate workspace symlinks from lock file
git status            # must show: nothing to commit, working tree clean
```

If `pnpm install` modified `pnpm-lock.yaml`, commit it before proceeding:

```bash
git add pnpm-lock.yaml
git commit -m "chore(workspace): * update lockfile after merge"
git push origin release/current
```

---

## Version Decision Checkpoint

### Step 4 — Dry-run to confirm the calculated version

```bash
cd packages/boreal-web-components
eval "$(fnm env)" && npx release-it --dry-run --no-npm --no-git.requireBranch --no-git.requireCleanWorkingDir --no-hooks --increment=minor
cd ../..
```

Expected output line:

```
🚀 Let's release @telesign/boreal-web-components (0.0.1...0.1.0-alpha.0)
```

> Note: the headline may show the base version without the `-alpha.0` suffix. Confirm the git tag and commit message lines show the full preRelease version before proceeding.

---

## Release Sequence

> **First releases** must be run from inside each package directory (not the workspace root) because `--increment=minor` does not forward through nested pnpm calls.
>
> For each package, release-it will:
>
> 1. Build via the `before:init` hook
> 2. Show a version prompt — review and confirm `0.1.0-alpha.0`
> 3. Write `package.json` + `CHANGELOG.md`
> 4. Commit, tag, push to Bitbucket, publish to npm with `--tag alpha`

---

### Step 5 — Release `@telesign/boreal-style-guidelines` ✅ DONE

**Published:** `0.1.0-alpha.0`

```bash
cd packages/boreal-styleguidelines
eval "$(fnm env)" && npx release-it --increment=minor
```

Verify:

```bash
npm dist-tag ls @telesign/boreal-style-guidelines
# → alpha: 0.1.0-alpha.0
# → latest: 0.1.0-alpha.0  (unavoidable on first publish — see Key Concepts)
```

---

### Step 6 — Release `@telesign/boreal-web-components` ✅ DONE

**Published:** `0.1.0-alpha.0`

```bash
cd packages/boreal-web-components
eval "$(fnm env)" && npx release-it --increment=minor
```

The `before:init` hook runs two things:

1. `turbo run build --filter=@telesign/boreal-web-components`
2. `tsx scripts/check-cem-changes.ts` — a breaking-change report from the Custom Elements Manifest; review it before confirming the version prompt

Verify:

```bash
npm dist-tag ls @telesign/boreal-web-components
# → alpha: 0.1.0-alpha.0
# → latest: 0.1.0-alpha.0  (unavoidable on first publish — see Key Concepts)
```

---

### Step 7 — Run `validate:pack:react` (pre-publish gate)

Packs real `.tgz` artifacts, installs into `react-testapp`, runs a production Vite build. **If this fails, stop — do not proceed to Step 8.**

```bash
pnpm validate:pack:react
```

Expected: `✅ Pipeline completed successfully — artifact validation passed`

---

### Step 8 — Release `@telesign/boreal-react`

```bash
cd packages/boreal-react
eval "$(fnm env)" && npx release-it --increment=minor
```

pnpm replaces `"workspace:*"` in the tarball's `package.json` with the exact published version of `@telesign/boreal-web-components` at tarball creation time. The local `package.json` on disk is never modified. This replacement only occurs because `publishPackageManager: "pnpm"` is set in `.release-it.json` — if that field were absent, release-it would invoke `npm publish`, which does not perform workspace protocol replacement and causes a registry 400 error.

> See `.claude/memory/release-it-pnpm-publish.md` for the full mechanics, the `publishCommand` trap to avoid, and the publish flow sequence diagram.

Verify:

```bash
npm dist-tag ls @telesign/boreal-react
# → alpha: 0.1.0-alpha.0
# → latest: 0.1.0-alpha.0  (unavoidable on first publish — see Key Concepts)
```

---

### Step 9 — Run `validate:pack:vue` (pre-publish gate)

Packs real `.tgz` artifacts, installs into `vue-testapp`, runs a production Vite build. **If this fails, stop — do not proceed to Step 10.**

```bash
pnpm validate:pack:vue
```

Expected: `✅ Pipeline completed successfully — artifact validation passed`

---

### Step 10 — Release `@telesign/boreal-vue`

```bash
cd packages/boreal-vue
eval "$(fnm env)" && npx release-it --increment=minor
```

The same `publishPackageManager: "pnpm"` mechanism applies — pnpm replaces `"workspace:*"` in the tarball's `package.json` with the exact published version of `@telesign/boreal-web-components` at tarball creation time.

Verify:

```bash
npm dist-tag ls @telesign/boreal-vue
# → alpha: 0.1.0-alpha.0
# → latest: 0.1.0-alpha.0  (unavoidable on first publish — see Key Concepts)
```

---

### Step 11 — Post-release verification for `@telesign/boreal-vue`

From a directory outside the monorepo:

```bash
mkdir /tmp/vue-alpha-test && cd /tmp/vue-alpha-test
npm install @telesign/boreal-vue@alpha
# → must install without error; confirm BdsBanner and BdsTypography are importable
```

---

### Step 12 — Commit `.release-it.json` changes

After all packages are released, restore and commit the config changes made during this session:

```bash
cd /path/to/boreal-ds   # workspace root
git stash pop
git add packages/boreal-styleguidelines/.release-it.json \
        packages/boreal-web-components/.release-it.json \
        packages/boreal-react/.release-it.json \
        packages/boreal-vue/.release-it.json
git commit -m "chore(release): * add preRelease alpha to release-it configs"
git push origin release/current
```

---

## Final Verification

### Step 13 — All four packages on npm

```bash
npm view @telesign/boreal-style-guidelines dist-tags
npm view @telesign/boreal-web-components dist-tags
npm view @telesign/boreal-react dist-tags
npm view @telesign/boreal-vue dist-tags
```

All must show `alpha: 0.1.0-alpha.0`. `latest` will also appear pointing to the same version — this is expected and acceptable for first publishes.

### Step 14 — Consumer install smoke test

From a directory outside the monorepo:

```bash
mkdir /tmp/alpha-test && cd /tmp/alpha-test
npm install @telesign/boreal-web-components@alpha
# → must install without error
```

### Step 15 — Notify internal test client

Share the new alpha version and these install commands:

```bash
npm install @telesign/boreal-web-components@alpha
npm install @telesign/boreal-react@alpha
npm install @telesign/boreal-vue@alpha
npm install @telesign/boreal-style-guidelines@alpha
```

---

## Subsequent Alpha Releases (after first publish)

Once all packages have a `0.1.0-alpha.0` tag, the workflow simplifies to:

```bash
# From workspace root — no extra flags needed
pnpm release:styles
pnpm release:wc
pnpm validate:pack:react && pnpm release:react
pnpm validate:pack:vue && pnpm release:vue
```

release-it reads `"preRelease": "alpha"` from `.release-it.json` and auto-calculates the version increment from commits since the last tag.

---

## Reference Files

| File                                        | Role                                                                                                                                  |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-*/.release-it.json`        | Per-package config (`"tag": "alpha"`, `"preRelease": "alpha"`, branch guard)                                                          |
| `.ai/guidelines/release-process.md`         | Authoritative release documentation                                                                                                   |
| `package.json` (root)                       | `release:styles`, `release:wc`, `release:react`, `release:vue`, `validate:pack`                                                       |
| `.claude/memory/release-it-pnpm-publish.md` | Mechanics of pnpm workspace protocol replacement, `publishPackageManager` field, `publishCommand` trap, publish flow sequence diagram |
