# 🧪 TEST CHECKOUT - COMPLETE GUIDE

## WHAT YOU'RE TESTING

End-to-end payment flow:

```
Login → Pricing Page → Checkout → Payment → Success → Verification
```

--

## STEP 1: Make Sure Everything Is Ready

### Check Render Environment (2 min):

Go to: https://dashboard.render.com/
Click your service → Environment tab

**Verify all 6 Stripe variables are set:**

```
✓ STRIPE_SECRET_KEY
✓ STRIPE_PUBLISHABLE_KEY
✓ STRIPE_PRICE_PRO
✓ STRIPE_PRICE_PREMIUM
✓ STRIPE_WEBHOOK_SECRET
✓ AMPLITUDE_API_KEY
```

**If any are missing:** Add them now, save, wait for redeploy (~5 min)

### Check App Is Running:

Visit: `https://YOUR-URL/payments/pricing`

**Should see:**

- Beautiful pricing page
- 3 tiers: Free, Pro ($199), Premium ($499)
- "Start Trial" buttons

**If you see errors:**

- Check Render logs
- Make sure deployment succeeded
- Verify all environment variables set

--

## STEP 2: Register Test Account (2 min)

### Create a new test user:

1. Go to: `https://YOUR-URL/register`
2. Fill out:
   ```
   Email: test@example.com
   Password: TestPassword123!
   Name: Test User
   ```
3. Click Register
4. Should redirect to welcome/onboarding screen

**Note your user ID** - you'll need it to verify later

--

## STEP 3: Navigate to Pricing (1 min)

### From Dashboard:

1. Click "Upgrade" or visit `/payments/pricing`
2. Should see the pricing page

### What to check:

- ✅ All 3 plans showing
- ✅ Prices correct ($199, $499)
- ✅ "Start Trial" buttons present
- ✅ Page loads without errors

**Open Browser Console (F12):**

- Should see no red errors
- Might see Amplitude tracking events (good!)

--

## STEP 4: Start Checkout (1 min)

### Click "Start Pro Trial" button

**What should happen:**

1. Button click triggers JavaScript
2. POST request to `/payments/create-checkout-session`
3. Redirect to Stripe checkout page

**Stripe Checkout Page looks like:**

- Stripe branding at top
- "Evident Pro" product name
- "$199.00 / month" pricing
- Payment form (card, email, name)
- Secure padlock icon in URL

**If redirect fails:**

- Check browser console for errors
- Verify you're logged in
- Check Render logs for backend errors

--

## STEP 5: Complete Payment (2 min)

### Use Stripe Test Card:

**Fill out the form:**

```
Email: test@example.com (any email)

Card Information:
Card number: 4242 4242 4242 4242
MM / YY: 12 / 27 (any future date)
CVC: 123 (any 3 digits)

Cardholder name: Test User

Country: United States
ZIP: 12345 (any 5 digits)
```

### Click "Subscribe" button

**What happens:**

1. Stripe processes payment (~2 seconds)
2. Webhook fires to your backend
3. Redirect to success page

--

## STEP 6: Success Page (30 sec)

### You should see:

```
✓ (big checkmark)
Payment Successful!
Your subscription is now active.
[Go to Dashboard] button
```

**Check:**

- ✅ Success message displayed
- ✅ Amplitude tracking fires
- ✅ "Go to Dashboard" button works

--

## STEP 7: Verify Everything Worked (5 min)

### A. Check Stripe Dashboard

**Payments:**

1. Go to: https://dashboard.stripe.com/test/payments
2. Should see your $199 payment
3. Status: **Succeeded**
4. Customer: test@example.com

**Subscriptions:**

1. Go to: https://dashboard.stripe.com/test/subscriptions
2. Should see new subscription
3. Status: **Active**
4. Plan: Evident Pro

**Webhooks:**

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click your webhook endpoint
3. Should see recent events:
   - `checkout.session.completed` → ✓ Succeeded
   - Response: 200 OK

### B. Check Amplitude Analytics

**Go to:** https://amplitude.com/

**Login and check:**

**Events (Analytics → Events):**

- `pricing_page_viewed`
- `subscription_success`

**Revenue (Analytics → Revenue):**

- New revenue event: $199.00
- User: test@example.com
- Event properties: plan=pro, type=subscription

**May take 1-2 minutes to appear in dashboard**

### C. Check Your Database (if accessible)

**User record should have:**

```sql
subscription_tier: "pro" (was "free")
subscription_status: "active"
stripe_customer_id: cus_... (Stripe customer ID)
```

**How to check:**

- If using PostgreSQL: Connect and query users table
- Or: Create admin endpoint to view user data
- Or: Check via Render shell

--

## STEP 8: Test Customer Portal (2 min)

### Access the portal:

1. While logged in, go to: `https://YOUR-URL/payments/portal`
2. Should redirect to Stripe Customer Portal

**What you should see:**

- Your subscription: Evident Pro
- Next payment: [Date] for $199.00
- Payment method: •••• 4242
- Options to:
  - Update payment method
  - Cancel subscription
  - View invoices

### Test cancellation (optional):

1. Click "Cancel subscription"
2. Confirm cancellation
3. Should see:
   - Subscription canceled
   - Access until end of billing period
4. Webhook fires: `customer.subscription.deleted`
5. Your app updates user status to "canceled"

--

## 🎉 SUCCESS CHECKLIST

**You successfully tested when:**

- ✅ Pricing page loads
- ✅ Checkout session created
- ✅ Redirected to Stripe
- ✅ Payment processed with test card
- ✅ Redirected to success page
- ✅ Payment shows in Stripe dashboard
- ✅ Webhook delivered successfully (200 OK)
- ✅ Subscription created and active
- ✅ Amplitude tracked revenue
- ✅ Customer portal accessible
- ✅ User tier updated in database

**If all ✅, YOU'RE READY FOR PRODUCTION!** 🚀

--

## 🚨 COMMON ISSUES & FIXES

### Issue: "Please log in" error when clicking checkout

**Cause:** Not logged in or session expired

**Fix:**

- Logout completely
- Register new account
- Try again

### Issue: Checkout button does nothing

**Cause:** JavaScript error

**Fix:**

- Open browser console (F12)
- Look for red errors
- Check if `fetch` request is made
- Verify STRIPE_PRICE_PRO is set in Render

### Issue: Payment succeeds but user still "free"

**Cause:** Webhook not processing

**Fix:**

- Check webhook was delivered (Stripe dashboard)
- Check webhook returns 200 OK
- Verify STRIPE_WEBHOOK_SECRET is correct
- Check Render logs for webhook errors

### Issue: Redirect to Stripe fails

**Cause:** Backend error creating checkout session

**Fix:**

- Check Render logs
- Verify STRIPE_SECRET_KEY is set
- Verify price IDs are correct
- Check user is authenticated

### Issue: Amplitude not tracking

**Cause:** API key missing or incorrect

**Fix:**

- Verify AMPLITUDE_API_KEY in Render
- Check browser console for tracking errors
- Use Amplitude debugger: https://analytics.amplitude.com/debugger

--

## 🧪 ADDITIONAL TEST SCENARIOS

### Test Different Cards:

**Successful payments:**

```
4242 4242 4242 4242 - Always succeeds
5555 5555 5555 4444 - Mastercard
3782 822463 10005 - Amex
```

**Failed payments:**

```
4000 0000 0000 0002 - Generic decline
4000 0000 0000 9995 - Insufficient funds
4000 0000 0000 0069 - Card expired
```

### Test Premium Plan:

1. Create new account
2. Click "Start Trial" on Premium ($499)
3. Complete checkout
4. Verify user gets "premium" tier

### Test Subscription Updates:

1. Subscribe to Pro
2. Go to customer portal
3. Click "Update subscription"
4. Choose Premium
5. Verify upgrade works
6. Webhook: `customer.subscription.updated`

--

## 📊 WHAT TO MONITOR

### Stripe Dashboard:

**Daily:**

- New subscriptions
- Payment success rate
- Failed payments
- Churn rate

**Weekly:**

- MRR (Monthly Recurring Revenue)
- Customer count
- Average revenue per user

### Amplitude Dashboard:

**Key Metrics:**

- Pricing page views
- Checkout starts
- Conversion rate (pricing → paid)
- Revenue per customer
- Time to convert

--

## ✅ READY FOR PRODUCTION

### Before switching to live mode:

**1. Test everything in test mode:**

- ✅ Multiple successful payments
- ✅ Failed payment handling
- ✅ Webhook delivery
- ✅ Customer portal
- ✅ Subscription updates
- ✅ Cancellations

**2. Create live products:**

- Create Pro and Premium in live mode
- Get live price IDs

**3. Get live API keys:**

- Publishable: pk*live*...
- Secret: sk*live*...

**4. Update environment:**

- Replace test keys with live keys
- Update price IDs
- Create live webhook
- Test with real $1 payment

**5. Launch!**

- Announce on social media
- Email beta users
- Product Hunt launch
- Start marketing

--

## 🎯 NEXT STEPS

### If test succeeded:

**Immediate:**

- [ ] Merge PR to main
- [ ] Document any issues found
- [ ] Plan production launch date

**This Week:**

- [ ] Beta user testing
- [ ] Create demo video
- [ ] Prepare marketing materials

**Next Week:**

- [ ] Switch to live mode
- [ ] Launch to public
- [ ] Monitor first real payments

--

## 💰 EXPECTED RESULTS

**First Month (Conservative):**

```
10 Pro users × $199 = $1,990 MRR
1 Premium × $499 = $499 MRR
────────────────────────────────
Total: $2,489 MRR
```

**Month 3 (Moderate):**

```
25 Pro × $199 = $4,975 MRR
3 Premium × $499 = $1,497 MRR
──────────────────────────────
Total: $6,472 MRR
```

**Month 6 (Aggressive):**

```
50 Pro × $199 = $9,950 MRR
10 Premium × $499 = $4,990 MRR
───────────────────────────────
Total: $14,940 MRR (~$180K ARR)
```

--

## 🎉 YOU DID IT!

**You now have:**

- ✅ Working payment system
- ✅ Verified checkout flow
- ✅ Revenue tracking
- ✅ Customer portal
- ✅ Production-ready infrastructure

**TIME TO MAKE MONEY!** 💰🚀

--

_Test completed - Ready for launch!_
