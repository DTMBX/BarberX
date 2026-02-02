#!/usr/bin/env pwsh
# Evident.info - AI Dependencies Installation Script
# Installs MIT/Apache/BSD licensed AI tools for constitutional violation detection

Write-Host "`n?? Evident AI Dependencies Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing license-compliant AI tools for:" -ForegroundColor Gray
Write-Host "  � Constitutional violation detection" -ForegroundColor White
Write-Host "  � BWC video forensic analysis" -ForegroundColor White
Write-Host "  � PDF legal document processing" -ForegroundColor White
Write-Host "  � Audio transcription & speaker ID" -ForegroundColor White
Write-Host "  � Case law matching & citations" -ForegroundColor White
Write-Host ""

Set-Location "C:\web-dev\github-repos\Evident.info"

# Check Python version
Write-Host "[1/8] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(9|10|11|12)") {
    Write-Host "  ? $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ??  Python 3.9+ required, found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "`n[2/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "  ? pip upgraded" -ForegroundColor Green

# Install PyTorch (CPU version for faster install, GPU optional)
Write-Host "`n[3/8] Installing PyTorch..." -ForegroundColor Yellow
Write-Host "  (This may take 5-10 minutes)" -ForegroundColor Gray
python -m pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? PyTorch installed (CPU version)" -ForegroundColor Green
} else {
    Write-Host "  ??  PyTorch installation had issues" -ForegroundColor Yellow
}

# Install Whisper AI (Audio Transcription)
Write-Host "`n[4/8] Installing Whisper AI..." -ForegroundColor Yellow
python -m pip install openai-whisper --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? Whisper AI installed (MIT License)" -ForegroundColor Green
}

# Install Transformers & Sentence Transformers
Write-Host "`n[5/8] Installing Hugging Face Transformers..." -ForegroundColor Yellow
python -m pip install transformers sentence-transformers --quiet
Write-Host "  ? Transformers installed (Apache 2.0)" -ForegroundColor Green

# Install SpaCy + Legal NLP Model
Write-Host "`n[6/8] Installing SpaCy & Legal NLP..." -ForegroundColor Yellow
python -m pip install spacy --quiet
python -m spacy download en_core_web_lg --quiet
Write-Host "  ? SpaCy + Legal model installed (MIT License)" -ForegroundColor Green

# Install LangChain (Constitutional Analysis)
Write-Host "`n[7/8] Installing LangChain for Legal Analysis..." -ForegroundColor Yellow
python -m pip install langchain langchain-openai langchain-anthropic langchain-community --quiet
Write-Host "  ? LangChain installed (MIT License)" -ForegroundColor Green

# Install remaining AI dependencies
Write-Host "`n[8/8] Installing remaining AI tools..." -ForegroundColor Yellow
python -m pip install -r requirements-ai.txt --quiet 2>&1 | Out-Null
Write-Host "  ? All AI dependencies installed" -ForegroundColor Green

# Verify installations
Write-Host "`n?? Verifying AI Components..." -ForegroundColor Cyan

python -c @'
import sys

components = {
    "Whisper AI (Audio Transcription)": "whisper",
    "Transformers (NLP)": "transformers",
    "SpaCy (Legal NLP)": "spacy",
    "LangChain (Constitutional Analysis)": "langchain",
    "PyTorch (Deep Learning)": "torch",
    "Sentence Transformers (Embeddings)": "sentence_transformers",
    "ChromaDB (Case Law Database)": "chromadb",
    "PyAnnote (Speaker ID)": "pyannote.audio"
}

print("\nInstalled Components:")
failed = []
for name, module in components.items():
    try:
        __import__(module.replace(".audio", ""))
        print(f"  ? {name}")
    except ImportError:
        print(f"  ? {name}")
        failed.append(name)

if failed:
    print(f"\n??  {len(failed)} component(s) need attention")
    sys.exit(1)
else:
    print("\n? All AI components verified!")
'@

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "? AI Installation Complete!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`n?? Capabilities Enabled:" -ForegroundColor Cyan
    Write-Host "  ? BWC Video Forensic Analysis" -ForegroundColor Green
    Write-Host "  ? Audio Transcription (Whisper)" -ForegroundColor Green
    Write-Host "  ? Speaker Diarization (Officer vs Civilian)" -ForegroundColor Green
    Write-Host "  ? Constitutional Violation Detection" -ForegroundColor Green
    Write-Host "  ? PDF Legal Document Analysis" -ForegroundColor Green
    Write-Host "  ? Case Law Matching & Citations" -ForegroundColor Green
    Write-Host "  ? Miranda Rights Violation Detection" -ForegroundColor Green
    Write-Host "  ? 4th Amendment Search/Seizure Analysis" -ForegroundColor Green
    Write-Host "  ? Excessive Force Detection" -ForegroundColor Green
    
    Write-Host "`n??  Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Set up API keys (OpenAI, Anthropic) in .env file" -ForegroundColor White
    Write-Host "  2. Run: python scripts/setup-constitutional-ai.py" -ForegroundColor White
    Write-Host "  3. Test: python -c 'from bwc_forensic_analyzer import BWCForensicAnalyzer; print(\"? Ready!\")'" -ForegroundColor White
    
} else {
    Write-Host "`n??  Some components need attention" -ForegroundColor Yellow
    Write-Host "Review errors above and retry failed installations" -ForegroundColor Gray
}

Write-Host ""
