# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest (main branch) | ✅ |
| Previous releases | ⚠️ Best effort |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow responsible disclosure:

### Private Reporting (Preferred)

1. **DO NOT** open a public GitHub issue
2. Use GitHub Security Advisories or email maintainers
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Varies by severity (critical: days, high: weeks, medium/low: next release)
- **Credit:** We acknowledge security researchers who follow responsible disclosure

## Security Measures

### Application Security

✅ **Client-Side Only:** No backend servers, reducing attack surface
✅ **No API Keys:** Bible API requires no authentication
✅ **HTTPS Enforced:** When deployed via GitHub Pages, Vercel, Netlify, etc.
✅ **No User Passwords:** Uses browser-based persistence only
✅ **No Third-Party Trackers:** No analytics or tracking by default

### Data Security

✅ **Local Storage Only:** All user data stored in browser KV storage
✅ **No Server Database:** Nothing stored on remote servers
✅ **No User Authentication:** No password/credential handling
✅ **Public Domain Content:** All Bible text is public domain

### Dependency Security

✅ **Automated Scanning:** Dependabot runs weekly
✅ **npm audit:** Run on every install
✅ **Known Vulnerabilities:** Monitored via GitHub Security Advisories
✅ **License Compliance:** All dependencies use permissive licenses

## Security Best Practices

### For Developers

- Never commit secrets, API keys, or credentials
- Validate all user input
- Keep dependencies updated
- Run `npm audit` before committing
- Follow secure coding guidelines

### Before Deployment

```bash
# Check for vulnerabilities
npm audit

# Update dependencies
npm update

# Test build
npm run build && npm run preview
```

## Security Checklist for Deployment

- [ ] Enable HTTPS
- [ ] Configure CSP headers
- [ ] Set secure headers
- [ ] Enable HSTS
- [ ] Audit dependencies
- [ ] Test in multiple browsers

---

**Last Updated:** January 2025
