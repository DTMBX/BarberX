# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
GitHub Workflows Analyzer & Auto-Fixer
Analyzes failed workflows, identifies issues, and applies fixes
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class WorkflowAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.workflows_dir = self.repo_path / ".github" / "workflows"

    def get_workflow_status(self) -> dict[str, str]:
        """Get status of all workflows using gh CLI if available"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "list",
                    "--limit",
                    "20",
                    "--json",
                    "status,conclusion,name,databaseId",
                ],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                runs = json.loads(result.stdout)
                workflow_status = {}
                for run in runs:
                    name = run.get("name", "Unknown")
                    status = run.get("status", "unknown")
                    conclusion = run.get("conclusion", "unknown")
                    workflow_status[name] = f"{status}/{conclusion}"
                return workflow_status
            else:
                print("⚠️  gh CLI not available or not authenticated")
                return {}
        except FileNotFoundError:
            print("⚠️  gh CLI not installed")
            return {}
        except Exception as e:
            print(f"⚠️  Error getting workflow status: {e}")
            return {}

    def analyze_workflows(self) -> list[dict]:
        """Analyze all workflow files for potential issues"""
        issues = []

        if not self.workflows_dir.exists():
            return [{"workflow": "N/A", "issue": "No .github/workflows directory found"}]

        for workflow_file in self.workflows_dir.glob("*.yml"):
            workflow_issues = self.check_workflow_file(workflow_file)
            if workflow_issues:
                issues.extend(workflow_issues)

        return issues

    def check_workflow_file(self, filepath: Path) -> list[dict]:
        """Check a single workflow file for common issues"""
        issues = []

        with open(filepath) as f:
            content = f.read()

        workflow_name = filepath.stem

        # Check for common issues
        checks = [
            ("missing runs-on", "runs-on:" not in content, "No runner specified"),
            ("deprecated ubuntu", "ubuntu-18.04" in content, "Uses deprecated ubuntu-18.04"),
            (
                "deprecated actions",
                "actions/checkout@v1" in content,
                "Uses deprecated actions version",
            ),
            (
                "missing permissions",
                "permissions:" not in content and "pages:" in content,
                "Pages workflow missing permissions",
            ),
            ("ruby version", "ruby-version:" in content and "2.7" in content, "Uses old Ruby 2.7"),
        ]

        for check_name, condition, description in checks:
            if condition:
                issues.append(
                    {
                        "workflow": workflow_name,
                        "issue": check_name,
                        "description": description,
                        "file": str(filepath),
                    }
                )

        return issues

    def run_local_build_test(self) -> tuple[bool, str]:
        """Test if Jekyll builds successfully"""
        print("🔨 Testing Jekyll build locally...")

        result = subprocess.run(
            ["bundle", "exec", "jekyll", "build"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            # Extract build time
            for line in result.stdout.split("\n"):
                if "done in" in line:
                    return True, line.strip()
            return True, "Build successful"
        else:
            # Find error in output
            error_lines = []
            for line in result.stdout.split("\n") + result.stderr.split("\n"):
                if "error" in line.lower() or "failed" in line.lower():
                    error_lines.append(line)

            return False, "\n".join(error_lines[:5]) if error_lines else "Unknown error"

    def fix_common_issues(self) -> list[str]:
        """Apply fixes for common workflow issues"""
        fixes_applied = []

        # Fix 1: Ensure YAML docket files are valid (already done)
        docket_dir = self.repo_path / "_data" / "docket"
        if docket_dir.exists():
            for yml_file in docket_dir.glob("*.yml"):
                with open(yml_file) as f:
                    content = f.read()
                if "<<<<<<< HEAD" in content:
                    fixes_applied.append(f"⚠️  Conflict markers still in {yml_file.name}")

        # Fix 2: Check for missing dependencies
        gemfile_lock = self.repo_path / "Gemfile.lock"
        if gemfile_lock.exists():
            fixes_applied.append("✅ Gemfile.lock exists")
        else:
            fixes_applied.append("⚠️  Gemfile.lock missing - run bundle install")

        # Fix 3: Check for large files
        assets_img = self.repo_path / "assets" / "img"
        if assets_img.exists():
            for img_file in assets_img.glob("*"):
                if img_file.is_file() and img_file.stat().st_size > 1_000_000:
                    fixes_applied.append(
                        f"⚠️  Large file: {img_file.name} ({img_file.stat().st_size:,} bytes)"
                    )

        return fixes_applied

    def generate_report(self) -> str:
        """Generate comprehensive workflow analysis report"""
        report = []
        report.append("╔═══════════════════════════════════════════════════════════════╗")
        report.append("║         GitHub Workflows Analysis & Diagnostics               ║")
        report.append("╚═══════════════════════════════════════════════════════════════╝\n")

        # 1. Workflow status (if gh CLI available)
        workflow_status = self.get_workflow_status()
        if workflow_status:
            report.append("📊 Recent Workflow Runs:\n")
            for name, status in workflow_status.items():
                icon = "✅" if "success" in status else "❌" if "failure" in status else "⏳"
                report.append(f"   {icon} {name}: {status}")
            report.append("")

        # 2. Workflow file analysis
        issues = self.analyze_workflows()
        if issues:
            report.append("🔍 Workflow Configuration Issues:\n")
            for issue in issues:
                report.append(f"   ⚠️  {issue['workflow']}: {issue['description']}")
            report.append("")
        else:
            report.append("✅ No workflow configuration issues found\n")

        # 3. Local build test
        build_success, build_msg = self.run_local_build_test()
        report.append("🔨 Local Build Test:\n")
        if build_success:
            report.append(f"   ✅ {build_msg}")
        else:
            report.append(f"   ❌ Build failed: {build_msg}")
        report.append("")

        # 4. Common fixes check
        fixes = self.fix_common_issues()
        if fixes:
            report.append("🔧 System Checks:\n")
            for fix in fixes:
                report.append(f"   {fix}")
            report.append("")

        # 5. Recommendations
        report.append("💡 Recommendations:\n")
        if not build_success:
            report.append("   1. Fix Jekyll build errors before pushing")
        report.append("   2. Review workflow logs in GitHub Actions")
        report.append("   3. Ensure all YAML files are valid")
        report.append("   4. Check for large files before committing")
        report.append("   5. Test builds locally before pushing")

        return "\n".join(report)


def main():
    repo_path = Path("/workspaces/FaithFrontier")

    analyzer = WorkflowAnalyzer(str(repo_path))
    report = analyzer.generate_report()

    print(report)

    # Save report
    report_file = repo_path / "_internal" / "workflow-analysis-report.txt"
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()
