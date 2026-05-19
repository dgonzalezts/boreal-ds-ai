# Sass Path Normalization — Windows Backslash and `require.resolve` in pnpm Workspaces

## The Problem — Backslashes in Sass Configuration

Sass has its own path parser and treats backslashes as escape characters, not directory separators. `path.resolve` returns OS-native separators — on Windows, these are backslashes. Any path constructed with `path.resolve` and passed directly to a Sass configuration field (`injectGlobalPaths`, `includePaths`, etc.) will cause Sass to fail silently or with a misleading error (`Can't find stylesheet to import` at line 1:1) on Windows.

Line 1:1 is the location of the `injectGlobalPaths` prepend, so that error location is the diagnostic signal: it means an injected global path could not be resolved, not that the component's own imports are wrong.

This issue is invisible on macOS because:
- macOS uses forward slashes natively
- Stencil's `.stencil/` cache stores compiled SCSS — on a warm cache, Stencil never re-invokes the Sass compiler, so the bad path is never evaluated

## The Fix

Apply `.map(p => p.replace(/\\/g, '/'))` to every array of paths passed to Sass configuration. Apply it at the array level so all present and future entries are covered without the risk of forgetting:

```typescript
injectGlobalPaths: [
  resolve(styleGuidelinesDir, 'stencil/_index.scss'),
  resolve(__dirname, 'src/styles/_commons.scss'),
  resolve(__dirname, 'src/styles/_interactions.scss'),
].map(p => p.replace(/\\/g, '/')),
```

This pattern applies to `injectGlobalPaths`, `includePaths`, and any other Stencil/Sass configuration field that accepts file paths.

## The Problem — `require.resolve` in pnpm Workspaces

`require.resolve('@telesign/boreal-style-guidelines/stencil')` is unreliable for locating package files in a pnpm workspace. On macOS, it resolves to a symlink path that Sass can follow. On Windows and Linux CI with a cold installation, `require.resolve` follows pnpm's virtual store symlinks to the real path deep inside `.pnpm/`, such as:

```
node_modules/.pnpm/@telesign+boreal-style-guidelines@0.x.y/node_modules/@telesign/boreal-style-guidelines/stencil/_index.scss
```

When Sass tries to resolve relative `@import` statements from that deeply-nested real path, it cannot find sibling files, so all imports in the injected file fail.

## The Fix

Construct paths from a known variable already resolved at config-load time instead of using `require.resolve`. In `stencil.config.ts`, the `styleGuidelinesDir` variable is already defined from `import.meta.resolve` or an equivalent mechanism — use it directly:

```typescript
// Unreliable: follows virtual store symlinks on pnpm+Windows
require.resolve('@telesign/boreal-style-guidelines/stencil')

// Reliable: resolves from the known package directory variable
resolve(styleGuidelinesDir, 'stencil/_index.scss')
```

See `package-dir-import-meta-resolve.md` for the correct pattern to locate an ESM-only package's directory for use as `styleGuidelinesDir`.

## Related

- `stencil-sass-inject-global-paths-constraint.md` — standalone compilation constraint (separate issue: `$boreal-*` variable availability, not path resolution)
- `package-dir-import-meta-resolve.md` — correct pattern for resolving ESM-only package directories

## Source

Windows-specific `pnpm dev:components` hang debugging session (2026-04-08). Reproduced and diagnosed via GitHub Actions `windows-latest` and `ubuntu-latest` runners.
