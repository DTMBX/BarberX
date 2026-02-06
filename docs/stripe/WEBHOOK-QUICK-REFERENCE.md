# Stripe Webhook Quick Reference Card

## 🎯 Endpoint URL

```
https://Evident.info/api/stripe/webhook
```

## ✅ Events to Enable (Copy This List)

### MUST HAVE (Your app won't work without these)

```
checkout.session.completed
customer.subscription.updated
customer.subscription.deleted
invoice.paid
invoice.payment_failed
```

### RECOMMENDED (Better user experience)

```
customer.subscription.created
customer.subscription.trial_will_end
invoice.payment_action_required
invoice.upcoming
```

### OPTIONAL (Nice to have)

```
customer.subscription.paused
customer.subscription.resumed
customer.created
customer.updated
payment_intent.succeeded
```

--

## 🔑 Environment Variable

```
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

--

## 📍 Where to Find Events in Stripe UI

```
Stripe Dashboard
    └── Developers (top menu)
            └── Webhooks
                    └── + Add endpoint
                            └── + Select events
                                    ├── Checkout
                                    │       └── session.completed ✓
                                    │
                                    ├── Customer
                                    │       ├── created ✓
                                    │       ├── updated ✓
                                    │       └── subscription
                                    │               ├── created ✓
                                    │               ├── updated ✓
                                    │               ├── deleted ✓
                                    │               ├── paused ✓
                                    │               ├── resumed ✓
                                    │               └── trial_will_end ✓
                                    │
                                    └── Invoice
                                            ├── paid ✓
                                            ├── payment_failed ✓
                                            ├── payment_action_required ✓
                                            └── upcoming ✓
```

--

## 🧪 Test Commands (Stripe CLI)

```bash
# Install
scoop install stripe          # Windows
brew install stripe           # Mac

# Login & Listen
stripe login
stripe listen -forward-to localhost:5000/api/stripe/webhook

# Trigger Events
stripe trigger checkout.session.completed
stripe trigger invoice.paid
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.deleted
```

--

## 📊 What Each Event Does

| Event                         | Trigger         | Result            |
| ----------------------------- | --------------- | ----------------- |
| `checkout.session.completed`  | User pays       | Tier → PAID       |
| `invoice.paid`                | Monthly renewal | Status → active   |
| `invoice.payment_failed`      | Card declined   | Status → past_due |
| `subscription.deleted`        | Sub expires     | Tier → FREE       |
| `subscription.trial_will_end` | 3 days left     | Send email        |

--

## 🔗 Quick Links

- **Add Webhook:** https://dashboard.stripe.com/test/webhooks/create
- **View Events:** https://dashboard.stripe.com/test/webhooks
- **Event Logs:** https://dashboard.stripe.com/test/events
