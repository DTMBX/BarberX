# ⚡ INSTANT WEBHOOK SETUP - COPY & PASTE

## 🎯 YOUR EXACT WEBHOOK URL

Based on your Render deployment:

```
https://Evident-backend.onrender.com/payments/webhook
```

**OR if using custom domain:**

```
https://Evident.info/payments/webhook
```

--

## 📋 3-STEP SETUP (5 MINUTES TOTAL)

### STEP 1: Add Webhook in Stripe (2 min)

**Click this link:** https://dashboard.stripe.com/test/webhooks/create

**Copy-paste these values:**

**Endpoint URL:**

```
https://Evident-backend.onrender.com/payments/webhook
```

**Description:**

```
Evident Payments
```

**Events to send - paste this into search and check each:**

```
checkout.session.completed
customer.subscription.updated
customer.subscription.deleted
invoice.payment_succeeded
invoice.payment_failed
```

**Click:** "Add endpoint"

--

### STEP 2: Get Signing Secret (1 min)

After clicking "Add endpoint":

1. You'll see **"Signing secret"** section
2. Click **"Reveal"**
3. **Copy the entire secret** (starts with `whsec_`)

--

### STEP 3: Add to Render (2 min)

**Click this link:** https://dashboard.render.com/

Then:

1. Click your web service
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Copy-paste:

```
Key: STRIPE_WEBHOOK_SECRET
Value: [paste your whsec_... secret here]
```

5. Click **"Save Changes"**
6. Wait 5 minutes

--

## ✅ DONE! THAT'S IT!

After 5 minutes, test with:

```
https://Evident-backend.onrender.com/payments/pricing
```

--

## 🧪 INSTANT TEST (1 MINUTE)

1. **Login:** https://Evident-backend.onrender.com/login
2. **Go to:** https://Evident-backend.onrender.com/payments/pricing
3. **Click:** "Start Pro Trial"
4. **Use card:** 4242 4242 4242 4242
5. **Done!** Should redirect to success page

--

## 🆘 IF STUCK

Just tell me:

- "Not working" - I'll troubleshoot
- "What's my URL?" - I'll find it
- "Where's my secret?" - I'll help locate it

**You're 5 minutes from accepting payments!** 🚀
