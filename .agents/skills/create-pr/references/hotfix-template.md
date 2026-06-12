# Hotfix Pull Request — Boreal DS

## Title Format

```
fix(<scope>): <TICKET-ID> <urgent issue fixed>
```

**Example:**

```
fix(web-components): EOA-10099 prevent XSS in bds-tooltip content
```

---

## Description of the Hotfix

[Detail the critical issue being fixed and the level of urgency. What is broken in production?]

**Example:**

> Production bds-tooltip allows unsanitized HTML in the `content` prop, creating an XSS vulnerability when rendering user-generated content. CVE-2026-XXXXX assigned. Severity: High.

---

## Impact of the Issue

[What is the immediate impact on users, system stability, or security?]

**Example:**

> - **Security**: XSS attack vector in any app using bds-tooltip with user input
> - **Affected versions**: boreal-web-components 2.1.0 - 2.4.2
> - **Users impacted**: All consumers rendering dynamic tooltip content
> - **Urgency**: Requires immediate patch and coordinated disclosure

---

## Description of the Hotfix

[Explain how the critical issue is being resolved]

**Example:**

> - Escape all HTML in `content` prop using DOMPurify sanitization
> - Add new `allowHtml` boolean prop (default: false) for intentional HTML use
> - Update JSDoc to warn about XSS risks when `allowHtml=true`
> - Backport fix to all affected minor versions (2.1.x, 2.2.x, 2.3.x, 2.4.x)

---

## Testing Conducted

[Detail the testing done to ensure the hotfix resolves the issue without causing additional problems]

**Automated:**

- [ ] XSS injection tests with malicious payloads
- [ ] Regression tests for existing tooltip functionality
- [ ] Integration tests with allowHtml enabled/disabled

**Manual:**

- [ ] Verified sanitization prevents script execution
- [ ] Tested legitimate HTML rendering with allowHtml=true
- [ ] Validated in production-like staging environment
- [ ] Confirmed no visual regressions

---

## Deployment Plan

[Outline the release and deployment strategy for this hotfix]

**Example:**

1. Publish patch versions: 2.4.3, 2.3.3, 2.2.3, 2.1.3
2. Update boreal-react and boreal-vue wrappers
3. Notify all teams via Slack #design-system-alerts
4. Update security advisory on GitHub
5. Coordinate with Security team for CVE disclosure

---

## Rollback Plan

[If the hotfix causes issues, how will it be rolled back?]

**Example:**

> If regressions detected: npm deprecate affected versions, publish rollback patch with original behavior + prominent security warning in README.

---

## Additional Remarks

[Notes for reviewers, including any potential risks or side effects]

**Example:**

> - **Breaking change risk**: Low — default behavior is safe, opt-in for HTML
> - **Performance impact**: Minimal — DOMPurify adds ~2KB gzipped
> - **Follow-up required**: Audit all other components for similar XSS vectors
> - **Communication**: Security team coordinating public disclosure timeline

---

## References

Closes EOA-XXXXX
Refs CVE-2026-XXXXX

---

## Checklist

### Hotfix Verification

- [ ] The hotfix addresses the critical issue effectively
- [ ] Root cause identified and fixed (not just symptoms)
- [ ] Tested thoroughly in production-like environment
- [ ] No new bugs or regressions introduced
- [ ] Rollback plan documented and ready

### Security (if applicable)

- [ ] Security team notified and coordinating disclosure
- [ ] CVE assigned and tracked
- [ ] Vulnerable versions clearly identified
- [ ] Patch versions prepared for all affected releases
- [ ] Security advisory drafted

### Testing

- [ ] Unit tests verify the fix works
- [ ] Regression tests prevent the issue from returning
- [ ] Edge cases tested (various inputs, scenarios)
- [ ] Integration tests pass
- [ ] Manual verification in staging environment

### Boreal DS Standards

- [ ] Follows conventional commit format
- [ ] Ticket and CVE references included
- [ ] TypeScript types are correct
- [ ] Design tokens preserved
- [ ] No unnecessary changes outside hotfix scope

### Communication

- [ ] All stakeholders informed about the hotfix
- [ ] Release notes prepared with severity and mitigation
- [ ] Migration guide provided if breaking change required
- [ ] Security advisory published (if applicable)
- [ ] Teams notified via appropriate channels

### Deployment Readiness

- [ ] Patch versions tagged and ready to publish
- [ ] CI/CD pipeline verified
- [ ] Deployment window scheduled (if needed)
- [ ] Monitoring and alerting configured
- [ ] On-call team briefed on potential issues
