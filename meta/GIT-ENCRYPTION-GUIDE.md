# Git Encryption Setup Guide for Evident

This repository uses **git-crypt** to transparently encrypt sensitive files at
rest in Git. This guide explains how team members can set up and use git-crypt
properly.

## 🔐 What is git-crypt?

git-crypt enables transparent encryption and decryption of files in a git
repository. Files which you choose to protect are encrypted when committed, and
decrypted when checked out. This means:

- Sensitive files are encrypted in the repository (including GitHub)
- Authorized users can read/edit files normally after unlocking
- Unauthorized users see only encrypted data

## 📋 Prerequisites

### Windows

```powershell
# Using Chocolatey
choco install git-crypt

# Or using Scoop
scoop install git-crypt

# Or download from: https://github.com/AGWA/git-crypt/releases
```

### macOS

```bash
brew install git-crypt
```

### Linux

```bash
# Debian/Ubuntu
sudo apt-get install git-crypt

# Fedora/RHEL
sudo dnf install git-crypt

# Arch
sudo pacman -S git-crypt
```

## 🚀 Initial Setup (First Time Only)

### For Repository Owner/Admin

1. **Initialize git-crypt** (Already done for this repo):

```bash
git-crypt init
```

2. **Add GPG users** (if using GPG keys):

```bash
# Export your GPG public key
gpg --export your-email@example.com > user.gpg

# Add the user
git-crypt add-gpg-user user.gpg
```

3. **Or export symmetric key** (simpler for small teams):

```bash
# Export the key to a secure location
git-crypt export-key /secure/location/Evident-git-crypt.key
```

### For Team Members

#### Option A: Using Symmetric Key (Recommended for Small Teams)

1. **Get the key** from repository admin (via secure channel like 1Password,
   Bitwarden, etc.)

2. **Clone the repository**:

```bash
git clone https://github.com/DTMBX/Evident.git
cd Evident
```

3. **Unlock the repository**:

```bash
git-crypt unlock /path/to/Evident-git-crypt.key
```

4. **Verify it's working**:

```bash
# Should show "not encrypted"
git-crypt status
```

#### Option B: Using GPG Keys (More Secure)

1. **Have admin add your GPG key** to the repository

2. **Clone and unlock**:

```bash
git clone https://github.com/DTMBX/Evident.git
cd Evident
git-crypt unlock
```

## 📂 What Files Are Encrypted?

Current encryption patterns in `.gitattributes`:

### Always Encrypted

- `secrets.enc`, `secrets.encrypted`, `*.secrets` - Explicit secret files
- `.env`, `.env.local`, `.env.production`, `.env.staging` - Environment files
  (if tracked)
- `*.key`, `*.pem`, `*.p12`, `*.pfx` - Private keys and certificates
- `barber-cam/**` - Body-worn camera footage and analysis
- `secure/**` - Secure output directory
- `database.ini`, `credentials.json` - Database credentials

### Never Tracked (in `.gitignore`)

- `.env` (local development - NOT committed)
- `*.db`, `*.sqlite` - Database files
- `logs/`, `*.log` - Log files
- `uploads/`, `bwc_videos/` - Uploaded content

## 🔧 Common Operations

### Check Encryption Status

```bash
# See which files are encrypted
git-crypt status

# Check specific file
git-crypt status path/to/file
```

### Lock Repository (Stop Decryption)

```bash
git-crypt lock
```

### Unlock Repository

```bash
# With symmetric key
git-crypt unlock /path/to/key

# With GPG
git-crypt unlock
```

### Verify File is Encrypted in Repo

```bash
# View raw encrypted content
git show HEAD:secure/passwords.txt | hexdump -C
```

## 🛡️ Security Best Practices

### DO ✅

- Keep the git-crypt key in a secure password manager (1Password, Bitwarden)
- Use GPG keys for larger teams
- Verify files are encrypted before pushing sensitive data
- Add new sensitive file patterns to `.gitattributes`
- Lock repository when not actively working

### DON'T ❌

- Commit the git-crypt key to the repository
- Share the key via email or chat
- Track truly sensitive files without encryption (add to `.gitattributes`)
- Commit `.env` files (use `.env.template` instead)
- Push to public forks without verifying encryption

## 📝 Adding New Encrypted Files

1. **Update `.gitattributes`**:

```properties
# Add new pattern
config/production/*.conf filter=git-crypt diff=git-crypt
```

2. **Force re-encrypt existing files**:

```bash
# Remove from index
git rm --cached path/to/file

# Re-add with new attributes
git add path/to/file
```

## 🔍 Troubleshooting

### "git-crypt: command not found"

- Install git-crypt (see Prerequisites)

### Files appear as gibberish

- Repository is locked. Run `git-crypt unlock /path/to/key`

### Changes not encrypting

- Check `.gitattributes` patterns
- Ensure file was added AFTER pattern was defined
- Try: `git rm --cached file && git add file`

### Key lost or corrupted

- Repository owner should generate new key
- All team members must re-unlock with new key

## 🔗 Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Unlock git-crypt
  run: |
    echo "${{ secrets.GIT_CRYPT_KEY }}" | base64 -d > /tmp/git-crypt-key
    git-crypt unlock /tmp/git-crypt-key
    rm /tmp/git-crypt-key
```

### Store Key in GitHub Secrets

```bash
# Encode key
base64 < Evident-git-crypt.key

# Add to GitHub Secrets as GIT_CRYPT_KEY
```

## 📚 Additional Resources

- [git-crypt Documentation](https://github.com/AGWA/git-crypt)
- [Git Attributes Documentation](https://git-scm.com/docs/gitattributes)
- [Security Best Practices](https://github.com/DTMBX/Evident/security)

## 🆘 Support

If you have issues with git-crypt setup:

1. Check this guide thoroughly
2. Verify git-crypt installation: `git-crypt --version`
3. Contact repository admin for key access
4. Open an issue if you believe there's a setup problem

---

**Last Updated**: January 31, 2026  
**Repository**: https://github.com/DTMBX/Evident  
**Maintained by**: Evident Team
