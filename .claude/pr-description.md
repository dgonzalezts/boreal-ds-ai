# PR Title

fix(multiple)!: EOA-18749 declare React 19 and Vue 3.5 peer dependencies in the wrappers

---

# PR Body

## ⚠️ BREAKING CHANGE Notice

**Type:**

- [x] Minimum version requirement change (Node.js, browsers, dependencies)

**Impact Level:**

- [x] **Low** — Affects only consumers on React below 19 or Vue below 3.5 (including Vue 2). Migration path below.

---

## Description of Breaking Change

`@pxglobal/boreal-react` and `@pxglobal/boreal-vue` now declare `peerDependencies`:

| Package | Peer dependency |
| --- | --- |
| `@pxglobal/boreal-react` | `react` `^19.0.0`, `react-dom` `^19.0.0` |
| `@pxglobal/boreal-vue` | `vue` `^3.5.0` |

Until now the wrappers declared no peers. React and Vue were devDependencies only, so consumers had no install-time signal about supported versions. The ranges match what the wrappers are built and validated against (React `^19.2.1`, Vue `^3.5.25`).

The Storybook "Framework Integration" page gets a callout stating the supported versions and the alternative for older apps. The versions in the callout are read from the wrapper `package.json` files.

---

## Justification

- Makes the supported framework versions explicit and enforced by the package manager (npm 7+ and pnpm install and check peers).
- Starts with a narrow range on purpose: widening a peer range later is not breaking, narrowing it is.
- React 19 is the first React version with full custom-element support, which the wrapper relies on.

---

## Migration Path

- **React 19 and Vue 3.5 or newer:** no action. Peers are already satisfied.
- **React below 19, or Vue below 3.5:** upgrade, or use `@pxglobal/boreal-web-components` directly, without a wrapper.
- **Vue 2:** the wrapper is not supported. Use the web components directly and configure Vue 2 to treat `bds-*` tags as custom elements. This path has not been tested in a Vue 2 app yet.

---

## Affected Packages

| Package | Change | Expected release |
| --- | --- | --- |
| `@pxglobal/boreal-react` | adds `peerDependencies` | `0.15.0` (breaking, below 1.0) |
| `@pxglobal/boreal-vue` | adds `peerDependencies` | `0.15.0` (breaking, below 1.0) |
| `@pxglobal/boreal-web-components` | none | not released |
| `@pxglobal/boreal-style-guidelines` | none | not released |

Storybook (`apps/boreal-docs`) is outside every package's path scope, so it does not trigger a release.

---

## Testing Conducted

**Automated:**

- [x] `pnpm validate:all` passes against the committed state (React and Vue pack validation).
- [x] Pre-push unit tests pass (4199 tests).
- [x] Packed tarballs checked: both contain the new `peerDependencies`, and `@pxglobal/boreal-web-components` is a concrete version (`0.14.1`), not `workspace:*`.

**Manual:**

- [ ] Storybook "Framework Integration" page renders the new callout with the correct versions.
- [ ] Reviewer confirms the ranges.

Not tested: installing the wrappers on React 18 or Vue 2 to see the actual peer warnings.

---

## Additional Remarks

- Ticket: release process hardening (EOA-18749).
- `validate:pack` restores `package.json` and the lockfile from git on exit, so changes to those files must be committed before running it.
- **Merge reminder:** use Squash and Merge and keep the title exactly as above. The `!` must stay in the title, because a `BREAKING CHANGE:` footer in Bitbucket's indented squash list is ignored.
- Follow-ups, not in this PR: a survey of the React and Vue versions used by target apps, a Vue 2 spike with the raw web components, and a pack validation against the lowest supported versions if the ranges are widened.

---

## References

Refs EOA-18749

---

## Checklist

- [x] Follows conventional commit format with `!`: `type(scope)!: TICKET description`
- [x] Ticket reference included
- [x] Title is 88 characters (limit 100) and uses an allowed scope
- [x] `validate:all` passes
- [x] Storybook docs updated
- [x] Migration path described
- [ ] Reviewer confirmed the version ranges
