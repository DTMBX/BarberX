# ANALYTICS INTEGRATION GUIDE - BarberX

**Status:** Ready for Setup  
**Platforms:** Mixpanel (Recommended) OR Amplitude  
**Estimated Setup Time:** 30 minutes  

---

## 🎯 WHY ANALYTICS?

Track user behavior to optimize conversion, reduce churn, and improve product-market fit.

**Key Metrics to Monitor:**
- User activation rate (complete onboarding)
- Feature adoption (uploads, analysis, document generation)
- Time to value (registration → first analysis)
- Conversion funnel (Free → Pro → Premium)
- Churn signals (inactive users, failed payments)

---

## 🏆 RECOMMENDED: Mixpanel

**Why Mixpanel?**
- ✅ Best for SaaS products
- ✅ Advanced cohort analysis
- ✅ Funnel visualization
- ✅ A/B testing built-in
- ✅ Retention analysis
- ✅ Free tier: 100K events/month (enough for beta)

### Setup Steps (10 minutes)

1. **Create Account**
   - Go to: https://mixpanel.com/register
   - Use your business email
   - Select "Product Analytics"
   - Choose "SaaS" industry

2. **Get Project Token**
   - Dashboard → Settings → Project Settings
   - Copy your Project Token (looks like: `a1b2c3d4e5f6...`)

3. **Add to Environment Variables**
   ```bash
   # On Render.com
   MIXPANEL_TOKEN=your_project_token_here
   ```

4. **Install SDK**
   ```bash
   pip install mixpanel
   ```
   (Already in requirements.txt)

---

## 📊 ALTERNATIVE: Amplitude

**Why Amplitude?**
- ✅ More visual interface
- ✅ Better for non-technical stakeholders
- ✅ Strong behavioral cohorts
- ✅ Free tier: 10M events/month

### Setup Steps (10 minutes)

1. **Create Account**
   - Go to: https://amplitude.com/signup
   - Use your business email
   - Select "Product Analytics"

2. **Get API Key**
   - Settings → Projects → API Keys
   - Copy your API Key

3. **Add to Environment Variables**
   ```bash
   AMPLITUDE_API_KEY=your_api_key_here
   ```

4. **Install SDK**
   ```bash
   pip install amplitude-analytics
   ```

---

## 🔧 INTEGRATION (Already Prepared!)

I've created a unified analytics service that works with both platforms.

### File: `utils/analytics.py` (Created Below)

**Features:**
- ✅ Works with Mixpanel OR Amplitude (or both!)
- ✅ Automatic environment detection
- ✅ Graceful fallback if keys missing
- ✅ User identification
- ✅ Event tracking with properties
- ✅ User profile updates
- ✅ Revenue tracking

### Key Events Tracked

1. **User Lifecycle**
   - `user_registered`
   - `user_logged_in`
   - `onboarding_started`
   - `onboarding_completed`
   - `subscription_created`
   - `subscription_upgraded`
   - `subscription_cancelled`

2. **Feature Usage**
   - `evidence_uploaded`
   - `analysis_requested`
   - `analysis_completed`
   - `document_generated`
   - `chat_message_sent`
   - `command_palette_used`

3. **Business Events**
   - `trial_started`
   - `trial_ending` (2 days before)
   - `payment_successful`
   - `payment_failed`
   - `churn_risk` (no activity 7 days)

---

## 📝 USAGE EXAMPLES

### Track User Registration
```python
from utils.analytics import track_event, identify_user

# Identify user
identify_user(user.id, {
    'email': user.email,
    'name': user.full_name,
    'tier': user.subscription_tier,
    'created_at': user.created_at.isoformat()
})

# Track registration
track_event(user.id, 'user_registered', {
    'tier': 'free',
    'source': request.args.get('utm_source', 'direct'),
    'referrer': request.referrer
})
```

### Track Evidence Upload
```python
track_event(current_user.id, 'evidence_uploaded', {
    'file_type': file.content_type,
    'file_size': file_size_mb,
    'case_id': case_id,
    'tier': current_user.subscription_tier
})
```

### Track Document Generation
```python
track_event(current_user.id, 'document_generated', {
    'document_type': 'motion',
    'word_count': word_count,
    'generation_time': elapsed_seconds,
    'tier': current_user.subscription_tier
})
```

### Track Revenue
```python
track_revenue(user.id, {
    'amount': 199.00,
    'plan': 'pro_monthly',
    'currency': 'USD'
})
```

---

## 📊 CRITICAL FUNNELS TO MONITOR

### 1. Activation Funnel
```
Registration → Welcome Screen → First Upload → First Analysis → First Document
```

**Target Conversion:** 50% registration → first document

### 2. Conversion Funnel
```
Free Tier → View Pricing → Trial Started → Payment Method → Paid Customer
```

**Target Conversion:** 25% free → paid

### 3. Retention Funnel
```
Day 1 Active → Day 7 Active → Day 14 Active → Day 30 Active
```

**Target Retention:** 40% D30 retention

---

## 🎯 KEY METRICS DASHBOARD

Create these charts in Mixpanel/Amplitude:

1. **Daily Active Users (DAU)**
   - Event: Any activity
   - Chart: Line graph, last 30 days

2. **Onboarding Completion Rate**
   - Events: `onboarding_started` → `onboarding_completed`
   - Chart: Funnel
   - Target: >60%

3. **Time to First Value**
   - Events: `user_registered` → `document_generated`
   - Chart: Distribution
   - Target: <1 hour

4. **Feature Adoption**
   - Events: `evidence_uploaded`, `analysis_requested`, `document_generated`
   - Chart: Stacked bar
   - Segment by tier

5. **Revenue Per User**
   - Event: `payment_successful`
   - Property: `amount`
   - Chart: Line graph
   - Target: $199 ARPU

6. **Churn Risk**
   - Cohort: Users inactive >7 days
   - Action: Trigger re-engagement email

---

## 🚀 IMPLEMENTATION CHECKLIST

### Week 1 (This Week)
- [ ] Choose platform: Mixpanel (✅ Recommended) or Amplitude
- [ ] Create account and get API token
- [ ] Add token to Render environment variables
- [ ] Install SDK (`pip install mixpanel`)
- [ ] Copy `utils/analytics.py` to project
- [ ] Add tracking to registration (5 min)
- [ ] Add tracking to onboarding (5 min)
- [ ] Test events in Mixpanel dashboard (10 min)

### Week 2
- [ ] Add tracking to all critical events
- [ ] Create 6 key dashboards
- [ ] Set up weekly email reports
- [ ] Configure alerts (trial ending, churn risk)

### Week 3
- [ ] Add cohort analysis
- [ ] Create A/B test for pricing page
- [ ] Set up funnel drop-off alerts
- [ ] Add custom user properties

---

## 💰 COST BREAKDOWN

### Mixpanel
- **Free Tier:** 100K events/month
- **Growth Tier:** $25/month for 1M events
- **Enterprise:** Custom pricing

### Amplitude
- **Free Tier:** 10M events/month (!)
- **Growth Tier:** $49/month
- **Enterprise:** Custom pricing

**Recommendation for BarberX:**
- Start with **Amplitude Free Tier** (10M events is huge)
- Switch to Mixpanel Growth if you need advanced features
- Cost: $0/month for first 6 months

---

## 🎨 EVENT NAMING CONVENTION

Follow this pattern for consistency:

**Format:** `object_action`

**Examples:**
- ✅ `user_registered`
- ✅ `evidence_uploaded`
- ✅ `document_generated`
- ❌ `registration` (too vague)
- ❌ `upload_evidence` (action_object is backwards)

**Properties Format:** `snake_case`

**Examples:**
- ✅ `file_type`, `user_tier`, `generation_time`
- ❌ `fileType`, `UserTier`, `generationTime`

---

## ✅ TESTING

Before going live, test events:

```python
# In Python console
from utils.analytics import track_event

# Test event
track_event('test_user_123', 'test_event', {
    'test_property': 'test_value',
    'timestamp': datetime.now().isoformat()
})

# Check Mixpanel dashboard → Live View
# Event should appear within 10 seconds
```

---

## 🔐 PRIVACY & COMPLIANCE

**GDPR Compliance:**
- ✅ Don't send PII (names, addresses) as event properties
- ✅ Use user_id only (not email)
- ✅ Add "Delete My Data" in user settings
- ✅ Document data retention policy (90 days)

**Data Minimization:**
- Only track what you'll actually use
- Avoid tracking sensitive case data
- Use hashed IDs for cases/documents

---

## 📚 RESOURCES

**Mixpanel:**
- Docs: https://docs.mixpanel.com/
- Python SDK: https://github.com/mixpanel/mixpanel-python
- Best Practices: https://mixpanel.com/blog/product-analytics-best-practices/

**Amplitude:**
- Docs: https://www.docs.developers.amplitude.com/
- Python SDK: https://github.com/amplitude/Amplitude-Python
- Behavioral Cohorts: https://help.amplitude.com/hc/en-us/articles/231881448

---

## 🎯 SUCCESS CRITERIA

Analytics setup is complete when:
- [ ] Platform account created
- [ ] SDK installed and configured
- [ ] 5+ events tracking successfully
- [ ] Dashboard showing live data
- [ ] Team can view metrics
- [ ] Alerts configured for critical events

---

## 📞 NEXT STEPS

1. **Choose your platform** (Mixpanel or Amplitude)
2. **Create account** (5 minutes)
3. **Get API token** (2 minutes)
4. **Tell me the token** and I'll integrate it
5. **Test events** (10 minutes)
6. **Launch!** 🚀

**Recommendation:** Start with **Amplitude** (10M free events is generous!)

---

*Created for BarberX Legal Technologies*  
*Data-driven product development starts now* 📊
