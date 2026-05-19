# Git Branch Syncing Guide

## Overview

This guide covers how to sync branches between the `github` remote and `origin` (Bitbucket) remote, including bidirectional syncing for the `main` branch and unidirectional syncing for feature branches.

### Prerequisites

Ensure both remotes are configured:

- `github`: https://github.com/jberrocal-tls/boreal-ds.git
- `origin`: ssh://git@bitbucket.c11.telesign.com:7999/dev/boreal-ds.git

Verify with:

```bash
git remote -v
```

---

## Branch Syncing Strategy

### Main Branch Syncing (Bidirectional)

The `main` branch serves as the **integration point** between both remotes:

- Changes from `github/main` should be synced to `origin/main`
- Changes from `origin/main` should be synced to `github/main`
- Both remotes should have an aligned `main` branch history

### Release Branch Strategy

- **`origin` (Bitbucket)**: Uses `release/current` as the default branch for production releases
- **`github`**: Continues using `main` as the default branch
- The `release/current` branch is **origin-only** and does not need to be replicated to GitHub
- Integration work flows through the `main` branch

### Feature Branch Syncing (Unidirectional)

Feature branches can be synced from one remote to another as needed, typically from `github` to `origin`.

---

## Syncing the Main Branch Bidirectionally

When both `github/main` and `origin/main` have diverged (each has commits the other doesn't have), follow this workflow:

### Step 1: Fetch Latest from Both Remotes

```bash
git fetch github
git fetch origin
```

### Step 2: Check for Divergence

```bash
# Check what commits are in origin/main but not in github/main
git log --oneline github/main..origin/main

# Check what commits are in github/main but not in origin/main
git log --oneline origin/main..github/main
```

If both commands show commits, the branches have diverged.

### Step 3: Merge to Unify History

**Option A: Merge via local main branch (Recommended)**

```bash
# Checkout local main
git checkout main

# Ensure it's up to date with one remote (e.g., origin)
git pull origin main

# Merge changes from github
git merge github/main

# Resolve any conflicts if needed
# After resolving, commit the merge

# Push unified history to both remotes
git push origin main
git push github main
```

**Option B: Direct remote-to-remote merge**

```bash
# Push github's main to origin (creating a non-fast-forward update)
git push origin github/main:main

# Then fetch and push back to github
git fetch origin
git push github origin/main:main
```

### Step 4: Verify Alignment

```bash
# Both should now point to the same commit
git log --oneline github/main -1
git log --oneline origin/main -1
```

---

## Handling Divergent Main Branch History

If you encounter a divergent history scenario:

### Prevention Strategy

1. **Always sync main bidirectionally** after merging pull requests on either remote
2. **Use main as the integration branch** for all cross-remote work
3. **Avoid direct commits to main** on either remote without syncing

### Recovery Workflow

When divergence occurs:

```bash
# 1. Fetch everything
git fetch --all

# 2. Create a local integration branch
git checkout -b sync/main-integration origin/main

# 3. Merge github's changes
git merge github/main

# 4. Resolve conflicts if any
# Edit conflicted files, then:
git add .
git commit -m "chore: sync main branches from github and origin"

# 5. Push to both remotes
git push origin sync/main-integration:main
git push github sync/main-integration:main

# 6. Update local main
git checkout main
git pull origin main

# 7. Clean up
git branch -d sync/main-integration
```

---

## Updating Release/Current Branch with Main Changes

After syncing the `main` branch bidirectionally, you need to update the `release/current` branch on origin (Bitbucket's default branch) to include all the latest changes.

### Workflow

```bash
# 1. Checkout the release/current branch
git checkout release/current

# 2. Ensure it's up to date with origin
git pull origin release/current

# 3. Merge the unified main branch
git merge main

# 4. Resolve conflicts if any
# Edit conflicted files, then:
git add .
git commit -m "chore: update release/current with latest main changes"

# 5. Push to origin
git push origin release/current

# 6. Verify the update
git log --oneline origin/release/current -5
```

### Important Notes

- **Always update `release/current` after syncing main** to keep Bitbucket's default branch current
- The `release/current` branch should contain all work from `main` plus any release-specific changes
- This branch is **not pushed to GitHub** - it remains origin-only

---

## Syncing Release/Current Changes Back to Main

When `release/current` contains commits that aren't in `main` yet (e.g., release-specific work or features developed directly on release/current), you need to merge those changes back to `main` and sync to both remotes.

### When to Use This Workflow

- After completing release-specific development on `release/current`
- When you need to consolidate all work back into `main`
- Before starting a new development cycle

### Step 1: Check What Needs Syncing

```bash
# Check commits in release/current but not in main
git log --oneline main..release/current
```

If this shows commits, proceed with the merge.

### Step 2: Merge Release/Current to Main

```bash
# 1. Checkout main
git checkout main

# 2. Ensure main is up to date
git pull origin main

# 3. Merge release/current into main
git merge release/current

# 4. Resolve conflicts if any
# Edit conflicted files, then:
git add .
git commit -m "chore: merge release/current changes back to main"
```

### Step 3: Push to Both Remotes

```bash
# Push to origin (Bitbucket)
git push origin main

# Push to github
git push github main
```

### Step 4: Verify Sync

```bash
# Verify both remotes are aligned
git fetch --all
git log --oneline github/main -1
git log --oneline origin/main -1

# Verify the changes are present
git log --oneline --grep="<keyword-from-release>" origin/main
```

### Complete Workflow Example

```bash
# Check what needs syncing
git log --oneline main..release/current

# Merge release/current to main
git checkout main
git pull origin main
git merge release/current

# Push to both remotes
git push origin main
git push github main

# Verify alignment
git fetch --all
git log --oneline github/main -1
git log --oneline origin/main -1
```

### Important Notes

- **This creates a bidirectional flow**: `main` ↔ `release/current`
- After this sync, both `main` branches and `release/current` will have the same commits
- Future work can continue: new features → `main` → sync to both remotes → merge to `release/current`
- This keeps the integration point (`main`) as the single source of truth across both git providers

---

## Syncing Feature Branches from GitHub to Origin

### Quick Method: One-liner (No Local Checkout)

This method pushes a branch directly from one remote to another without creating a local branch.

### Steps

1. **Fetch the latest branches from github**

   ```bash
   git fetch github
   ```

2. **Verify the branch exists**

   ```bash
   git branch -r | grep github/<branch-name>
   ```

3. **Push the branch to origin**
   ```bash
   git push origin refs/remotes/github/<branch-name>:refs/heads/<branch-name>
   ```

### Example

```bash
# Fetch all branches from github
git fetch github

# Verify the branch exists
git branch -r | grep github/feature/create-automatic-local-packages

# Push to origin
git push origin refs/remotes/github/feature/create-automatic-local-packages:refs/heads/feature/create-automatic-local-packages
```

---

## Alternative Method: Via Local Checkout

Use this method if you want to work on the branch locally or need to merge changes.

### Steps

1. **Fetch the latest from github**

   ```bash
   git fetch github
   ```

2. **Checkout the branch locally**

   ```bash
   git checkout -b <branch-name> github/<branch-name>
   ```

3. **Push to origin**
   ```bash
   git push -u origin <branch-name>
   ```

### Example

```bash
git fetch github
git checkout -b feature/create-automatic-local-packages github/feature/create-automatic-local-packages
git push -u origin feature/create-automatic-local-packages
```

---

## Syncing All Branches

To sync all branches from github to origin:

```bash
# Fetch all branches
git fetch github

# Sync each branch
git branch -r | grep 'github/' | grep -v 'HEAD' | sed 's/github\///' | while read branch; do
  echo "Syncing branch: $branch"
  git push origin "refs/remotes/github/$branch:refs/heads/$branch"
done
```

---

## Merging Changes Between Branches

If both remotes have the same branch with different commits, use merge instead of direct push:

```bash
# Checkout the local branch
git checkout <branch-name>

# Merge changes from github
git merge github/<branch-name>

# Resolve conflicts if needed, then push
git push origin <branch-name>
```

---

## Troubleshooting

### Error: "src refspec does not match any"

**Cause**: The branch doesn't exist on the remote you're trying to fetch from.

**Solution**:

1. Fetch the latest: `git fetch github`
2. List available branches: `git branch -r | grep github`
3. Verify the branch name is correct

### Error: Push rejected (non-fast-forward)

**Cause**: The branch on origin has commits that github doesn't have.

**Solution**: Use the merge method instead of direct push to preserve both histories.

### Error: "matched multiple remote tracking branches"

**Error message**:

```
fatal: 'feature/create-automatic-local-packages' matched multiple (2) remote tracking branches
```

**Cause**: The branch exists on multiple remotes (e.g., both `github` and `origin`), and git doesn't know which one to use.

**Solutions**:

1. **Specify the remote explicitly (Recommended)**:

   ```bash
   # Checkout from origin
   git checkout --track origin/<branch-name>

   # OR checkout from github
   git checkout --track github/<branch-name>
   ```

2. **Use the `-b` flag with explicit remote**:

   ```bash
   # Create local branch tracking origin
   git checkout -b <branch-name> origin/<branch-name>

   # OR create local branch tracking github
   git checkout -b <branch-name> github/<branch-name>
   ```

3. **Set a default remote for checkouts**:

   ```bash
   # Set origin as default remote
   git config checkout.defaultRemote origin

   # Now this will work
   git checkout <branch-name>
   ```

4. **Check which remotes have the branch**:
   ```bash
   git branch -r | grep <branch-name>
   ```

**Recommendation**: When syncing from `github` to `origin`, checkout from `origin` after syncing:

```bash
git checkout --track origin/<branch-name>
```

---

---

## Updating Local References to Origin Remote Branches

### Fetch Latest Changes

```bash
# Fetch all branches from origin
git fetch origin

# Fetch from all remotes
git fetch --all

# Fetch and prune deleted branches
git fetch origin --prune
```

### Update Your Current Local Branch

```bash
# Pull changes from origin for current branch
git pull origin <branch-name>

# Or simply (if tracking is set up)
git pull
```

### View Updated Remote Branches

```bash
# List all remote branches
git branch -r

# Show origin branches only
git branch -r | grep origin
```

### Update Local Branch from Remote

```bash
# Switch to the branch
git checkout <branch-name>

# Pull latest changes
git pull origin <branch-name>
```

### Reset Local Branch to Match Remote Exactly

If you want to discard local changes and match the remote exactly:

```bash
git checkout <branch-name>
git reset --hard origin/<branch-name>
```

**Important**: `git fetch` only updates your local references to remote branches (like `origin/main`). It doesn't modify your local working branches. You need `git pull` or `git merge` to actually update your local branches with the fetched changes.

---

## Summary

### Main Branch Bidirectional Sync

**When main branches have diverged:**

```bash
# Fetch from both remotes
git fetch --all

# Merge locally
git checkout main
git pull origin main
git merge github/main

# Push to both remotes
git push origin main
git push github main
```

### Feature Branch Sync (GitHub → Origin)

**Quick sync (recommended for new branches):**

```bash
git fetch github
git push origin refs/remotes/github/<branch-name>:refs/heads/<branch-name>
```

**Merge approach (for existing branches with divergent history):**

```bash
git checkout <branch-name>
git merge github/<branch-name>
git push origin <branch-name>
```

**Update local references to remote branches:**

```bash
git fetch origin --prune
```

### Key Principles

- **`main` branch**: Always sync bidirectionally between `github` and `origin`
- **`release/current` branch**: Origin-only, not replicated to GitHub
- **Feature branches**: Sync unidirectionally as needed (typically `github` → `origin`)
- **Integration point**: Use `main` for all cross-remote collaboration

### Complete Sync Workflow

**When main branches diverge and release/current has unique changes:**

```bash
# 1. Sync divergent main branches
git fetch --all
git checkout main
git pull origin main
git merge github/main
git push origin main
git push github main

# 2. Update release/current with unified main
git checkout release/current
git pull origin release/current
git merge main
git push origin release/current

# 3. (If needed) Sync release/current changes back to main
git checkout main
git merge release/current
git push origin main
git push github main

# 4. Verify everything is aligned
git fetch --all
git log --oneline github/main -1
git log --oneline origin/main -1
git log --oneline origin/release/current -1
```

### Workflow Summary

1. **Forward Flow**: `github/main` ↔ `origin/main` → `release/current`
2. **Reverse Flow**: `release/current` → `main` → sync to both remotes
3. **Result**: All branches contain the same commits, properly integrated
