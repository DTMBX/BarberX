# Domain Configuration — www.evident.icu

> **Canonical domain:** `www.evident.icu` **Apex domain:** `evident.icu`
> **Hosting:** GitHub Pages (Actions workflow) **Repository:** `xTx396/Evident`

---

## DNS Records

### GitHub Pages (Required)

| Type  | Host | Value                | TTL  |
| ----- | ---- | -------------------- | ---- |
| A     | @    | 185.199.108.153      | 3600 |
| A     | @    | 185.199.109.153      | 3600 |
| A     | @    | 185.199.110.153      | 3600 |
| A     | @    | 185.199.111.153      | 3600 |
| CNAME | www  | **xTx396.github.io** | 3600 |

> **CRITICAL:** The `www` CNAME must point to `xTx396.github.io`, NOT
> `dtmbx.github.io`.

### Proton Mail (DO NOT MODIFY)

| Type  | Host                            | Value                                       | Notes              |
| ----- | ------------------------------- | ------------------------------------------- | ------------------ |
| MX    | @                               | mail.protonmail.ch (priority 10)            | Primary MX         |
| MX    | @                               | mailsec.protonmail.ch (priority 20)         | Fallback MX        |
| TXT   | @                               | v=spf1 include:\_spf.protonmail.ch ~all     | SPF                |
| TXT   | \_dmarc                         | v=DMARC1; p=quarantine; ...                 | DMARC policy       |
| CNAME | protonmail.\_domainkey          | protonmail.domainkey.xxx.domains.proton.ch  | DKIM               |
| CNAME | protonmail2.\_domainkey         | protonmail2.domainkey.xxx.domains.proton.ch | DKIM               |
| CNAME | protonmail3.\_domainkey         | protonmail3.domainkey.xxx.domains.proton.ch | DKIM               |
| TXT   | \_github-pages-challenge-xTx396 | (value from GitHub Settings)                | Pages verification |

> Email addresses (`@tillerstead.com`) are Proton Mail and remain unchanged.

---

## GitHub Settings

1. Go to **Settings → Pages** in the repository
2. **Source:** Deploy from a branch → change to **GitHub Actions**
3. **Custom domain:** Enter `www.evident.icu`
4. **Enforce HTTPS:** Check ✅ (enable once DNS propagates)

---

## Files in This Repo

| File                           | Purpose                                                           |
| ------------------------------ | ----------------------------------------------------------------- |
| `CNAME`                        | Contains `www.evident.icu` — tells GitHub Pages the custom domain |
| `_config.yml` (`url:`)         | `https://www.evident.icu` — canonical URL for Jekyll              |
| `.github/workflows/jekyll.yml` | Build + deploy workflow with CNAME verification step              |
| `robots.txt`                   | Sitemap URL points to `https://www.evident.icu/sitemap.xml`       |

---

## Verification Checklist

```bash
# 1. Verify DNS A records (apex)
dig +short evident.icu A
# Expected: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153

# 2. Verify www CNAME
dig +short www.evident.icu CNAME
# Expected: xTx396.github.io.

# 3. Verify MX records (Proton Mail)
dig +short evident.icu MX
# Expected: 10 mail.protonmail.ch.  20 mailsec.protonmail.ch.

# 4. Verify SPF
dig +short evident.icu TXT | grep spf
# Expected: v=spf1 include:_spf.protonmail.ch ~all

# 5. Test HTTPS
curl -sI https://www.evident.icu | head -5
# Expected: HTTP/2 200

# 6. Test apex redirect
curl -sI https://evident.icu | grep -i location
# Expected: Location: https://www.evident.icu/
```

---

## Troubleshooting

- **404 on custom domain:** CNAME file missing from `_site/` build artifact. The
  workflow has a step to copy it.
- **DNS not propagating:** Wait 1-48 hours. Check with `dig` commands above.
- **HTTPS not available:** Enable "Enforce HTTPS" in GitHub Settings → Pages
  after DNS propagates.
- **Email broken:** Never modify MX, SPF, DMARC, or DKIM records. Email
  addresses stay `@tillerstead.com`.

---

_Last updated: 2026-01-26_
