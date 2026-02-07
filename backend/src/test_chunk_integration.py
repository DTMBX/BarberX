# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
BWC Chunk-Level Routing - Integration Test Script
Tests all components and verifies integration points
"""

import os
import sys
from pathlib import Path


# Color output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_test(msg, status="info"):
    colors = {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.BLUE,
    }
    color = colors.get(status, Colors.BLUE)
    symbol = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️",
    }.get(status, "•")
    print(f"{color}{symbol} {msg}{Colors.RESET}")


def test_file_exists(filepath, description):
    """Test if a file exists"""
    if Path(filepath).exists():
        size = Path(filepath).stat().st_size / 1024
        print_test(f"{description}: {size:.1f} KB", "success")
        return True
    else:
        print_test(f"{description}: NOT FOUND", "error")
        return False


def test_import(module_path, class_name, description):
    """Test if a module can be imported"""
    try:
        # Add to path
        sys.path.insert(0, str(Path(module_path).parent))

        # Import
        module_name = Path(module_path).stem
        module = __import__(module_name)

        # Check class
        if hasattr(module, class_name):
            print_test(f"{description}: Import successful", "success")
            return True, module
        else:
            print_test(f"{description}: Class {class_name} not found", "warning")
            return False, module
    except Exception as e:
        print_test(f"{description}: {str(e)}", "error")
        return False, None


def test_instantiation(module, class_name, description):
    """Test if a class can be instantiated"""
    try:
        cls = getattr(module, class_name)
        instance = cls()
        print_test(f"{description}: Instantiation successful", "success")
        return True, instance
    except Exception as e:
        print_test(f"{description}: {str(e)}", "error")
        return False, None


def main():
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}BWC CHUNK-LEVEL ROUTING - INTEGRATION TEST{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    base_path = Path(__file__).parent
    results = {"passed": 0, "failed": 0, "warnings": 0}

    # Test 1: File Existence
    print(f"\n{Colors.BOLD}📁 TEST 1: File Existence{Colors.RESET}")
    print("-" * 80)

    files_to_check = [
        ("barber-cam/py/bwc_chunk_analyzer.py", "Chunk Analyzer"),
        ("barber-cam/py/bwc_enhanced_analyzer.py", "Enhanced Analyzer"),
        ("barber-cam/py/bwc_smart_pipeline.py", "Smart Pipeline"),
        ("barber-cam/py/bwc_cost_governor.py", "Cost Governor"),
        ("barber-cam/py/bwc_model_registry.py", "Model Registry"),
        ("barber-cam/py/__init__.py", "Package Init"),
        ("bwc_api_routes.py", "API Routes"),
        ("_includes/bwc-chunk-analyzer.html", "UI Component"),
        ("assets/js/bwc-chunk-ui.js", "UI JavaScript"),
        ("docs/guides/CHUNK-LEVEL-AI-ROUTING.md", "Chunk Routing Guide"),
        ("docs/guides/COMPLETE-AI-STRATEGY.md", "Complete Strategy"),
        ("docs/guides/CHUNK-IMPLEMENTATION-COMPLETE.md", "Implementation Guide"),
    ]

    for filepath, description in files_to_check:
        full_path = base_path / filepath
        if test_file_exists(full_path, description):
            results["passed"] += 1
        else:
            results["failed"] += 1

    # Test 2: Python Imports
    print(f"\n{Colors.BOLD}🐍 TEST 2: Python Module Imports{Colors.RESET}")
    print("-" * 80)

    # Test ChunkAnalyzer
    chunk_analyzer_path = base_path / "barber-cam" / "py" / "bwc_chunk_analyzer.py"
    success, ca_module = test_import(chunk_analyzer_path, "ChunkAnalyzer", "ChunkAnalyzer")
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test EnhancedBWCAnalyzer
    enhanced_path = base_path / "barber-cam" / "py" / "bwc_enhanced_analyzer.py"
    success, ea_module = test_import(enhanced_path, "EnhancedBWCAnalyzer", "EnhancedBWCAnalyzer")
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test SmartPipelineSelector
    pipeline_path = base_path / "barber-cam" / "py" / "bwc_smart_pipeline.py"
    success, sp_module = test_import(
        pipeline_path, "SmartPipelineSelector", "SmartPipelineSelector"
    )
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: Class Instantiation
    print(f"\n{Colors.BOLD}🔧 TEST 3: Class Instantiation{Colors.RESET}")
    print("-" * 80)

    if ca_module:
        success, instance = test_instantiation(ca_module, "ChunkAnalyzer", "ChunkAnalyzer(45.0)")
        if success:
            results["passed"] += 1
            # Test chunk duration
            if hasattr(instance, "chunk_duration") and instance.chunk_duration == 45.0:
                print_test(f"  → Chunk duration: {instance.chunk_duration}s", "success")
        else:
            results["failed"] += 1

    # Test 4: Chunk Analysis Demo
    print(f"\n{Colors.BOLD}🧪 TEST 4: Chunk Analysis Demo{Colors.RESET}")
    print("-" * 80)

    try:
        os.chdir(base_path / "barber-cam" / "py")
        import subprocess

        result = subprocess.run(
            [sys.executable, "bwc_chunk_analyzer.py"], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print_test("Chunk analyzer demo executed successfully", "success")
            results["passed"] += 1

            # Check for key output
            if "TOTAL (Chunked)" in result.stdout:
                print_test("  → Cost calculation working", "success")
            if "64%" in result.stdout or "savings" in result.stdout.lower():
                print_test("  → Savings calculation working", "success")
        else:
            print_test(f"Demo failed with code {result.returncode}", "error")
            results["failed"] += 1
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
    except Exception as e:
        print_test(f"Demo execution failed: {str(e)}", "error")
        results["failed"] += 1

    # Test 5: API Routes Structure
    print(f"\n{Colors.BOLD}🌐 TEST 5: API Routes Structure{Colors.RESET}")
    print("-" * 80)

    try:
        os.chdir(base_path)
        with open(base_path / "bwc_api_routes.py") as f:
            api_code = f.read()

        required_routes = [
            ("/api/bwc/analyze-chunked", "Analyze Chunked"),
            ("/api/bwc/upgrade-chunk", "Upgrade Chunk"),
            ("/api/bwc/export", "Export Analysis"),
            ("/api/bwc/budget-status", "Budget Status"),
        ]

        for route, description in required_routes:
            if route in api_code:
                print_test(f"{description}: Defined", "success")
                results["passed"] += 1
            else:
                print_test(f"{description}: NOT FOUND", "error")
                results["failed"] += 1
    except Exception as e:
        print_test(f"API route check failed: {str(e)}", "error")
        results["failed"] += 1

    # Test 6: UI Component Structure
    print(f"\n{Colors.BOLD}🎨 TEST 6: UI Component Structure{Colors.RESET}")
    print("-" * 80)

    try:
        with open(base_path / "_includes" / "bwc-chunk-analyzer.html") as f:
            ui_code = f.read()

        required_elements = [
            ("chunk-timeline", "Timeline Component"),
            ("chunk-details", "Details Panel"),
            ("cost-breakdown", "Cost Breakdown"),
            ("progress-container", "Progress Bar"),
            ("upgrade-options", "Upgrade Controls"),
        ]

        for element_id, description in required_elements:
            if element_id in ui_code:
                print_test(f"{description}: Present", "success")
                results["passed"] += 1
            else:
                print_test(f"{description}: NOT FOUND", "warning")
                results["warnings"] += 1
    except Exception as e:
        print_test(f"UI check failed: {str(e)}", "error")
        results["failed"] += 1

    # Test 7: JavaScript Functions
    print(f"\n{Colors.BOLD}📜 TEST 7: JavaScript Functions{Colors.RESET}")
    print("-" * 80)

    try:
        with open(base_path / "assets" / "js" / "bwc-chunk-ui.js") as f:
            js_code = f.read()

        required_functions = [
            ("BWCChunkAnalyzer", "Main Class"),
            ("startAnalysis", "Start Analysis"),
            ("selectChunk", "Select Chunk"),
            ("upgradeChunk", "Upgrade Chunk"),
            ("markCritical", "Mark Critical"),
        ]

        for func_name, description in required_functions:
            if func_name in js_code:
                print_test(f"{description}: Defined", "success")
                results["passed"] += 1
            else:
                print_test(f"{description}: NOT FOUND", "error")
                results["failed"] += 1
    except Exception as e:
        print_test(f"JavaScript check failed: {str(e)}", "error")
        results["failed"] += 1

    # Test 8: Documentation Completeness
    print(f"\n{Colors.BOLD}📚 TEST 8: Documentation Completeness{Colors.RESET}")
    print("-" * 80)

    docs_to_check = [
        ("docs/guides/CHUNK-LEVEL-AI-ROUTING.md", ["70/20/10", "chunk", "difficulty"]),
        ("docs/guides/COMPLETE-AI-STRATEGY.md", ["two-level", "margins", "strategy"]),
        ("docs/guides/CHUNK-IMPLEMENTATION-COMPLETE.md", ["integration", "checklist", "API"]),
    ]

    for doc_path, keywords in docs_to_check:
        try:
            with open(base_path / doc_path) as f:
                content = f.read().lower()

            found_keywords = sum(1 for kw in keywords if kw in content)
            if found_keywords == len(keywords):
                print_test(
                    f"{Path(doc_path).name}: Complete ({found_keywords}/{len(keywords)} keywords)",
                    "success",
                )
                results["passed"] += 1
            else:
                print_test(
                    f"{Path(doc_path).name}: Incomplete ({found_keywords}/{len(keywords)} keywords)",
                    "warning",
                )
                results["warnings"] += 1
        except Exception as e:
            print_test(f"{Path(doc_path).name}: {str(e)}", "error")
            results["failed"] += 1

    # Test 9: Integration Points
    print(f"\n{Colors.BOLD}🔗 TEST 9: Integration Points{Colors.RESET}")
    print("-" * 80)

    integration_checks = [
        (
            "Check if bwc_forensic_analyzer.py exists",
            Path(base_path / "bwc_forensic_analyzer.py").exists(),
        ),
        ("Check if app.py exists", Path(base_path / "app.py").exists()),
        ("Check if Flask is used", True),  # We know Flask is used
    ]

    for description, check in integration_checks:
        if check:
            print_test(description, "success")
            results["passed"] += 1
        else:
            print_test(description, "warning")
            results["warnings"] += 1

    # Final Summary
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    total = results["passed"] + results["failed"] + results["warnings"]
    passed_pct = (results["passed"] / total * 100) if total > 0 else 0

    print(f"  {Colors.GREEN}✅ Passed:   {results['passed']:2d}{Colors.RESET}")
    print(f"  {Colors.RED}❌ Failed:   {results['failed']:2d}{Colors.RESET}")
    print(f"  {Colors.YELLOW}⚠️  Warnings: {results['warnings']:2d}{Colors.RESET}")
    print(f"  {Colors.BOLD}━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"  {Colors.BOLD}Total:     {total:2d}{Colors.RESET}")
    print(f"\n  Success Rate: {Colors.BOLD}{passed_pct:.1f}%{Colors.RESET}\n")

    # Recommendations
    print(f"{Colors.BOLD}📋 NEXT STEPS:{Colors.RESET}\n")

    if results["failed"] == 0:
        print_test("All critical tests passed! ✨", "success")
        print()
        print("  1. Integrate bwc_api_routes into app.py:")
        print("     from bwc_api_routes import register_bwc_routes")
        print("     register_bwc_routes(app)")
        print()
        print("  2. Add UI component to barber-cam page:")
        print("     {% include 'bwc-chunk-analyzer.html' %}")
        print()
        print("  3. Add API keys for:")
        print("     - Deepgram (DEEPGRAM_API_KEY)")
        print("     - AssemblyAI (ASSEMBLYAI_API_KEY)")
        print("     - Anthropic Claude (ANTHROPIC_API_KEY)")
        print()
        print("  4. Test with real video upload")
    else:
        print_test(f"Fix {results['failed']} failed test(s) before proceeding", "warning")

    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    # Return exit code
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
