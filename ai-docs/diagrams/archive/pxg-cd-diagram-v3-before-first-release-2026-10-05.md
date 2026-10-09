# CD Diagram v3 — Boreal DS

## Changes from v2

- **Trigger is a manual release job** on `release/current`, not an automatic run on merge. The manual trigger/approval *is* the gate — the separate STG deploy + manual-approval stage is removed.
- **Versioning stays on `release-it`** (Option A): `pnpm run release:all --ci` (bump + changelog). No Changesets (`pnpm version-packages` / `.changeset` files removed).
- **Storybook is published to Chromatic** (public for alpha) — the S3 + CloudFront Storybook deployment across STG/PROD is removed.
- **One production distribution** (S3 + CloudFront) hosts two content sets via path prefixes: **Library CDN** `/components/v{version}/` + `/components/latest/`, and **static assets (icons/fonts)** `/icons/v{version}/` + `/icons/latest/`. No STG/PROD duplication.
- **Library CDN serves the browser build (UMD/IIFE)** for **enterprise clients with npm registry restrictions** — a **new output target** on `boreal-web-components` (see CI v3).
- **npm provenance removed** (unsupported on self-hosted Jenkins and requires a public source repo); publishing uses a **granular automation token** for `@pxglobal`.
- Scope `@boreal-ds/*` → **`@pxglobal/*`**; versions stay **`0.x` (preMajor)** — e.g. the first `@pxglobal` release is `0.14.0`, not `1.2.3`.
- **No GitHub/Bitbucket "Release" object:** release-it creates and pushes the git tags; notifications carry the notes.
- Final convergence covers the three real outputs: **npm publish + Storybook (Chromatic) + Library CDN**.

## Deferred / out of scope

- STG/PROD multi-environment duplication (single production CDN).
- A separate `packages/boreal-icons` package (icon assets are served from the shared static-assets path).
- npm provenance and trusted publishing.

---

```mermaid
flowchart TD
  Start([Manual trigger: Release Job<br/>on release/current]) --> R_Install[Setup Node 22.23.3<br/>.node-version + corepack → pnpm 11<br/>pnpm install --frozen-lockfile]

  R_Install --> R_Release[Run Release<br/>pnpm run release:all --ci<br/>release-it — bump versions + changelog<br/>0.x / preMajor]
  R_Release --> R_Commit[Commit Version + Changelog<br/>push via service account<br/>skip ci in message]
  R_Commit --> R_SBOM[Generate SBOM<br/>CycloneDX — archive sbom.json]
  R_SBOM --> R_Auth[Authenticate npm<br/>granular automation token<br/>scope @pxglobal<br/>NO provenance]
  R_Auth --> R_Publish[Publish Packages<br/>@pxglobal/boreal-web-components<br/>@pxglobal/boreal-react<br/>@pxglobal/boreal-vue<br/>@pxglobal/boreal-style-guidelines]
  R_Publish --> R_Tag[Push Tags<br/>release-it]
  R_Tag --> Parallel{Parallel Release Outputs}

  Parallel -->|Storybook| SB_Publish[Publish Storybook to Chromatic<br/>pnpm run deploy:docs<br/>CHROMATIC_PROJECT_TOKEN<br/>public for alpha]
  Parallel -->|Library CDN + Static Assets| CDN_Upload[Deploy to S3 + CloudFront<br/>one production distribution<br/>/components/v0.14.0/ + /components/latest/<br/>/icons/v0.14.0/ + /icons/latest/<br/>invalidate latest paths only]

  SB_Publish --> FinalGate{All Release Steps Complete?}
  CDN_Upload --> FinalGate

  R_Publish -.Publish Failed.-> Fail([❌ Partial Release<br/>manual intervention<br/>no auto-rollback])
  R_Tag -.Tag Failed.-> Fail
  CDN_Upload -.Upload Failed.-> CDN_Rollback[❌ Rollback CDN<br/>repoint /latest/ to previous<br/>notify team]
  CDN_Rollback --> Fail

  FinalGate -.Any Step Failed.-> Fail
  FinalGate -->|All Success ✓| FinalNotify[🎉 Release Complete<br/>Email — Teams when channel exists<br/>version + install cmd + links]
  FinalNotify --> Success([✅ Released<br/>npm + Storybook + CDN live])

  %% Styling
  classDef cdJob fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
  classDef cdnJob fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
  classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#000
  classDef fail fill:#ffcdd2,stroke:#d32f2f,stroke-width:2px,color:#000
  classDef success fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,color:#000
  classDef rollback fill:#ff8a80,stroke:#d32f2f,stroke-width:3px,color:#000
  classDef endFail fill:#ef5350,stroke:#c62828,stroke-width:3px,color:#fff
  classDef endSuccess fill:#66bb6a,stroke:#388e3c,stroke-width:3px,color:#fff

  class R_Install,R_Release,R_Commit,R_SBOM,R_Auth,R_Publish,R_Tag,SB_Publish cdJob
  class CDN_Upload cdnJob
  class Parallel,FinalGate decision
  class Fail fail
  class CDN_Rollback rollback
  class FinalNotify success
  class Success endSuccess
```
