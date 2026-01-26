# BarberX Payment System - Test Guide

**Date:** January 26, 2026  
**Status:** ✅ Payment routes deployed and live  
**Mode:** TEST (using Stripe test keys)

---

## ✅ DEPLOYMENT STATUS

- ✅ Payment code merged to main
- ✅ Pushed to GitHub successfully
- ✅ Render deployment complete
- ✅ Pricing page live: https://barberx.info/payments/pricing
- ✅ Webhook configured in Stripe
- ✅ Webhook secret added to Render
- ⚠️ Database migration needed (run via Render Shell)

---

## 🧪 TEST CHECKOUT FLOW

### Step 1: Visit Pricing Page
```
URL: https://barberx.info/payments/pricing
Expected: See pricing table with Professional ($199) and Premium ($499) plans
```

### Step 2: Select a Plan
- Click "Subscribe" on either Professional or Premium plan
- Expected: Redirect to Stripe Checkout page

### Step 3: Enter Test Payment Details

**Test Card Number:** `4242 4242 4242 4242`

**Other Test Cards Available:**
- `4000 0025 0000 3155` - Requires authentication (3D Secure)
- `4000 0000 0000 9995` - Declined card
- `4000 0082 6000 0000` - Declined (insufficient funds)

**Card Details:**
- Expiry: Any future date (e.g., `12/26`)
- CVC: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)
- Email: Any email address

### Step 4: Complete Checkout
- Click "Subscribe" or "Pay"
- Expected: Payment processing → Success page

### Step 5: Verify Success
- ✅ Redirected to `/payments/success` page
- ✅ Success message displayed
- ✅ Analytics event fired (check browser console)

---

## 🔍 VERIFY WEBHOOK DELIVERY

### In Stripe Dashboard

1. **Go to Webhooks:**
   ```
   https://dashboard.stripe.com/test/webhooks/we_1StxRKHGgvJKMFG1nEgqpfm4
   ```

2. **Check Recent Events:**
   - Should see `checkout.session.completed` event
   - Status: `Succeeded` (green checkmark)
   - Response code: `200`

3. **View Event Details:**
   - Click on the event
   - Check "Request body" for customer/subscription data
   - Check "Response" for webhook acknowledgment

### Expected Webhook Events

After successful checkout, you should see:

1. **`checkout.session.completed`**
   - Triggered when payment succeeds
   - Creates/upgrades user subscription
   - Updates user tier

2. **`customer.subscription.created`** (if new subscription)
   - Contains subscription details
   - Billing cycle info

3. **`invoice.payment_succeeded`**
   - First payment processed
   - Invoice created

---

## 📊 VERIFY IN DATABASE

### Check User Tier Upgrade

After test checkout, verify the user's tier was upgraded:

```bash
# Via Render Shell
python -c "
from app import app, db
from models_auth import User

with app.app_context():
    # Replace with the email you used in checkout
    user = User.query.filter_by(email='test@example.com').first()
    if user:
        print(f'User: {user.email}')
        print(f'Tier: {user.tier.name}')
        print(f'Subscription active: {user.is_subscription_active}')
    else:
        print('User not found')
"
```

Expected output:
```
User: test@example.com
Tier: PROFESSIONAL  (or PREMIUM)
Subscription active: True
```

---

## 🐛 TROUBLESHOOTING

### Pricing Page Returns 404
**Cause:** Payment routes not deployed  
**Solution:** Check Render deployment logs, ensure latest commit deployed

### Webhook Not Firing
**Cause:** Webhook URL incorrect or secret missing  
**Solution:** 
1. Verify webhook endpoint: `https://barberx.info/payments/webhook`
2. Check Render env var: `STRIPE_WEBHOOK_SECRET` is set
3. Check webhook events are selected in Stripe dashboard

### Checkout Redirects But No Success Page
**Cause:** Session handling or database error  
**Solution:**
1. Check Render logs for errors
2. Verify database migration ran
3. Check user exists and tier updated

### Test Card Declined
**Cause:** Wrong test card number  
**Solution:** Use exact card number: `4242 4242 4242 4242`

---

## 🔄 SWITCHING TO LIVE MODE

### When Ready for Real Payments

1. **Create Live Webhook in Stripe:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Click "Add endpoint"
   - URL: `https://barberx.info/payments/webhook`
   - Events: Same 5 events as test mode
   - Copy new webhook secret (starts with `whsec_`)

2. **Update Render Environment Variables:**
   - Go to Render dashboard → Environment tab
   - Update `STRIPE_WEBHOOK_SECRET` with LIVE secret
   - Verify `STRIPE_SECRET_KEY` is live key (starts with `sk_live_`)
   - Verify `STRIPE_PUBLISHABLE_KEY` is live key (starts with `pk_live_`)
   - Ensure `STRIPE_PRICE_PRO` and `STRIPE_PRICE_PREMIUM` use live price IDs

3. **Test with Real Card:**
   - Use your own card
   - Process test payment
   - Immediately issue refund in Stripe dashboard
   - Verify full flow works

4. **Go Live:**
   - Remove test mode warning from pricing page (if any)
   - Update marketing materials
   - Monitor Stripe dashboard for real payments

---

## 📋 WEBHOOK EVENTS CONFIGURED

Our webhook listens for these 5 events:

1. **`checkout.session.completed`**
   - When: Customer completes payment
   - Action: Create/upgrade subscription, update user tier

2. **`customer.subscription.updated`**
   - When: Subscription plan changes, billing updates
   - Action: Update user tier and limits

3. **`customer.subscription.deleted`**
   - When: Subscription cancelled or expires
   - Action: Downgrade user to FREE tier

4. **`invoice.payment_succeeded`**
   - When: Recurring payment succeeds
   - Action: Extend subscription, log payment

5. **`invoice.payment_failed`**
   - When: Recurring payment fails
   - Action: Email user, attempt retry, suspend account if needed

---

## ✅ SUCCESS CRITERIA

Payment system is working correctly when:

- ✅ Pricing page loads and displays plans
- ✅ Clicking "Subscribe" redirects to Stripe Checkout
- ✅ Test card payment succeeds
- ✅ User redirected to success page
- ✅ Webhook fires and shows "Succeeded" in Stripe
- ✅ User tier updated in database
- ✅ Analytics event tracked
- ✅ No errors in Render logs

---

## 🎯 CURRENT TEST STATUS

**Last Tested:** January 26, 2026

| Test | Status | Notes |
|------|--------|-------|
| Pricing page loads | ✅ | Returns 200 OK |
| Stripe elements present | ⏳ | Needs browser test |
| Test card checkout | ⏳ | Ready to test |
| Webhook delivery | ⏳ | Ready to verify |
| User tier upgrade | ⏳ | Needs database check |
| Success page redirect | ⏳ | Needs checkout test |
| Analytics tracking | ⏳ | Needs browser test |

**Next:** Complete manual checkout test with browser

---

## 📞 SUPPORT RESOURCES

- **Stripe Test Cards:** https://stripe.com/docs/testing
- **Stripe Dashboard:** https://dashboard.stripe.com/test/payments
- **Render Logs:** https://dashboard.render.com/web/srv-cug5crbtq21c73dcuvcg/logs
- **Webhook Testing:** https://dashboard.stripe.com/test/webhooks

---

*Ready to accept your first paying customer!* 🎉
