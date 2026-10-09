# release-it + pnpm publish — Mechanics and Gotchas

Source: First alpha release session (2026-03-10), release-it `19.2.4`. Re-verified in the first `@pxglobal` release (2026-10-09), release-it `21.1.0`: same mechanics. The published React and Vue tarballs pin `@pxglobal/boreal-web-components` at the exact version (`0.14.0`). The publish step shows as `npm publish` in release-it's output but runs `pnpm publish` because of `publishPackageManager`.

---

## Critical: `publishCommand` is not a valid release-it option

Adding `"publishCommand": "pnpm publish --no-git-checks"` to a `.release-it.json` file is **silently ignored**. The field does not exist in release-it's npm plugin. When the field is present, release-it falls back to `npm publish`, bypassing pnpm entirely.

The source of this behavior in `node_modules/release-it/lib/plugin/npm/npm.js`:

```js
const publishPackageManager = this.options.publishPackageManager || 'npm';
return this.exec([publishPackageManager, 'publish', ...args], { ... });
```

The only supported field for overriding the publish executable is `publishPackageManager`.

---

## Correct release-it npm block for pnpm publish

```json
"npm": {
  "publish": true,
  "publishPath": ".",
  "tag": "latest",
  "publishPackageManager": "pnpm",
  "publishArgs": ["--no-git-checks"]
}
```

| Field | Purpose |
|---|---|
| `publishPackageManager` | Swaps the publish executable (default: `npm`). Setting `"pnpm"` triggers workspace protocol replacement. |
| `publishArgs` | Extra flags appended to the publish command. `--no-git-checks` is pnpm-specific. |
| `tag` | npm dist-tag (equivalent to `--tag latest`; it was `alpha` until the move to `@pxglobal`, when the alpha suffix and dist-tag were dropped). |

When `publishPackageManager` is not `npm`, release-it automatically omits the `--workspaces=false` flag it would otherwise append for npm.

---

## pnpm workspace protocol replacement

`workspace:*` in `dependencies` is resolved by pnpm **at tarball creation time only**. The `package.json` on disk is never modified. The tarball's `package.json` receives the resolved version string.

| Protocol in `package.json` | Published as (if referenced package is at `0.14.0`) |
|---|---|
| `workspace:*` | `0.14.0` (exact pin) |
| `workspace:^` | `^0.14.0` (caret range) |
| `workspace:~` | `~0.14.0` (tilde range) |

Workspace replacement only occurs when pnpm is the publish executor. If `npm publish` runs instead (e.g. because `publishCommand` was used or `publishPackageManager` was omitted), the raw `workspace:*` string leaks into the published tarball and the registry rejects it with a 400 error.

---

## `workspace:*` (exact pin) is the policy while below 1.0

`workspace:^` (caret range) mirrors the Beeq reference project pattern, but caret ranges only make sense once semver guarantees are in force. While the library is below 1.0 (alpha, `preMajor`):

- Exact pin ensures consumers receive the specific tested combination of packages; the wrappers are always released after web-components, so they never lag behind.
- Below 1.0 a caret range only spans patch versions (`^0.14.0` covers `0.14.x`), and breaking changes bump the minor version, so a range would add little.

Use `workspace:^` only when the package reaches a stable release baseline.

---

## Why `dependencies` (not `peerDependencies`) for internal packages

Placing `@pxglobal/boreal-web-components` in `peerDependencies` of `@pxglobal/boreal-react` shifts the installation burden to the consumer. They must install the peer explicitly. The correct pattern keeps it in `dependencies` so pnpm includes it automatically when the consumer installs `@pxglobal/boreal-react`.

The `peerDependencies` approach was explored as a workaround for the `workspace:*` leak, but the root fix was ensuring pnpm executes the publish step (via `publishPackageManager: "pnpm"`).

---

## Full publish flow

The sequence (prerelease validation, path-scoped bump, changelog, `pnpm publish` with the pin replacement, npm's approval step, commit/tag/push) is in `ai-docs/diagrams/release-it-publish-flow.md`. The procedure is in `RELEASING.md`.

---

## Affected files

| File | Change made in the first alpha release session |
|---|---|
| `packages/boreal-react/.release-it.json` | Replaced invalid `publishCommand` with `publishPackageManager: "pnpm"` and `publishArgs: ["--no-git-checks"]` |
| `packages/boreal-vue/.release-it.json` | Same fix |
| `packages/boreal-react/package.json` | Kept `@pxglobal/boreal-web-components: "workspace:*"` in `dependencies` (not `peerDependencies`) |

---

## Beeq reference pattern (for context)

`@beeq/react` places `@beeq/core: "^1.9.0"` in `dependencies`, not `peerDependencies`. Beeq uses Nx (not pnpm workspaces), so no `workspace:*` protocol is involved. The Boreal DS equivalent achieves the same auto-install behaviour via `workspace:*` in `dependencies` combined with `publishPackageManager: "pnpm"`.
