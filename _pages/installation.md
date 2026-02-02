---
layout: default
title: "Installation Guide | Evident"
permalink: /docs/installation/
description: "Complete installation guide for Evident local AI tools and platform setup."
---

<style>
  .install-hero {
    background: linear-gradient(135deg, #c41e3a 0%, #1e40af 100%);
    color: white;
    padding: 4rem 2rem 3rem;
    text-align: center;
    margin-bottom: 3rem;
  }
  
  .install-hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .install-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 2rem 4rem;
  }
  
  .install-section {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    margin-bottom: 2rem;
  }
  
  .install-section h2 {
    color: #c41e3a;
    margin-bottom: 1.5rem;
    font-size: 1.75rem;
  }
  
  .install-section h3 {
    color: #0a0a0f;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    font-size: 1.25rem;
  }
  
  pre {
    background: #0a0a0f;
    color: #10b981;
    padding: 1.5rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    font-size: 0.875rem;
    line-height: 1.6;
  }
  
  code {
    background: #f3f4f6;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
    color: #c41e3a;
  }
  
  pre code {
    background: none;
    padding: 0;
    color: inherit;
  }
  
  .step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: #c41e3a;
    color: white;
    border-radius: 50%;
    font-weight: 700;
    margin-right: 0.75rem;
  }
  
  .install-steps {
    counter-reset: step;
  }
  
  .install-step {
    margin-bottom: 2rem;
    padding-left: 2.5rem;
    position: relative;
  }
  
  .install-step::before {
    counter-increment: step;
    content: counter(step);
    position: absolute;
    left: 0;
    top: 0;
    width: 32px;
    height: 32px;
    background: #c41e3a;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
  }
  
  .warning {
    background: rgba(245, 158, 11, 0.1);
    border-left: 4px solid #f59e0b;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 1rem 0;
  }
  
  .success {
    background: rgba(16, 185, 129, 0.1);
    border-left: 4px solid #10b981;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    margin: 1rem 0;
  }
</style>

<div class="install-hero">
  <h1>Installation Guide</h1>
  <p>Set up Evident in 15 minutes</p>
</div>

<div class="install-container">
  
  <div class="install-section">
    <h2>System Requirements</h2>
    
    <h3>Minimum Requirements</h3>
    <ul>
      <li><strong>OS:</strong> Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)</li>
      <li><strong>RAM:</strong> 8GB</li>
      <li><strong>Storage:</strong> 50GB free space</li>
      <li><strong>Python:</strong> 3.8 or later</li>
    </ul>
    
    <h3>Recommended for Best Performance</h3>
    <ul>
      <li><strong>RAM:</strong> 16GB or more</li>
      <li><strong>GPU:</strong> NVIDIA with 6GB+ VRAM (CUDA support)</li>
      <li><strong>Storage:</strong> SSD with 100GB+ free space</li>
      <li><strong>CPU:</strong> Intel i7 / AMD Ryzen 7 or better</li>
    </ul>
  </div>
  
  <div class="install-section">
    <h2>Quick Start (Windows)</h2>
    
    <div class="install-steps">
      <div class="install-step">
        <h3>Install Python</h3>
        <p>Download Python 3.12 from <a href="https://www.python.org/downloads/" target="_blank">python.org</a></p>
        <div class="warning">
          <strong>Important:</strong> Check "Add Python to PATH" during installation!
        </div>
      </div>
      
      <div class="install-step">
        <h3>Clone or Download Evident</h3>
        <pre><code>git clone https://github.com/yourusername/Evident.info.git
cd Evident.info</code></pre>
        <p>Or download ZIP from GitHub and extract.</p>
      </div>
      
      <div class="install-step">
        <h3>Run Installation Script</h3>
        <pre><code>.\install_local_ai.ps1</code></pre>
        <p>This will:</p>
        <ul>
          <li>Create a Python virtual environment</li>
          <li>Install all required packages</li>
          <li>Download AI models (~5GB)</li>
          <li>Set up the database</li>
        </ul>
        <div class="warning">
          <strong>Note:</strong> First-time setup takes 10-15 minutes depending on your internet speed.
        </div>
      </div>
      
      <div class="install-step">
        <h3>Initialize the Database</h3>
        <pre><code>python init_auth.py</code></pre>
        <p>This creates your user account and sets up the database.</p>
      </div>
      
      <div class="install-step">
        <h3>Start the Platform</h3>
        <pre><code>python app.py</code></pre>
        <p>Open your browser to <a href="http://localhost:5000">http://localhost:5000</a></p>
      </div>
    </div>
    
    <div class="success">
      <strong>✅ You're all set!</strong> Login with your credentials and start processing evidence.
    </div>
  </div>
  
  <div class="install-section">
    <h2>Quick Start (macOS/Linux)</h2>
    
    <div class="install-steps">
      <div class="install-step">
        <h3>Install Python</h3>
        <p>macOS:</p>
        <pre><code>brew install python@3.12</code></pre>
        <p>Linux:</p>
        <pre><code>sudo apt update
sudo apt install python3.12 python3-pip python3-venv</code></pre>
      </div>
      
      <div class="install-step">
        <h3>Clone Repository</h3>
        <pre><code>git clone https://github.com/yourusername/Evident.info.git
cd Evident.info</code></pre>
      </div>
      
      <div class="install-step">
        <h3>Create Virtual Environment</h3>
        <pre><code>python3 -m venv .venv
source .venv/bin/activate</code></pre>
      </div>
      
      <div class="install-step">
        <h3>Install Dependencies</h3>
        <pre><code>pip install -r requirements.txt
pip install -r tillerstead-toolkit/backend/requirements-local-ai.txt</code></pre>
      </div>
      
      <div class="install-step">
        <h3>Initialize and Run</h3>
        <pre><code>python init_auth.py
python app.py</code></pre>
        <p>Visit <a href="http://localhost:5000">http://localhost:5000</a></p>
      </div>
    </div>
  </div>
  
  <div class="install-section">
    <h2>GPU Support (Optional but Recommended)</h2>
    
    <h3>NVIDIA GPU Setup</h3>
    <p>For 5-10x faster processing:</p>
    
    <div class="install-step">
      <h3>Install CUDA Toolkit</h3>
      <p>Download CUDA 11.8 from <a href="https://developer.nvidia.com/cuda-downloads" target="_blank">NVIDIA</a></p>
    </div>
    
    <div class="install-step">
      <h3>Install PyTorch with CUDA</h3>
      <pre><code>pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118</code></pre>
    </div>
    
    <div class="install-step">
      <h3>Verify GPU</h3>
      <pre><code>python -c "import torch; print(torch.cuda.is_available())"</code></pre>
      <p>Should output: <code>True</code></p>
    </div>
  </div>
  
  <div class="install-section">
    <h2>Troubleshooting</h2>
    
    <h3>Python not found</h3>
    <p>Make sure Python is in your PATH. Restart terminal/PowerShell after installation.</p>
    
    <h3>Permission denied errors</h3>
    <p>Run PowerShell as Administrator (Windows) or use <code>sudo</code> (Linux/macOS).</p>
    
    <h3>Out of memory</h3>
    <p>Close other applications. Reduce batch size in AI processing settings. Consider upgrading RAM.</p>
    
    <h3>Slow processing</h3>
    <p>Enable GPU support (see above). Reduce video resolution. Process in smaller batches.</p>
    
    <h3>Port 5000 already in use</h3>
    <pre><code>python app.py --port 8080</code></pre>
    
    <div class="warning">
      <strong>Still having issues?</strong> Contact support at <a href="mailto:support@Evident.info">support@Evident.info</a>
    </div>
  </div>
  
  <div class="install-section">
    <h2>Next Steps</h2>
    <ul>
      <li>✅ Read the <a href="/docs/">User Guide</a></li>
      <li>✅ Process your first BWC video</li>
      <li>✅ Explore the forensic analysis tools</li>
      <li>✅ Check out <a href="/cases/">Real Cases</a> for examples</li>
      <li>✅ Join the community forum for tips and tricks</li>
    </ul>
  </div>
  
</div>
