# Evident Technologies Security Guidelines

## 🔒 Security Best Practices

### Sensitive Files - NEVER COMMIT

The following files contain sensitive information and must NEVER be committed to
Git:

#### Environment Variables

- `.env`
- `.env.local`
- `.env.production`
- `.env.staging`
- Any file containing API keys or secrets

#### Database Files

- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `instance/*.db`

#### Signing Certificates & Keys

- `*.keystore`
- `*.jks`
- `*.p12`
- `*.mobileprovision`
- `*.cer`
- `*.pem`
- `*.key`

#### Configuration Files

- `appsettings.Production.json`
- `appsettings.Staging.json`
- `config.production.py`
- `launchSettings.json`

#### Financial & Business Data

- `INVESTOR-LOG.md`
- `*CONFIDENTIAL*.md`
- `*.xlsx` (financial spreadsheets)
- `excel-sheets/`

---

## ✅ Safe to Commit

These files are safe to commit and should be in version control:

- `.env.template` - Template with placeholder values
- `appsettings.json` - Development settings only
- `appsettings.Development.json` - Local development settings
- Source code files (`.py`, `.cs`, `.xaml`, etc.)
- Documentation (`.md` files)
- Build scripts (`.ps1`, `.sh`)
- Configuration templates

---

## 🔐 Encryption Strategy

### For Sensitive Configuration Files

If you need to commit production configuration:

1. **Use Environment Variables** (Recommended)

   ```bash
   # Store in CI/CD secrets, not in files
   export OPENAI_API_KEY=sk-...
   export STRIPE_SECRET_KEY=sk_live_...
   ```

2. **Use git-crypt** (For team collaboration)

   ```bash
   # Install git-crypt
   brew install git-crypt  # macOS
   choco install git-crypt # Windows

   # Initialize
   git-crypt init

   # Add users
   git-crypt add-gpg-user USER_ID

   # Mark files for encryption in .gitattributes
   echo "*.production.json filter=git-crypt diff=git-crypt" >> .gitattributes
   echo "config.production.py filter=git-crypt diff=git-crypt" >> .gitattributes
   ```

3. **Use Azure Key Vault / AWS Secrets Manager** (Production)
   - Store all secrets in cloud secret management
   - Reference secrets by name in code
   - Never store actual values in files

---

## 🛡️ Pre-Commit Checklist

Before committing, verify:

- [ ] No `.env` files staged
- [ ] No database files (`.db`, `.sqlite`)
- [ ] No API keys in code
- [ ] No signing certificates
- [ ] No financial data
- [ ] No user data or PII
- [ ] `.gitignore` is up to date
- [ ] Secrets are in environment variables

---

## 🔍 Scanning for Secrets

### Manual Check

```bash
# Search for potential secrets in staged files
git diff --cached | grep -i "api_key\|secret\|password\|token"
```

### Automated Tools

#### git-secrets (Recommended)

```bash
# Install
brew install git-secrets  # macOS
choco install git-secrets # Windows

# Setup
git secrets --install
git secrets --register-aws

# Add custom patterns
git secrets --add 'sk-[a-zA-Z0-9]{48}'  # OpenAI keys
git secrets --add 'sk_live_[a-zA-Z0-9]{99}'  # Stripe keys
```

#### TruffleHog

```bash
# Scan repository history
trufflehog git file://. --only-verified
```

---

## 🚨 If You Accidentally Commit Secrets

### Immediate Actions

1. **Revoke the exposed secret immediately**
   - Regenerate API keys
   - Rotate passwords
   - Invalidate tokens

2. **Remove from Git history**

   ```bash
   # Using BFG Repo-Cleaner (recommended)
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # Force push (WARNING: Rewrites history)
   git push --force
   ```

3. **Notify team members**
   - Alert all collaborators
   - Have them re-clone the repository

4. **Update secrets**
   - Generate new keys
   - Update production systems
   - Test thoroughly

---

## 📋 Environment Variable Management

### Development

```bash
# Create .env from template
cp .env.template .env

# Edit with your local values
nano .env
```

### Production

**Option 1: Cloud Provider Secrets**

```bash
# Azure
az keyvault secret set --vault-name EvidentVault --name OpenAIKey --value "sk-..."

# AWS
aws secretsmanager create-secret --name OpenAIKey --secret-string "sk-..."
```

**Option 2: CI/CD Secrets**

```yaml
# GitHub Actions
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
```

**Option 3: Docker Secrets**

```bash
# Create secret
echo "sk-..." | docker secret create openai_key -

# Use in docker-compose.yml
secrets:
  - openai_key
```

---

## 🔑 API Key Rotation Schedule

Rotate secrets regularly:

- **Development keys**: Every 90 days
- **Production keys**: Every 30 days
- **After team member departure**: Immediately
- **After suspected breach**: Immediately

---

## 📊 Security Audit

Run regular security audits:

```bash
# Check for secrets in history
git log -p | grep -i "api_key\|secret\|password"

# List all tracked files
git ls-files

# Check .gitignore effectiveness
git status --ignored
```

---

## 🎯 Quick Reference

### Files to NEVER commit:

- `.env*` (except `.env.template`)
- `*.db`, `*.sqlite`
- `*.keystore`, `*.p12`, `*.pem`
- `appsettings.Production.json`
- `*CONFIDENTIAL*.md`
- `*.xlsx` (financial data)

### Safe to commit:

- `.env.template`
- Source code
- Documentation
- Build scripts
- Development configs

### Tools:

- `git-secrets` - Prevent commits with secrets
- `git-crypt` - Encrypt files in Git
- `trufflehog` - Scan for secrets
- `BFG Repo-Cleaner` - Remove secrets from history

---

## 📞 Security Incident Response

If you discover a security issue:

1. **Do NOT commit the fix immediately**
2. Assess the scope of exposure
3. Revoke/rotate compromised credentials
4. Fix the vulnerability
5. Test thoroughly
6. Document the incident
7. Commit the fix with appropriate message

---

## ✅ Current Repository Status

This repository has:

- ✅ Comprehensive `.gitignore`
- ✅ `.env.template` for safe configuration
- ✅ Security documentation
- ✅ No secrets in committed files
- ✅ Build artifacts excluded
- ✅ Database files excluded

**Last Security Audit**: January 31, 2026 **Next Scheduled Audit**: February 28,
2026
