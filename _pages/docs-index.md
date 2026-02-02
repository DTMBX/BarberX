---
layout: default
title: "Documentation | Evident"
permalink: /docs/
description: "Complete documentation for Evident — guides, tutorials, and API references."
---

<style>
  .docs-hero {
    background: linear-gradient(135deg, #c41e3a 0%, #1e40af 100%);
    color: white;
    padding: 4rem 2rem 3rem;
    text-align: center;
  }
  
  .docs-hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .docs-container {
    max-width: 1200px;
    margin: 4rem auto;
    padding: 0 2rem;
  }
  
  .docs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
  }
  
  .doc-card {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    transition: transform 0.3s, box-shadow 0.3s;
    text-decoration: none;
    display: block;
  }
  
  .doc-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }
  
  .doc-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .doc-card h2 {
    color: #c41e3a;
    margin-bottom: 0.75rem;
    font-size: 1.5rem;
  }
  
  .doc-card p {
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
  }
  
  .doc-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: #10b981;
    color: white;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  .badge-new {
    background: #10b981;
  }
  
  .badge-updated {
    background: #f59e0b;
  }
  
  .quick-links {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
  
  .quick-links h2 {
    color: #c41e3a;
    margin-bottom: 1.5rem;
  }
  
  .quick-links ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .quick-links li {
    padding: 0.75rem 0;
    border-bottom: 1px solid #e0e0e8;
  }
  
  .quick-links li:last-child {
    border-bottom: none;
  }
  
  .quick-links a {
    color: #0a0a0f;
    text-decoration: none;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .quick-links a:hover {
    color: #c41e3a;
  }
  
  .quick-links a::after {
    content: "→";
    font-size: 1.25rem;
    opacity: 0.5;
  }
</style>

<div class="docs-hero">
  <h1>📚 Documentation</h1>
  <p>Everything you need to master Evident</p>
</div>

<div class="docs-container">
  
  <div class="docs-grid">
    
    <a href="/docs/installation/" class="doc-card">
      <span class="doc-badge badge-new">Updated</span>
      <div class="doc-icon">🚀</div>
      <h2>Installation Guide</h2>
      <p>Get Evident running in 15 minutes. Step-by-step setup for Windows, macOS, and Linux with GPU support.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">📖</div>
      <h2>User Guide</h2>
      <p>Complete walkthrough of Evident features. Learn to process videos, extract transcripts, and analyze evidence.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">⚙️</div>
      <h2>Configuration</h2>
      <p>Customize Evident for your workflow. Settings, preferences, and optimization tips.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">🤖</div>
      <h2>AI Models</h2>
      <p>Deep dive into the AI models powering Evident. Whisper, pyannote, YOLO, spaCy, and more.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">🔌</div>
      <h2>API Reference</h2>
      <p>Premium/Enterprise API documentation. Integrate Evident into your existing tools and workflows.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">🛠️</div>
      <h2>Troubleshooting</h2>
      <p>Common issues and solutions. GPU problems, memory errors, installation failures, and more.</p>
    </a>
    
    <a href="/cases/" class="doc-card">
      <div class="doc-icon">⚖️</div>
      <h2>Real Cases</h2>
      <p>Learn from actual case studies. See how Evident is used in real legal investigations.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">🎓</div>
      <h2>Video Tutorials</h2>
      <p>Watch and learn. Screen recordings showing Evident workflows from start to finish.</p>
    </a>
    
    <a href="#" class="doc-card">
      <div class="doc-icon">🔐</div>
      <h2>Security & Privacy</h2>
      <p>How Evident protects your data. Chain of custody, encryption, and compliance documentation.</p>
    </a>
    
  </div>
  
  <div class="quick-links">
    <h2>Quick Links</h2>
    <ul>
      <li><a href="/docs/installation/">Quick Start Guide</a></li>
      <li><a href="/pricing/">View Pricing & Tiers</a></li>
      <li><a href="/auth/signup">Create Free Account</a></li>
      <li><a href="/faq/">Frequently Asked Questions</a></li>
      <li><a href="/contact/">Contact Support</a></li>
      <li><a href="https://github.com/yourusername/Evident.info" target="_blank">GitHub Repository</a></li>
    </ul>
  </div>
  
  <div style="margin-top: 3rem; padding: 2rem; background: rgba(196, 30, 58, 0.05); border-left: 4px solid #c41e3a; border-radius: 8px;">
    <h3 style="margin-top: 0; color: #c41e3a;">Can't find what you're looking for?</h3>
    <p style="margin-bottom: 1rem; color: #374151;">
      Our documentation is constantly evolving. If you need help with something not covered here:
    </p>
    <ul style="color: #374151;">
      <li>Check the <a href="/faq/" style="color: #c41e3a; font-weight: 600;">FAQ page</a></li>
      <li>Email us at <a href="mailto:support@Evident.info" style="color: #c41e3a; font-weight: 600;">support@Evident.info</a></li>
      <li>File an issue on <a href="https://github.com/yourusername/Evident.info/issues" style="color: #c41e3a; font-weight: 600;">GitHub</a></li>
    </ul>
  </div>
  
</div>
