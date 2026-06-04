# GitHub Copilot Instructions — Boreal DS

Boreal DS is a multi-brand design system monorepo for Proximus Group (brands: Proximus, Masiv, Telesign, BICS). It is maintained with pnpm workspaces and Turborepo.

**Package structure:**
- `boreal-web-components` — Stencil 4.x web components (TypeScript, SCSS)
- `boreal-react` / `boreal-vue` — auto-generated framework wrappers
- `boreal-styleguidelines` — Style Dictionary design tokens
- `boreal-docs` (app) — Storybook 10.x documentation

**Key constraints:**
- Node.js 22+ via fnm (`fnm use` before any Node/pnpm command)
- pnpm 10+ only; always install from workspace root
- All commits must follow `type(scope): TICKET-ID description`

---

Detailed coding standards, naming conventions, architectural patterns, and documentation requirements are maintained in `ai-docs/docs/` and loaded automatically via `.github/instructions/`:

- `base.instructions.md` — general TypeScript, naming, commit format
- `frontend.instructions.md` — Stencil, SCSS, tokens, Storybook patterns
- `documentation.instructions.md` — JSDoc, MDX, story structure
- `security.instructions.md` — dependency management, publishing, TypeScript safety
- `workflow.instructions.md` — monorepo tooling, release process, CI
