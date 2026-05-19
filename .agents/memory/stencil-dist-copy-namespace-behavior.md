# Stencil — `dist` Output Target Copy Behavior and Namespace Subfolder Placement

## Where Stencil Places Copied Files

Stencil's `dist` output target places all `copy` entries that use a relative `dest` path inside `dist/<namespace>/`, not at the `dist/` root. The namespace is the value of the top-level `namespace` field in `stencil.config.ts`.

For `packages/boreal-web-components`, the namespace is `"boreal-web-components"`, so:

```ts
copy: [
  { src: '…/css',  dest: 'css'  },
  { src: '…/scss', dest: 'scss' },
]
```

produces:

```
dist/boreal-web-components/css/
dist/boreal-web-components/scss/
```

The `package.json` export map expects those paths at `dist/css/` and `dist/scss/` respectively, which means the files land in the wrong location out of the box.

## The `postbuild.js` Bridge

`packages/boreal-web-components/scripts/postbuild.js` corrects the placement by promoting the Stencil-generated subdirectory contents to the expected root-level paths:

- `dist/boreal-web-components/css/` → `dist/css/`
- `dist/boreal-web-components/scss/` → `dist/scss/`

It runs automatically via the npm lifecycle hook in `packages/boreal-web-components/package.json`:

```json
"postbuild": "node scripts/postbuild.js"
```

## Critical Gotcha — Stale `dist/` Masks the Bug

Removing the `"postbuild"` key from `package.json` scripts (not deleting the script file itself) silently disables the promotion step. A stale `dist/` from a previous successful build will appear correct, making the problem invisible until the directory is cleaned.

Always run `rm -rf dist` before testing this promotion path. Without a clean build, missing or misplaced files will not surface as errors.

## Why Build Orchestration Must Live Outside `publish.js`

`scripts-boreal/bin/publish.js` packs already-built artifacts. It does not trigger builds. Invoking the pack script on a fresh clone or a clean `dist/` without a prior build produces a tarball with an empty or missing `dist/`.

Build orchestration belongs in the root `package.json` scripts via Turborepo, not inside the packaging script. This ensures the correct build is always present before packing runs. See `scripts-boreal-pack-pipeline.md` for how the Turborepo task graph enforces this.

Source: EOA-10230 deployment and publishing implementation session (2026-03-10).
