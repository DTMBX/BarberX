# Environment Variables Security Guide

## 🔐 Critical Assessment

### **MUST BE SECRET** ❌ NEVER COMMIT TO CODE

| Variable                  | Sensitivity | Why It's Secret                                                 | Current Status          |
| ------------------------- | ----------- | --------------------------------------------------------------- | ----------------------- |
| **SECRET_KEY**            | 🔴 CRITICAL | Flask session encryption - compromised = session hijacking      | ⚠️ Weak default in .env |
| **STRIPE_SECRET_KEY**     | 🔴 CRITICAL | Full access to Stripe account - can charge cards, refunds, etc. | ❌ MISSING from .env    |
| **STRIPE_WEBHOOK_SECRET** | 🔴 CRITICAL | Validates webhook authenticity - prevents payment fraud         | ❌ MISSING from .env    |
| **AMPLITUDE_API_KEY**     | 🟠 HIGH     | Access to analytics data - can track/modify user events         | ❌ MISSING from .env    |
| **OPENAI_API_KEY**        | 🔴 CRITICAL | Billed to your account - can rack up thousands in charges       | ⚠️ Commented out        |
| **ANTHROPIC_API_KEY**     | 🔴 CRITICAL | Same as OpenAI - direct billing access                          | ⚠️ Commented out        |
| **HUGGINGFACE_TOKEN**     | 🟠 HIGH     | Access to private models and datasets                           | ⚠️ Commented out        |

### **SHOULD BE IN ENV** ✅ Not Secret, But Environment-Specific

| Variable                   | Sensitivity | Why It's in Env                                                | Current Status       |
| -------------------------- | ----------- | -------------------------------------------------------------- | -------------------- |
| **STRIPE_PUBLISHABLE_KEY** | 🟢 PUBLIC   | Intentionally public (client-side), but env for easy switching | ❌ MISSING from .env |
| **STRIPE_PRICE_PRO**       | 🟢 PUBLIC   | Stripe Price IDs are public references                         | ❌ MISSING from .env |
| **STRIPE_PRICE_PREMIUM**   | 🟢 PUBLIC   | Same - just product references                                 | ❌ MISSING from .env |
| **FLASK_ENV**              | 🟢 CONFIG   | Controls debug mode, caching - different per environment       | ✅ Already in .env   |
| **CORS_ORIGINS**           | 🟢 CONFIG   | Domain whitelist - changes per deployment                      | ✅ Already in .env   |
| **MAX_CONTENT_LENGTH**     | 🟢 CONFIG   | Upload limits - may differ by tier/environment                 | ✅ Already in .env   |
| **DATABASE_URL**           | 🟡 MEDIUM   | Connection string (contains password if remote DB)             | ⚠️ Commented out     |

--

## 🚨 Current Security Issues

### ❌ **CRITICAL: Weak SECRET_KEY**

```bash
# Current .env (line 2)
SECRET_KEY=Evident-legal-tech-2026-super-secure-change-me
```

**Problem:** This is a predictable, weak key that's likely committed to version control.

**Attack Vector:**

- Session hijacking
- Cookie forgery
- CSRF token bypass

**Fix:**

```bash
# Generate a strong key:
python -c "import secrets; print(secrets.token_hex(32))"

# Then update .env:
SECRET_KEY=<generated-64-char-hex-string>
```

### ❌ **MISSING: Stripe Configuration**

The code expects these variables but they're not in .env:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_PRO`
- `STRIPE_PRICE_PREMIUM`

**Impact:** Stripe integration won't work; payment processing will fail.

### ❌ **MISSING: Analytics Configuration**

- `AMPLITUDE_API_KEY` - Analytics tracking won't work

--

## ✅ Recommended .env Structure

**Created:** `.env.example` (template file)

### **Usage:**

```bash
# 1. Copy template
cp .env.example .env

# 2. Fill in your secrets
nano .env  # or use your editor

# 3. Verify .env is in .gitignore
cat .gitignore | grep .env
```

### **What's Different:**

- ✅ Clear sections: SECRETS vs PUBLIC vs CONFIG
- ✅ Comments explain each variable's purpose
- ✅ Security warnings for critical secrets
- ✅ Generation instructions for SECRET_KEY
- ✅ All Stripe variables included
- ✅ Production deployment checklist

--

## 🔒 Security Best Practices

### **1. Never Commit Secrets**

```bash
# Check what's tracked:
git status

# If .env is tracked, remove it:
git rm -cached .env
git commit -m "Remove .env from tracking"

# Verify .gitignore includes:
.env
.env.local
.env.production
```

### **2. Use Environment-Specific Files**

```
.env.example        # Template (safe to commit)
.env                # Development (NEVER commit)
.env.production     # Production (NEVER commit)
.env.staging        # Staging (NEVER commit)
```

### **3. Rotate Secrets Regularly**

- SECRET_KEY: Every 90 days or after team member departure
- API Keys: When exposed or every 6 months
- Webhook Secrets: If webhook logs show suspicious activity

### **4. Use Secret Management in Production**

Consider using:

- **Render:** Environment variables dashboard (encrypted at rest)
- **Heroku:** Config vars
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **GitHub Secrets** (for CI/CD)

### **5. Limit Secret Access**

- Production secrets: Only ops team
- Development secrets: Only developers
- Use separate Stripe accounts for test vs live

--

## 🎯 Immediate Action Items

### **Priority 1: CRITICAL** 🔴

- [ ] Generate strong `SECRET_KEY` and update .env
- [ ] Add all Stripe variables to .env
- [ ] Verify .env is NOT committed to Git
- [ ] Add .env.example to version control

### **Priority 2: HIGH** 🟠

- [ ] Add `AMPLITUDE_API_KEY` if using analytics
- [ ] Set up production secrets in Render/deployment platform
- [ ] Review access to production environment variables
- [ ] Document who has access to production secrets

### **Priority 3: MEDIUM** 🟡

- [ ] Create .env.production with live keys
- [ ] Set up secret rotation schedule
- [ ] Add pre-commit hook to prevent .env commits
- [ ] Document secret recovery procedures

--

## 🛡️ Validation Script

```bash
# Check for exposed secrets in Git history
git log -all -full-history -source -oneline - .env

# Search for potential secrets in codebase
grep -r "sk_live_\|sk_test_\|whsec_\|SECRET_KEY=" --exclude-dir=.git .

# Verify .gitignore is working
git check-ignore -v .env
```

--

## 📋 Pre-Deployment Checklist

Before deploying to production:

- [ ] All secrets use strong, random values
- [ ] No hardcoded secrets in code (all use os.getenv())
- [ ] .env is in .gitignore and NOT in repo
- [ ] Production uses different secrets than development
- [ ] Stripe uses live keys (sk*live*, pk*live*)
- [ ] SESSION_COOKIE_SECURE=True for HTTPS
- [ ] FLASK_ENV=production (disables debug mode)
- [ ] CORS_ORIGINS set to actual domain(s)
- [ ] Database uses PostgreSQL (not SQLite)
- [ ] Backup of all secrets stored securely offline

--

## 🔗 Related Documentation

- `.env.example` - Template with all required variables
- `.gitignore` - Verify secrets are excluded
- `STRIPE-BUSINESS-SETUP.md` - Stripe configuration guide
- `DEPLOYMENT-GUIDE.md` - Production deployment steps

--

## 🆘 If Secrets Are Exposed

### **If .env was committed:**

1. **Immediately rotate all secrets**
   - Generate new SECRET_KEY
   - Rotate Stripe keys in dashboard
   - Regenerate webhook secret
   - Rotate API keys

2. **Remove from Git history**

   ```bash
   git filter-branch -force -index-filter \
     "git rm -cached -ignore-unmatch .env" \
     -prune-empty -tag-name-filter cat - -all

   git push origin -force -all
   ```

3. **Notify affected parties**
   - Security team
   - Stripe support
   - API providers

### **If pushed to public GitHub:**

- Assume ALL secrets are compromised
- GitHub automatically scans for secrets and may alert you
- Rotate everything immediately
- Consider secrets burned - generate new ones

--

## ✅ Current Status Summary

| Category       | Status       | Action Needed         |
| -------------- | ------------ | --------------------- |
| .gitignore     | ✅ Good      | .env is excluded      |
| SECRET_KEY     | ⚠️ Weak      | Generate strong key   |
| Stripe Secrets | ❌ Missing   | Add to .env           |
| API Keys       | ⚠️ Commented | Add if using features |
| .env.example   | ✅ Created   | Commit to repo        |
| Documentation  | ✅ Complete  | This file             |

--

**Last Updated:** January 26, 2026  
**Severity:** 🔴 HIGH - Immediate action required for SECRET_KEY and Stripe secrets
