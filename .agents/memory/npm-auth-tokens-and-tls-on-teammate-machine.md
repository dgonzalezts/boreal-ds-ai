# npm Authentication, Tokens and TLS on a Teammate's Machine

Source: the second release attempt from a teammate's machine (2026-10-13).

---

## Errors in the order they appeared

| Error | Cause | Fix |
| --- | --- | --- |
| `E403` "Two-factor authentication or granular access token with bypass 2fa enabled is required" | The account had no real 2FA (an emailed login code is not a 2FA factor); the first token also had a personal scope and no bypass | Enable 2FA and use `npm login`, or a token with scope `@pxglobal` and bypass 2FA |
| `E404` on `PUT` for a version that did not exist yet | npm answers an unauthorized publish with 404. A token created on npmjs.com is not installed on the machine; `~/.npmrc` held a different credential under the registry key | `npm config set //registry.npmjs.org/:_authToken=<token>` |
| `SELF_SIGNED_CERT_IN_CHAIN` on React | Company proxy re-signs HTTPS. pnpm 11 ignores `cafile` for `publish` (see the matrix below); web-components passed because it publishes through npm | pnpm 11: `NODE_EXTRA_CA_CERTS=<company root certificate PEM>` in the shell profile. pnpm 12: `cafile` in `.npmrc` instead |

## Which TLS setting each client honors (verified 2026-11-13)

Tested with certificate verification on, against a local HTTPS registry signed by a private CA that stands in for the proxy.

| Client | `view` | `publish` |
| --- | --- | --- |
| pnpm 11.28.2 | `NODE_EXTRA_CA_CERTS` and `cafile` | `NODE_EXTRA_CA_CERTS` only; `cafile` fails with `UNABLE_TO_VERIFY_LEAF_SIGNATURE` |
| pnpm 12.18.0 | `cafile` (project or user `.npmrc`); `NODE_EXTRA_CA_CERTS` is IGNORED (its HTTP client is not Node's; error `invalid peer certificate`) | `cafile` (project or user `.npmrc`) |
| npm | not tested | honors a user-level `cafile` |

`strict-ssl=false` hides all of this: every check passes with verification off, so a green run proves nothing about the certificate setup. The repository's `RELEASING.md` documents the setting.

Test technique: start a throwaway HTTPS server with a CA made by `openssl`, use a clean `HOME` and run the client with `env -u NODE_EXTRA_CA_CERTS` so no inherited setting masks the result.

## Facts

- A token's "Packages and scopes" must include the scope of the package (`@pxglobal`). A personal scope (`@username`) cannot publish organization packages. The Organizations field only covers organization settings and members; it is not needed to publish.
- The owner publishes with an interactive login: the account has 2FA with a security key, and each publish is held for a browser approval. No token is involved.
- A token with bypass 2FA publishes without approval (a "validating" state for some minutes, then available). Bypass tokens lose direct publishing around January 2027 and then only stage a publish (npm changelog of 2026-07-08).
- An npm organization can enforce 2FA for its members; members without 2FA are then flagged for removal from the organization. Enable 2FA on the account before turning enforcement on.
- Never disable TLS verification (`strict-ssl=false`, `NODE_TLS_REJECT_UNAUTHORIZED=0`).
- The company root certificate is public but not stored in the repository; ask IT for it.

Related: [[npm-staged-publishing-first-release]], [[release-sequencing-wc-react-vue]].
