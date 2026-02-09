#!/usr/bin/env python3
"""
Phase 9 Quick Start Script
Setup testing environment and generate fixtures
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def run_command(cmd, description):
    """Run shell command and report status"""
    print(f"▶ {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS\n")
            return True
        else:
            print(f"⚠️  {description} - PARTIAL SUCCESS (exit code: {result.returncode})\n")
            return False
    except Exception as e:
        print(f"❌ {description} - FAILED: {e}\n")
        return False

def main():
    """Main setup routine"""
    root = Path(__file__).parent
    os.chdir(root)
    
    print_header("PHASE 9: TESTING SUITE QUICK START")
    print("📋 Setting up batch document processing test suite\n")
    
    # Step 1: Check Python version
    print_header("STEP 1: Checking Environment")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}")
    
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK\n")
    
    # Step 2: Install dependencies
    print_header("STEP 2: Installing Dependencies")
    
    if not run_command(
        "pip install --upgrade pip setuptools wheel",
        "Upgrading pip/setuptools"
    ):
        print("⚠️  Some upgrades failed, continuing...")
    
    if not run_command(
        "pip install -r requirements-phase9.txt",
        "Installing Phase 9 dependencies"
    ):
        print("⚠️  Some dependencies failed to install")
        print("     This may be due to binary dependencies (pytesseract, easyocr)")
        print("     See PHASE_9_QUICK_START.md for manual setup instructions")
    
    # Step 3: Generate test fixtures
    print_header("STEP 3: Generating Test Fixtures")
    
    try:
        from tests.phase9.fixtures.generate_fixtures import (
            generate_sample_pdfs,
            generate_dismissed_case_pdfs
        )
        
        sample_dir = root / "tests" / "phase9" / "fixtures" / "sample_pdfs"
        dismissed_dir = root / "tests" / "phase9" / "fixtures" / "dismissed_cases"
        
        os.makedirs(sample_dir, exist_ok=True)
        os.makedirs(dismissed_dir, exist_ok=True)
        
        generate_sample_pdfs(str(sample_dir))
        generate_dismissed_case_pdfs(str(dismissed_dir))
        
        print("✅ Test fixtures generated\n")
    except ImportError as e:
        print(f"⚠️  Could not generate fixtures (importing): {e}")
    except Exception as e:
        print(f"⚠️  Could not generate fixtures: {e}")
    
    # Step 4: Run initial test
    print_header("STEP 4: Running Initial Test")
    
    test_cmd = "pytest tests/phase9/unit/batch_processing/test_pdf_batch_loader.py -v --tb=short -k 'test_pdf_loader_initialization'"
    
    if run_command(test_cmd, "Running PDF loader initialization test"):
        print("🎉 Phase 9 setup complete!\n")
    else:
        print("⚠️  Initial test failed - check installation\n")
    
    # Step 5: Display next steps
    print_header("NEXT STEPS")
    
    print("""
1️⃣  Run all Phase 9 tests:
    pytest tests/phase9/ -v

2️⃣  Run specific test category:
    pytest tests/phase9/unit/batch_processing/ -v        # Unit tests
    pytest tests/phase9/integration/ -v                   # Integration tests
    pytest tests/phase9/performance/ -v                   # Performance tests

3️⃣  Run with coverage report:
    pytest tests/phase9/ --cov=models/batch_document_processing --cov-report=html

4️⃣  Watch mode (auto-rerun on file change):
    pytest-watcher tests/phase9/ -v

5️⃣  Run in parallel (faster):
    pytest tests/phase9/ -v -n auto

📖 Read documentation:
   - PHASE_9_QUICK_START.md (this week's workflow)
   - MASTER_IMPLEMENTATION_CHECKLIST.md (complete roadmap)
   - PHASE_9_10_11_ENHANCED_PLAN.md (technical specs)

🚀 Status: Phase 9 ready to begin!
""")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
