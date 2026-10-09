# release-it Publish Flow

> **Scope:** how a Boreal DS package release runs today (verified in the rehearsal and the first real release, 2026-10-09). Procedure, preconditions and recovery: `RELEASING.md`. Policy: `CONTRIBUTING.md`. The earlier alpha-phase diagram (`@telesign`, `alpha` dist-tag) is in `archive/`.

## Expected release process

```mermaid
flowchart TD
  subgraph C["1 · Contribution — every PR"]
    C1["Branch off release/current"] --> C2["Conventional commits<br/>(commitlint via Husky)"]
    C2 --> C3["PR title in Conventional Commits format<br/>! if breaking, @handles in backticks"]
    C3 --> C4["Squash and merge<br/>= one commit on release/current"]
  end
  C4 --> R0
  subgraph R["2 · Release — maintainer or CI, clean release/current"]
    R0["pnpm release:all"] --> S{"style-guidelines:<br/>releasable commits in its folder?"}
    S -- yes --> SR["build · bump · CHANGELOG · publish · commit · tag · push"]
    S -- no --> SK["skip"]
    SR --> W{"web-components:<br/>releasable commits in WC or style-guidelines?"}
    SK --> W
    W -- yes --> WR["build + CEM check · bump · CHANGELOG · publish · commit · tag · push"]
    W -- no --> WK["skip"]
    WR --> REV["validate:pack:react<br/>(prerelease hook, runs before every React attempt)"]
    WK --> REV
    REV -- fails --> X["STOP — fix, then release the remaining packages<br/>one at a time (RELEASING.md)"]
    REV -- passes --> RE{"React:<br/>releasable commits in React, WC or style-guidelines?"}
    RE -- yes --> RER["bump · publish · commit · tag · push<br/>(no CHANGELOG)"]
    RE -- no --> REK["skip"]
    RER --> VUV["validate:pack:vue<br/>(prerelease hook)"]
    REK --> VUV
    VUV -- fails --> X
    VUV -- passes --> VU{"Vue:<br/>releasable commits in Vue, WC or style-guidelines?"}
    VU -- yes --> VUR["bump · publish · commit · tag · push<br/>(no CHANGELOG)"]
    VU -- no --> VUK["skip"]
  end
  VUR --> A{"npm holds a publish<br/>for approval?"}
  VUK --> A
  A -- yes --> AP["Maintainer approves in the browser<br/>(passkey / 2FA), dependency order"]
  A -- no --> V
  AP --> V["Verify: npm view, wrapper pins,<br/>tags, changelogs, tarballs"]
```

Releasable = `feat`, `fix`, `perf`, `revert`, or breaking. Each check looks at commits since **that package's own** last tag, touching its own folder (web-components also counts style-guidelines; React and Vue also count both).

## One package, step by step

```mermaid
sequenceDiagram
    participant P as Maintainer
    participant PRE as prerelease hook (React, Vue only)
    participant RI as release-it
    participant CL as changelog plugin + hook (WC, SG only)
    participant PM as pnpm publish
    participant REG as npm registry
    participant GIT as Bitbucket (release/current)

    P->>PRE: pnpm release:react
    PRE->>PRE: validate:pack:react — pack, install, build the test app
    PRE->>RI: continue to release-it (runs even if the package is later skipped)
    RI->>RI: build · git fetch · find last tag (git.tagMatch) · commits since, path-scoped
    RI->>RI: one bump from the highest level (breaking > feat/fix/perf/revert)
    RI->>RI: npm version (package.json only)
    RI->>CL: write CHANGELOG, then link the new heading to its Bitbucket compare page
    RI->>PM: pnpm publish --no-git-checks (tag latest)
    PM->>PM: workspace:* → exact version in the tarball package.json (local file unchanged)
    PM->>REG: publish tarball
    REG-->>PM: accepted (may be held for approval, staged publishing)
    PM-->>RI: exit 0 — release-it does not wait for the approval
    RI->>GIT: commit chore(release) · tag @pxglobal/boreal-react@x.y.z · push --follow-tags --no-verify
    P->>REG: approve the held version in the browser (passkey / 2FA)
    REG-->>P: version installable, latest = x.y.z
```

Notes:

- Publish happens **before** the commit, tag and push. A failed publish leaves nothing committed; a failed push leaves the package published with a local commit and tag (recovery: `RELEASING.md`).
- The commit, tag and push can happen up to a couple of minutes before an approved version becomes installable.
- A brand-new package name also gets a public placeholder version `0.0.0-stage` on its first publish.
