---
name: mutations-testing
description: Use PROACTIVELY when checking if tests catch real bugs, assessing test suite quality, finding weak tests, or measuring mutation score. Validates test effectiveness beyond coverage metrics by introducing code mutations. Supports Stryker (JS/TS), PIT (Java), mutmut (Python). Not for projects without existing test suites.
---

# Mutation Testing

## Overview

This skill sets up mutation testing to evaluate test suite quality by introducing deliberate code changes (mutants) and verifying tests catch them. A high mutation score indicates tests are effective at catching real bugs.

**Version:** 0.2.0
**Status:** Updated

## What This Skill Does

**Mutation Testing Workflow:**

1. **Analyze** codebase to identify mutation targets
2. **Generate** mutants (deliberate code changes)
3. **Run** test suite against each mutant
4. **Report** mutation score and surviving mutants
5. **Recommend** test improvements for weak spots

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

## Supported Frameworks

| Language              | Framework | Command                                        |
| --------------------- | --------- | ---------------------------------------------- |
| JavaScript/TypeScript | Stryker   | `npx stryker run`                              |
| Java                  | PIT       | `mvn org.pitest:pitest-maven:mutationCoverage` |
| Python                | mutmut    | `mutmut run`                                   |

## Mutation Score

| Score  | Interpretation                                         |
| ------ | ------------------------------------------------------ |
| 100%   | Ship it — every mutant killed                          |
| 90–99% | Acceptable — document surviving mutants before merging |
| 75–89% | Add tests to cover gaps                                |
| < 75%  | Poor — tests need major improvement                    |

## Common Mutations

| Type        | Example                    | Tests Should Catch  |
| ----------- | -------------------------- | ------------------- |
| Arithmetic  | `+` → `-`                  | Math logic errors   |
| Conditional | `>` → `>=`                 | Boundary conditions |
| Boolean     | `true` → `false`           | Logic inversions    |
| Return      | `return x` → `return null` | Null handling       |
| Remove call | `validate()` → removed     | Missing validations |

## Installation Summary

For JavaScript/TypeScript (Stryker) — scoped to a single package:

```bash
pnpm add -D --filter <package-name> @stryker-mutator/core @stryker-mutator/jest-runner
```

For Python (mutmut):

```bash
pip install mutmut
mutmut run
```

## Quick Start

1. Ensure test suite exists and passes
2. Install mutation testing framework
3. Configure mutation targets (critical code paths)
4. Run mutation analysis
5. Review surviving mutants
6. Add/improve tests for uncaught mutations

## Performance Considerations

- Mutation testing is **compute-intensive**
- Start with critical modules only
- Use incremental mode for CI
- Cache results between runs
- Consider parallel execution

## Success Criteria

- Mutation testing framework installed
- Configuration targets critical code paths
- Initial mutation run completes
- Mutation score reported
- Action plan for surviving mutants

## Project Setup

The working Stryker configuration for this monorepo lives in:
`packages/boreal-web-components/MUTATION_TESTING.md`

It covers reuse steps, config file locations, and the `local/mutation-testing` branch that holds the Stryker install without polluting feature branches.

## Version History

- **0.2.0** - Updated score targets, scoped install command, replaced dead resource links with project setup pointer
- **0.1.0** - Initial release with Stryker, PIT, mutmut support
