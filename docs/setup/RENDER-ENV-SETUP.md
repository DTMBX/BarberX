# Render.com Environment Variables Setup

**Last Updated:** January 28, 2026  
**Status:** Required for production deployment

## Critical Action Required

After the recent security fixes, the following environment variables **must be
set** on Render.com before the app will work correctly.

## 🔐 Required Environment Variables

### 1. Navigate to Render Dashboard

1. Go to https://dashboard.render.com
2. Select your **Evident.info** web service
3. Click **Environment** tab in the left sidebar

### 2. Add/Update These Variables

Click **Add Environment Variable** for each:

#### **Core Security** (REQUIRED)

```bash
SECRET_KEY=<generate-64-char-random-string>
ADMIN_EMAIL=admin@Evident.info
ADMIN_PASSWORD=<your-secure-admin-password>
```

**Generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

#### **Database** (Auto-set if PostgreSQL attached)

```bash
DATABASE_URL=<auto-populated-by-render>
```

✅ This should already be set if you created a PostgreSQL database

#### **Stripe Payment Processing** (REQUIRED for pricing page)

```bash
STRIPE_PRICING_TABLE_ID=prctbl_YOUR_ACTUAL_PRICING_TABLE_ID
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_ACTUAL_PUBLISHABLE_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_ACTUAL_SECRET_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_ACTUAL_WEBHOOK_SECRET
```

**⚠️ SECURITY CRITICAL:** The example keys shown above in previous versions were
LIVE production credentials and have been removed. You MUST use your own Stripe
credentials from your Stripe Dashboard.

**Where to find these:**

1. Go to https://dashboard.stripe.com
2. **STRIPE_PRICING_TABLE_ID**: Products → Pricing Tables → Create/Select Table
   → Copy Table ID (starts with `prctbl_`)
3. **STRIPE_PUBLISHABLE_KEY**: Developers → API keys → Publishable key (starts
   with `pk_live_`)
4. **STRIPE_SECRET_KEY**: Developers → API keys → Secret key → Reveal (starts
   with `sk_live_`)
5. **STRIPE_WEBHOOK_SECRET**: Developers → Webhooks → Add endpoint → Copy
   signing secret (starts with `whsec_`)

#### **Optional Services**

```bash
# OpenAI (for AI features)
OPENAI_API_KEY=sk-proj-<your-key>

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AWS S3 (for large file storage)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_BUCKET_NAME=Evident-uploads
AWS_REGION=us-east-1
```

### 3. Save and Deploy

1. Click **Save Changes** at the bottom
2. Render will automatically redeploy your app
3. Wait 2-3 minutes for deployment to complete
4. Check logs for "✅ Configuration loaded successfully"

## 🔍 Verification Steps

### Test Environment Variables

```bash
# In Render Shell (Dashboard → Shell tab)
echo $SECRET_KEY        # Should show your secret key
echo $DATABASE_URL      # Should show postgres://...
echo $STRIPE_PUBLISHABLE_KEY  # Should show pk_live_...
```

### Test App Functionality

1. **Visit your app**: https://Evident-info.onrender.com
2. **Check pricing page**: https://Evident-info.onrender.com/pricing
   - Should show Stripe pricing table
   - No console errors about missing publishable key
3. **Test admin login**: https://Evident-info.onrender.com/auth/login
   - Use ADMIN_EMAIL and ADMIN_PASSWORD
   - Should login successfully

## 📊 Expected Render Environment Tab

After setup, your Environment tab should show:

```
✓ SECRET_KEY               ••••••••••••••••••••••••
✓ DATABASE_URL             postgres://user:pass@host/db
✓ ADMIN_EMAIL              admin@Evident.info
✓ ADMIN_PASSWORD           ••••••••••••••••
✓ STRIPE_PRICING_TABLE_ID  prctbl_1Su2jmHGgvJKMFG1wn1Lum5i
✓ STRIPE_PUBLISHABLE_KEY   pk_live_51RjUMa...
✓ STRIPE_SECRET_KEY        ••••••••••••••••••••••••
✓ STRIPE_WEBHOOK_SECRET    ••••••••••••••••••••••••
○ OPENAI_API_KEY           (optional)
○ MAIL_SERVER              (optional)
```

## ⚠️ Security Notes

1. **Never commit** `.env` files to Git
2. **Rotate credentials** every 90 days
3. **Use different keys** for development vs production
4. **Test mode first**: Use `sk_test_` and `pk_test_` keys before going live
5. **Monitor Stripe dashboard** for unauthorized charges

## 🐛 Troubleshooting

### Error: "SECRET_KEY environment variable is required"

**Fix:** Add SECRET_KEY in Render Environment tab

### Error: "Stripe publishable key not found"

**Fix:** Add STRIPE_PUBLISHABLE_KEY and STRIPE_PRICING_TABLE_ID

### Error: "Database connection failed"

**Fix:** Verify DATABASE_URL is set (should be auto-populated)

### Pricing table doesn't load

**Fix:** Check browser console for errors. Verify STRIPE*PUBLISHABLE_KEY starts
with `pk_live*`(not`pk*test*`)

## 📞 Support

- **Render Docs**: https://render.com/docs/environment-variables
- **Stripe Docs**: https://stripe.com/docs/keys
- **Evident Issues**: https://github.com/DTB396/Evident.info/issues

--

**Status:**

- ✅ Code updated to use environment variables
- ⏳ **PENDING**: Render.com environment variables must be set manually
- ⏳ **PENDING**: Test deployment after setting variables
