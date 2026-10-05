---
ticket: EOA-18749
status: draft
created: 2026-10-01
---

# Release tooling evaluation rubric — release-it (Option A) vs. changesets (Option B)

Supports the Decision section of `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md`.
Plans: `ai-work/plans/EOA-18749-release-process-remediation-patch-release-it.md` (A), `ai-work/plans/EOA-18749-release-process-remediation-migrate-changesets.md` (B).

## How to use

1. **Gate criteria** are pass/fail. An option that fails any gate is out, regardless of score.
2. Score each weighted criterion 1–5 using the anchors. Weighted score = Σ(score × weight) / 5 (max 100).
3. Each reviewer scores independently first, then compares. Discuss any criterion where scores differ by ≥ 2.
4. Run the sensitivity check at the end before deciding.

## Gate criteria (pass/fail)

| # | Gate | A | B | Evidence |
|---|---|---|---|---|
| G1 | **No dummy releases**: a package with no changes since its last release is not published | Pass (config) | Pass (native) | A: `git.requireCommits: true` + `git.requireCommitsFail: false` + `git.commitsPath: "."` skip a package with no commits in its folder (verified in installed `release-it@19.2.4`, `lib/plugin/git/Git.js:49`). Wrappers still need "release if WC released in this run" logic. B: no changeset → no release; dependents are bumped only when their dependency is released. |
| G2 | Wrappers never ship with a stale WC pin (defect #5) | Pass (topology/script) | Pass (native) | A: wrappers are forced to release when WC releases. B: `updateInternalDependencies` + `determineDependents`. |
| G3 | Works without CI/pipeline access (current reality until EOA-18870) | Pass | Pass | Both can run locally from `release/current`. |
| G4 | Supports the `-alpha.N` track now and graduation to `1.0.0` later | Pass | Pass | A: `preRelease` + `strictSemVer`. B: `changeset pre enter alpha` / `pre exit`. |

A wrapper release that only repins a new WC version is **not** a dummy release. It ships a real dependency change and carries a `### Dependencies` changelog entry.

## Weighted criteria

| # | Criterion | Weight | 1 = | 3 = | 5 = |
|---|---|---|---|---|---|
| C1 | **Team friction** — change to the team's daily habits | 20 | New per-PR artifact + new mental model + retraining | One new habit, easy to learn | Nothing changes for contributors |
| C2 | **Integration & standardization** — monorepo-native, consistent across the 4 packages, Turborepo-recommended | 15 | Per-package custom glue, inconsistent | Consistent but hand-orchestrated | Single root config + single command, industry-standard |
| C3 | **Alignment with `ai-docs/guidelines/release-process.md`** | 15 | Guideline must be rewritten | Several sections rewritten | Only corrections needed |
| C4 | **Defect coverage** (#1–#5 from the audit) | 15 | ≤ 2 fixed | 4 fixed, one partial | All structurally fixed |
| C5 | **Failure visibility** — when someone breaks the convention, how and when is it noticed? | 10 | Silent, noticed after publish | Noticed at release time | Visible in the PR diff during review |
| C6 | **Delivery cost & risk in PI9** | 10 | New tool + migration + guideline rewrite | Moderate scripting | Config flags only |
| C7 | **Changelog quality for consumers** | 5 | Raw commit subjects, noisy | Filtered commit subjects | Human-written, consumer-facing |
| C8 | **`@proximus` migration / stable graduation effort** | 5 | Manual hacks per package | Documented manual steps | Native, no anchors needed |
| C9 | **Future CI readiness** (if EOA-18870 grants pipelines) | 5 | Needs server-side hook | Possible with scripting | Built-in check command |

## Draft scores (Claude, 2026-10-01 — for discussion, not final)

| # | Weight | A | B | Rationale |
|---|---|---|---|---|
| C1 | 20 | 5 | 2 | A: same commands, same commit flow; only "write a valid squash title" (already expected). B: every PR needs `pnpm changeset add` and a consumer-facing summary. |
| C2 | 15 | 3 | 5 | A: 4 `.release-it.json` files each need `strictSemVer`, path scoping ×2, `requireCommits`, URL formatter, plus shell orchestration. B: one `.changeset/config.json`, `changeset version` + `changeset publish`, Turborepo's documented recommendation. |
| C3 | 15 | 5 | 2 | The guideline is written for release-it (overview, version-progression table, Job 5d Jenkins stage, anchor-tag graduation steps, "Changesets has been removed"). A only corrects it. B rewrites most of it. |
| C4 | 15 | 3 | 5 | A: #2 and #3 native, #4 custom, #5 by topology, #1 only partial (title compliance unenforced). B: #1, #2, #3, #5 don't apply; #4 custom. |
| C5 | 10 | 2 | 4 | A: a malformed squash title is typed at merge time, after review, and silently dropped from changelog and bump. B: a missing `.changeset/*.md` shows up in the PR diff; `pnpm changeset status` self-check. |
| C6 | 10 | 4 | 2 | A: mostly config + one orchestration script. B: new tool, entering pre mode over existing `-alpha.N` tags, retire release-it, re-point `check-cem-changes.ts`, rewrite the guideline. |
| C7 | 5 | 2 | 4 | A: commit subjects (e.g. "Fix adjusments on PR" leaked into today's changelogs). B: summaries written for consumers. |
| C8 | 5 | 3 | 4 | A: anchor tags per package + remove `"tag": "alpha"` ×4 (documented in the guideline). B: changelogs come from changeset files, not the git log, so no anchor tags; `pre exit` to graduate. |
| C9 | 5 | 3 | 4 | A: `release-it --ci` is CI-ready, but the PR-title gate still needs a server-side hook. B: `changeset status --since=release/current` is a ready-made CI gate. |
| **Total** | **100** | **73** | **68** | |

## Sensitivity check

- **C1 + C3 overlap.** The guideline was written for release-it, so C3 partly measures C1 again. If C3's weight drops to 5 and the extra 10 is split evenly across C4 and C5 (+5 each), the scores flip to A = 68, B = 73 and B wins.
- **Timeline.** If the decision needs to land before the teammate's PTO (2026-10-06), C6 dominates, so A.
- **Natural switch point.** The cheapest moment to adopt B is the `@proximus` / `1.0.0` boundary: new package names start fresh changelogs, and B needs no anchor tags. Choosing A now doesn't close off B later.

## Revisit triggers (if A is chosen)

- A merged `feat`/`fix` PR is missing from a generated changelog (title-format miss) more than once in a PI.
- EOA-18870 grants CI/pipeline access. Re-score C5 and C9.
- Graduation to `@proximus` / `1.0.0` is scheduled (EOA-18867). Re-run this rubric before the scope rename.
