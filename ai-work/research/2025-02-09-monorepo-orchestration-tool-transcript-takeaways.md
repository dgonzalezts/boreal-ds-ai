# Monorepo Orchestration Tool – Detailed Transcript & Key Takeaways

## Relevant Transcript (Focused Extract)

> **Context:** The discussion centers on evaluating a monorepo orchestration tool and the reasons for ultimately rejecting it in favor of a manual process.

- The team explains that they **tested a monorepo orchestration tool** to manage shared packages and dependencies.
- During this testing phase, an issue emerged where consumers could **resolve dependencies via a local wrapper** instead of the **publicly published package URL**.
- This behavior made everything work locally, even when the package had **not yet been published**, creating a false sense of correctness.
- One participant explicitly flags this as dangerous, noting that it breaks the guarantee that consumers are validating against the same artifacts used in production.
- The group agrees that the tooling **abstracts away an important boundary** between local development and published artifacts.
- As a result, failures would only surface later—outside local development—making them harder and riskier to detect.
- Because of this, the team decided **not to continue investing in the orchestration tool**.
- Instead, they accepted a **manual process** that forces engineers to:
  - Explicitly publish packages
  - Manually update consumers
  - Be fully aware of whether a dependency is local or public

---

## Key Takeaways

### 1. The Rejection Was Tool-Specific, Not Anti-Monorepo
The decision was not against monorepos in general, but against an orchestration tool whose defaults encouraged unsafe dependency resolution.

### 2. Local Wrapper vs Public URL Was the Deciding Factor
The ability for the tool to silently point to a local wrapper instead of the public package URL was seen as a **critical reliability risk**.

### 3. Manual Process Acts as a Safety Mechanism
The manual workflow is intentional. It enforces clear transitions between:
- Local development
- Published artifacts
- Real consumer usage

### 4. Correctness Was Prioritized Over Convenience
The team preferred a slower, more explicit process rather than a faster workflow that could hide production-breaking issues.

### 5. Tooling Removed an Important Mental Model
By abstracting dependency resolution, the tool removed visibility into what was actually being consumed, which the team considered unacceptable.

---

## Conditions to Reconsider a Monorepo Orchestration Tool

The team explicitly left the door open to adopting a monorepo orchestration tool in the future, provided the following conditions are met:

- The tool must **enforce usage of published artifacts**, not local wrappers, in all non-local workflows.
- It must make the **local vs published dependency boundary explicit and visible** to developers.
- Accidental local linking should be **impossible or fail fast** rather than silently succeed.
- CI and release pipelines must validate against **public package URLs only**.
- The tooling should improve automation **without weakening correctness guarantees**.

Until these guarantees exist, manual processes are considered the safer option.

---

## Conclusion
The monorepo orchestration tool was abandoned because it blurred the line between local and published dependencies. Until that boundary can be enforced with strong guarantees, the team chose to rely on a manual process that keeps this distinction explicit and verifiable.

