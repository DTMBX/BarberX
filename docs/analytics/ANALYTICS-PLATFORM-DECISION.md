# Analytics Platform Comparison & Recommendation

**Date:** January 27, 2026  
**Decision:** Choose your analytics platform  
**Timeline:** 15 minutes to set up

--

## 🏆 RECOMMENDATION: Start with Amplitude

### Why Amplitude?

**For Evident specifically:**

1. **More Generous Free Tier**
   - Amplitude: 10M events/month FREE
   - Mixpanel: 100K events/month FREE
   - At 500 users: Amplitude free tier covers you for 12+ months
   - At 500 users: Mixpanel free tier you'll hit in ~3 months

2. **Better for Early Stage**
   - More visual interface (easier for solo founder)
   - Better behavioral analysis
   - Stronger retention analytics
   - Built-in experimentation

3. **Easier Onboarding**
   - Simpler UI for non-data-scientists
   - Better dashboards out of the box
   - Faster time to insights

4. **Enterprise-Ready When You Scale**
   - Used by: Dropbox, PayPal, NBCUniversal
   - Easy to upgrade as you grow
   - Strong customer success team

--

## 📊 Side-by-Side Comparison

| Feature              | Amplitude ✅  | Mixpanel       |
| -------------------- | ------------- | -------------- |
| **Free Tier Events** | 10M/month     | 100K/month     |
| **Free Tier Users**  | Unlimited     | 1,000 MTU      |
| **Ease of Use**      | ⭐⭐⭐⭐⭐    | ⭐⭐⭐⭐       |
| **User Interface**   | More visual   | More technical |
| **Funnel Analysis**  | Excellent     | Excellent      |
| **Cohort Analysis**  | Excellent     | Very good      |
| **Retention Charts** | Best-in-class | Very good      |
| **A/B Testing**      | Built-in      | Built-in       |
| **Revenue Tracking** | Built-in      | Built-in       |
| **API Quality**      | Excellent     | Excellent      |
| **Data Export**      | CSV, JSON     | CSV, JSON      |
| **Integrations**     | 100+          | 100+           |
| **Learning Curve**   | Easy          | Moderate       |
| **Startup-Friendly** | ✅ Very       | ✅ Yes         |
| **Enterprise Scale** | ✅ Yes        | ✅ Yes         |

--

## 💰 Pricing Comparison (When You Scale)

### Year 1 Projections (Based on Roadmap)

**Month 3:** 100 users

- Amplitude: FREE (well under limit)
- Mixpanel: FREE (just under limit)

**Month 6:** 500 users, ~250K events/month

- Amplitude: FREE
- Mixpanel: Paid ($89-199/month)

**Month 12:** 5,000 users, ~2.5M events/month

- Amplitude: FREE
- Mixpanel: Paid ($299-899/month)

**Month 18:** 25,000 users, ~12M events/month

- Amplitude: Paid (~$1,000/month)
- Mixpanel: Paid (~$2,000-3,000/month)

**First Year Savings with Amplitude:** $3,000-5,000

--

## 🚀 Quick Setup: Amplitude (15 minutes)

### Step 1: Create Account (5 min)

1. Go to: https://amplitude.com/signup
2. Enter:
   - Email: your@email.com
   - Company: Evident Legal Technologies
   - Role: Founder
   - Industry: Legal Tech
   - Team Size: 1-10
3. Click "Start Free Trial" (it's actually free forever for your usage)

### Step 2: Create Project (2 min)

1. Project Name: "Evident Production"
2. Copy your API Key (starts with a long string)
3. **Save it** - you'll need it next

### Step 3: Add to Render Environment (3 min)

1. Go to Render dashboard
2. Navigate to your web service
3. Environment → Add Environment Variable
4. **Name:** `AMPLITUDE_API_KEY`
5. **Value:** (paste your API key)
6. Click "Save"
7. Redeploy (it will restart automatically)

### Step 4: Verify (5 min)

Run this Python snippet to test:

```python
# Test analytics locally (optional)
import os
os.environ['AMPLITUDE_API_KEY'] = 'your_api_key_here'

from utils.analytics import track_event, identify_user

# Test user identification
identify_user('test_user_123', {
    'email': 'test@example.com',
    'name': 'Test User',
    'tier': 'free'
})

# Test event tracking
track_event('test_user_123', 'test_event', {
    'test_property': 'Hello from Evident!'
})

print("✅ Analytics test complete! Check Amplitude dashboard in 1-2 minutes.")
```

Then check Amplitude dashboard:

- Events → Live Stream
- You should see your test event appear!

--

## 📊 Essential Dashboards to Create (Week 2)

### Dashboard 1: User Acquisition

**Metrics:**

- New user signups (daily/weekly)
- Signup source (organic, referral, paid)
- Activation rate (% who complete onboarding)
- Time to first value (signup → first analysis)

### Dashboard 2: Engagement

**Metrics:**

- Daily Active Users (DAU)
- Weekly Active Users (WAU)
- Monthly Active Users (MAU)
- Feature adoption rates:
  - Evidence uploads
  - AI analysis
  - Document generation
  - Command palette usage

### Dashboard 3: Revenue & Conversion

**Metrics:**

- Free → Pro conversion rate
- Pro → Premium upgrade rate
- MRR (Monthly Recurring Revenue)
- Churn rate
- Customer Lifetime Value (LTV)
- Payback period

### Dashboard 4: Product Health

**Metrics:**

- Error rates by feature
- Average session duration
- Pages per session
- Feature usage trends
- User retention cohorts

--

## 🎯 Critical Events to Track (Already Implemented)

Your `utils/analytics.py` already tracks these - just add the API key:

### User Lifecycle ✅

```python
track_event(user_id, 'user_registered', {...})
track_event(user_id, 'user_logged_in', {...})
track_event(user_id, 'onboarding_started', {...})
track_event(user_id, 'onboarding_completed', {...})
```

### Feature Usage ✅

```python
track_event(user_id, 'evidence_uploaded', {...})
track_event(user_id, 'analysis_completed', {...})
track_event(user_id, 'document_generated', {...})
track_event(user_id, 'command_palette_used', {...})
```

### Revenue Events ✅

```python
track_subscription_change(user_id, old_tier, new_tier, amount)
track_revenue(user_id, amount, {...})
```

--

## 🔔 Alerts to Set Up (Week 3)

### Critical Alerts

1. **Churn Risk:** User inactive for 7 days
2. **Trial Ending:** 2 days before trial expires
3. **Payment Failed:** Immediate notification
4. **High Error Rate:** >5% errors in 1 hour
5. **Drop in Signups:** <50% of 7-day average

### Growth Alerts

1. **New Milestone:** Every 100 users
2. **Revenue Milestone:** Each $1K MRR increase
3. **Viral Coefficient:** >0.3 (users referring users)
4. **Feature Adoption:** >10% using new feature

--

## 📈 Success Metrics (From Roadmap)

### Month 6 Goals

- [ ] 500 total users tracked
- [ ] 80%+ activation rate
- [ ] <5% monthly churn
- [ ] 20% free → paid conversion

### Month 12 Goals

- [ ] 5,000 total users
- [ ] 10+ cohorts analyzed
- [ ] Conversion funnel optimized (>25% conversion)
- [ ] User segmentation by behavior

--

## 🎓 Learning Resources

### Amplitude Academy (Free)

- "Getting Started with Amplitude" (1 hour)
- "Building Your First Dashboard" (30 min)
- "Advanced Cohort Analysis" (1 hour)

### Essential Reading

- Amplitude Blog: "SaaS Metrics That Matter"
- Book: "Lean Analytics" by Croll & Yoskovitz
- Guide: "The Ultimate Guide to SaaS Metrics"

--

## ✅ Action Items

### Today (15 minutes)

- [ ] Create Amplitude account
- [ ] Get API key
- [ ] Add to Render environment
- [ ] Test with sample event
- [ ] Verify in Amplitude dashboard

### This Week (2 hours)

- [ ] Create 4 essential dashboards
- [ ] Set up critical alerts
- [ ] Train yourself on Amplitude interface
- [ ] Document key metrics to track
- [ ] Share access with advisors/investors

### Next Month

- [ ] Weekly metric review routine
- [ ] A/B test onboarding flow
- [ ] Analyze user cohorts
- [ ] Optimize conversion funnel
- [ ] Build product roadmap from data

--

## 🔄 Alternative: Use Both (Advanced)

**Why use both?**

- Amplitude: Main analytics (free, powerful)
- Mixpanel: Backup/comparison (free tier adequate)

Your `utils/analytics.py` supports BOTH simultaneously:

```bash
# In Render environment
AMPLITUDE_API_KEY=your_amplitude_key
MIXPANEL_TOKEN=your_mixpanel_token
```

Events will be sent to both platforms automatically.

**When to do this:**

- When you have more than 1 team member
- When preparing for fundraising (show redundancy)
- When you want to compare analytics platforms
- Never hurts to have backup data!

--

## 💡 Pro Tips

### 1. Track Everything Early

Don't wait until you "need" it. Historical data is invaluable.

### 2. Use Consistent Naming

- Events: `snake_case` (e.g., `evidence_uploaded`)
- Properties: `snake_case` (e.g., `file_type`)
- Values: consistent units (e.g., always USD, always seconds)

### 3. Include Context

Every event should have:

- `timestamp` (automatic)
- `user_id` (required)
- `subscription_tier` (for segmentation)
- `platform` (web, mobile, api)

### 4. Monitor Funnels Weekly

- What % of users complete onboarding?
- Where do users drop off?
- Which features drive retention?
- What leads to upgrades?

### 5. Act on Insights

Analytics are useless without action:

- Low activation? Improve onboarding
- High churn? Add retention features
- Low conversion? Optimize pricing
- Drop-off point? Fix that UX

--

## 🎯 Final Recommendation

**Start with Amplitude:**

1. More generous free tier
2. Easier to use
3. Better for legal/compliance tracking
4. Scales with you
5. Free for 12+ months

**Setup time:** 15 minutes  
**Cost:** $0 (for your usage)  
**Value:** Priceless insights 📊

--

## 📞 Next Steps

1. **Now:** Create Amplitude account (5 min)
2. **Today:** Add API key to Render (3 min)
3. **This week:** Build 4 dashboards (2 hours)
4. **Next week:** Set up alerts (1 hour)
5. **Ongoing:** Weekly metric reviews (30 min/week)

**Ready to track your growth!** 🚀

Need help with:

- Creating specific dashboards?
- Setting up alerts?
- Interpreting analytics data?

Let me know! 📊
