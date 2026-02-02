---
layout: default
title: "Pricing | Evident"
permalink: /pricing/
description: "Simple, transparent pricing for Evident. Start free, upgrade as you grow. No hidden fees."
---

<link rel="stylesheet" href="{{ '/assets/css/brand-tokens.css' | relative_url }}">

<style>
  .pricing-hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
    background: linear-gradient(135deg, var(--barber-red, #c41e3a) 0%, var(--barber-blue, #1e40af) 100%);
    color: white;
    margin-bottom: 4rem;
  }
  
  .pricing-hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: 700;
  }
  
  .pricing-hero p {
    font-size: 1.25rem;
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto 4rem;
    padding: 0 2rem;
  }
  
  .pricing-card {
    background: white;
    border: 2px solid #e0e0e8;
    border-radius: 24px;
    padding: 2.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
  }
  
  .pricing-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.15);
    border-color: var(--barber-red, #c41e3a);
  }
  
  .pricing-card.featured {
    border-color: var(--barber-red, #c41e3a);
    border-width: 3px;
    box-shadow: 0 8px 32px rgba(196, 30, 58, 0.2);
  }
  
  .pricing-badge {
    position: absolute;
    top: -12px;
    right: 24px;
    background: var(--barber-red, #c41e3a);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .pricing-tier {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--barber-red, #c41e3a);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .pricing-price {
    font-size: 3.5rem;
    font-weight: 700;
    color: #0a0a0f;
    margin-bottom: 0.5rem;
  }
  
  .pricing-price sup {
    font-size: 1.5rem;
    font-weight: 500;
  }
  
  .pricing-period {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2rem;
  }
  
  .pricing-cta {
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, var(--barber-red, #c41e3a) 0%, var(--barber-blue, #1e40af) 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-decoration: none;
    display: block;
    text-align: center;
  }
  
  .pricing-cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(196, 30, 58, 0.4);
  }
  
  .pricing-cta.secondary {
    background: white;
    color: var(--barber-red, #c41e3a);
    border: 2px solid var(--barber-red, #c41e3a);
  }
  
  .pricing-features {
    list-style: none;
    padding: 0;
    margin: 2rem 0;
  }
  
  .pricing-features li {
    padding: 0.75rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    font-size: 0.9375rem;
    color: #374151;
  }
  
  .pricing-features svg {
    flex-shrink: 0;
    margin-top: 0.125rem;
  }
  
  .pricing-faq {
    max-width: 800px;
    margin: 4rem auto;
    padding: 0 2rem;
  }
  
  .pricing-faq h2 {
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
  }
  
  .faq-item {
    margin-bottom: 1.5rem;
  }
  
  .faq-question {
    font-weight: 600;
    color: #0a0a0f;
    margin-bottom: 0.5rem;
  }
  
  .faq-answer {
    color: #6b7280;
    line-height: 1.6;
  }
</style>

<div class="pricing-hero">
  <h1>Simple, Transparent Pricing</h1>
  <p>Start free, upgrade as you grow. No hidden fees. Cancel anytime.</p>
</div>

<div class="pricing-grid">
  
  <!-- Free Tier -->
  <div class="pricing-card">
    <div class="pricing-tier">Free</div>
    <div class="pricing-price"><sup>$</sup>0</div>
    <div class="pricing-period">Forever free</div>
    
    <a href="/auth/signup" class="pricing-cta secondary">Start Free</a>
    
    <ul class="pricing-features">
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>2 BWC videos/month</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>50 document pages/month</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>30 min AI transcription</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>100 search queries</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>500MB storage</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Community support</span>
      </li>
    </ul>
  </div>
  
  <!-- Professional Tier -->
  <div class="pricing-card featured">
    <div class="pricing-badge">Most Popular</div>
    <div class="pricing-tier">Professional</div>
    <div class="pricing-price"><sup>$</sup>49</div>
    <div class="pricing-period">per month</div>
    
    <a href="/auth/signup" class="pricing-cta">Get Started</a>
    
    <ul class="pricing-features">
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span><strong>25 BWC videos/month</strong></span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>1,000 document pages</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>10 hours AI transcription</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span><strong>Unlimited search</strong></span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>25GB storage</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>No watermarks</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Email support (48hr)</span>
      </li>
    </ul>
  </div>
  
  <!-- Premium Tier -->
  <div class="pricing-card">
    <div class="pricing-tier">Premium</div>
    <div class="pricing-price"><sup>$</sup>149</div>
    <div class="pricing-period">per month</div>
    
    <a href="/auth/signup" class="pricing-cta">Get Started</a>
    
    <ul class="pricing-features">
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span><strong>100 BWC videos/month</strong></span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>10,000 document pages</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>50 hours AI transcription</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>250GB storage</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span><strong>API access</strong></span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Forensic analysis suite</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Priority support (24hr)</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>White-label exports</span>
      </li>
    </ul>
  </div>
  
  <!-- Enterprise Tier -->
  <div class="pricing-card">
    <div class="pricing-tier">Enterprise</div>
    <div class="pricing-price"><sup>$</sup>499</div>
    <div class="pricing-period">per month</div>
    
    <a href="/auth/signup" class="pricing-cta">Contact Sales</a>
    
    <ul class="pricing-features">
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span><strong>Unlimited everything</strong></span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>1TB storage</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Full API access with SLA</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>24/7 priority support</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Dedicated account manager</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>On-premise deployment option</span>
      </li>
      <li>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        <span>Training & onboarding</span>
      </li>
    </ul>
  </div>
  
</div>

<div class="pricing-faq">
  <h2>Frequently Asked Questions</h2>
  
  <div class="faq-item">
    <div class="faq-question">Can I upgrade or downgrade at any time?</div>
    <div class="faq-answer">Yes! You can change your plan at any time. Upgrades take effect immediately, and downgrades apply at the end of your current billing cycle.</div>
  </div>
  
  <div class="faq-item">
    <div class="faq-question">Is there a free trial for paid plans?</div>
    <div class="faq-answer">The Free tier is available forever with no credit card required. You can test the platform and upgrade when ready.</div>
  </div>
  
  <div class="faq-item">
    <div class="faq-question">What happens if I exceed my limits?</div>
    <div class="faq-answer">You'll receive a notification when you approach your limits. You can either wait until next month's reset or upgrade to a higher tier for instant access.</div>
  </div>
  
  <div class="faq-item">
    <div class="faq-question">Do you offer annual billing?</div>
    <div class="faq-answer">Yes! Contact us for annual billing options with a 20% discount.</div>
  </div>
  
  <div class="faq-item">
    <div class="faq-question">Is my data secure?</div>
    <div class="faq-answer">Absolutely. All processing happens locally on your machine. We never see your evidence files. Your data stays on your hardware.</div>
  </div>
</div>
