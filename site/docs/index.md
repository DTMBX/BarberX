---
title: "Evident Legal Technologies Documentation"
layout: default
permalink: /docs/
description: "Documentation for Evident's evidence processing, verification, and eDiscovery platform."
extra_css:
  - /assets/css/pages/docs.css
---

<div class="docs-hero">
  <h1>📚 Evident Documentation</h1>
  <p>AI-powered eDiscovery and forensic analysis for legal professionals</p>
</div>

<div class="docs-grid">
  <div class="docs-card">
    <h3>🌐 For All Users</h3>
    <p>Access Evident via the web at <a href="https://Evident.info">Evident.info</a>. No installation required for standard users — all features available securely through the web app.</p>
    <a href="/register">Get Started Free →</a>
  </div>
  
  <div class="docs-card enterprise">
    <h3>🏢 For Enterprise</h3>
    <p>Enterprise customers can download and run the local library for air-gapped deployments. Contact support for access to the enterprise package.</p>
    <a href="mailto:support@Evident.info">Contact Sales →</a>
  </div>
</div>

<div class="docs-toc">
  <h2>Quick Navigation</h2>
  <ul>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#user-guide">User Guide</a></li>
    <li><a href="#api-reference">API Reference</a></li>
    <li><a href="#faq">FAQ</a></li>
    <li><a href="#troubleshooting">Troubleshooting</a></li>
    <li><a href="#support">Support & Community</a></li>
  </ul>
</div>

<div id="overview" class="docs-section">
  <h2>Overview</h2>
  <p>Evident is a local-first, privacy-focused legal tech platform for processing body-worn camera (BWC) footage, police reports, and legal documents. Features include:</p>
  <ul>
    <li><strong>100% Local AI</strong> — No cloud required, data never leaves your machine</li>
    <li><strong>Multi-user Authentication</strong> — Role-based access control for teams</li>
    <li><strong>Chain of Custody</strong> — SHA-256 hashing and audit logging</li>
    <li><strong>Advanced Analysis</strong> — Transcription, entity extraction, discrepancy detection</li>
    <li><strong>Exports Formatted For Court Submission</strong> — PDF, DOCX, JSON formats with custody reports</li>
  </ul>
</div>

<div id="getting-started" class="docs-section">
  <h2>Getting Started</h2>
  
  <h3>🚀 Quick Start (15 minutes)</h3>
  <ol>
    <li><strong>Create Account:</strong> <a href="/register">Sign up for free</a> (no credit card required)</li>
    <li><strong>Install AI Tools:</strong> Follow our <a href="/docs/installation/">Installation Guide</a></li>
    <li><strong>Upload Evidence:</strong> Drag & drop your first BWC video to the <a href="/analyzer">Analyzer</a></li>
    <li><strong>Review Results:</strong> Get transcripts, entities, and discrepancy reports in minutes</li>
  </ol>
  
  <h3>💻 System Requirements</h3>
  <ul>
    <li>Windows 10/11, macOS 10.15+, or Linux</li>
    <li>Python 3.8 or higher</li>
    <li>8GB RAM minimum (16GB recommended)</li>
    <li>10GB free disk space</li>
    <li>GPU optional (CUDA-enabled for faster processing)</li>
  </ul>
  
  <p><a href="/docs/installation/">View Complete Installation Guide →</a></p>
</div>

<div id="user-guide" class="docs-section">
  <h2>User Guide</h2>

  <h3>Logging In</h3>
  <p>Use the password you set during registration or reset via the admin panel.</p>

  <h3>Uploading Evidence</h3>
  <p>Go to the dashboard and use the upload form for BWC videos, PDFs, or images. Supported formats: MP4, MOV, PDF, JPG, PNG, CSV, JSON, DOCX, and more.</p>

  <h3>AI-Powered Analysis</h3>
  <p>Transcribe audio, extract text, and run entity recognition on uploaded files. All processing is local—no data leaves your machine.</p>

  <h3>Search & Export</h3>
  <p>Use semantic search to find relevant evidence. Export exhibits formatted for court submission as PDF, DOCX, or JSON.</p>
</div>

<div id="api-reference" class="docs-section">
  <h2>API Reference</h2>
  <p>RESTful endpoints for evidence upload, user management, and analysis. Available on Professional, Premium, and Enterprise tiers.</p>
  <p><a href="/api">View Full API Documentation →</a></p>
</div>

<div id="faq" class="docs-section">
  <h2>FAQ</h2>
  <p>Common questions about Evident features, pricing, security, and technical requirements.</p>
  <p><a href="/faq/">View FAQ →</a></p>
</div>

<div id="troubleshooting" class="docs-section">
  <h2>Troubleshooting</h2>
  <ul>
    <li><strong>Missing dependencies:</strong> Run <code>pip install -r requirements.txt</code></li>
    <li><strong>Database errors:</strong> Ensure your database URI is correct and migrations are applied</li>
    <li><strong>AI features unavailable:</strong> Install required AI dependencies (see requirements.txt)</li>
    <li><strong>Port in use:</strong> Change the PORT environment variable or stop the conflicting process</li>
  </ul>
</div>

<div id="support" class="docs-section">
  <h2>Support & Community</h2>
  <ul>
    <li><strong>Email:</strong> <a href="mailto:support@Evident.info">support@Evident.info</a></li>
    <li><strong>GitHub:</strong> <a href="https://github.com/DTB396/Evident.info/issues">Report Issues</a></li>
    <li><strong>Documentation:</strong> <a href="/docs/">Full Docs</a></li>
    <li><strong>Changelog:</strong> <a href="../CHANGELOG.md">View release notes</a></li>
  </ul>
</div>

Evident Legal Technologies © 2026. All rights reserved.
