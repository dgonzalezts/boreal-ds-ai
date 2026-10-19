# WIP - target Jenkins pipeline: ONE job, several stages (details TBC)

Draw.io source: [`boreal-jenkins-pipeline-wip.drawio`](boreal-jenkins-pipeline-wip.drawio)

**Status: WIP. No Jenkinsfile exists yet; stage details are TBC. Storybook deploy stays manual.**

```mermaid
flowchart LR
    TRG["Trigger<br/>TBC (merge, schedule or on demand)"]

    subgraph JOB["One Jenkins job (WIP)"]
        direction LR
        Q["Stage: Quality<br/>ITOPS-63109<br/>ITOPS-72071 (TBC)"]
        L["Stage: Lint"]
        T["Stage: Tests"]
        B["Stage: Build<br/>ITOPS-63110 (components)<br/>ITOPS-63111 (Storybook) - TBC"]
        REL["Stage: Release<br/>ITOPS-72204 publish to internal registry"]
    end

    AWS["Registry authentication<br/>(details TBC)"]
    NPMRC["Jenkins configures registry access at run time<br/>(details TBC)"]
    CA["Internal registry<br/>ITOPS-72203 (details TBC)"]
    GIT["Bitbucket: release commit + tags<br/>push to release/current (rights TBC)"]
    NPM["Public npm (ITOPS-72205)<br/>To be confirmed - after stable version"]

    TRG -.-> Q
    Q -.-> L
    L -.-> T
    T -.-> B
    B -. "artifacts" .-> REL
    REL -. "needs credentials" .-> AWS
    AWS -. "credentials" .-> NPMRC
    NPMRC -. "pnpm release:all --ci" .-> CA
    REL -. "tag + push" .-> GIT
    REL -. "deferred - TBC" .-> NPM

    classDef wip fill:#f5f5f5,stroke:#666,stroke-dasharray:5 5,color:#000
    class TRG,Q,L,T,B,REL,AWS,NPMRC,CA,GIT,NPM wip
```
