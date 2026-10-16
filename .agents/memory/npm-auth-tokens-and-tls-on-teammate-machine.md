# npm Authentication, Tokens and TLS on a Teammate's Machine

Source: the second release attempt from a teammate's machine (2026-10-13).

---

## Errors in the order they appeared

| Error | Cause | Fix |
| --- | --- | --- |
| `E403` "Two-factor authentication or granular access token with bypass 2fa enabled is required" | The account had no real 2FA (an emailed login code is not a 2FA factor); the first token also had a personal scope and no bypass | Enable 2FA and use `npm login`, or a token with scope `@pxglobal` and bypass 2FA |
| `E404` on `PUT` for a version that did not exist yet | npm answers an unauthorized publish with 404. A token created on npmjs.com is not installed on the machine; `~/.npmrc` held a different credential under the registry key | `npm config set //registry.npmjs.org/:_authToken=<token>` |
| `SELF_SIGNED_CERT_IN_CHAIN` on React | Company proxy re-signs HTTPS. pnpm 11 reads only auth and registry settings from `.npmrc`, so `cafile` is ignored; web-components passed because it publishes through npm | `NODE_EXTRA_CA_CERTS=<company root certificate PEM>` in the shell profile |

## Facts

- A token's "Packages and scopes" must include the scope of the package (`@pxglobal`). A personal scope (`@username`) cannot publish organization packages. The Organizations field only covers organization settings and members; it is not needed to publish.
- The owner publishes with an interactive login: the account has 2FA with a security key, and each publish is held for a browser approval. No token is involved.
- A token with bypass 2FA publishes without approval (a "validating" state for some minutes, then available). Bypass tokens lose direct publishing around January 2027 and then only stage a publish (npm changelog of 2026-07-08).
- An npm organization can enforce 2FA for its members; members without 2FA are then flagged for removal from the organization. Enable 2FA on the account before turning enforcement on.
- Never disable TLS verification (`strict-ssl=false`, `NODE_TLS_REJECT_UNAUTHORIZED=0`).
- The company root certificate is public but not stored in the repository; ask IT for it.

Related: [[npm-staged-publishing-first-release]], [[release-sequencing-wc-react-vue]].
