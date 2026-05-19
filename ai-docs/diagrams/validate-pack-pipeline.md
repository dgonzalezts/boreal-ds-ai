# validate:pack Pipeline Diagrams

Diagrams documenting the `pnpm validate:pack` pipeline for `@telesign/boreal-web-components`, covering the full build sequence and the critical `postbuild.js` promotion step.

---

## Sequence: validate:pack end-to-end

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant Root as Root package.json
    participant Turbo as Turborepo
    participant Stencil as Stencil Build
    participant Post as postbuild.js
    participant Pack as pnpm pack
    participant React as boreal-react build
    participant CopyS as copy-styles.js (bin)

    Dev->>Root: pnpm validate:pack
    Root->>Turbo: turbo run validate:pack --filter=scripts-boreal
    Note over Turbo: dependsOn triggers upstream build first
    Turbo->>Stencil: @telesign/boreal-web-components#build
    Stencil->>Stencil: Compile components + run copy tasks
    Note over Stencil: css/ and scss/ land at<br/>dist/boreal-web-components/ (namespaced)
    Stencil->>Post: npm lifecycle: postbuild
    Post->>Post: Promote dist/boreal-web-components/css → dist/css/<br/>Promote dist/boreal-web-components/scss → dist/scss/
    Post-->>Turbo: exit 0 ✅
    Turbo->>Pack: scripts-boreal#validate:pack → pnpm pack
    Note over Pack: Snapshots "files[]"<br/>dist/ now contains css/ and scss/ at root
    Pack-->>Turbo: telesign-boreal-web-components-0.0.1.tgz
    Turbo->>React: install tgz + pnpm build
    React->>CopyS: boreal-copy-styles bin (from installed tgz)
    CopyS->>CopyS: existsSync(dist/css/) → true ✅
    CopyS->>React: Copy CSS/SCSS into boreal-react/dist/
    React-->>Turbo: build OK ✅
    Turbo-->>Dev: Pipeline completed successfully ✅
```

---

## Flowchart: postbuild.js promotion decision

```mermaid
flowchart TD
    A([stencil build]) --> B[dist output target\nnamespace: 'boreal-web-components']
    B --> C["dist/boreal-web-components/\n├── css/  ← copy dest='css'\n├── scss/ ← copy dest='scss'\n├── *.esm.js\n└── *.cjs.js"]

    C --> D{postbuild.js\nrunning?}

    D -->|YES — npm lifecycle hook| E["dist/\n├── css/   ← promoted ✅\n├── scss/  ← promoted ✅\n└── boreal-web-components/"]
    D -->|NO — key removed from package.json| F["dist/\n└── boreal-web-components/\n    ├── css/  ← stranded here\n    └── scss/ ← stranded here"]

    E --> G[pnpm pack snapshots 'files'\ndist/css/ and dist/scss/ included in .tgz]
    F --> H[pnpm pack snapshots 'files'\ndist/css/ and dist/scss/ MISSING from .tgz]

    G --> I[Consumer: boreal-copy-styles]
    H --> I

    I --> J{"existsSync\ndist/css/"}
    J -->|true ✅| K[Copy from @telesign/boreal-web-components\nStyles copied correctly]
    J -->|false ❌| L[Fallback: boreal-style-guidelines/dist\nbut it is a devDep — absent from tgz]
    L --> M[💥 ENOENT crash — pipeline fails]

    style D fill:#f5a623,color:#000
    style E fill:#417505,color:#fff
    style K fill:#417505,color:#fff
    style F fill:#9b0000,color:#fff
    style L fill:#9b0000,color:#fff
    style M fill:#9b0000,color:#fff
```
