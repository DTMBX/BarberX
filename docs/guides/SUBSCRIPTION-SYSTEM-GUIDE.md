# Evident Subscription System - Complete Implementation Guide

## 🎯 Overview

This guide covers the complete implementation of the **tiered subscription system** with Stripe integration, usage tracking, and access gating for Evident.

--

## 📦 What's Included

### **New Files Created:**

1. **`stripe_subscription_service.py`** - Stripe payment integration
   - Checkout session creation
   - Customer portal management
   - Webhook event handling
   - Subscription lifecycle management

2. **`tier_gating.py`** - Access control middleware
   - `@require_tier()` - Require minimum tier for routes
   - `@check_usage_limit()` - Enforce monthly limits
   - `@require_feature()` - Feature-based access control
   - `TierGate` - Helper class for templates

3. **`migrate_add_stripe_subscriptions.py`** - Database migration
   - Adds Stripe fields to User model
   - Adds usage tracking fields
   - Creates necessary indexes

4. **`templates/usage_dashboard.html`** - User dashboard
   - Current plan display
   - Usage statistics with progress bars
   - Feature access indicators
   - Upgrade CTAs
   - "Manage Billing" button (Stripe Portal)

5. **`integrate_subscription_system.py`** - Automation script
   - Adds imports to app.py
   - Registers blueprints
   - Adds dashboard route
   - Updates .env configuration

6. **`create_test_subscription_accounts.py`** - Test accounts
   - Creates accounts for each tier
   - Enables local testing

### **Files Modified:**

1. **`models_auth.py`** - Updated tier pricing and limits
   - PRO: $49/month, 10 PDFs, 2 hrs video, 10 cases
   - PREMIUM: $249/month, unlimited
   - ENTERPRISE: Custom pricing, unlimited, self-hosted
   - Added Stripe subscription fields
   - Added usage tracking fields

--

## 🏗️ Architecture

### **Tier Structure**

| Tier           | Price   | Trial  | PDF Limit | Video Limit | Cases     | Features                 |
| -------------- | ------- | ------ | --------- | ----------- | --------- | ------------------------ |
| **FREE**       | $0      | —      | 1 doc     | ❌          | 1         | Basic                    |
| **PRO**        | $49/mo  | 3 days | 10 docs   | 2 hrs/mo    | 10        | AI Assistant (Basic)     |
| **PREMIUM**    | $249/mo | ❌     | Unlimited | Unlimited   | Unlimited | Full AI, API, Timeline   |
| **ENTERPRISE** | Custom  | ❌     | Unlimited | Unlimited   | Unlimited | Self-Hosted, White-Label |

### **Usage Tracking**

Each month, the system tracks:

- PDF documents processed
- BWC video hours used
- Videos processed
- Cases created
- API calls made
- Storage used

Limits are enforced via middleware decorators on routes.

### **Stripe Integration Flow**

1. **Signup:** User creates FREE account
2. **Upgrade:** User clicks "Upgrade" → Stripe Checkout
3. **Payment:** Stripe processes payment
4. **Webhook:** Stripe sends `checkout.session.completed`
5. **Activation:** System upgrades user tier
6. **Usage:** User can now access PRO/PREMIUM features
7. **Renewal:** Stripe auto-charges monthly
8. **Cancel:** User can cancel via Stripe Portal

--

## 🚀 Installation & Setup

### **Step 1: Database Migration**

Run the migration to add Stripe fields:

```bash
python migrate_add_stripe_subscriptions.py
```

**This adds:**

- `stripe_customer_id` - Stripe customer ID
- `stripe_subscription_id` - Active subscription ID
- `stripe_subscription_status` - Status (active, canceled, etc.)
- `stripe_current_period_end` - Billing cycle end date
- `trial_end` - Trial expiration date
- `is_on_trial` - Trial status flag
- `bwc_video_hours_used` - Video hours tracking
- `pdf_documents_processed` - PDF document count
- `cases_created` - Case count

### **Step 2: Integrate Code**

Run the integration script:

```bash
python integrate_subscription_system.py
```

**This will:**

- ✅ Add imports to app.py
- ✅ Register Stripe blueprint
- ✅ Add usage dashboard route
- ✅ Update .env with Stripe placeholders
- ✅ Create test account script

### **Step 3: Configure Stripe**

#### **3.1 Create Products in Stripe Dashboard**

1. Go to https://dashboard.stripe.com/products
2. Click **"+ Add product"**

**PRO Product:**

- Name: `Evident Professional`
- Price: `$49.00 USD`
- Billing period: `Monthly`
- Trial period: **3 days**
- Copy the **Price ID** (starts with `price_...`)

**PREMIUM Product:**

- Name: `Evident Premium`
- Price: `$249.00 USD`
- Billing period: `Monthly`
- Trial period: **None**
- Copy the **Price ID**

#### **3.2 Get API Keys**

1. Go to https://dashboard.stripe.com/apikeys
2. Copy **Publishable key** (starts with `pk_test_...` or `pk_live_...`)
3. Copy **Secret key** (starts with `sk_test_...` or `sk_live_...`)

#### **3.3 Update .env**

Add Stripe configuration to `.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_PRICE_PRO=price_YOUR_PRO_PRICE_ID_HERE
STRIPE_PRICE_PREMIUM=price_YOUR_PREMIUM_PRICE_ID_HERE
```

#### **3.4 Set Up Webhook**

1. Go to https://dashboard.stripe.com/webhooks
2. Click **"+ Add endpoint"**
3. Endpoint URL: `https://Evident.info/api/stripe/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Click **"Add endpoint"**
6. Copy **Signing secret** (starts with `whsec_...`)
7. Add to `.env`:

```bash
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

### **Step 4: Create Test Accounts**

```bash
python create_test_subscription_accounts.py
```

**Test Accounts Created:**

- `free@Evident.test` / test123 (FREE tier)
- `pro@Evident.test` / test123 (PRO tier)
- `premium@Evident.test` / test123 (PREMIUM tier)
- `enterprise@Evident.test` / test123 (ENTERPRISE tier)
- `admin@Evident.test` / admin123 (ADMIN)

### **Step 5: Restart Flask App**

```bash
python app.py
```

--

## 🧪 Testing

### **Test Subscription Flow**

1. **Login as FREE user:**

   ```
   Email: free@Evident.test
   Password: test123
   ```

2. **Go to pricing page:**

   ```
   http://localhost:5000/pricing
   ```

3. **Click "Upgrade to PRO" button**
   - Should redirect to Stripe Checkout
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any CVC

4. **Complete checkout**
   - Should redirect back to `/dashboard?checkout=success`
   - User tier should be upgraded to PRO
   - 3-day trial should be active

5. **Check usage dashboard:**

   ```
   http://localhost:5000/dashboard/usage
   ```

   - Should show PRO tier
   - Should show "Trial Active" badge
   - Should show 0/10 PDFs used
   - Should show 0/2 video hours used

### **Test Stripe Portal**

1. Click **"Manage Billing"** button on usage dashboard
2. Should redirect to Stripe Customer Portal
3. Can update payment method
4. Can cancel subscription
5. Can view invoices

### **Test Usage Limits**

1. **Upload 10 PDFs** (as PRO user)
2. **Try to upload 11th PDF**
   - Should get error: "Monthly PDF limit exceeded"
   - Should show upgrade prompt

3. **Upload 2 hours of video**
4. **Try to upload more**
   - Should get error: "Monthly video hours limit exceeded"

### **Test Tier Gating**

**Premium Feature Test:**

```python
from tier_gating import require_tier
from models_auth import TierLevel

@app.route('/api/premium-feature')
@require_tier(TierLevel.PREMIUM)
def premium_feature():
    return jsonify({"message": "Premium content!"})
```

1. Login as FREE user → Access `/api/premium-feature`
   - Should get 403 error
   - Should show upgrade prompt

2. Login as PREMIUM user → Access `/api/premium-feature`
   - Should work ✅

--

## 🎨 Frontend Integration

### **Update Pricing Page**

Add Stripe checkout buttons to `pricing.html`:

```html
<!-- PRO Tier ->
<button onclick="subscribeToPlan('PROFESSIONAL')" class="btn btn-primary">
  Start 3-Day Free Trial
</button>

<!-- PREMIUM Tier ->
<button onclick="subscribeToPlan('PREMIUM')" class="btn btn-success">
  Upgrade to Premium
</button>

<script>
  async function subscribeToPlan(tier) {
    try {
      const response = await fetch("/api/stripe/create-checkout-session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ tier: tier }),
      });

      const data = await response.json();

      if (data.url) {
        window.location.href = data.url;
      } else {
        alert("Error: " + data.error);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to start checkout");
    }
  }
</script>
```

### **Add Usage Indicators**

Show usage warnings in dashboard:

```html
{% if get_remaining_usage(current_user, 'pdf_documents_per_month') < 3 %}
<div class="alert alert-warning">
  <i class="fas fa-exclamation-triangle"></i>
  You have {{ get_remaining_usage(current_user, 'pdf_documents_per_month') }}
  PDFs remaining this month!
  <a href="/pricing">Upgrade for unlimited</a>
</div>
{% endif %}
```

### **Add Upgrade CTAs**

When users hit limits, show upgrade prompts:

```html
{% if not can_access_feature(current_user, 'timeline_builder') %}
<div class="feature-locked">
  <i class="fas fa-lock"></i>
  <h4>Timeline Builder</h4>
  <p>Upgrade to Premium to unlock this feature</p>
  <a href="/pricing" class="btn btn-success">Upgrade Now</a>
</div>
{% endif %}
```

--

## 🔒 Security Best Practices

### **Environment Variables**

**NEVER commit these to Git:**

- `STRIPE_SECRET_KEY` - Server-side only
- `STRIPE_WEBHOOK_SECRET` - For webhook validation

**Safe to expose:**

- `STRIPE_PUBLISHABLE_KEY` - Used in frontend JavaScript

### **Webhook Verification**

The webhook endpoint verifies signatures:

```python
event = stripe.Webhook.construct_event(
    payload, sig_header, STRIPE_WEBHOOK_SECRET
)
```

This prevents unauthorized requests from spoofing Stripe events.

### **Idempotency**

Webhooks may be sent multiple times. The system handles this:

```python
user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
if not user:
    return  # Ignore duplicate events
```

--

## 📊 Admin Tools

### **View User Subscriptions**

Admin can see all subscriptions:

```python
@app.route('/admin/subscriptions')
@require_tier(TierLevel.ADMIN)
def admin_subscriptions():
    users = User.query.filter(User.tier != TierLevel.FREE).all()

    return render_template('admin/subscriptions.html', users=users)
```

### **Manually Change Tier**

Admin can upgrade/downgrade users:

```python
@app.route('/admin/change-tier/<int:user_id>', methods=['POST'])
@require_tier(TierLevel.ADMIN)
def admin_change_tier(user_id):
    user = User.query.get_or_404(user_id)
    new_tier = request.form.get('tier')

    user.tier = TierLevel[new_tier]
    db.session.commit()

    return redirect('/admin/subscriptions')
```

### **Usage Analytics**

Track overall usage:

```python
from sqlalchemy import func

total_pdfs = db.session.query(
    func.sum(UsageTracking.pdf_documents_processed)
).scalar()

total_videos = db.session.query(
    func.sum(UsageTracking.bwc_videos_processed)
).scalar()
```

--

## 🐛 Troubleshooting

### **Webhook Not Receiving Events**

1. Check webhook URL is publicly accessible
2. Use ngrok for local testing: `ngrok http 5000`
3. Update Stripe webhook URL to ngrok URL
4. Check webhook signature secret matches `.env`

### **Checkout Not Working**

1. Check `STRIPE_PUBLISHABLE_KEY` in frontend
2. Check `STRIPE_SECRET_KEY` in backend
3. Check `STRIPE_PRICE_PRO` and `STRIPE_PRICE_PREMIUM` match Stripe Dashboard
4. Check browser console for JavaScript errors

### **Usage Limits Not Enforcing**

1. Check middleware is applied: `@check_usage_limit(...)`
2. Check user tier: `print(current_user.tier)`
3. Check usage tracking: `usage = UsageTracking.get_or_create_current(user.id)`
4. Check limits: `print(current_user.get_tier_limits())`

### **Stripe Portal Not Opening**

1. Check user has `stripe_customer_id`
2. Check `STRIPE_SECRET_KEY` is set
3. Check return URL is valid

--

## ✅ Deployment Checklist

- [ ] Database migration completed
- [ ] Stripe products created (PRO, PREMIUM)
- [ ] Stripe API keys added to `.env`
- [ ] Webhook endpoint configured
- [ ] Test accounts created
- [ ] Subscription flow tested
- [ ] Usage limits tested
- [ ] Stripe Portal tested
- [ ] Frontend pricing page updated
- [ ] Usage dashboard accessible
- [ ] Upgrade CTAs added
- [ ] Production Stripe keys obtained (when ready to launch)

--

## 🚀 Next Phase: Windows Desktop App

**Planned Features:**

- Electron-based desktop application
- Offline-first architecture with sync
- License key validation (like Enterprise tier)
- Local processing option (Whisper, Tesseract)
- Automatic updates
- System tray integration

**Timeline:** 2-3 weeks after subscription system is live

--

## 📞 Support

**Issues?**

- Check logs: `./logs/Evident.log`
- Test accounts: Use `*@Evident.test` credentials
- Stripe logs: https://dashboard.stripe.com/logs
- Webhook events: https://dashboard.stripe.com/webhooks

**Success!** 🎉

Your subscription system is ready to generate revenue!
