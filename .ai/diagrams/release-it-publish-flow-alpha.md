# release-it Publish Flow — Alpha Phase

> **Scope:** This diagram describes the publish sequence during the **alpha release phase**, where `workspace:*` (exact pin) is used and `publishPackageManager: "pnpm"` is required to prevent the raw workspace protocol from leaking into the published tarball.
>
> See `.claude/memory/release-it-pnpm-publish.md` for the full mechanics and gotchas.

```mermaid
sequenceDiagram
    participant RI as release-it
    participant FS as Local filesystem
    participant pnpm
    participant WS as pnpm-workspace.yaml
    participant REG as npm registry

    RI->>FS: bump version in package.json (e.g. 0.1.0-alpha.2)
    RI->>pnpm: exec ["pnpm", "publish", "--no-git-checks", "--tag", "alpha"]

    pnpm->>WS: read workspace root & packages globs
    pnpm->>FS: read boreal-react/package.json
    note over pnpm: finds dependencies:<br/>"@telesign/boreal-web-components": "workspace:*"

    pnpm->>FS: read boreal-web-components/package.json
    note over pnpm: resolves version: "0.1.0-alpha.0"

    pnpm->>pnpm: replace workspace:* → "0.1.0-alpha.0"<br/>in tarball package.json only<br/>(local file unchanged)

    pnpm->>pnpm: pack tarball (.tgz)
    note over pnpm: tarball package.json shows:<br/>"@telesign/boreal-web-components": "0.1.0-alpha.0"

    pnpm->>REG: publish tarball with --tag alpha
    REG-->>pnpm: 200 OK
    pnpm-->>RI: exit 0
    RI->>FS: git commit + tag + push
```
