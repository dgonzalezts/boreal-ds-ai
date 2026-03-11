---
description: Base development rules and guidelines for Boreal DS, applicable to all AI agents working in this monorepo.
applyTo: "**"
---

# Base Instructions — Boreal DS

## 1. Core Principles

- **Small tasks, one at a time**: Work in focused, incremental steps. Never advance more than one logical step without verifying the result.
- **Test-driven development**: Write failing tests before implementing new functionality. Target ≥ 90% statement coverage for all Stencil components.
- **Type safety**: All code must be fully typed. No `any` — use `unknown` or precise union types instead.
- **Clear naming**: Use clear, descriptive names for all variables, functions, props, and events. Follow the `bds-[name]` prefix convention for all web component tags.
- **Incremental changes**: Prefer small, focused changes over large, complex modifications. Each commit should represent one logical unit of work.
- **Question assumptions**: Always verify designs against Figma and specs against the work ticket before implementing. Do not assume undocumented behaviour.
- **Pattern detection**: Detect and reuse existing patterns (token usage, prop reflection rules, slot conventions, test helpers) rather than introducing new ones.

## 2. Language Standards

All technical artefacts must be written in English, including:

- Source code (variables, functions, classes, error messages, log messages)
- Documentation (README files, MDX stories, JSDoc)
- Git commit messages and changeset descriptions
- Test names and story descriptions
- Configuration files and scripts

## 3. Specific Standards

For detailed guidelines covering specific areas of the monorepo, refer to:

- [Workflow Instructions](./workflow.instructions.md) — End-to-end change lifecycle: discovery, design, specification, development, validation, and release
- [Frontend Instructions](./frontend.instructions.md) — Stencil component conventions, SCSS and design token patterns, accessibility, unit testing, and release workflow
- [Documentation Instructions](./documentation.instructions.md) — Storybook story file structure, argTypes rules, MDX documentation sections, and the two-type docs/story component rule

## 4. Deep Reference Documentation

For detailed operational runbooks, patterns, and architectural context beyond these instructions, see:

- [Definition of Done Checklist](../../.ai/guidelines/DoD_checklist.md) — Comprehensive DoD criteria for production-ready changes
- [Release Process](../../.ai/guidelines/release-process.md) — Step-by-step runbook for versioning and publishing packages
- [Plop Generator Learnings](../../.ai/guidelines/plop-generator-learnings.md) — Code generation patterns and template development
- [Scripts (Boreal)](../../.ai/guidelines/scripts-boreal.md) — Custom monorepo tooling and utility scripts

These reference docs provide deep dives into specific workflows and tooling. The instruction files above remain the primary source for agent directives and coding standards.
