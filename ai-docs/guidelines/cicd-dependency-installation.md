# CI/CD Dependency Installation Plan

## Overview

This document outlines the dependency installation strategy for our CI/CD pipeline using pnpm in our monorepo.

## Current Setup

### Package Manager

- **Tool**: pnpm v10.7.1
- **Workspace**: Monorepo structure with multiple packages

### Configuration Files

#### `.npmrc` (apps/boreal-docs/)

```
enable-pre-post-scripts=true
ignore-scripts=false
```

**Purpose**:

- Allows lifecycle scripts (pre/post install) to execute
- Required for packages like `esbuild` that download platform-specific binaries during postinstall

## CI/CD Installation Command

### Primary Command

```bash
pnpm install --frozen-lockfile
```

**Why this command:**

- ✅ Ensures reproducible builds
- ✅ Fails if lockfile is out of sync with package.json
- ✅ Doesn't modify the lockfile
- ✅ Equivalent to `npm ci`

### Enhanced Command (Recommended)

```bash
pnpm install --frozen-lockfile --prefer-offline
```

**Additional benefits:**

- Prioritizes local cache over network requests
- Faster and more reliable in CI environments
- Reduces network dependency

## Execution Location

**Run from repository root:**

```bash
cd /path/to/boreal-ds
pnpm install --frozen-lockfile
```

pnpm automatically handles workspace dependencies across all packages.

## Important Considerations

### 1. Script Execution

- The `.npmrc` configuration allows all build scripts to run
- This is necessary for dependencies like `esbuild`, `playwright`, etc.
- Build scripts execute during installation to prepare platform-specific binaries

### 2. Security

- Current configuration trusts all dependencies to run scripts
- For enhanced security, consider using `pnpm approve-builds` during development
- Review dependencies regularly for security concerns

### 3. Lockfile Management

- **Never commit** changes to `pnpm-lock.yaml` from CI
- CI should only read the lockfile, never write to it
- If lockfile is outdated, the build should fail (caught by `--frozen-lockfile`)

### 4. Cache Strategy

- Configure CI to cache the pnpm store directory
- Default location: `~/.pnpm-store`
- Significantly speeds up subsequent builds

## Example CI Configuration

### GitHub Actions

```yaml
steps:
  - uses: actions/checkout@v4

  - uses: pnpm/action-setup@v3
    with:
      version: 10.7.1

  - uses: actions/setup-node@v4
    with:
      node-version: 22
      cache: "pnpm"

  - name: Install dependencies
    run: pnpm install --frozen-lockfile --prefer-offline

  - name: Build
    run: pnpm build
```

### GitLab CI

```yaml
install:
  script:
    - corepack enable
    - pnpm install --frozen-lockfile --prefer-offline
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .pnpm-store
```

## Troubleshooting

### Issue: Build scripts are ignored

**Solution**: Ensure `.npmrc` contains:

```
enable-pre-post-scripts=true
ignore-scripts=false
```

### Issue: Lockfile out of sync

**Solution**:

1. Run `pnpm install` locally
2. Commit the updated `pnpm-lock.yaml`
3. Push changes

### Issue: Platform-specific binary failures

**Solution**: Ensure build scripts run (check `.npmrc`) and that the CI platform matches deployment target

## Files to Commit

✅ Must be committed:

- `pnpm-lock.yaml`
- `apps/boreal-docs/.npmrc`
- `package.json` files

❌ Should NOT be committed:

- `node_modules/`
- `.pnpm-store/`

## Future Improvements

- [ ] Consider selective script approval using `pnpm.onlyBuiltDependencies` for enhanced security
- [ ] Implement lockfile verification in pre-commit hooks
- [ ] Monitor and optimize pnpm store cache size
- [ ] Document platform-specific dependencies

---

**Last Updated**: January 19, 2026
**Related Issue**: Build script warnings during `pnpm install`
