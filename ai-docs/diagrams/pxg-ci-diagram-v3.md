# CI Diagram v3 — Boreal DS

## Changes from v2

- Release tooling stays on `release-it` (Option A, ADR 0013): the `changeset status` gate is **removed** and replaced by **PR-title validation** (Conventional Commits + commitlint scopes). With squash-only merges, the PR title is the changelog/version source. Bitbucket's squash message lists the squashed commits indented, so a `BREAKING CHANGE:` footer inside it is ignored: the `!` in the title is what marks a breaking release, and a bare `@name` in a title becomes a link to a page that does not exist (verified in the first real release; see `CONTRIBUTING.md` and `RELEASING.md`).
- Added **type checks** alongside ESLint in Job 1.
- Every job pins **Node from `.node-version` (22.23.3)** and enables **pnpm 11 via corepack**.
- Coverage command is `pnpm turbo run test:coverage`; the gate stays at **80%** (matches `packages/boreal-web-components/testing.config.ts`). Tests: **Stencil test** (web-components) and **Vitest** (style-guidelines).
- Package scope `@boreal-ds/*` → **`@pxglobal/*`** (applied across jobs).
- Job 1b SonarQube: **self-hosted SonarQube** (SonarQube Cloud does not support on-prem Bitbucket Server); coverage fed via lcov.
- Job 1c: `pnpm audit --audit-level=critical`; Checkmarx SAST/SCA handled in Phase 2.
- Job 2: corrected build outputs — **no CJS bundle** (Stencil emits `dist/` ESM + loader); `components-build/` custom elements with type declarations; **`custom-elements.json` (CEM)** plus the `check:cem` breaking-change report; added **`pnpm run validate:all`** (React/Vue wrapper generation). Archive `dist/`, `components-build/`, `loader/`, `custom-elements.json`.
- Job 2 also produces the **browser build (UMD/IIFE)** for the Library CDN — a **new output target** (`umd/`), for enterprise/no-npm consumers (see CD v3).
- Job 3: **build only** — publishing Storybook to Chromatic moved to the release job (CD).
- CI gate: Phase 1 requires Jobs 1–3 via the Bitbucket *Required builds* merge check; Phase 2 adds SonarQube (Job 1b) and `pnpm audit` (Job 1c) to the required set.
- Job 4 (Phase 3): accessibility uses **axe-core only** (drop Pa11y), WCAG **2.2 AA**; visual regression via **Chromatic** (non-blocking for alpha); E2E uses **Playwright only** (drop Cypress), Chromium-first; **Lighthouse deferred**; bundle analysis is informational (no threshold defined yet).
- Notifications: **email now**, Microsoft Teams once a channel exists.

---

```mermaid
flowchart TD
  Start([Start: Pull Request<br/>Opened/Updated]) --> Parallel{Parallel Execution}

  %% Job 1 - Code Quality (Phase 1)
  Parallel -->|Job 1: Code Quality| J1_Checkout[Checkout Code<br/>PR Branch]
  J1_Checkout --> J1_Setup[Setup Node 22.23.3<br/>.node-version + corepack → pnpm 11]
  J1_Setup --> J1_Install[Install Dependencies<br/>pnpm install --frozen-lockfile]
  J1_Install --> J1_PRT[Validate PR Title<br/>Conventional Commits + commitlint scopes<br/>breaking change needs the ! in the title<br/>no bare @handle outside backticks<br/>squash-only = changelog source]
  J1_PRT --> J1_Lint[Run ESLint + Type Checks<br/>pnpm lint]
  J1_Lint --> J1_Test[Run Unit Tests<br/>pnpm test<br/>Stencil test + Vitest]
  J1_Test --> J1_Coverage[Check Coverage<br/>pnpm turbo run test:coverage<br/>Minimum 80%]
  J1_Coverage --> J1_Archive[Archive Test Results<br/>JUnit XML]
  J1_Archive --> J1_End[Job 1 Complete ✓]
  J1_PRT -.Invalid Title.-> NotifyFail1[❌ Notify Team<br/>Email — Teams when channel exists]
  J1_Lint -.Failure.-> NotifyFail1
  J1_Test -.Failure.-> NotifyFail1
  J1_Coverage -.Below 80%.-> NotifyFail1

  %% Job 1b - SonarQube Quality Gate (Phase 2) - self-hosted
  Parallel -->|Job 1b: SonarQube<br/>Phase 2| J1b_Checkout[Checkout Code<br/>PR Branch]
  J1b_Checkout --> J1b_Install[Setup + Install<br/>Node .node-version, pnpm 11<br/>pnpm install --frozen-lockfile]
  J1b_Install --> J1b_Sonar[Run Self-Hosted SonarQube<br/>sonar-scanner<br/>lcov: coverage/lcov.info]
  J1b_Sonar --> J1b_Gate[Check Quality Gate<br/>• 80% Coverage<br/>• Zero Critical Issues<br/>• Technical Debt &lt; 5%]
  J1b_Gate --> J1b_Archive[Archive Report<br/>SonarQube Dashboard Link]
  J1b_Archive --> J1b_End[Job 1b Complete ✓]
  J1b_Gate -.Quality Gate Failed.-> NotifyFail1b[❌ Notify Team<br/>Email — Teams when channel exists]

  %% Job 1c - Dependency Security (Phase 2)
  Parallel -->|Job 1c: Dependency Security<br/>Phase 2| J1c_Checkout[Checkout Code<br/>PR Branch]
  J1c_Checkout --> J1c_Install[Setup + Install<br/>Node .node-version, pnpm 11<br/>pnpm install --frozen-lockfile]
  J1c_Install --> J1c_Audit[Run Security Audit<br/>pnpm audit --audit-level=critical<br/>Known Vulnerabilities]
  J1c_Audit --> J1c_Gate[Check Threshold<br/>Block if Critical Found]
  J1c_Gate --> J1c_Archive[Archive Security Report<br/>JSON]
  J1c_Archive --> J1c_End[Job 1c Complete ✓]
  J1c_Gate -.Critical Vulnerabilities.-> NotifyFail1c[❌ Notify Team<br/>Email — Teams when channel exists]
  J1c_Audit -.Checkmarx SAST/SCA Phase 2.-> J1c_End

  %% Job 2 - Build Components (Phase 1)
  Parallel -->|Job 2: Build Components| J2_Checkout[Checkout Code<br/>PR Branch]
  J2_Checkout --> J2_Install[Setup + Install<br/>Node .node-version, pnpm 11<br/>pnpm install --frozen-lockfile]
  J2_Install --> J2_Build[Build Components<br/>pnpm build — Turborepo<br/>all packages in dependency order]
  J2_Build --> J2_CEM[Generate CEM + Report<br/>custom-elements.json<br/>pnpm --filter @pxglobal/boreal-web-components check:cem]
  J2_CEM --> J2_Validate[Validate Build Outputs<br/>• dist/ ESM + loader<br/>• components-build/ custom elements<br/>• Type Declarations<br/>• custom-elements.json<br/>• UMD/IIFE browser build]
  J2_Validate --> J2_Wrappers[Validate Wrapper Generation<br/>pnpm run validate:all<br/>React + Vue from Stencil output targets]
  J2_Wrappers --> J2_Archive[Archive Library Artifacts<br/>dist/ + components-build/<br/>loader/ + custom-elements.json<br/>umd/ browser build]
  J2_Archive --> J2_End[Job 2 Complete ✓]
  J2_Build -.Build Failed.-> NotifyFail2[❌ Notify Team<br/>Email — Teams when channel exists]
  J2_CEM -.CEM Failed / Missing JSDoc.-> NotifyFail2
  J2_Validate -.Invalid Output.-> NotifyFail2
  J2_Wrappers -.Wrapper Cannot Generate.-> NotifyFail2

  %% Job 3 - Build Storybook (Phase 1)
  Parallel -->|Job 3: Build Storybook| J3_Checkout[Checkout Code<br/>PR Branch]
  J3_Checkout --> J3_Install[Setup + Install<br/>Node .node-version, pnpm 11<br/>pnpm install --frozen-lockfile]
  J3_Install --> J3_Build[Build Storybook<br/>pnpm --filter @pxglobal/boreal-docs run build<br/>storybook-static/]
  J3_Build --> J3_Validate[Validate Storybook Build<br/>• Stories parse / no import errors<br/>• Static assets present]
  J3_Validate --> J3_Archive[Archive Storybook Artifacts<br/>storybook-static/]
  J3_Archive --> J3_End[Job 3 Complete ✓]
  J3_Build -.Build Failed.-> NotifyFail3[❌ Notify Team<br/>Email — Teams when channel exists]
  J3_Validate -.Invalid Stories.-> NotifyFail3
  J3_Validate -.Publish happens in CD release job.-> J3_End

  %% Convergence - CI Gate
  J1_End --> CIGate{CI Quality Gate<br/>Bitbucket Required Builds}
  J2_End --> CIGate
  J3_End --> CIGate
  J1b_End -.Phase 2.-> CIGate
  J1c_End -.Phase 2.-> CIGate

  CIGate -.Any Required Job Failed.-> FailEnd([❌ CI Failed<br/>PR Blocked<br/>Cannot Merge])
  CIGate -->|Required Jobs Passed ✓| J4_Start{Phase 3 Tests<br/>Enabled?}

  %% Job 4 - Comprehensive Testing (Phase 3)
  J4_Start -->|Enabled| J4_Accessibility[Accessibility<br/>axe-core — WCAG 2.2 AA<br/>Storybook a11y addon + test-runner]
  J4_Accessibility --> J4_Visual[Visual Regression<br/>Chromatic per PR<br/>Non-blocking for alpha]
  J4_Visual --> J4_E2E[E2E<br/>Playwright — Chromium-first]
  J4_E2E --> J4_Perf[Performance<br/>Lighthouse — DEFERRED<br/>revisit with product pages]
  J4_Perf --> J4_Bundle[Bundle Analysis<br/>Informational — no threshold yet]
  J4_Bundle --> J4_Gate{All Enabled Tests Passed?}
  J4_Gate -->|Yes| NotifySuccess[✅ Notify Team<br/>Ready to Merge<br/>Email — Teams when channel exists]
  J4_Gate -->|No| NotifyFail4[❌ Notify Team<br/>E2E / Visual / A11y Failure]
  J4_Start -->|Not yet| NotifySuccess
  NotifySuccess --> SuccessEnd([✅ CI Success<br/>PR Approved<br/>Ready to Merge])
  NotifyFail4 --> FailEnd

  %% Styling
  classDef ciJob fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
  classDef secJob fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
  classDef phase3 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
  classDef deferred fill:#eceff1,stroke:#90a4ae,stroke-width:2px,color:#455a64,stroke-dasharray: 5 5
  classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000
  classDef notifyFail fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#000
  classDef notifySuccess fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
  classDef endFail fill:#ef5350,stroke:#c62828,stroke-width:3px,color:#fff
  classDef endSuccess fill:#66bb6a,stroke:#388e3c,stroke-width:3px,color:#fff

  class J1_Checkout,J1_Setup,J1_Install,J1_PRT,J1_Lint,J1_Test,J1_Coverage,J1_Archive ciJob
  class J2_Checkout,J2_Install,J2_Build,J2_CEM,J2_Validate,J2_Wrappers,J2_Archive ciJob
  class J3_Checkout,J3_Install,J3_Build,J3_Validate,J3_Archive ciJob
  class J1b_Checkout,J1b_Install,J1b_Sonar,J1b_Gate,J1b_Archive secJob
  class J1c_Checkout,J1c_Install,J1c_Audit,J1c_Gate,J1c_Archive secJob
  class J4_Accessibility,J4_Visual,J4_E2E,J4_Bundle phase3
  class J4_Perf deferred
  class Parallel,CIGate,J4_Gate,J4_Start decision
  class NotifyFail1,NotifyFail1b,NotifyFail1c,NotifyFail2,NotifyFail3,NotifyFail4 notifyFail
  class NotifySuccess,J1_End,J1b_End,J1c_End,J2_End,J3_End notifySuccess
  class FailEnd endFail
  class SuccessEnd endSuccess
```
