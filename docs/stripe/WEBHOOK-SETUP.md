# Stripe Webhook Setup Guide for Evident

> Complete guide for connecting Stripe webhooks to handle subscriptions,
> payments, and member management.

--

## 🚀 QUICK START (5 Minutes)

### Step 1: Open Stripe Webhooks

Go to your Stripe Dashboard:

- **Test Mode:** https://dashboard.stripe.com/test/webhooks
- **Live Mode:** https://dashboard.stripe.com/webhooks

### Step 2: Click "+ Add Endpoint"

Look for the **"+ Add endpoint"** button (top right corner).

### Step 3: Configure Your Endpoint

```
┌─────────────────────────────────────────────────────────────┐
│  Add a webhook endpoint                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Endpoint URL:                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ https://Evident.info/api/stripe/webhook                 ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  Description (optional):                                     │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Evident Membership & Subscription Webhooks              ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  Listen to:  ○ Events on your account                        │
│              ○ Events on Connected accounts                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Select Events (See Detailed List Below)

Click **"+ Select events"** button, then follow the event selection guide.

### Step 5: Get Your Signing Secret

After creating the endpoint:

1. Click on your new endpoint in the list
2. Find **"Signing secret"** section
3. Click **"Reveal"** to see the secret
4. Copy it (starts with `whsec_`)

### Step 6: Add Secret to Your Server

```bash
# Add to .env file or hosting environment
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

--

## 📋 EVENT SELECTION GUIDE

In Stripe's new UI, events are organized by category. Here's exactly what to
select:

### CATEGORY: Checkout

Click **"Checkout"** in the left sidebar, then check:

| ✓   | Event Name                   | What It Does for Evident                                             |
| --- | ---------------------------- | -------------------------------------------------------------------- |
| ☑️  | `checkout.session.completed` | **CRITICAL:** Activates new subscription, upgrades user to paid tier |
| ☐   | `checkout.session.expired`   | Optional: Track abandoned checkouts                                  |

**How to find:** Checkout → `session` → check `completed`

--

### CATEGORY: Customer

Click **"Customer"** in the left sidebar, then check:

| ✓   | Event Name         | What It Does for Evident             |
| --- | ------------------ | ------------------------------------ |
| ☑️  | `customer.created` | Logs new Stripe customer creation    |
| ☑️  | `customer.updated` | Syncs email/name changes from Stripe |
| ☐   | `customer.deleted` | Optional: Handle account deletion    |

**How to find:** Customer → check `created` and `updated`

--

### CATEGORY: Customer > Subscription

This is the **MOST IMPORTANT** category. Click **"Customer"** → expand
**"subscription"**:

| ✓   | Event Name                             | What It Does for Evident                                     |
| --- | -------------------------------------- | ------------------------------------------------------------ |
| ☑️  | `customer.subscription.created`        | Records new subscription in database                         |
| ☑️  | `customer.subscription.updated`        | **CRITICAL:** Handles plan changes, renewals, status changes |
| ☑️  | `customer.subscription.deleted`        | **CRITICAL:** Downgrades user to FREE when subscription ends |
| ☑️  | `customer.subscription.paused`         | Marks subscription as paused (if you enable this feature)    |
| ☑️  | `customer.subscription.resumed`        | Reactivates paused subscription                              |
| ☑️  | `customer.subscription.trial_will_end` | **IMPORTANT:** Sends reminder 3 days before trial ends       |

**How to find:** Customer → `subscription` → check all 6 events above

--

### CATEGORY: Invoice

Click **"Invoice"** in the left sidebar:

| ✓   | Event Name                        | What It Does for Evident                                         |
| --- | --------------------------------- | ---------------------------------------------------------------- |
| ☑️  | `invoice.paid`                    | **CRITICAL:** Confirms successful payment, extends subscription  |
| ☑️  | `invoice.payment_failed`          | **CRITICAL:** Marks account as past_due, triggers dunning emails |
| ☑️  | `invoice.payment_action_required` | Notifies when 3D Secure authentication needed                    |
| ☑️  | `invoice.upcoming`                | Alerts before next billing (good for usage-based charges)        |
| ☐   | `invoice.created`                 | Optional: Track invoice creation                                 |
| ☐   | `invoice.finalized`               | Optional: Track finalized invoices                               |

**How to find:** Invoice → check `paid`, `payment_failed`,
`payment_action_required`, `upcoming`

--

### CATEGORY: Payment Intent (Optional)

For one-time payments or add-ons. Click **"Payment Intent"**:

| ✓   | Event Name                      | What It Does for Evident                     |
| --- | ------------------------------- | -------------------------------------------- |
| ☐   | `payment_intent.succeeded`      | Confirms one-time payment (add-ons, credits) |
| ☐   | `payment_intent.payment_failed` | Logs failed one-time payments                |

**How to find:** Payment Intent → check `succeeded` and `payment_failed` if
needed

--

## 📊 VISUAL: Events to Select in New Stripe UI

```
Stripe Dashboard → Developers → Webhooks → + Add endpoint

Select events to listen to:
┌────────────────────────────────────────────────────────────────┐
│ 🔍 Search events...                                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ▼ Checkout                                                    │
│     ☑️ checkout.session.completed         ← MUST HAVE          │
│                                                                │
│  ▼ Customer                                                    │
│     ☑️ customer.created                                        │
│     ☑️ customer.updated                                        │
│     ▼ subscription                                             │
│        ☑️ customer.subscription.created                        │
│        ☑️ customer.subscription.updated   ← MUST HAVE          │
│        ☑️ customer.subscription.deleted   ← MUST HAVE          │
│        ☑️ customer.subscription.paused                         │
│        ☑️ customer.subscription.resumed                        │
│        ☑️ customer.subscription.trial_will_end                 │
│                                                                │
│  ▼ Invoice                                                     │
│     ☑️ invoice.paid                       ← MUST HAVE          │
│     ☑️ invoice.payment_failed             ← MUST HAVE          │
│     ☑️ invoice.payment_action_required                         │
│     ☑️ invoice.upcoming                                        │
│                                                                │
│  ▼ Payment Intent (optional)                                   │
│     ☐ payment_intent.succeeded                                 │
│     ☐ payment_intent.payment_failed                            │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                              [ Add events ]  [ Cancel ]        │
└────────────────────────────────────────────────────────────────┘
```

--

## 🎯 EVENT DETAILS: What Each One Does

### 🟢 checkout.session.completed

**When:** User completes payment on checkout page  
**What happens:**

- User's tier upgrades (FREE → PROFESSIONAL/PREMIUM)
- Stripe subscription ID saved to user record
- Subscription start date recorded
- User redirected to dashboard with success message

```
User clicks "Subscribe" → Stripe Checkout → Payment success → This webhook fires
                                                                    ↓
                                                         User tier = PROFESSIONAL
```

--

### 🟢 customer.subscription.updated

**When:** Any change to subscription (renewal, plan change, status change)  
**What happens:**

- Updates subscription status (active, past_due, canceled)
- Updates billing period end date
- Handles plan upgrades/downgrades
- Updates trial status

```
Monthly renewal succeeds → This webhook fires → Extends billing period by 1 month
```

--

### 🟢 customer.subscription.deleted

**When:** Subscription is fully canceled/expired  
**What happens:**

- User tier downgrades to FREE
- Subscription end date recorded
- Access to paid features revoked

```
User cancels subscription → Billing period ends → This webhook fires
                                                        ↓
                                              User tier = FREE
```

--

### 🟢 invoice.paid

**When:** Any invoice is successfully paid  
**What happens:**

- Confirms subscription renewal
- Updates subscription status to "active"
- Logs payment amount for records

```
Card charged successfully → This webhook fires → subscription_status = "active"
```

--

### 🟢 invoice.payment_failed

**When:** Payment attempt fails (card declined, expired, etc.)  
**What happens:**

- Subscription status set to "past_due"
- Dunning process begins (Stripe retries)
- User should receive email to update payment method

```
Card declined → This webhook fires → subscription_status = "past_due"
                                            ↓
                              Stripe retries payment automatically
                              (usually 3 more attempts over 2 weeks)
```

--

### 🟡 customer.subscription.trial_will_end

**When:** 3 days before free trial ends  
**What happens:**

- Opportunity to send reminder email
- User can update payment method or cancel

```
Trial started Jan 1 (14-day trial) → Jan 11: This webhook fires → Send reminder email
                                                                         ↓
                                                              "Your trial ends in 3 days!"
```

--

### 🟡 invoice.payment_action_required

**When:** Payment needs extra verification (3D Secure, etc.)  
**What happens:**

- User needs to complete authentication
- Send email with link to complete payment

```
Bank requires verification → This webhook fires → Send "Complete your payment" email
```

--

### 🟡 invoice.upcoming

**When:** ~3 days before next invoice is created  
**What happens:**

- Good time to add usage-based charges
- Can send "upcoming bill" notification

```
Next billing in 3 days → This webhook fires → Add any metered usage charges
```

--

## 🔧 AFTER SETUP: Get Your Webhook Secret

1. **Go to your webhooks list:** https://dashboard.stripe.com/webhooks
2. **Click on your endpoint** (the one you just created)
3. **Find "Signing secret"** section on the right side
4. **Click "Reveal"** button
5. **Copy the secret** (looks like `whsec_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`)

### Add to Your Environment:

**Local Development (.env file):**

```bash
STRIPE_WEBHOOK_SECRET=whsec_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456
```

**Render.com:**

1. Go to Dashboard → Your Service → Environment
2. Click "Add Environment Variable"
3. Key: `STRIPE_WEBHOOK_SECRET`
4. Value: `whsec_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`
5. Click "Save Changes"

**Other Hosts (Heroku, Railway, etc.):**

```bash
# Via CLI
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_xxx
railway variables set STRIPE_WEBHOOK_SECRET=whsec_xxx
```

--

## 🧪 TESTING YOUR WEBHOOKS

### Method 1: Stripe CLI (Recommended)

```bash
# 1. Install Stripe CLI
# Windows (PowerShell):
scoop install stripe

# Mac:
brew install stripe/stripe-cli/stripe

# 2. Login to your Stripe account
stripe login

# 3. Forward webhooks to your local server
stripe listen -forward-to localhost:5000/api/stripe/webhook

# 4. In another terminal, trigger test events:
stripe trigger checkout.session.completed
stripe trigger invoice.paid
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.deleted
```

### Method 2: Stripe Dashboard Test

1. Go to your webhook endpoint in Dashboard
2. Click **"Send test webhook"**
3. Select an event type
4. Click **"Send test webhook"**
5. Check response (should be 200 OK)

--

## ✅ FINAL CHECKLIST

```
□ Created webhook endpoint with URL: https://Evident.info/api/stripe/webhook

□ Selected these events:
  □ checkout.session.completed
  □ customer.subscription.created
  □ customer.subscription.updated
  □ customer.subscription.deleted
  □ customer.subscription.trial_will_end
  □ invoice.paid
  □ invoice.payment_failed
  □ invoice.payment_action_required
  □ invoice.upcoming

□ Copied signing secret (whsec_...)

□ Added STRIPE_WEBHOOK_SECRET to:
  □ Local .env file (for development)
  □ Render/hosting environment (for production)

□ Tested with Stripe CLI or Dashboard test webhook

□ Verified in server logs: "📥 Stripe webhook received: [event_type]"
```

--

## 🔗 Useful Links

| Resource                 | URL                                             |
| ------------------------ | ----------------------------------------------- |
| Webhook Dashboard (Test) | https://dashboard.stripe.com/test/webhooks      |
| Webhook Dashboard (Live) | https://dashboard.stripe.com/webhooks           |
| All Event Types          | https://stripe.com/docs/api/events/types        |
| Stripe CLI Download      | https://stripe.com/docs/stripe-cli              |
| Webhook Best Practices   | https://stripe.com/docs/webhooks/best-practices |
| Testing Webhooks         | https://stripe.com/docs/webhooks/test           |

--

## 🆘 Troubleshooting

### "Webhook signature verification failed"

- Check `STRIPE_WEBHOOK_SECRET` is correct
- Make sure you're using the secret for the right endpoint (test vs live)
- Don't modify the raw request body before verification

### "Endpoint not receiving events"

- Verify URL is exactly `https://Evident.info/api/stripe/webhook`
- Check your server is running and accessible
- Look at "Recent events" in Stripe Dashboard for delivery attempts

### "Event received but nothing happens"

- Check server logs for errors
- Verify user has `stripe_customer_id` set
- Make sure database connection is working
