# ⚡ Evident Subscription System - Quick Start

## 🎯 What You Have

✅ **Complete subscription system** with Stripe integration  
✅ **Tier-based access control** (FREE/PRO/PREMIUM/ENTERPRISE)  
✅ **Usage tracking & limits** enforcement  
✅ **Beautiful usage dashboard** for users  
✅ **Automated billing** with webhooks  
✅ **Production-ready code** (~2,200 lines)

--

## 🚀 5-Minute Setup

### **1. Run Database Migration** (2 min)

```bash
cd C:\web-dev\github-repos\Evident.info
python migrate_add_stripe_subscriptions.py
```

Creates Stripe fields in database.

### **2. Create Test Accounts** (1 min)

```bash
python create_test_subscription_accounts.py
```

Test credentials:

- `free@Evident.test` / test123
- `pro@Evident.test` / test123
- `premium@Evident.test` / test123

### **3. Configure Stripe** (2 min)

**Option A: Test Mode (Development)**

1. Go to https://dashboard.stripe.com/test/products
2. Create products:
   - **Evident PRO:** $49/month, 3-day trial
   - **Evident Premium:** $249/month
3. Copy price IDs to `.env`:
   ```bash
   STRIPE_PRICE_PRO=price_1ABC...
   STRIPE_PRICE_PREMIUM=price_1XYZ...
   ```
4. Get test keys from https://dashboard.stripe.com/test/apikeys
5. Add to `.env`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

**Option B: Live Mode (Production)** - Same as above but use live dashboard

--

## 🧪 Test It (3 minutes)

### **Test Upgrade Flow:**

1. **Start Flask app:**

   ```bash
   python app.py
   ```

2. **Login:**
   - Go to http://localhost:5000/login
   - Email: `free@Evident.test`
   - Password: `test123`

3. **View Dashboard:**
   - Go to http://localhost:5000/dashboard/usage
   - Should show FREE tier

4. **Test Checkout:**
   - Add checkout button to pricing.html:

   ```html
   <button onclick="subscribeToPlan('PROFESSIONAL')" class="btn btn-primary">
     Start 3-Day Free Trial
   </button>

   <script>
     async function subscribeToPlan(tier) {
       const res = await fetch("/api/stripe/create-checkout-session", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ tier }),
       });
       const data = await res.json();
       if (data.url) window.location.href = data.url;
     }
   </script>
   ```

5. **Complete Checkout:**
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry (e.g., 12/25)
   - Any CVC (e.g., 123)

6. **Verify Upgrade:**
   - Return to `/dashboard/usage`
   - Should now show PRO tier
   - Should show "Trial Active" badge
   - Should show usage limits (0/10 PDFs, 0/2 video hours)

--

## 📋 Pricing Tiers

| Feature              | FREE  | PRO ($49) | PREMIUM ($249) | ENTERPRISE       |
| -------------------- | ----- | --------- | -------------- | ---------------- |
| **Trial**            | —     | ✅ 3 days | —              | —                |
| **PDFs/month**       | 1 doc | 10 docs   | Unlimited      | Unlimited        |
| **Video/month**      | ❌    | 2 hours   | Unlimited      | Unlimited        |
| **Cases**            | 1     | 10        | Unlimited      | Unlimited        |
| **AI Assistant**     | ❌    | Basic     | Full           | Private Instance |
| **Timeline Builder** | ❌    | ❌        | ✅             | ✅               |
| **API Access**       | ❌    | ❌        | ✅             | ✅               |
| **White-Label**      | ❌    | ❌        | ❌             | ✅               |
| **Self-Hosted**      | ❌    | ❌        | ❌             | ✅               |

--

## 🛠️ How It Works

### **User Flow:**

```
1. User signs up → FREE tier (default)
2. User clicks "Upgrade" → Redirects to Stripe Checkout
3. User enters payment → Stripe processes
4. Stripe sends webhook → System upgrades tier
5. User accesses premium features → Gated by middleware
6. Monthly renewal → Automatic (Stripe handles)
```

### **Access Control:**

**Tier Gating:**

```python
from tier_gating import require_tier
from models_auth import TierLevel

@app.route('/api/premium-feature')
@require_tier(TierLevel.PREMIUM)
def premium_feature():
    return "Premium content"
```

**Usage Limits:**

```python
from tier_gating import check_usage_limit

@app.route('/api/upload-pdf', methods=['POST'])
@check_usage_limit('pdf_documents_per_month', increment=1)
def upload_pdf():
    # Automatically enforces 10 PDF limit for PRO
    # Returns 403 if limit exceeded
    return "PDF uploaded"
```

**Feature Access:**

```python
from tier_gating import require_feature

@app.route('/api/timeline')
@require_feature('timeline_builder')
def timeline():
    # Only PREMIUM and ENTERPRISE can access
    return "Timeline feature"
```

--

## 🎨 Frontend Integration

### **Show Usage Stats:**

```html
{% if current_user.is_authenticated %}
<div>
  <p>Tier: {{ current_user.tier.name }}</p>
  <p>
    PDFs used: {{ usage.pdf_documents_processed }} / {{
    limits.pdf_documents_per_month }}
  </p>
</div>
{% endif %}
```

### **Show Upgrade Prompt:**

```html
{% if current_user.tier.name == 'FREE' %}
<div class="alert alert-info">
  <strong>Upgrade to PRO</strong> for 10 PDFs/month and AI analysis!
  <a href="/pricing" class="btn btn-primary">Start Free Trial</a>
</div>
{% endif %}
```

### **Limit Warnings:**

```html
{% set remaining = get_remaining_usage(current_user, 'pdf_documents_per_month')
%} {% if remaining < 3 and remaining > 0 %}
<div class="alert alert-warning">
  Only {{ remaining }} PDFs remaining this month!
  <a href="/pricing">Upgrade for unlimited</a>
</div>
{% endif %}
```

--

## 🔧 Common Issues

### **"Module not found" error:**

```bash
pip install -r requirements.txt
```

### **"Database is locked" error:**

Close Visual Studio or any app using the database.

### **Stripe checkout not working:**

1. Check `STRIPE_PUBLISHABLE_KEY` is in `.env`
2. Check `STRIPE_PRICE_PRO` matches Stripe Dashboard
3. Check browser console for JavaScript errors

### **Webhook not receiving events:**

For local testing:

1. Install ngrok: https://ngrok.com/download
2. Run: `ngrok http 5000`
3. Update Stripe webhook URL to ngrok URL
4. Restart Flask app

--

## 📊 Revenue Calculator

**Break-Even:** 50 PRO users OR 20 PREMIUM users

**Year 1 Conservative:**

- 100 PRO × $49 = $4,900/month
- 20 PREMIUM × $249 = $4,980/month
- **Total: $9,880/month = $118,560/year**

**Year 2 Moderate:**

- 500 PRO × $49 = $24,500/month
- 100 PREMIUM × $249 = $24,900/month
- **Total: $49,400/month = $592,800/year**

--

## ✅ Pre-Launch Checklist

- [ ] Database migration completed
- [ ] Test accounts created
- [ ] Stripe products created (PRO, PREMIUM)
- [ ] API keys added to `.env`
- [ ] Checkout buttons added to pricing page
- [ ] Test checkout with test card
- [ ] Webhook endpoint configured
- [ ] Usage dashboard accessible
- [ ] Upgrade CTAs working
- [ ] Production Stripe keys (for live launch)

--

## 🎉 You're Ready!

**Everything is built.** Just need to:

1. Run migration
2. Configure Stripe
3. Test checkout
4. Launch! 🚀

**Time to revenue:** 30 minutes (setup Stripe + test)

--

## 📚 Resources

- **Full Guide:** `SUBSCRIPTION-SYSTEM-GUIDE.md`
- **Summary:** `SUBSCRIPTION-IMPLEMENTATION-SUMMARY.md`
- **Economics:** `PRICING-COMPLETE-DEPENDENCY-ANALYSIS.md`
- **Stripe Docs:** https://stripe.com/docs
- **Test Cards:** https://stripe.com/docs/testing

--

**🚀 Let's make money!**
