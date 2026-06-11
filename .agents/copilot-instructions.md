# GitHub Copilot Instructions — Boreal DS

Boreal DS is a multi-brand design system monorepo for Proximus Group (brands: Proximus, Masiv, Telesign, BICS). It is maintained with pnpm workspaces and Turborepo.

**Package structure:**

- `boreal-web-components` — Stencil 4.x web components (TypeScript, SCSS)
- `boreal-react` / `boreal-vue` — auto-generated framework wrappers
- `boreal-styleguidelines` — Style Dictionary design tokens
- `boreal-docs` (app) — Storybook 10.x documentation

**Tooling constraints:**

- Node.js 22+ via fnm — run `fnm use` before any Node/pnpm command
- pnpm 10+ only; always install from the workspace root (`pnpm add -D -w`)
- All commits must follow `type(scope): TICKET-ID description` via `pnpm commit`
- Never edit `pnpm-lock.yaml` manually

---

## Non-negotiable rules

**TypeScript**

- All code must be fully typed. No `any` — use `unknown` or precise union types.
- `"noImplicitAny": false` at the root is a legacy Stencil setting; treat implicit `any` as an error regardless.
- All exported public API surfaces must have explicit types — no inferred `any` leaking into `.d.ts` output.

**Security**

- Never read, write, or modify `*.env` / `.env.*` files without explicit user permission.
- Never include secret values in code, commit messages, PR descriptions, or any output.
- Never suggest committing `.env` files, even when a `.gitignore` entry exists.

**Components**

- All web component tags use the `bds-[name]` prefix.
- Use design tokens (`var(--boreal-*)`) exclusively — no hard-coded colours, spacing, or radii.
- Use bare `@Event()` — no `bubbles` or `composed` unless the event must bubble to a parent `@Listen()`.
- Unit test coverage must reach ≥ 90% statements before a PR is merged.

**Release**

- Releases run from `release/current` only, via `pnpm release:*` scripts (Engineering Lead responsibility).
- Always run with `--dry-run` first. Never publish `boreal-docs` or `react-testapp`.
- Before writing any package version into a plan or command, fetch the current version from `https://registry.npmjs.org/<package>/latest`.

---

## Skills and reference documentation

Detailed patterns, runbooks, and domain knowledge are available as agent skills in `.agents/skills/`. Load the relevant skill when working in that area.

| Area                             | Skill                                                    | Key guideline file                                    |
| -------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| Stencil component implementation | `stencil-component-knowledge`                            | `ai-docs/guidelines/stencil-best-practices.md`        |
| Unit tests                       | `testing-knowledge`                                      | `ai-docs/guidelines/stencil-unit-testing-patterns.md` |
| Storybook stories + MDX docs     | `documentation-knowledge`                                | `ai-docs/guidelines/storybook-patterns.md`            |
| JSDoc                            | `documentation-knowledge`                                | `ai-docs/guidelines/jsdoc-template.md`                |
| CI/CD, build, release            | `infra-knowledge`                                        | `ai-docs/guidelines/release-process.md`               |
| Code review                      | `code-reviewer`                                          | `ai-docs/guidelines/code-review-checklist.md`         |
| New component SDLC               | `create-component` → `writing-plans` → `executing-plans` | `ai-docs/guidelines/stencil-best-practices.md`        |
| PR descriptions                  | `create-pr`                                              | —                                                     |

**Definition of Done** — every change must satisfy all criteria in `ai-docs/guidelines/code-review-checklist.md` before merging to `release/current`.
