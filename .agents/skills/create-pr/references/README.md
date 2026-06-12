# PR Templates & Examples — Boreal DS

This directory contains structured PR templates and reference examples for creating pull request descriptions that follow Boreal DS engineering conventions.

---

## Quick Start

1. **Identify your PR type** (feature, bugfix, docs, etc.)
2. **Open the matching template** from the table below
3. **Fill in all sections**, replacing placeholder text
4. **Check applicable checklist items** (`[x]`)
5. **Delete non-applicable sections**
6. **Copy to your PR** (or use `.claude/pr-description.md`)

---

## Templates by Type

| Template               | File                                                       | Use Case                                                   |
| ---------------------- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| 🎯 **Feature**         | [feature-template.md](feature-template.md)                 | New components, functionality, or capabilities             |
| 🐛 **Bug Fix**         | [bugfix-template.md](bugfix-template.md)                   | Defect fixes, error corrections, incorrect behavior        |
| 🚨 **Hotfix**          | [hotfix-template.md](hotfix-template.md)                   | Urgent production fixes requiring immediate deployment     |
| 🔧 **Refactoring**     | [refactoring-template.md](refactoring-template.md)         | Code improvements with no functional changes               |
| 📚 **Documentation**   | [documentation-template.md](documentation-template.md)     | README, JSDoc, Storybook, guides                           |
| 🔒 **Security Patch**  | [security-patch-template.md](security-patch-template.md)   | XSS, CSRF, CVE fixes, security vulnerabilities             |
| ✅ **Test**            | [test-template.md](test-template.md)                       | Unit/integration test additions or fixes (no impl changes) |
| ⚡ **Performance**     | [performance-template.md](performance-template.md)         | Speed, memory, or bundle size optimizations                |
| 💥 **Breaking Change** | [breaking-change-template.md](breaking-change-template.md) | API changes requiring consumer code updates                |

---

## Reference Examples

For quick reference showing Boreal DS PR style without the full template structure, see:

- **[pr-examples.md](pr-examples.md)** — Concise real-world PR examples

---

## PR Title Format

All PRs must follow conventional commits:

```
<type>(<scope>): <TICKET-ID> <imperative description>
```

For breaking changes, add `!` after scope:

```
<type>(<scope>)!: <TICKET-ID> <imperative description>
```

**Examples:**

```
feat(web-components): EOA-10099 add bds-text-field component
fix(web-components): EOA-10088 prevent focus trap in bds-modal
docs(boreal-docs): EOA-10077 add FACE integration guide
refactor(web-components): EOA-10065 extract shared validation logic
perf(web-components): EOA-10054 reduce bds-table render time by 60%
feat(web-components)!: EOA-10042 rename bds-input to bds-text-field
```

---

## Template Sections Explained

### Core Sections (All Templates)

- **Description**: What changed and why (the "what" and "why")
- **Implementation Details**: How it was done (approach, patterns, decisions)
- **Impact Analysis**: Effects on existing code, performance, behavior
- **Testing Conducted**: Automated tests + manual verification
- **Additional Remarks**: Context for reviewers, deferred work, constraints
- **References**: Ticket links (`Refs` or `Closes` EOA-XXXXX)
- **Checklist**: Boreal DS quality gates (tokens, coverage, accessibility, etc.)

### Specialized Sections (Specific Templates)

- **Bug Fix**: Steps to reproduce, root cause analysis
- **Hotfix**: Urgency level, deployment plan, rollback strategy
- **Security**: CVE info, severity assessment, disclosure timeline
- **Performance**: Before/after metrics, benchmarking methodology
- **Breaking Change**: Migration path, automated migration tools, deprecation period

---

## Checklist Usage

Each template includes Boreal DS-specific checklists. Use them to verify:

✅ **General Standards**

- Conventional commit format
- TypeScript strict mode (no `any`)
- All tests pass locally

✅ **Boreal DS Component Standards**

- Design tokens (`var(--boreal-*)`) — no hard-coded values
- Component prefix (`bds-`)
- Explicit TypeScript types
- Event conventions (bare `@Event()`)

✅ **Testing & Quality**

- Unit test coverage ≥ 90%
- Accessibility verified (keyboard, screen readers)
- No console errors

✅ **Documentation**

- JSDoc on public APIs
- Storybook story added/updated
- README updated if API changed

**How to use:**

- Check completed items: `- [x] Design tokens used`
- Leave unchecked if not applicable: `- [ ] N/A for this PR`
- Delete entire sections that don't apply

---

## Issue Reference Syntax

| Syntax                | Effect                                         |
| --------------------- | ---------------------------------------------- |
| `Refs EOA-XXXXX`      | Links the PR to the ticket (ticket stays open) |
| `Closes EOA-XXXXX`    | Links and auto-closes ticket on PR merge       |
| `Refs #123`           | Cross-references another PR                    |
| `Refs CVE-2026-XXXXX` | Links to CVE (security patches)                |

---

## Best Practices

1. **Use the right template** — don't force-fit your PR into the wrong category
2. **Fill, don't copy** — templates are guides, not literal copy-paste content
3. **Delete placeholders** — remove all `[example text]` and unused sections
4. **Check the checklist** — it catches common quality issues before review
5. **Link to plans** — for complex PRs, link to `ai-work/plans/` instead of writing novels
6. **Show, don't tell** — screenshots/videos for UI changes, benchmarks for performance
7. **Think of reviewers** — what context do they need to review effectively?

---

## Questions?

- **For PR writing help**: Use the `create-pr` skill
- **For code review**: See `ai-docs/guidelines/code-review-checklist.md`
- **For commit messages**: Use `pnpm commit` (enforces conventional commits)
- **For release process**: See `ai-docs/guidelines/release-process.md`
