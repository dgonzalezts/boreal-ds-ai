# Security Patch Pull Request — Boreal DS

## Title Format

```
fix(<scope>): <TICKET-ID> <security vulnerability fixed>
```

**Example:**

```
fix(web-components): EOA-10099 sanitize HTML in bds-tooltip content prop
```

---

## ⚠️ Security Notice

**Visibility:** This PR may contain sensitive security information.

- [ ] PR marked as **Draft** until coordinated disclosure
- [ ] Security team notified
- [ ] CVE assigned (if applicable)

---

## Description of the Security Vulnerability

[Detail the vulnerability and the security risk it poses. Include severity rating.]

**Example:**

> **Vulnerability**: XSS (Cross-Site Scripting) in bds-tooltip component
> **Severity**: High (CVSS 7.5)
> **Attack Vector**: User-controlled content rendered as unsanitized HTML
> **Affected Versions**: boreal-web-components 2.1.0 - 2.4.2
> **CVE**: CVE-2026-XXXXX (pending assignment)

---

## Impact of the Vulnerability

[Discuss implications for system security, user data protection, and potential exploit scenarios]

**Example:**

> - **Exploit scenario**: Attacker injects `<script>` tag via tooltip content, executes arbitrary JavaScript in user's browser
> - **Data at risk**: Session tokens, cookies, localStorage data
> - **Users affected**: All apps using bds-tooltip with user-generated content
> - **Likelihood**: High — common pattern in customer support chat features

---

## Description of the Security Patch

[Detail the vulnerability fix and how it mitigates the security risk]

**Example:**

> - Sanitize all HTML in `content` prop using DOMPurify (trusted sanitization library)
> - Add opt-in `allowHtml` boolean prop (default: false) for intentional HTML rendering
> - Update JSDoc with security warning when `allowHtml=true`
> - Add Content Security Policy recommendations to documentation
> - Backport fix to all affected versions (2.1.x - 2.4.x)

---

## Testing Conducted

[Provide testing details to ensure the vulnerability is fully addressed and no new issues introduced]

**Security Testing:**

- [ ] XSS payload tests (OWASP Top 10 vectors)
- [ ] DOM-based XSS tests
- [ ] Reflected XSS tests
- [ ] Sanitization bypass attempts
- [ ] CSP compatibility verified

**Regression Testing:**

- [ ] Existing functionality works with sanitization enabled
- [ ] Legitimate HTML renders correctly with allowHtml=true
- [ ] Performance impact measured (acceptable)
- [ ] No new console errors or warnings

**Penetration Testing:**

- [ ] Security team review completed
- [ ] Third-party audit (if required)
- [ ] Exploit verified as no longer possible

---

## Severity Assessment

**CVSS Score:** [e.g., 7.5 High]

**CWE Classification:** [e.g., CWE-79: Cross-Site Scripting]

**Severity Justification:**
[Explain the severity rating based on exploitability, impact, and scope]

---

## Affected Versions

| Package               | Vulnerable Versions | Patched Versions           |
| --------------------- | ------------------- | -------------------------- |
| boreal-web-components | 2.1.0 - 2.4.2       | 2.1.3, 2.2.3, 2.3.3, 2.4.3 |
| boreal-react          | 2.1.0 - 2.4.2       | 2.1.3, 2.2.3, 2.3.3, 2.4.3 |
| boreal-vue            | 2.1.0 - 2.4.2       | 2.1.3, 2.2.3, 2.3.3, 2.4.3 |

---

## Mitigation Steps for Users

[Provide clear upgrade instructions and temporary workarounds]

**Immediate Action Required:**

1. Upgrade to latest patch version: `pnpm update @telesign/boreal-web-components`
2. Review all usage of `bds-tooltip` with user-generated content
3. Audit other components for similar XSS vectors

**Temporary Workaround (if upgrade not immediately possible):**

```typescript
// Manually sanitize content before passing to tooltip
import DOMPurify from 'dompurify';
<bds-tooltip content={DOMPurify.sanitize(userInput)} />
```

---

## Disclosure Timeline

[Coordinated disclosure schedule]

**Example:**

- **Day 0**: Vulnerability reported to security@telesign.com
- **Day 1**: Security team triage and severity assessment
- **Day 3**: Patch development completed
- **Day 5**: Security advisory drafted
- **Day 7**: Patch released, coordinated disclosure begins
- **Day 14**: Public CVE disclosure (after user upgrade window)

---

## Additional Remarks

[Notes on potential risks, follow-up work, or related security concerns]

**Example:**

> - **Follow-up required**: Audit bds-alert, bds-banner, and bds-notification for similar XSS risks
> - **Breaking change**: allowHtml defaults to false (safe by default)
> - **Migration effort**: Low — most apps don't need HTML in tooltips
> - **Dependencies**: DOMPurify adds ~8KB gzipped (acceptable for security)

---

## References

Closes EOA-XXXXX
Refs CVE-2026-XXXXX
[Link to security advisory when published]

---

## Checklist

### Security Verification

- [ ] The patch adequately addresses the identified vulnerability
- [ ] No new vulnerabilities introduced by the patch
- [ ] Security testing completed with penetration test scenarios
- [ ] Third-party security review completed (if required)
- [ ] Exploit verified as no longer possible after patch

### CVE & Disclosure

- [ ] CVE requested/assigned (if applicable)
- [ ] Security advisory drafted and ready to publish
- [ ] Coordinated disclosure timeline established
- [ ] Affected users identified and notification plan ready
- [ ] Public disclosure timing coordinated with security team

### Testing

- [ ] XSS payload tests pass (no script execution)
- [ ] Sanitization library (DOMPurify) integrated correctly
- [ ] Regression tests verify no functional breakage
- [ ] Performance impact acceptable
- [ ] All existing tests pass

### Patch Quality

- [ ] Patch follows secure coding best practices
- [ ] Defense-in-depth approach applied (multiple layers of protection)
- [ ] Input validation and output encoding implemented
- [ ] Secure defaults enforced (allowHtml=false by default)
- [ ] No security warnings in dependency audit

### Boreal DS Standards

- [ ] Follows conventional commit format
- [ ] TypeScript types are correct and safe
- [ ] Design tokens preserved
- [ ] Component API maintains backward compatibility (if possible)
- [ ] Documentation updated with security warnings

### Communication

- [ ] Security team notified and coordinating disclosure
- [ ] All stakeholders informed via secure channel
- [ ] Release notes prepared with severity and mitigation steps
- [ ] Migration guide provided (if breaking change required)
- [ ] Security advisory ready to publish

### Deployment Readiness

- [ ] Patch versions prepared for all affected releases
- [ ] CI/CD pipeline verified
- [ ] Rollback plan documented
- [ ] Monitoring configured to detect exploit attempts
- [ ] Post-deployment verification plan ready
