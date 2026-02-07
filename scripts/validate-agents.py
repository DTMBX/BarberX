# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
Evident Custom Copilot Agents - Testing & Validation

This file demonstrates and validates the 7 custom agents created for Evident.
Run validation checks to ensure agents are properly configured.
"""

import json
import os
from pathlib import Path

import yaml


def validate_agents_config():
    """Validate that copilot-agents.yml is properly configured."""

    print("🔍 Validating Evident Custom Copilot Agents Configuration\n")

    # Check if agents file exists
    agents_path = Path(__file__).parent.parent / ".github" / "copilot-agents.yml"

    if not agents_path.exists():
        print("❌ ERROR: .github/copilot-agents.yml not found!")
        return False

    print(f"✅ Found agents configuration at: {agents_path}\n")

    # Load and parse YAML
    try:
        with open(agents_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ ERROR: Failed to parse YAML: {e}")
        return False

    print("✅ Successfully parsed copilot-agents.yml\n")

    # Validate structure
    if "agents" not in config:
        print("❌ ERROR: Missing 'agents' key in configuration")
        return False

    agents = config["agents"]
    expected_agents = [
        "legal-compliance",
        "bwc-forensics",
        "flask-backend",
        "frontend-dev",
        "database-architect",
        "security-devops",
        "documentation",
    ]

    print("📋 Checking for required agents:\n")

    all_present = True
    for agent_name in expected_agents:
        if agent_name in agents:
            agent_config = agents[agent_name]
            print(f"  ✅ {agent_name}")

            # Validate agent structure
            required_keys = ["name", "description", "model", "tools", "instructions"]
            for key in required_keys:
                if key not in agent_config:
                    print(f"     ⚠️  Missing '{key}' field")
                    all_present = False
        else:
            print(f"  ❌ {agent_name} - MISSING")
            all_present = False

    if not all_present:
        print("\n❌ VALIDATION FAILED: Some agents are missing or incomplete")
        return False

    print(f"\n✅ All {len(expected_agents)} agents properly configured\n")

    # Display agent details
    print("🤖 Agent Details:\n")
    for agent_name, agent_config in agents.items():
        print(f"  • {agent_name}")
        print(f"    Name: {agent_config.get('name', 'N/A')}")
        print(f"    Model: {agent_config.get('model', 'N/A')}")
        print(f"    Tools: {len(agent_config.get('tools', []))} tools")
        print(f"    Instructions: {len(agent_config.get('instructions', ''))} chars")
        print()

    return True


def check_key_files():
    """Check if key repository files mentioned in agent instructions exist."""

    print("📁 Checking key files referenced by agents:\n")

    key_files = {
        "Legal Compliance": [
            "data_rights.py",
            "models_data_rights.py",
            "DATA-RIGHTS-COMPLIANCE.md",
            "COPYRIGHT-QUICK-START.md",
        ],
        "BWC Forensics": ["bwc_forensic_analyzer.py", "bwc_web_app.py", "BWC-ANALYSIS-GUIDE.md"],
        "Flask Backend": ["app.py", "auth_routes.py", "models_auth.py", "ROUTE-MAP.md"],
        "Frontend": ["index.html", "assets/css/style.css", "admin.html"],
        "Database": ["models_auth.py", "models_data_rights.py", "add_missing_columns.py"],
        "Security": ["SECURITY.md", "DEPLOYMENT-COMPLETE.md", "LAUNCH-CHECKLIST.md"],
        "Documentation": ["README-NEW.md", "ADMIN-QUICK-START.md", "WEB-APP-GUIDE.md"],
    }

    repo_root = Path(__file__).parent.parent

    all_exist = True
    for category, files in key_files.items():
        print(f"  {category}:")
        for file_path in files:
            full_path = repo_root / file_path
            if full_path.exists():
                print(f"    ✅ {file_path}")
            else:
                print(f"    ❌ {file_path} - MISSING")
                all_exist = False
        print()

    return all_exist


def generate_usage_examples():
    """Generate example prompts for each agent."""

    print("💡 Example Usage in GitHub Copilot Chat:\n")

    examples = {
        "@legal-compliance": [
            "Review this export function for copyright violations",
            "Check if this PDF export complies with fair use doctrine",
            "Validate attribution requirements for this case law citation",
            "Ensure this database schema prevents Westlaw content republishing",
        ],
        "@bwc-forensics": [
            "Implement SHA-256 hashing for video file integrity",
            "Add Whisper AI transcription to this video analysis pipeline",
            "Create chain of custody logging for evidence files",
            "Build timeline reconstruction from multiple BWC sources",
        ],
        "@flask-backend": [
            "Add role-based access control to this API endpoint",
            "Create bulk export endpoint with attorney certification",
            "Implement rate limiting on case search API",
            "Integrate copyright compliance into PDF export route",
        ],
        "@frontend-dev": [
            "Create responsive case list component with pagination",
            "Build accessible file upload interface with drag-drop",
            "Optimize hero animation to 60fps GPU-accelerated",
            "Design mobile-first evidence gallery with keyboard nav",
        ],
        "@database-architect": [
            "Design schema for multi-file BWC case management",
            "Create migration script to add export_manifests table",
            "Add indexes to optimize case search queries",
            "Plan SQLite to PostgreSQL migration strategy",
        ],
        "@security-devops": [
            "Configure SSL certificate for production deployment",
            "Implement secrets management with environment variables",
            "Set up GitHub Actions CI/CD pipeline for automated testing",
            "Add rate limiting and DDoS protection to public endpoints",
        ],
        "@documentation": [
            "Write 5-minute quick start guide for attorneys",
            "Document REST API endpoints with curl examples",
            "Create attorney-friendly user guide for BWC analyzer",
            "Update deployment checklist with new compliance steps",
        ],
    }

    for agent, prompts in examples.items():
        print(f"{agent}:")
        for i, prompt in enumerate(prompts, 1):
            print(f"  {i}. {prompt}")
        print()


def main():
    """Run all validation checks."""

    print("=" * 80)
    print("Evident Custom Copilot Agents - Validation Suite")
    print("=" * 80)
    print()

    # Validate configuration
    config_valid = validate_agents_config()

    # Check key files
    files_exist = check_key_files()

    # Generate usage examples
    generate_usage_examples()

    # Final summary
    print("=" * 80)
    print("📊 Validation Summary")
    print("=" * 80)
    print()

    if config_valid and files_exist:
        print("✅ All validation checks passed!")
        print("✅ Agents are properly configured and ready to use")
        print()
        print("🚀 Next Steps:")
        print("  1. Open GitHub Copilot Chat in your IDE")
        print("  2. Type @ and select an agent (e.g., @legal-compliance)")
        print("  3. Ask your question or request code changes")
        print()
        return True
    else:
        print("❌ Validation failed - some issues need to be resolved")
        if not config_valid:
            print("  • Fix agents configuration in .github/copilot-agents.yml")
        if not files_exist:
            print("  • Ensure all referenced files exist in the repository")
        print()
        return False


if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed. Installing...")
        import subprocess

        subprocess.check_call(["pip", "install", "pyyaml"])
        import yaml

    success = main()
    exit(0 if success else 1)
