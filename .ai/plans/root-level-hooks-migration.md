---
status: done
---

# Migration Plan: Package-Level to Root-Level Git Hooks

## Executive Summary

Migrate git hooks from `packages/boreal-web-components/.husky/` to root-level to fix cross-package validation issues. This addresses the problem where commits to `apps/boreal-docs/` are incorrectly validated by `boreal-web-components` hooks.

**Problem:** Git hooks are monorepo-wide (one `.git` folder) but current setup runs package-specific validation, causing failures when committing to other packages.

**Solution:** Move hooks to root, create package-aware lint-staged configuration that only runs linting/formatting on packages that have the tools configured.

---

## Critical Files Overview

### Files to Create (Root Level)

- `/package.json` - Root package.json with husky setup
- `/.husky/pre-commit` - Root pre-commit hook
- `/.husky/commit-msg` - Root commit message validation
- `/.lintstagedrc.js` - Package-aware lint-staged configuration
- `/commitlint.config.js` - Root commitlint configuration

### Files to Modify

- `/packages/boreal-web-components/package.json` - Remove `prepare` script and hook dependencies

### Files to Delete

- `/packages/boreal-web-components/.husky/` - Entire directory (move to root first)
- `/packages/boreal-web-components/.lintstagedrc.json` - Package-level config
- `/packages/boreal-web-components/commitlint.config.ts` - Package-level config

---

## Design Decisions

### Decision 1: No Workspace Configuration (Keep Independent Packages)

**Chosen Approach:** Keep packages independent without pnpm/npm workspaces

**Rationale:**

- Current setup has no workspace configuration
- Each package manages its own dependencies independently
- Adding workspaces would be a larger architectural change
- The monorepo currently works well without workspaces

**Trade-offs:**

- ✅ Minimal changes to existing structure
- ✅ No risk of breaking existing dependency management
- ❌ Can't use `pnpm --filter` commands
- ❌ Must use `cd` to change directories in lint-staged

### Decision 2: JavaScript Configuration Files (.js vs .json)

**Chosen Approach:** Use `.lintstagedrc.js` (JavaScript) for lint-staged, `.js` for commitlint

**Rationale:**

- Need to use `cd` commands to run package-specific scripts
- JavaScript allows better control over command execution
- Can add comments explaining the configuration
- Easier to maintain and extend

### Decision 3: Package-Aware Linting (Not Monorepo-Wide)

**Chosen Approach:** Only run linting on packages that have tools configured

**Packages WITH linting:**

- `packages/boreal-web-components/` - Full ESLint, Prettier, tests
- `apps/boreal-docs/` - ESLint, Prettier (no tests in hooks)

**Packages WITHOUT linting:**

- `packages/boreal-react/` - No linting (wrapper library)
- `packages/boreal-vue/` - No linting (wrapper library)
- `packages/boreal-styleguidelines/` - No linting (test-only package)

**Rationale:**

- Don't force linting on packages that don't have it configured
- Wrapper packages (react, vue) are minimal and don't need heavy tooling
- Can add linting to other packages later without changing root hooks

### Decision 4: Commit Message Format

**Chosen Approach:** Keep existing commit types, add optional scope enforcement

**Current commit types:** feat, fix, docs, build, ci, refactor, revert, style, chore, ticket, perf

**Scope pattern observed in repo:** EOA-XXXX ticket numbers in commit messages (not in scope position)

**Configuration:**

- Keep all 11 existing commit types (including `ticket` type)
- Make scope optional (not enforced)
- Document recommended format: `type(package): EOA-XXXX message`
- Examples:
  - `feat(web-components): EOA-9176 add new button component`
  - `fix(docs): EOA-9606 correct installation instructions`

**Rationale:**

- Maintains backward compatibility with existing commits
- Doesn't disrupt team's current workflow
- EOA ticket numbers can stay in the message body
- Scope helps identify which package is affected (useful for monorepo)

---

## Implementation Steps

### Phase 1: Backup Current Configuration

```bash
# 1. Create backup directory
mkdir -p /Users/dgonzalez/projects/src/boreal-ds/.backup-hooks

# 2. Backup current hooks configuration
cp -r /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/.husky .backup-hooks/
cp /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/.lintstagedrc.json .backup-hooks/
cp /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/commitlint.config.ts .backup-hooks/
cp /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/package.json .backup-hooks/

# 3. Note current git config
git config core.hooksPath > .backup-hooks/previous-hooks-path.txt
```

### Phase 2: Create Root Package.json

Create `/package.json`:

```json
{
  "name": "@boreal-ds/root",
  "version": "1.0.0",
  "private": true,
  "description": "Boreal Design System Monorepo",
  "scripts": {
    "prepare": "husky"
  },
  "devDependencies": {
    "@commitlint/cli": "^20.3.1",
    "@commitlint/config-conventional": "^20.3.1",
    "husky": "^9.1.7",
    "lint-staged": "^16.2.7"
  }
}
```

**Why this structure:**

- `private: true` - Root package won't be published
- `prepare` script runs `husky` (Husky 9.x simplified API)
- DevDependencies match versions from boreal-web-components
- Minimal configuration, focused only on git hooks

### Phase 3: Create Root Commitlint Configuration

Create `/commitlint.config.js`:

```javascript
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Keep all existing commit types from boreal-web-components
    "type-enum": [
      2,
      "always",
      [
        "feat", // New feature
        "fix", // Bug fix
        "docs", // Documentation changes
        "build", // Build system changes
        "ci", // CI/CD changes
        "refactor", // Code refactoring
        "revert", // Revert previous commit
        "style", // Code style changes (formatting)
        "chore", // Maintenance tasks
        "ticket", // Ticket-related changes
        "perf", // Performance improvements
      ],
    ],
    // Scope is optional but recommended
    "scope-empty": [0], // Allow commits without scope
    // Recommended scopes (not enforced)
    "scope-enum": [
      1, // Warning level (not blocking)
      "always",
      ["web-components", "docs", "react", "vue", "styleguidelines", "root"],
    ],
  },
};
```

### Phase 4: Create Root Lint-Staged Configuration

Create `/.lintstagedrc.js`:

```javascript
module.exports = {
  // ============================================
  // BOREAL WEB COMPONENTS (Stencil package)
  // ============================================
  "packages/boreal-web-components/src/**/*.{css,scss}": (filenames) => {
    return `cd packages/boreal-web-components && npm run format`;
  },
  "packages/boreal-web-components/src/**/*.{js,jsx,ts,tsx}": (filenames) => {
    const commands = [
      "cd packages/boreal-web-components && npm run lint:fix",
      "cd packages/boreal-web-components && npm run format",
      "cd packages/boreal-web-components && npm run test -- -- --findRelatedTests",
    ];
    return commands;
  },

  // ============================================
  // BOREAL DOCS (Storybook app)
  // ============================================
  "apps/boreal-docs/**/*.{ts,tsx}": (filenames) => {
    const commands = [
      "cd apps/boreal-docs && npm run lint:fix",
      "cd apps/boreal-docs && npm run format",
    ];
    return commands;
  },
  "apps/boreal-docs/**/*.{js,json,css,md}": (filenames) => {
    return `cd apps/boreal-docs && npm run format`;
  },

  // ============================================
  // NOTE: boreal-react, boreal-vue, and boreal-styleguidelines
  // are intentionally excluded as they don't have linting tools configured
  // ============================================
};
```

**Why this structure:**

- Uses functions to run commands in correct directory context
- Preserves existing behavior for boreal-web-components (lint, format, test)
- Adds boreal-docs with its own rules (lint, format, no tests)
- Clear comments explaining which packages are included/excluded
- Each package uses its own npm scripts (maintains independence)

### Phase 5: Create Root Husky Hooks

#### Create `/.husky/pre-commit`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo ""
echo "🔍 Running pre-commit checks on changed files..."
echo ""

npx lint-staged
```

#### Create `/.husky/commit-msg`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo ""
echo "🔒 Commit message format is enforced across the monorepo!"
echo ""
echo "✅ Use format: type(scope): message"
echo "🔧 Example: feat(web-components): EOA-9176 add button component"
echo "🔧 Example: fix(docs): EOA-9606 correct installation guide"
echo ""
echo "🔹 Valid types: feat, fix, docs, chore, refactor, style, build, ci, etc."
echo "🔹 Recommended scopes: web-components, docs, react, vue, styleguidelines"
echo ""

npx commitlint --edit $1
```

### Phase 6: Update Package-Level Configuration

#### Modify `/packages/boreal-web-components/package.json`:

Remove these sections:

- `"prepare": "cd ../.. && husky packages/boreal-web-components/.husky"` (from scripts)
- `"@commitlint/cli": "^20.3.1"` (from devDependencies)
- `"@commitlint/config-conventional": "^20.3.1"` (from devDependencies)
- `"husky": "^9.1.7"` (from devDependencies)
- `"lint-staged": "^16.2.7"` (from devDependencies)

Keep these scripts (still needed for the package):

- `"lint-staged": "lint-staged --debug"` - Keep this for local testing
- `"lint": "eslint"`
- `"lint:fix": "eslint --fix"`
- `"format": "prettier --write 'src/**/*.{ts,tsx,css,scss,json}'"`
- `"format:check": "prettier --check 'src/**/*.{ts,tsx,css,scss,json}'"`

**Why:** Package still needs its own lint/format scripts for:

- Local development (developers running npm run lint manually)
- CI/CD pipelines
- Being called by root lint-staged configuration

### Phase 7: Clean Up Package-Level Files

```bash
# Delete package-level hook configuration
rm -rf /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/.husky
rm /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/.lintstagedrc.json
rm /Users/dgonzalez/projects/src/boreal-ds/packages/boreal-web-components/commitlint.config.ts
```

### Phase 8: Install Root Dependencies and Initialize Hooks

```bash
# 1. Navigate to root
cd /Users/dgonzalez/projects/src/boreal-ds

# 2. Install root dependencies (this also runs the prepare script)
npm install

# 3. Verify hooks were installed
ls -la .husky/

# 4. Check git config
git config core.hooksPath
# Should output: .husky/_
```

### Phase 9: Test the Configuration

#### Test 1: Verify hook installation

```bash
# Check that hooks are executable and in the right place
ls -la .husky/
cat .husky/pre-commit
cat .husky/commit-msg
```

Expected: Both files exist and are executable (755 permissions)

#### Test 2: Test commit message validation

```bash
# Test invalid commit message (should FAIL)
git commit --allow-empty -m "invalid message"
# Expected: Commitlint error about format

# Test valid commit message (should SUCCEED)
git commit --allow-empty -m "feat(web-components): test root-level hooks"
# Expected: Commit succeeds
```

#### Test 3: Test pre-commit hooks with boreal-web-components changes

```bash
# Make a small change to web-components
echo "// test comment" >> packages/boreal-web-components/src/index.ts

# Stage the file
git add packages/boreal-web-components/src/index.ts

# Try to commit (hooks should run linting on web-components)
git commit -m "test(web-components): verify pre-commit hooks"

# Verify hooks ran
# Expected: See "Running pre-commit checks" message and lint output
```

#### Test 4: Test pre-commit hooks with boreal-docs changes

```bash
# Make a small change to docs
echo "// test comment" >> apps/boreal-docs/src/stories/example.ts

# Stage the file
git add apps/boreal-docs/src/stories/example.ts

# Try to commit (hooks should run linting on docs, NOT web-components)
git commit -m "docs(docs): verify docs-specific hooks"

# Verify hooks ran on docs only
# Expected: See linting output for docs, not web-components
```

#### Test 5: Test commits to packages without linting

```bash
# Make a change to boreal-react (no linting configured)
echo "// test" >> packages/boreal-react/lib/index.ts

# Stage the file
git add packages/boreal-react/lib/index.ts

# Try to commit (hooks should NOT fail, react has no linting)
git commit -m "chore(react): test hook skipping"

# Expected: Commit succeeds without running linting (no tools configured)
```

#### Test 6: Test cross-package commits

```bash
# Make changes to multiple packages
echo "// test" >> packages/boreal-web-components/src/index.ts
echo "// test" >> apps/boreal-docs/src/stories/example.ts

# Stage both files
git add packages/boreal-web-components/src/index.ts
git add apps/boreal-docs/src/stories/example.ts

# Commit both (should run appropriate hooks for each package)
git commit -m "chore(root): test multi-package commit"

# Expected: Hooks run for both web-components AND docs
```

---

## Rollback Strategy

If something goes wrong, here's how to restore the old configuration:

### Quick Rollback (Restore Package-Level Hooks)

```bash
cd /Users/dgonzalez/projects/src/boreal-ds

# 1. Unset root-level hooks
git config --unset core.hooksPath

# 2. Restore boreal-web-components configuration
cp -r .backup-hooks/.husky packages/boreal-web-components/
cp .backup-hooks/.lintstagedrc.json packages/boreal-web-components/
cp .backup-hooks/commitlint.config.ts packages/boreal-web-components/
cp .backup-hooks/package.json packages/boreal-web-components/

# 3. Reinstall boreal-web-components dependencies
cd packages/boreal-web-components
npm install

# 4. Verify old hooks work
git config core.hooksPath
# Should output: packages/boreal-web-components/.husky/_
```

### Clean Rollback (Remove Root Configuration)

```bash
# Delete root-level files created during migration
rm /Users/dgonzalez/projects/src/boreal-ds/package.json
rm /Users/dgonzalez/projects/src/boreal-ds/package-lock.json
rm -rf /Users/dgonzalez/projects/src/boreal-ds/node_modules
rm -rf /Users/dgonzalez/projects/src/boreal-ds/.husky
rm /Users/dgonzalez/projects/src/boreal-ds/.lintstagedrc.js
rm /Users/dgonzalez/projects/src/boreal-ds/commitlint.config.js

# Then follow Quick Rollback steps above
```

---

## Post-Migration Tasks

### 1. Update Documentation

Update `/README.md` to mention:

- Git hooks are now configured at root level
- All commits are validated for message format
- Pre-commit checks run automatically on staged files
- Which packages have linting configured

### 2. Team Communication

Notify the team:

- Git hooks have moved to root level
- Commit message format is now enforced for ALL commits (not just web-components)
- Recommended commit format: `type(package): EOA-XXXX message`
- How to run linting manually if needed

### 3. CI/CD Verification

Ensure CI/CD pipelines still work:

- Pipelines should not rely on package-level hooks
- Linting should be run explicitly in CI (not via hooks)
- Tests should still pass

### 4. Optional: Add Scope Enforcement

If the team wants stricter commit format in the future, change in `/commitlint.config.js`:

```javascript
// Change from warning to error
'scope-enum': [
  2,  // Error level (blocking)
  'always',
  ['web-components', 'docs', 'react', 'vue', 'styleguidelines', 'root'],
],
// Require scope to be present
'scope-empty': [2, 'never'],
```

---

## Success Criteria

✅ Commits to `apps/boreal-docs/` no longer validated by `boreal-web-components` rules

✅ Commits to `packages/boreal-web-components/` still run full lint/format/test checks

✅ Commits to `packages/boreal-react/` or `boreal-vue/` don't fail due to missing linting tools

✅ All commits validated for conventional commit message format

✅ Cross-package commits run appropriate checks for each package

✅ Git config shows hooks path as `.husky/_` (not package-specific)

✅ No duplicate dependency installations (husky, commitlint, lint-staged only at root)

---

## Additional Notes

### Why This Approach Works

1. **Fixes the Cross-Package Issue:** Hooks now understand which package is being modified and apply the correct rules

2. **Maintains Package Independence:** Each package still has its own lint/format scripts and can be developed independently

3. **No Workspace Complexity:** Avoids adding pnpm/npm workspaces configuration (which would be a larger change)

4. **Backward Compatible:** Preserves existing commit types and patterns

5. **Extensible:** Easy to add linting to other packages later (just add to `.lintstagedrc.js`)

### Future Improvements

- **Add linting to wrapper packages:** If boreal-react and boreal-vue grow, add ESLint/Prettier and include them in lint-staged

- **Consider workspaces:** If the team needs better dependency management, migrate to pnpm workspaces

- **Automate changelog generation:** With conventional commits enforced, tools like `standard-version` or `semantic-release` could auto-generate changelogs

- **Add pre-push hooks:** Consider adding hooks that run tests before pushing to remote

### Troubleshooting

**Problem:** Hooks not running after migration

```bash
# Solution: Reinstall hooks
npm run prepare
git config core.hooksPath
```

**Problem:** Lint-staged running on wrong package

```bash
# Solution: Check glob patterns in .lintstagedrc.js
# Ensure paths match exactly: packages/boreal-web-components/src/**/*.ts
```

**Problem:** Commits taking too long

```bash
# Solution: Reduce hook checks (e.g., remove tests from pre-commit)
# Or skip hooks for emergency commits: git commit --no-verify
```

**Problem:** "command not found" errors in hooks

```bash
# Solution: Ensure commands use full paths or package-relative paths
# Use: cd packages/boreal-web-components && npm run lint
# Not: npm run lint (wrong context)
```

---

## Estimated Time

- **Phase 1-2 (Backup & Create Root Files):** 10 minutes
- **Phase 3-5 (Configuration Files):** 15 minutes
- **Phase 6-7 (Clean Up Package Files):** 10 minutes
- **Phase 8 (Install & Initialize):** 5 minutes
- **Phase 9 (Testing):** 20-30 minutes
- **Documentation Updates:** 15 minutes

**Total:** ~75-90 minutes for complete migration and testing

---

## Summary

This migration moves git hooks from package-level to root-level, fixing the cross-package validation issue while maintaining package independence. The solution is simple, extensible, and doesn't require adding workspace management tools. After migration, commits to any package will use the correct validation rules for that package, and the team can continue using their existing commit message patterns.
