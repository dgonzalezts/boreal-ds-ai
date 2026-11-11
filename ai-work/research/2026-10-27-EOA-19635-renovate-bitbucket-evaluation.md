# Renovate on Bitbucket Server: evaluation (EOA-20024)

Status: research half done 2026-10-30; DevOps answers outstanding; no recommendation recorded yet.

## Sources

- Renovate docs, Bitbucket Data Center and Server platform: https://docs.renovatebot.com/modules/platform/bitbucket-server/
- Renovate docs, Dependency Dashboard: https://docs.renovatebot.com/key-concepts/dashboard/
- Renovate docs, FAQ (features not supported on every platform): https://docs.renovatebot.com/faq/
- Renovate docs, security presets (`minimumReleaseAge`): https://docs.renovatebot.com/presets-security/
- Mend, Renovate Enterprise self-hosted: https://docs.mend.io/renovate/latest/mend-renovate-enterprise-self-hosted
- Mend, Mend for Bitbucket Data Center: https://docs.mend.io/renovate/latest/mend-for-bitbucket-data-center

## Repository starting point

- No `renovate.json`, `renovate.json5`, `.renovaterc` or `.renovaterc.json` exists, and `package.json` has no `renovate` key (checked 2026-10-30).
- Policy phases (ADR-0016): Phase 1 manual monthly ticket, Phase 2 scheduled Jenkins report, Phase 3 self-hosted Renovate in Jenkins subject to DevOps approval.

## Renovate `platform=bitbucket-server`: requirements

| Requirement | Detail |
| --- | --- |
| Platform setting | `platform=bitbucket-server` in the Renovate config; `endpoint` points at the Bitbucket Server URL |
| Account | A dedicated Renovate user (default username `renovate-bot`; set `username` otherwise) with write access to the project |
| Credentials | An HTTP access token for that account, passed as `token`, `RENOVATE_TOKEN` or `--token`. Project or repository based tokens work only as `token` |
| Git transport | `--git-fs=http` in the documented test setup; SSH is not shown in the docs |
| Hosting | Self-hosted only: Renovate CLI run on a schedule (here, Jenkins) |
| Database note | With MySQL or MariaDB, `unicodeEmoji` must be `false` in the global config |

## Limitations on this platform

| Limitation | Source | Effect on the Boreal policy |
| --- | --- | --- |
| No assignees on PRs | Platform page | Reviewers cannot be auto-assigned; the PR list must be watched |
| No adding or removing labels | Platform page | The labels the policy would use (`dependencies`, `security`) cannot be applied by the bot |
| Creating issues not implemented (config-error alerts) | Platform page | A broken config produces no visible alert; check the Jenkins job log |
| `automergeStrategy` not implemented; all values behave as `auto` | Platform page | Merge strategy follows the repository default; the policy's squash-merge rule must be the repository default |
| Dependency Dashboard needs issues with Markdown checkboxes | Dashboard page | The dashboard is not available, so there is no single page showing pending majors and the approval flow for majors via the dashboard does not work |
| Jira issue creation unsupported on Bitbucket Server | FAQ | No Jira tickets from the bot; tickets for majors stay manual |

## Policy features and how Renovate would cover them

| Policy item | Renovate coverage | Open point |
| --- | --- | --- |
| Monthly window | `schedule:monthly` preset (first day of the month before 4 AM) or a custom `schedule` | The Jenkins job must run inside that window |
| Patch and minor batched in one PR | Group with a `packageRules` entry (`groupName`) | To be confirmed against the 6 holds |
| Majors in a separate PR per family | Separate PRs by default; families via `packageRules` and `matchPackageNames` | To be confirmed |
| Holds (caps and pins) | Not automatic: a cap needs a rule such as `allowedVersions` per package, kept in step with the manifest range | Hold register would live in two places |
| Minimum release age | `minimumReleaseAge` per rule (the security preset uses 3 days); does not apply to lockfile maintenance, pins, rollbacks and bumps | Repo already has pnpm `minimumReleaseAge` of 1 day, which still applies when the lockfile is regenerated |
| Security fixes within 2 weeks | `vulnerabilityAlerts` options; the docs example uses labels and assignees, which this platform cannot apply | To be confirmed which alert source is available without GitHub |
| Gates (`validate:all`, Storybook build) | Run by the Bitbucket PR build, not by Renovate | Needs the existing Jenkins PR job to run on bot PRs |
| Lockfile format and post-update steps | Renovate rewrites `pnpm-lock.yaml`; this repo formats the lockfile with the web-components Prettier | To be confirmed with a trial on a fork or test repository |

## Comparison with Mend

| Option | What it is | Notes |
| --- | --- | --- |
| Self-hosted Renovate CLI (open source) | The engine run by Jenkins | Free; the limitations above apply; we operate it |
| Mend Renovate Enterprise, self-hosted | Mend's packaging of the same engine with horizontal scaling, support and extra features | Mend lists Bitbucket Data Center among its supported platforms; the engine limitations on the platform page still need to be re-checked for this edition; licence and cost to be confirmed |
| Mend Renovate Community Edition | Free self-hosted app | Bitbucket Data Center support for this edition could not be confirmed from the sources found |
| Mend for Bitbucket Data Center | A separate self-hosted Mend integration that includes automated dependency fix PRs (Mend Remediate) | Part of Mend's paid product; scope and cost to be confirmed |

## Open questions for DevOps

1. Bot account: may a dedicated Bitbucket user (for example `renovate-bot`) be created, and with which write scope (this project only)?
2. Token: who creates and rotates the HTTP access token, and where is it stored (Jenkins credentials)?
3. Jenkins hosting: which agent runs the job, which Node and Docker versions are available, can the agent reach the npm registry and Bitbucket, and is a monthly schedule acceptable?
4. Is a Mend licence already available to the company, which would make the Enterprise or Mend for Bitbucket Data Center options viable?

## DevOps answers

| Question | Answer | Date | Source |
| --- | --- | --- | --- |
| Bot account | To be confirmed | | |
| Token | To be confirmed | | |
| Jenkins hosting | To be confirmed | | |
| Mend licence | To be confirmed | | |

## Recommendation

To be confirmed after the DevOps answers. One of: proceed, defer, reject.
