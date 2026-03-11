# Monorepo Orchestration Tools & Workspace Research

> **Source:** Claude.ai shared conversation
> **Date:** February 9, 2025
> **Topic:** Monorepo orchestration tools, npm/pnpm/yarn workspaces, and recommended stack for a component library

---

## Overview

This conversation covers a deep-dive into monorepo tooling — specifically how **workspace managers** (npm, pnpm, yarn) and **orchestration tools** (Turborepo, Nx, Lerna, Rush) differ, complement each other, and which combination is best suited for a component library with Azure DevOps CI/CD infrastructure.

---

## Core Concept: Two-Layer Architecture

Monorepo tooling is best understood as two distinct layers:

| Layer | Role | Tools |
|---|---|---|
| **Workspace Layer** | File system: package linking, dependency hoisting, single lockfile | npm, pnpm, yarn |
| **Orchestration Layer** | Intelligence: caching, task scheduling, affected detection, parallelization | Turborepo, Nx, Lerna, Rush |

> **Analogy:** Workspaces = file system. Orchestration tools = operating system running on top of it.

---

## Ecosystem Comparison Matrix

| Feature | npm/pnpm Workspaces | Turborepo | Nx | Lerna | Rush |
|---|---|---|---|---|---|
| Setup Complexity | Minimal | Low | Medium | Low | High |
| Task Orchestration | ❌ Manual | ✅ Pipeline-based | ✅ DAG-based | ⚠️ Basic | ✅ Advanced |
| Local Caching | ❌ | ✅ Hash-based | ✅ Hash-based | ❌ | ✅ Hash-based |
| Remote Caching | ❌ | ✅ (Vercel) | ✅ (Nx Cloud) | ❌ | ✅ (Custom) |
| Dependency Graph | ❌ | ⚠️ Implicit | ✅ Explicit | ⚠️ Basic | ✅ Explicit |
| Task Parallelization | ❌ | ✅ Automatic | ✅ Automatic | ⚠️ Flag-based | ✅ Automatic |
| Code Generation | ❌ | ❌ | ✅ Powerful | ❌ | ⚠️ Limited |
| Affected Detection | ❌ | ⚠️ Basic | ✅ Advanced | ⚠️ Basic | ✅ Advanced |
| IDE Integration | ❌ | ⚠️ Basic | ✅ VSCode plugin | ❌ | ⚠️ Basic |
| Learning Curve | Low | Low | Medium-High | Low | High |
| Best For | Simple monorepos | Vercel ecosystem | Enterprise/complex | Legacy migration | Large orgs |

---

## Workspace Manager Recommendation: pnpm

### Why pnpm Over npm/yarn

| Feature | npm | yarn (classic) | yarn (berry) | pnpm |
|---|---|---|---|---|
| Install Speed | Baseline (1x) | 1.2–1.5x faster | 1.5–2x faster | **2–3x faster** |
| Disk Space | Baseline | Similar | Similar | **~70% less** |
| Strict Dependencies | ❌ | ❌ | ✅ | ✅ |
| Monorepo Support | ✅ Basic | ✅ Good | ✅ Good | **✅ Excellent** |
| Lockfile Merge Conflicts | Frequent | Frequent | Less | **Minimal** |
| Node Modules Structure | Flat (messy) | Flat (messy) | PnP (breaking) | **Symlinked (clean)** |

**Real-world numbers (500 deps in a component library monorepo):**
- `npm install` → 2m 15s, 1.2 GB
- `yarn install` → 1m 45s, 1.2 GB
- `pnpm install` → **45s, 380 MB**

### Key pnpm Advantages

1. **Content-Addressable Store** — packages are stored once globally and symlinked, eliminating duplicates.
2. **Strict Dependency Resolution** — prevents "phantom dependencies" (using packages that aren't declared in `package.json`), which is critical for component libraries whose consumers may not have transitive deps.
3. **`workspace:*` Protocol** — ensures internal packages always reference the local version during development, eliminating version mismatch bugs.
4. **Native CI/CD support** — GitHub Actions has official `pnpm/action-setup` action; Azure DevOps integration is well-documented.

### Migration from npm to pnpm

```bash
# 1. Install pnpm globally
npm install -g pnpm

# 2. Convert existing lockfile
pnpm import  # Converts package-lock.json → pnpm-lock.yaml

# 3. Create workspace config
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'

# 4. Install with strict lockfile
pnpm install --frozen-lockfile
```

**Azure Pipelines integration:**
```yaml
- script: |
    npm install -g pnpm
    pnpm config set store-dir $(Pipeline.Workspace)/.pnpm-store
  displayName: 'Setup pnpm'

- task: Cache@2
  inputs:
    key: 'pnpm | "$(Agent.OS)" | pnpm-lock.yaml'
    path: $(Pipeline.Workspace)/.pnpm-store
  displayName: 'Cache pnpm store'

- script: pnpm install --frozen-lockfile
  displayName: 'Install dependencies'
```

---

## Orchestration Tool Recommendation: Turborepo

### Why Turborepo Over Nx (for a component library)

| Criterion | Turborepo | Nx | Winner |
|---|---|---|---|
| Learning Curve | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐⭐ Steeper | Turborepo |
| Configuration | Single `turbo.json` | Multiple config files | Turborepo |
| TypeScript Focus | Perfect fit | Multi-language | Turborepo |
| Vercel/Next.js | Native integration | Good support | Turborepo |
| CI/CD Integration | Minimal changes | More setup | Turborepo |
| Caching Speed | 45–60% reduction | 70–90% reduction | Nx |
| Best Team Size | Small–medium | Large enterprise | Turborepo |

### When Nx Would Be Better
- 100+ packages
- Mixed languages (Java, Go, Python + JS)
- Need sophisticated code generators
- Dedicated DevOps team
- Distributed task execution at scale

### How Turborepo Caching Works

Turborepo generates a **hash-based cache key** from:
- Input source files (e.g., `src/**/*.ts`)
- Dependency outputs (e.g., `../utils/dist`)
- Declared environment variables
- Task configuration itself

Cache is stored in `node_modules/.cache/turbo/` as compressed `.tar.zst` archives.

**Performance example (15-package TypeScript monorepo):**

| Scenario | pnpm only | + Turborepo | + Nx |
|---|---|---|---|
| First build | 124s | 118s | 121s |
| Second build (cached) | 124s | **2.1s** | **1.8s** |
| Changed 1 file | 124s | **14s** | **12s** |
| Changed 5 files | 124s | **38s** | **35s** |

### Cache Invalidation Rules

| Change | Cache Result |
|---|---|
| Nothing changed | ✅ Cache HIT |
| Source file modified | ❌ Cache MISS (+ all dependents) |
| Dependency version changed | ❌ Cache MISS (+ all dependents) |
| Unrelated file (e.g., README) changed | ✅ Cache HIT |

---

## Turborepo Configuration

### Minimal `turbo.json` for a Component Library

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**"],
      "cache": true
    },
    "lint": {
      "cache": true
    },
    "test": {
      "dependsOn": ["build"],
      "cache": true
    },
    "storybook:build": {
      "dependsOn": ["^build"],
      "outputs": ["storybook-static/**"],
      "cache": true
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Key Pipeline Concepts

- `"dependsOn": ["^build"]` — the `^` means "upstream packages must build first"
- `"dependsOn": ["build"]` — (no `^`) means "this package's own build must run first"
- `"cache": false` — disables caching for long-running/watch tasks like `dev`
- `"persistent": true` — marks tasks that stay running (watchers)

### Common Pitfalls

1. **Missing `^`** — `"dependsOn": ["build"]` (no caret) doesn't wait for upstream packages.
2. **Over-caching** — not declaring `env` variables in pipeline config causes stale builds when env changes.
3. **Huge cache sizes** — exclude source maps and `.d.ts` files from cache outputs:
   ```json
   "outputs": ["dist/**", "!dist/**/*.map", "!dist/**/*.d.ts"]
   ```

---

## Affected-Only Builds

Turborepo supports building only what changed from a git ref:

```bash
# Build only packages changed since last commit
turbo run build --filter=[HEAD^1]

# Build only packages changed since main branch
turbo run build --filter=[main]
```

This is powerful for CI — pull request pipelines only rebuild and test what was actually affected.

---

## Remote Caching (Optional, Advanced)

### Turborepo with Vercel
```bash
npx turbo login
npx turbo link
```

In CI:
```yaml
env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: my-team
```

### Nx Cloud
```bash
npx nx connect-to-nx-cloud
```

---

## Recommended Stack

```
┌─────────────────────────────────────────────┐
│         Turborepo (Orchestration)           │
│  - Task caching & scheduling                │
│  - Dependency-aware build order             │
│  - Affected detection per git diff          │
├─────────────────────────────────────────────┤
│         pnpm workspaces (Foundation)        │
│  - Package linking via workspace:*          │
│  - Content-addressable storage              │
│  - Strict phantom dependency prevention     │
├─────────────────────────────────────────────┤
│         Azure DevOps Pipelines (CI/CD)      │
│  - Existing infrastructure kept intact      │
│  - Minimal pipeline changes needed          │
│  - pnpm cache step added                    │
└─────────────────────────────────────────────┘
```

---

## Quick Start Implementation (4 Steps)

```bash
# 1. Create pnpm workspace config
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'

# 2. Install pnpm & import lockfile
pnpm import

# 3. Add Turborepo
pnpm add turbo -D -w

# 4. Update root package.json scripts
```

```json
{
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "dev": "turbo run dev --parallel",
    "lint": "turbo run lint"
  }
}
```

> No changes are needed to individual package `package.json` files — Turborepo picks up existing scripts automatically.

---

## Cost-Benefit Summary

| Investment | Effort |
|---|---|
| Initial setup (pnpm + Turborepo) | 2–4 hours |
| Team training | ~1 day |
| CI/CD pipeline updates | 1–2 days |

| Benefit | Impact |
|---|---|
| Faster builds | 45–60% via caching |
| Less disk space | ~70% (pnpm store) |
| No phantom dependencies | Stricter dep resolution |
| Automatic task ordering | No manual coordination needed |
| Future scalability | Grows to 50+ packages without rearchitecture |

---

## Decision Criteria: When to Reconsider Nx

Stick with Turborepo until any of these thresholds are crossed:
- **50+ packages** in the monorepo
- **Multi-language** (non-JS/TS) packages introduced
- **20+ developers** contributing simultaneously
- Need for **distributed task execution** across cloud agents
- Heavy reliance on **code generation** scaffolding

---

## References

- [Turborepo documentation](https://turbo.build/repo/docs)
- [pnpm workspaces](https://pnpm.io/workspaces)
- [Nx documentation](https://nx.dev)
- [pnpm/action-setup GitHub Action](https://github.com/pnpm/action-setup)
