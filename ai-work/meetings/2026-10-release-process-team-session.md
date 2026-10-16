# Release process team session

**Duration:** 30 minutes
**Related plan:** `ai-work/plans/EOA-18749-release-process-remediation-patch-release-it.md` (T14, "Follow-up meeting")

## Goal

Everyone understands the rules that affect their pull requests today, and who may release while the Jenkins job is not live.

## Pre-read (5 minutes, before the meeting)

- `RELEASING.md`
- The "Release & Versioning" section of `CONTRIBUTING.md`

## Agenda

| Time      | Topic                                                                                                                                                                                                                                                                                            | Outcome                                                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| 0–10 min  | **PR titles and squash merges.** The squashed PR title is the source of the version bump and the changelog. Format, scopes, and `!` for breaking changes. Two or three examples of a wrong title and what it produces.                                                                             | Everyone writes correct titles.                               |
| 10–20 min | **The release flow.** What `release:all` does, in order: build, bump, publish, commit, tag, push. The batch rule: one bump per package, the highest level wins. How to read the failure table in `RELEASING.md`, especially "published, then the push failed".                                       | Everyone can tell when a release is half-done and who to call. |
| 20–25 min | **Direction.** CodeArtifact as the internal registry, then Jenkins as the single release owner. Public npm publishing is to be confirmed: the library may stay internal, and limitations may appear. What changes for the team: little for contributors; the machine-specific steps (npm login, 2FA) go away once Jenkins runs the release. | No surprises when Jenkins arrives.                            |
| 25–30 min | **Interim rules and open points.** Who may release manually, and only one release at a time. The backup publisher. Questions.                                                                                                                                                                      | Decisions recorded below.                                     |

## Decisions to record

1. Who runs manual releases until Jenkins is live, and does that stop afterwards?
2. Who is the single backup publisher? Add that person to the `@pxglobal` npm organization with publish rights and 2FA (a membership change, not a new shared account).
3. Where do people report a failed or half-finished release?

## Out of scope for this session

- Jenkins internals and CodeArtifact configuration. They are not decided yet.
- The static assets (S3 and CloudFront) work. It is not in Q4.
- New npm users or tokens. Jenkins publishing to CodeArtifact uses AWS roles, and an npm automation identity is only needed if public publishing is confirmed.

## Notes

_To fill in during the meeting._

### Decisions

-

### Actions

-
