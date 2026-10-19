# Current manual release flow (maintainer machine, macOS/Linux)

Draw.io source: [`boreal-release-flow.drawio`](boreal-release-flow.drawio)

```mermaid
flowchart TD
    PR["PR (Conventional Commit title)<br/>squash-merge into release/current"]
    PRE["Maintainer: fnm use, pnpm install --frozen-lockfile,<br/>npm whoami, on release/current, clean tree"]

    subgraph REL["pnpm release:all (workspace-concurrency=1)"]
        direction TB
        R1["release-it: @pxglobal/boreal-style-guidelines"]
        R2["release-it: @pxglobal/boreal-web-components<br/>before:init build + check:cem"]
        R3["release-it: @pxglobal/boreal-react<br/>prerelease: validate:pack:react"]
        R4["release-it: @pxglobal/boreal-vue<br/>prerelease: validate:pack:vue"]
        R1 -- "1 -> 2" --> R2
        R2 -- "2 -> 3" --> R3
        R3 -- "3 -> 4" --> R4
    end

    PUB["npm publish (pnpm publish)<br/>public @pxglobal; may need browser approval"]
    TAG["Commit + tag @pxglobal/pkg@version<br/>push --follow-tags to origin"]
    DOC["pnpm deploy:docs<br/>Storybook build + Chromatic"]

    PR -- "merged" --> PRE
    PRE -- "pnpm release:all" --> R1
    R3 -- "after bump (each package)" --> PUB
    PUB -- "then" --> TAG
    TAG -- "after all packages released" --> DOC

    classDef step fill:#dae8fc,stroke:#6c8ebf,color:#000
    classDef rel fill:#fff2cc,stroke:#d6b656,color:#000
    classDef out fill:#d5e8d4,stroke:#82b366,color:#000
    class PR,PRE step
    class R1,R2,R3,R4 rel
    class PUB,TAG,DOC out
```

The edge from the React node to `PUB` is drawn that way in the draw.io source. In practice every package that has a releasable bump goes through publish, tag and push, as described in `RELEASING.md`.
