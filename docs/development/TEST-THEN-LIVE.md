# 🎯 RECOMMENDED PATH - TEST THEN LIVE

## ✅ BEST APPROACH: 20 Minutes to Confident Launch

--

## PHASE 1: TEST MODE (10 min)

### Step 1: Create Test Webhook

```
URL: https://Evident.info/payments/webhook
Mode: TEST mode
Events: 5 events (checkout, subscription, invoice)
Get signing secret → Add to Render as STRIPE_WEBHOOK_SECRET
```

### Step 2: Test Checkout

```
Visit: /payments/pricing
Click: "Start Pro Trial"
Card: 4242 4242 4242 4242
Complete → Verify success page
Check: Stripe dashboard shows $199 test payment
Check: Webhook fired successfully
```

### Step 3: Verify Everything

```
✓ Payment processed
✓ Success page shows
✓ Webhook delivered
✓ User upgraded in database
✓ Analytics tracked revenue
```

**Result:** You know it works! ✅

--

## PHASE 2: GO LIVE (10 min)

### Step 4: Switch to Live Keys

```
Update Render environment:
- STRIPE_SECRET_KEY = sk_live_... (your live key)
- STRIPE_PUBLISHABLE_KEY = pk_live_... (your live key)
- Keep same STRIPE_PRICE_PRO and STRIPE_PRICE_PREMIUM
```

### Step 5: Create Live Webhook

```
URL: https://Evident.info/payments/webhook
Mode: LIVE mode
Events: Same 5 events
Get NEW signing secret → Update STRIPE_WEBHOOK_SECRET in Render
```

### Step 6: Test with Real Money

```
Visit: /payments/pricing
Pay yourself $199 (real charge!)
Verify it works
Go to Stripe → Refund yourself
```

### Step 7: LAUNCH!

```
You're now accepting real payments! 🎉
```

--

## ⏰ TIMELINE:

```
00:00 - Create test webhook
00:05 - Test with fake card
00:10 - Verified working! ✓

00:11 - Switch to live keys
00:13 - Create live webhook
00:15 - Test with real $199
00:18 - Refund yourself
00:20 - LIVE! 🚀
```

--

## 💰 TOTAL COST:

**Test mode:** $0 (fake money)
**Live test:** $199 (you refund yourself)
**Stripe refund fee:** ~$0.30
**Net cost:** $0.30 to test safely

**Worth it for confidence!**

--

## 🎯 READY TO START?

**Say "Yes, let's test first"** and I'll guide you through:

1. Test webhook setup (5 min)
2. Test payment (2 min)
3. Switch to live (5 min)
4. Live payment (2 min)
5. Launch! (1 min)

**Total: 20 min to confident launch** 🚀
