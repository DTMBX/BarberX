# 🤝 COURTLISTENER + Evident: ALIGNED MISSIONS FOR JUSTICE

**CourtListener's Mission:** Free access to legal materials  
**Evident's Mission:** Democratize legal research at 1/10th the cost  
**Shared Goal:** Close the justice gap

--

## 🎯 UNDERSTANDING COURTLISTENER & FREE LAW PROJECT

### **Who They Are:**

- **Organization:** Free Law Project (501(c)(3) non-profit)
- **Founded:** 2010 by Michael Lissner & Brian Carver
- **Mission:** "Making the law free and accessible to all"
- **Funding:** Donations, grants, API subscriptions
- **Philosophy:** Open data, transparency, public access

### **What They Believe:**

> "The law belongs to the people, not private companies. Everyone should have
> free access to primary legal materials without paywalls or subscriptions."

### **Why They Built CourtListener:**

1. **Break Westlaw/LexisNexis monopoly** ($2,000/month is unjust)
2. **Support public interest** (legal aid, pro se, researchers)
3. **Preserve legal history** (digitize old opinions)
4. **Enable innovation** (open API for developers like you)
5. **Increase transparency** (judge data, financial disclosures)

--

## 🎯 Evident'S ROLE IN THEIR MISSION

### **How We Align Perfectly:**

**1. We're NOT Competition - We're Amplification**

- CourtListener: Free research platform (direct users)
- Evident: Professional platform (solo practitioners, law firms, schools)
- **Relationship:** We extend their reach to commercial users who need more
  features

**2. We Share Values:**

- ✅ Open access to law
- ✅ Affordable legal tools
- ✅ Breaking corporate monopolies
- ✅ Supporting public interest
- ✅ Closing justice gap

**3. We Add Value They Don't:**

- AI legal assistant (ChatGPT integration)
- Evidence analysis (BWC, documents)
- Mobile apps (iOS/Android)
- Law school integrations
- Professional tier features
- Customer support

**4. We Contribute Back:**

- Promote CourtListener to our users
- Donate portion of revenue
- Share improvements/bug fixes
- Add citations to their database
- Expand their impact

--

## 🚀 PROPER USE OF COURTLISTENER API

### **✅ WHAT'S ALLOWED & ENCOURAGED:**

**1. Commercial Use - YES!**

- CourtListener explicitly allows commercial use
- You CAN charge for value-added services
- You SHOULD build on top of their data
- Just maintain attribution and contribute back

**2. Building Professional Tools - YES!**

- AI-powered search
- Citation analysis (Shepardizing)
- Judge intelligence
- Mobile apps
- Case management
- Document assembly

**3. Charging Users - YES!**

- You can charge $50/month for Evident
- This funds your business AND supports open access
- Reinvest profits in features that help mission

**4. Caching Data - YES!**

- Store cases in your database (reduces API calls)
- Build your own citation network
- Create derived works (summaries, analytics)
- Just keep data updated

--

### **❌ WHAT'S NOT ALLOWED:**

**1. Reselling Raw Data - NO**

- Don't sell direct access to CourtListener data
- Don't compete with their bulk data service
- Don't claim data as proprietary

**2. Hiding Sources - NO**

- Must attribute CourtListener
- Must make users aware of open alternatives
- Don't pretend you own primary sources

**3. Abuse - NO**

- No scraping beyond API
- Respect rate limits (100 req/min)
- Don't DDOS their servers
- Report bugs, don't exploit

**4. Monopolizing - NO**

- Don't create artificial scarcity
- Don't lock users into proprietary formats
- Allow data export
- Support open standards

--

## 🤝 HOW TO BE A GOOD API PARTNER

### **1. Attribution (Always)**

**In Your App:**

```
Legal data provided by CourtListener and Free Law Project
Learn more: https://www.courtlistener.com

Evident is built on open legal data. While our AI and analysis
tools are proprietary, the underlying case law is freely available
at CourtListener.com.
```

**In Your Footer:**

```html
<footer>
  <p>
    Case data: <a href="https://www.courtlistener.com">CourtListener</a> | A project of
    <a href="https://free.law">Free Law Project</a>
  </p>
</footer>
```

**On Pricing Page:**

```
Evident provides professional tools and AI analysis. The underlying
legal data is freely available at CourtListener.com. We charge for
our value-added features, not for access to the law.
```

--

### **2. Contribute Back (Regularly)**

**Financial Support:**

- [ ] Donate 2-5% of revenue to Free Law Project
- [ ] Sponsor specific features/improvements
- [ ] Support their annual fundraiser
- **Link:** https://donate.free.law/

**Technical Contributions:**

- [ ] Report bugs via GitHub: https://github.com/freelawproject/courtlistener
- [ ] Submit pull requests for improvements
- [ ] Share your citation algorithms
- [ ] Help with data quality

**Data Contributions:**

- [ ] Upload missing opinions you find
- [ ] Add citations to their database
- [ ] Correct errors in metadata
- [ ] Share PACER documents via RECAP

**Community Support:**

- [ ] Answer questions on their forum
- [ ] Write blog posts promoting CourtListener
- [ ] Speak at conferences about open legal data
- [ ] Train law students on their tools

--

### **3. Respect Their Infrastructure**

**Rate Limits:**

- Free tier: 100 requests/minute
- Cache aggressively to reduce calls
- Use bulk data for large imports
- Upgrade to paid tier if needed: https://www.courtlistener.com/help/api/rest/

**Efficient API Use:**

```python
# ✅ GOOD: Cache results
def get_case(citation):
    # Check local database first
    cached = db.get_case(citation)
    if cached:
        return cached

    # Only call API if not cached
    result = courtlistener_api.get(citation)
    db.store_case(result)
    return result

# ❌ BAD: Hit API every time
def get_case(citation):
    return courtlistener_api.get(citation)  # Wastes their resources
```

**Use Webhooks for Real-time:**

- Instead of polling, use webhooks:
  https://www.courtlistener.com/help/api/webhooks/
- Get notified when new cases filed
- Reduces server load

**Use Bulk Data for Large Imports:**

- For 1,000+ cases, use bulk files:
  https://www.courtlistener.com/help/api/bulk-data/
- Download entire database once
- Update incrementally via API

--

### **4. Be Transparent with Users**

**In Your Marketing:**

```
Evident uses open legal data from CourtListener, a non-profit
dedicated to making the law free and accessible.

We charge for our AI analysis, professional tools, and support—
not for access to the law itself.

Want free access? Visit CourtListener.com
Want professional tools? Use Evident ($50/month)
```

**On Your Website:**

- Link to CourtListener on every case page
- Explain what you add (AI, mobile, support)
- Show users they have free alternatives
- **Why?** Builds trust, supports mission, differentiates on value

--

## 💡 STRATEGIC PARTNERSHIP OPPORTUNITIES

### **1. Official Partnership with Free Law Project**

**Reach out to:**

- **Email:** info@free.law
- **Contact:** Michael Lissner (Founder)
- **Purpose:** Discuss formal partnership

**Proposal Template:**

```
Subject: Partnership Proposal - Evident Legal Research Platform

Dear Free Law Project team,

I'm building Evident, a legal research platform that uses CourtListener's
API to democratize professional legal tools.

Our mission aligns perfectly with yours:
• Break Westlaw/LexisNexis monopoly ($50/month vs $2,000/month)
• Support solo practitioners, legal aid, law students
• Open access to law (we attribute CourtListener on every page)
• Close the justice gap

How we use your API:
✓ 10M+ opinions for professional research
✓ Citation analysis (Shepardizing equivalent)
✓ Judge intelligence (education, ideology, finances)
✓ Mobile apps (iOS/Android)
✓ AI legal assistant (ChatGPT integration)

How we give back:
✓ Donate 5% of revenue to Free Law Project
✓ Promote CourtListener to 10,000+ users
✓ Contribute code improvements
✓ Share citation data

I'd love to discuss:
1. Official partnership/endorsement
2. Co-marketing opportunities
3. Data contribution agreements
4. Long-term collaboration

Can we schedule a 30-minute call?

Best,
[Your Name]
Evident Legal Technologies
https://Evident.info
```

**Benefits of Partnership:**

- ✅ Credibility (Free Law Project endorsement)
- ✅ Featured on their partners page
- ✅ Access to their community
- ✅ Priority API support
- ✅ Joint press releases

--

### **2. Academic Collaboration**

**Harvard Law School (Caselaw Access Project):**

- CourtListener partners with Harvard CAP
- You can use both APIs
- Position as "Powered by Harvard Law + Free Law Project"

**Law School Partnerships:**

- Offer Evident to schools using CourtListener
- "Professional tier for students learning on free tools"
- Train students on both platforms

--

### **3. Legal Aid Network**

**Coordinate with:**

- National Legal Aid & Defender Association (using CourtListener)
- Public defender offices (need professional tools)
- Pro bono networks

**Offer:**

- Free CourtListener for basic research
- Evident ($25/month) for AI analysis, mobile, support
- Seamless upgrade path

--

## 📊 REVENUE SHARING MODEL

### **Option 1: Donation Model**

- 2-5% of gross revenue to Free Law Project
- Monthly automatic donations
- Public transparency (builds trust)

**Example:**

- Month 1: $2,500 revenue → $125 donation
- Month 3: $127,000 revenue → $6,350 donation
- Year 1: $16M revenue → $800K donation

**Impact:**

- Funds CourtListener development
- Shows commitment to mission
- Tax-deductible (they're 501(c)(3))

--

### **Option 2: API Subscription**

- Pay for premium API tier
- Higher rate limits (1,000+ req/min)
- Priority support
- Bulk data access

**Current tiers:**

- Free: 100 req/min
- Researcher: $500/month (5,000 req/min)
- Commercial: Custom pricing

**When to upgrade:**

- 10,000+ users (heavy API use)
- Need faster imports
- Real-time updates critical

--

### **Option 3: Hybrid Model** (Recommended)

- Start: Free tier + 2% donations
- 1,000 users: Researcher tier ($500/month) + 3% donations
- 10,000 users: Commercial tier + 5% donations

**Why?**

- Scales with your business
- Supports their infrastructure
- Shows long-term commitment

--

## 🛠️ TECHNICAL INTEGRATION ROADMAP

### **WEEK 1: Foundation (Import Core Cases)**

**Day 1: Test API Integration**

```bash
cd C:\web-dev\github-repos\Evident.info

# Test single case import
python -c "from legal_library import LegalLibrary; ll = LegalLibrary(); print(ll.ingest_from_courtlistener('410 U.S. 113'))"

# Should return Roe v. Wade data
```

**Day 2-3: Import Foundation Cases**

```bash
# Import all 27 foundation cases
python overnight_library_builder.py -practice-area all

# Check results
cat logs/import_report_*.json
```

**Expected:** 27 cases successfully imported

**Day 4-5: Build Citation Network**

```python
# For each foundation case, get citing cases
from citation_network_analyzer import CitationNetworkAnalyzer

analyzer = CitationNetworkAnalyzer()
network = analyzer.build_citation_network('410 U.S. 113', depth=2)
# Gets cases citing Roe, and cases citing those cases
```

**Day 6-7: Test Shepardizing**

```python
from citation_network_analyzer import shepardize

# Test Shepard's-style analysis
report = shepardize('410 U.S. 113')
print(report['signal'])  # Should show RED_FLAG (overruled)
print(report['authority_score'])  # Historical significance
```

--

### **WEEK 2: Scale Up (1,000 Top Cases)**

**Create import script:**

```python
# top_cases_import.py
from legal_library import LegalLibrary

# Most-cited Supreme Court cases
top_cases = [
    '347 U.S. 483',    # Brown v. Board
    '384 U.S. 436',    # Miranda v. Arizona
    '410 U.S. 113',    # Roe v. Wade
    # ... 997 more
]

ll = LegalLibrary()
for citation in top_cases:
    try:
        ll.ingest_from_courtlistener(citation)
        print(f"✓ Imported: {citation}")
    except Exception as e:
        print(f"✗ Failed: {citation} - {e}")
```

**Run import:**

```bash
python top_cases_import.py
# Takes ~2 hours (respects rate limits)
```

--

### **WEEK 3: Judge Intelligence**

**Import judge profiles:**

```python
from judge_intelligence import JudgeIntelligence

ji = JudgeIntelligence()

# Get all Supreme Court justices
justices = ji.get_supreme_court_justices()

for justice in justices:
    profile = ji.get_judge_profile(justice['name'])
    education = ji.get_education_history(justice['id'])
    ideology = ji.get_ideology_score(justice['id'])

    print(f"{justice['name']}: {ideology} (ideology score)")
```

--

### **WEEK 4: Deploy Features**

**Build UI for:**

- [ ] Case search (10M+ opinions)
- [ ] Shepardizing (good law verification)
- [ ] Judge intelligence dashboard
- [ ] Citation network graphs
- [ ] AI legal assistant

**Test end-to-end:**

```
1. User searches: "miranda rights"
2. Results: Miranda v. Arizona + 100+ citing cases
3. Click case → See full opinion
4. Click "Shepardize" → See citation treatment
5. Click judge name → See judge profile
6. Ask AI: "Summarize this case" → Get summary
```

--

## 🎓 EDUCATIONAL MISSION ALIGNMENT

### **Free Law Project's Education Goals:**

1. Train law students on open tools
2. Support legal aid education
3. Democratize legal research skills
4. Reduce dependence on expensive tools

### **How Evident Supports This:**

**1. Free Tier for Students**

- Basic access to 10M+ cases
- Attribution to CourtListener
- "Learn on free tools, upgrade for professional features"

**2. Law School Partnerships**

- Students use CourtListener for class
- Evident for clinics/externships
- Smooth transition to professional tools

**3. Legal Aid Training**

- Free CourtListener workshops
- Subsidized Evident for offices
- Documentation showing both tools

**4. Content Creation**

- Blog: "How to use CourtListener effectively"
- Videos: "Free legal research skills"
- Guides: "CourtListener + Evident workflows"

--

## 💬 MESSAGING FRAMEWORK

### **How to Talk About CourtListener:**

**✅ DO:**

```
"Evident is built on CourtListener's open legal data, provided by
the non-profit Free Law Project. We add professional features like
AI analysis, mobile apps, and expert support."

"All our case law comes from CourtListener.com (free). We charge
for AI, mobile access, and customer support—not for access to the law."

"Support open access: Use CourtListener for free research, or upgrade
to Evident for professional tools at 1/10th Westlaw's price."
```

**❌ DON'T:**

```
"We have exclusive access to 10M cases" (Misleading)
"Our proprietary legal database" (False)
"Only Evident has this data" (Untrue)
```

--

## 🎯 MISSION METRICS (Track Impact)

### **CourtListener's Metrics:**

- Unique users/month
- API calls/day
- Cases accessed
- Downloads/month

### **Evident's Contribution:**

- Users introduced to CourtListener: **\_**
- Donations to Free Law Project: $**\_**
- Cases added to database: **\_**
- Bug reports/fixes submitted: **\_**
- Law students trained: **\_**
- Legal aid orgs supported: **\_**

### **Shared Impact:**

- Justice gap closed: **\_** people served
- Cost savings: $**\_** (vs Westlaw)
- Open access reach: **\_** organizations
- Legal education improved: **\_** students

--

## ✅ IMMEDIATE ACTION ITEMS

**Today:**

- [x] API key added to Render ✅
- [ ] Run: `python overnight_library_builder.py -practice-area all`
- [ ] Add CourtListener attribution to website footer
- [ ] Set up monthly $50 donation to Free Law Project

**This Week:**

- [ ] Import 1,000 top cases
- [ ] Build Shepardizing UI
- [ ] Add "Data by CourtListener" to every case page
- [ ] Email Free Law Project about partnership

**This Month:**

- [ ] Donate 2% of revenue
- [ ] Write blog post: "How we use CourtListener"
- [ ] Submit bug fix to their GitHub
- [ ] Feature CourtListener in law school pitch

**This Quarter:**

- [ ] Official partnership announced
- [ ] 10,000 users exposed to CourtListener
- [ ] $5,000+ donated to Free Law Project
- [ ] Joint press release on democratizing legal research

--

## 🚀 START NOW

**1. Import foundation cases:**

```bash
cd C:\web-dev\github-repos\Evident.info
python overnight_library_builder.py -practice-area all
```

**2. Add attribution:** Edit `templates/components/footer.html`:

```html
<footer>
  <p>
    Legal data provided by
    <a href="https://www.courtlistener.com">CourtListener</a>, a project of
    <a href="https://free.law">Free Law Project</a>
  </p>
</footer>
```

**3. Make first donation:** Go to: https://donate.free.law/ Amount: $50 (or 2%
of your first revenue)

**4. Email partnership proposal:** To: info@free.law Subject: "Partnership
Proposal - Evident" Use template above

--

**TOGETHER, WE'RE MAKING THE LAW FREE AND ACCESSIBLE TO ALL** 🤝⚖️
