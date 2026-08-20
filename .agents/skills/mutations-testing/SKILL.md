---
name: mutations-testing
description: Use PROACTIVELY when checking if tests catch real bugs, assessing test suite quality, finding weak tests, or measuring mutation score. Validates test effectiveness beyond coverage metrics by introducing code mutations. Supports Stryker (JS/TS), PIT (Java), mutmut (Python). Not for projects without existing test suites.
---

# Mutation Testing

## Overview

This skill sets up mutation testing to evaluate test suite quality by introducing deliberate code changes (mutants) and verifying tests catch them. A high mutation score indicates tests are effective at catching real bugs.

## When to Use This Skill

**Use when:**

- Coverage is high but confidence in tests is low
- Validating test suite effectiveness
- Finding tests that pass but don't catch real bugs
- Preparing for production release
- Improving test quality beyond coverage metrics

**Don't use if:**

- No existing test suite
- Test coverage below 50% (improve coverage first)
- CI pipeline can't afford extra runtime

## Trigger Phrases

- "Set up mutation testing"
- "Are my tests catching bugs?"
- "Check test effectiveness" / "Test quality analysis"
- "Run mutation analysis" / "Mutation score"
- "Find weak tests"

## Mutation Score Targets

| Score  | Verdict                                                |
| ------ | ------------------------------------------------------ |
| 100%   | Ship it — every mutant killed                          |
| 90–99% | Acceptable — document surviving mutants before merging |
| < 90%  | Add tests before merging                               |

## Common Mutations

| Type        | Example                    | Tests Should Catch  |
| ----------- | -------------------------- | ------------------- |
| Arithmetic  | `+` → `-`                  | Math logic errors   |
| Conditional | `>` → `>=`                 | Boundary conditions |
| Boolean     | `true` → `false`           | Logic inversions    |
| Return      | `return x` → `return null` | Null handling       |
| Remove call | `validate()` → removed     | Missing validations |

---

## Boreal DS — Stryker Workflow (JavaScript/TypeScript)

Stryker runs in an isolated git worktree so the working branch stays completely clean — no `git restore` needed, no risk of accidentally committing Stryker files.

Config templates live in `.agents/skills/mutations-testing/templates/` and are always present regardless of which branch you are on.

### Step 1 — Create a throwaway worktree

```bash
# Safe to run from any worktree or the main checkout —
# REPO_ROOT always resolves to the primary checkout's absolute path.
COMPONENT=bds-my-component
REPO_ROOT=$(git worktree list --porcelain | awk 'NR==1{print $2}')
git worktree add "$REPO_ROOT/.worktrees/mutation-$COMPONENT" HEAD
cd "$REPO_ROOT/.worktrees/mutation-$COMPONENT"
fnm use
```

### Step 2 — Copy config templates

```bash
cp .agents/skills/mutations-testing/templates/stryker.component.config.mjs \
   packages/boreal-web-components/stryker.$COMPONENT.config.mjs

cp .agents/skills/mutations-testing/templates/jest.stryker.config.cjs \
   packages/boreal-web-components/jest.stryker.config.cjs
```

### Step 3 — Fill in component paths

Edit `packages/boreal-web-components/stryker.$COMPONENT.config.mjs` — update `mutate`:

```js
mutate: [
  'src/components/<category>/<component>/<component>.tsx',
],
```

Edit `packages/boreal-web-components/jest.stryker.config.cjs` — update `testMatch`:

```js
testMatch: ['<rootDir>/src/components/<category>/<component>/__test__/**/*.spec.tsx'],
```

### Step 4 — Add ESLint ignores

In `packages/boreal-web-components/eslint.config.ts`, add to the `ignores` array:

```ts
'*.config.mjs',
'*.config.cjs',
'.stryker-tmp/',
```

`.stryker-tmp/` is critical, not optional — see "Constraint: exclude `.stryker-tmp/` from ESLint" below.

### Step 5 — Install Stryker (scoped to the component package)

```bash
pnpm add -D --filter boreal-web-components @stryker-mutator/core @stryker-mutator/jest-runner
```

### Step 6 — Run and capture results

The templates already cap `concurrency: 2` (Stryker) and `maxWorkers: 1` (Jest) — see "Memory Safety" below before raising either value.

```bash
cd packages/boreal-web-components
npx stryker run stryker.$COMPONENT.config.mjs > mutation.md 2>&1
cat mutation.md
```

If the run reports mutants as `timed out` in unusually high numbers, suspect memory pressure before suspecting slow tests — re-check after confirming the concurrency caps are in place.

### Step 7 — Review surviving mutants and improve tests

Open `mutation.md`. For each surviving mutant:

- **Arithmetic / conditional survivors** — add boundary-value assertions
- **Boolean survivors** — add an explicit `false` branch test
- **Return-value survivors** — assert on the returned value, not just side effects
- **Absent-prop survivors** — assert that a CSS variable or attribute is absent when the prop is unset (use `not.toContain` / `toBeNull`)
- **String-mutation survivors** — use `expect.stringContaining('propName')` instead of an exact-string assert

Re-run after each fix until the score is ≥ 90%.

### Step 8 — Copy results back and clean up

```bash
# Copy results back to the main workspace, then remove the worktree.
# REPO_ROOT must be set (see Step 1); re-derive it if running in a fresh shell:
#   REPO_ROOT=$(git worktree list --porcelain | awk 'NR==1{print $2}')
mkdir -p "$REPO_ROOT/ai-work/qa/mutation-reports"
cp packages/boreal-web-components/mutation.md \
   "$REPO_ROOT/ai-work/qa/mutation-reports/mutation-$COMPONENT.md"

# Discard the worktree — all Stryker files disappear with it
cd "$REPO_ROOT"
git worktree remove "$REPO_ROOT/.worktrees/mutation-$COMPONENT" --force
```

The working branch is untouched. No `git restore`, no manual `pnpm remove`.

---

## Other Languages

| Language | Framework | Command                                        |
| -------- | --------- | ---------------------------------------------- |
| Java     | PIT       | `mvn org.pitest:pitest-maven:mutationCoverage` |
| Python   | mutmut    | `mutmut run`                                   |

## Performance Considerations

- Mutation testing is compute-intensive. Start with the single component file, not the whole package.
- `coverageAnalysis: 'perTest'` in the template is the most accurate mode but also the slowest. Use `'off'` for a quick first pass.
- The `.stryker-tmp/` directory is created in the worktree and removed with it — no cleanup needed.

## Memory Safety

Stryker's default `concurrency` is roughly `CPUs - 1` — on an 11-CPU/18GB machine this spawned 10 parallel worker processes, each booting its own full Jest+ts-jest instance, and OOM'd the machine before the run finished (confirmed on `bds-pagination`, 2026-07-07). Mutants reported as `timed out` in that run turned out to be memory-pressure artifacts, not genuinely slow tests — capping concurrency dropped the timeout count to 0 on re-run.

Both templates in this skill already set:

- `concurrency: 2` in `stryker.component.config.mjs`
- `maxWorkers: 1` in `jest.stryker.config.cjs`

Keep both caps unless the machine is known to have memory to spare. If you must raise them, raise one at a time and watch `ps aux | grep jest-worker` / `top -l 1 | grep PhysMem` (macOS) during the run rather than assuming headroom.

## Constraint: exclude `.stryker-tmp/` from ESLint

The pure throwaway-worktree flow (Steps 1–8) never hits this — `.stryker-tmp/` is discarded with
the worktree before any commit happens. It bites when a task needs the worktree to *persist*
across the Stryker run — e.g. closing real test gaps found by surviving mutants and committing
those spec-file fixes from that same worktree (as opposed to a pure "run Stryker, read the
report, discard" pass).

Each Stryker run creates one `.stryker-tmp/sandbox-<hash>/` directory per concurrent worker —
a full copy of `src/`. Confirmed on `bds-date-picker` (EOA-16692 Task 23, 2026-08-19): three
Stryker runs against the same live worktree left multiple sandbox copies on disk; the next
`git commit`'s lint-staged hook (`eslint --fix` under `projectService: true`, i.e. type-aware
linting building a full TS program) swept them all in — one file changed, but the type program
now spanned every file across every sandbox. A hook that normally finishes in ~13s took over
6 minutes and was killed by a 2-minute tool timeout on the first attempt.

Step 4's `ignores` array above already includes `.stryker-tmp/` — treat it as load-bearing, not
optional, any time the worktree will see a `git commit` or `git push` (which also runs hooks)
after Stryker has run in it. If a commit/push hook is taking dramatically longer than a normal
run on that package, suspect this before suspecting the change itself — check for `sandbox-*`
directories under `.stryker-tmp/` first.
