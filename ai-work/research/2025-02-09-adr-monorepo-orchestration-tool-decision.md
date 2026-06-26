# ADR: Monorepo Orchestration Tool Decision

## Status
Rejected

## Context
The team evaluated a monorepo orchestration tool to manage shared packages and dependencies across the repository. The goal was to reduce manual steps and improve developer efficiency.

During testing, the tool introduced behavior where consumers could resolve dependencies via local wrappers instead of publicly published package URLs. This created scenarios where systems worked locally without validating against real production artifacts.

## Decision
The team decided **not to adopt** the monorepo orchestration tool and to continue using a manual process for dependency management and package publication.

## Rationale
- The tool blurred the boundary between **local development** and **published artifacts**.
- Local wrappers could be used unintentionally, masking missing or incorrect publications.
- This reduced confidence that changes were validated in production-like conditions.
- Correctness and reliability were prioritized over developer convenience.

## Consequences
### Positive
- Clear and explicit control over what is published and consumed
- Strong guarantees that consumers use real, public artifacts
- Reduced risk of late-stage or production-only failures

### Negative
- Slower workflows
- Increased manual effort
- Higher coordination cost between teams

## Future Considerations
A monorepo orchestration tool may be reconsidered if it:
- Enforces public artifact usage outside local development
- Makes dependency resolution explicit and auditable
- Prevents silent fallback to local wrappers
- Integrates safely with CI and release pipelines

Until then, the manual process remains the accepted trade-off.

