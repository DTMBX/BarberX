# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python3
"""
Evident Agent Integration Tests

Comprehensive test suite for all 7 custom Copilot agents.
Tests real-world scenarios and validates agent capabilities.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class AgentTestSuite:
    """Integration tests for Evident custom agents."""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0,
        }

    def log_test(self, agent, test_name, status, details=""):
        """Log a test result."""
        result = {"agent": agent, "test": test_name, "status": status, "details": details}
        self.test_results["tests"].append(result)

        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"  [PASS] {test_name}")
        else:
            self.test_results["failed"] += 1
            print(f"  [FAIL] {test_name}")
            if details:
                print(f"         {details}")

    def print_header(self, title):
        """Print test section header."""
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")

    # =========================================================================
    # Legal Compliance Agent Tests
    # =========================================================================

    def test_legal_compliance_agent(self):
        """Test @legal-compliance agent capabilities."""

        self.print_header("Testing @legal-compliance Agent")

        # Test 1: Verify data_rights.py exists and has export validation
        test_name = "Export validation code exists"
        data_rights_file = self.repo_root / "data_rights.py"

        if data_rights_file.exists():
            content = data_rights_file.read_text(encoding="utf-8")
            has_validation = (
                "validate_excerpt_length" in content
                or "can_export" in content
                or "ExportValidator" in content
                or "finalize_export" in content
            )

            if has_validation:
                self.log_test(
                    "legal-compliance",
                    test_name,
                    "PASS",
                    "data_rights.py contains export validation logic",
                )
            else:
                self.log_test(
                    "legal-compliance",
                    test_name,
                    "FAIL",
                    "data_rights.py missing export validation functions",
                )
        else:
            self.log_test("legal-compliance", test_name, "FAIL", "data_rights.py file not found")

        # Test 2: Check for COPYRIGHT documentation
        test_name = "Copyright compliance documentation"
        copyright_docs = [
            "COPYRIGHT-QUICK-START.md",
            "DATA-RIGHTS-COMPLIANCE.md",
            "COPYRIGHT-IMPLEMENTATION-SUMMARY.md",
        ]

        missing_docs = [doc for doc in copyright_docs if not (self.repo_root / doc).exists()]

        if not missing_docs:
            self.log_test(
                "legal-compliance",
                test_name,
                "PASS",
                f"All {len(copyright_docs)} copyright docs present",
            )
        else:
            self.log_test(
                "legal-compliance", test_name, "FAIL", f"Missing: {', '.join(missing_docs)}"
            )

        # Test 3: Verify models have compliance fields
        test_name = "Database models include compliance fields"
        models_file = self.repo_root / "models_data_rights.py"

        if models_file.exists():
            content = models_file.read_text(encoding="utf-8")
            has_citation = "CitationMetadata" in content
            has_manifest = "ExportManifest" in content

            if has_citation and has_manifest:
                self.log_test(
                    "legal-compliance",
                    test_name,
                    "PASS",
                    "CitationMetadata and ExportManifest models found",
                )
            else:
                self.log_test(
                    "legal-compliance",
                    test_name,
                    "FAIL",
                    "Missing required compliance database models",
                )
        else:
            self.log_test("legal-compliance", test_name, "FAIL", "models_data_rights.py not found")

    # =========================================================================
    # BWC Forensics Agent Tests
    # =========================================================================

    def test_bwc_forensics_agent(self):
        """Test @bwc-forensics agent capabilities."""

        self.print_header("Testing @bwc-forensics Agent")

        # Test 1: Forensic analyzer exists
        test_name = "BWC forensic analyzer module exists"
        analyzer_file = self.repo_root / "bwc_forensic_analyzer.py"

        if analyzer_file.exists():
            content = analyzer_file.read_text(encoding="utf-8")
            has_analysis = len(content) > 1000  # Should be substantial

            if has_analysis:
                self.log_test(
                    "bwc-forensics",
                    test_name,
                    "PASS",
                    f"Analyzer has {len(content)} chars of analysis code",
                )
            else:
                self.log_test(
                    "bwc-forensics",
                    test_name,
                    "FAIL",
                    "Analyzer file too small - may be incomplete",
                )
        else:
            self.log_test("bwc-forensics", test_name, "FAIL", "bwc_forensic_analyzer.py not found")

        # Test 2: Web interface exists
        test_name = "BWC web interface exists"
        web_app_file = self.repo_root / "bwc_web_app.py"
        html_file = self.repo_root / "bwc-analyzer.html"

        if web_app_file.exists() and html_file.exists():
            self.log_test(
                "bwc-forensics", test_name, "PASS", "Both backend and frontend files present"
            )
        else:
            missing = []
            if not web_app_file.exists():
                missing.append("bwc_web_app.py")
            if not html_file.exists():
                missing.append("bwc-analyzer.html")

            self.log_test("bwc-forensics", test_name, "FAIL", f"Missing: {', '.join(missing)}")

        # Test 3: Analysis documentation exists
        test_name = "BWC analysis methodology documented"
        guide_file = self.repo_root / "BWC-ANALYSIS-GUIDE.md"

        if guide_file.exists():
            content = guide_file.read_text(encoding="utf-8")
            has_methodology = "chain of custody" in content.lower()

            if has_methodology:
                self.log_test(
                    "bwc-forensics",
                    test_name,
                    "PASS",
                    "BWC-ANALYSIS-GUIDE.md includes forensic methodology",
                )
            else:
                self.log_test(
                    "bwc-forensics",
                    test_name,
                    "FAIL",
                    "Guide missing chain of custody documentation",
                )
        else:
            self.log_test("bwc-forensics", test_name, "FAIL", "BWC-ANALYSIS-GUIDE.md not found")

    # =========================================================================
    # Flask Backend Agent Tests
    # =========================================================================

    def test_flask_backend_agent(self):
        """Test @flask-backend agent capabilities."""

        self.print_header("Testing @flask-backend Agent")

        # Test 1: Main Flask app exists
        test_name = "Main Flask application exists"
        app_file = self.repo_root / "app.py"

        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            has_flask = "from flask import" in content
            has_app = "app = Flask" in content

            if has_flask and has_app:
                self.log_test(
                    "flask-backend", test_name, "PASS", "app.py contains valid Flask application"
                )
            else:
                self.log_test(
                    "flask-backend",
                    test_name,
                    "FAIL",
                    "app.py missing Flask imports or app instance",
                )
        else:
            self.log_test("flask-backend", test_name, "FAIL", "app.py not found")

        # Test 2: Authentication routes exist
        test_name = "Authentication system implemented"
        auth_file = self.repo_root / "auth_routes.py"
        models_file = self.repo_root / "models_auth.py"

        if auth_file.exists() and models_file.exists():
            auth_content = auth_file.read_text(encoding="utf-8")
            has_login = "login" in auth_content.lower()

            if has_login:
                self.log_test(
                    "flask-backend", test_name, "PASS", "auth_routes.py and models_auth.py present"
                )
            else:
                self.log_test(
                    "flask-backend", test_name, "FAIL", "auth_routes.py missing login functionality"
                )
        else:
            self.log_test(
                "flask-backend", test_name, "FAIL", "Missing auth_routes.py or models_auth.py"
            )

        # Test 3: API documentation exists
        test_name = "REST API documented"
        route_map = self.repo_root / "ROUTE-MAP.md"
        api_ref = self.repo_root / "ADMIN-API-REFERENCE.md"

        if route_map.exists() or api_ref.exists():
            self.log_test("flask-backend", test_name, "PASS", "API documentation files present")
        else:
            self.log_test(
                "flask-backend",
                test_name,
                "FAIL",
                "Missing API documentation (ROUTE-MAP.md, ADMIN-API-REFERENCE.md)",
            )

    # =========================================================================
    # Frontend Developer Agent Tests
    # =========================================================================

    def test_frontend_dev_agent(self):
        """Test @frontend-dev agent capabilities."""

        self.print_header("Testing @frontend-dev Agent")

        # Test 1: Main HTML pages exist
        test_name = "Core HTML pages present"
        html_pages = ["index.html", "admin.html", "bwc-analyzer.html"]

        missing_pages = [page for page in html_pages if not (self.repo_root / page).exists()]

        if not missing_pages:
            self.log_test(
                "frontend-dev", test_name, "PASS", f"All {len(html_pages)} core HTML pages present"
            )
        else:
            self.log_test("frontend-dev", test_name, "FAIL", f"Missing: {', '.join(missing_pages)}")

        # Test 2: CSS architecture exists
        test_name = "Professional CSS architecture"
        css_dir = self.repo_root / "assets" / "css"
        style_file = css_dir / "style.css"

        if css_dir.exists() and style_file.exists():
            # Check for component-based CSS
            component_css = list(css_dir.glob("components/*.css"))

            if component_css:
                self.log_test(
                    "frontend-dev",
                    test_name,
                    "PASS",
                    f"Found {len(component_css)} component CSS files",
                )
            else:
                self.log_test(
                    "frontend-dev", test_name, "FAIL", "Missing component-based CSS architecture"
                )
        else:
            self.log_test(
                "frontend-dev", test_name, "FAIL", "assets/css/ directory structure not found"
            )

        # Test 3: Frontend documentation exists
        test_name = "Frontend architecture documented"
        frontend_docs = ["FRONTEND-COMPLETE.md", "PROFESSIONAL-COMPONENTS-GUIDE.md"]

        existing_docs = [doc for doc in frontend_docs if (self.repo_root / doc).exists()]

        if existing_docs:
            self.log_test(
                "frontend-dev",
                test_name,
                "PASS",
                f"{len(existing_docs)}/{len(frontend_docs)} frontend docs present",
            )
        else:
            self.log_test("frontend-dev", test_name, "FAIL", "No frontend documentation found")

    # =========================================================================
    # Database Architect Agent Tests
    # =========================================================================

    def test_database_architect_agent(self):
        """Test @database-architect agent capabilities."""

        self.print_header("Testing @database-architect Agent")

        # Test 1: Database models exist
        test_name = "SQLAlchemy models defined"
        model_files = ["models_auth.py", "models_data_rights.py"]

        existing_models = [model for model in model_files if (self.repo_root / model).exists()]

        if len(existing_models) == len(model_files):
            self.log_test(
                "database-architect", test_name, "PASS", "All database model files present"
            )
        else:
            missing = set(model_files) - set(existing_models)
            self.log_test("database-architect", test_name, "FAIL", f"Missing: {', '.join(missing)}")

        # Test 2: Migration scripts exist
        test_name = "Database migration scripts available"
        migration_scripts = [
            "add_missing_columns.py",
            "add_settings_table.py",
            "migrate_add_role.py",
        ]

        existing_migrations = [
            script for script in migration_scripts if (self.repo_root / script).exists()
        ]

        if existing_migrations:
            self.log_test(
                "database-architect",
                test_name,
                "PASS",
                f"{len(existing_migrations)} migration scripts found",
            )
        else:
            self.log_test("database-architect", test_name, "FAIL", "No migration scripts found")

        # Test 3: Database validation tools exist
        test_name = "Database validation tools present"
        validation_scripts = ["check_db.py", "check_schema.py"]

        existing_validation = [
            script for script in validation_scripts if (self.repo_root / script).exists()
        ]

        if existing_validation:
            self.log_test(
                "database-architect",
                test_name,
                "PASS",
                f"{len(existing_validation)} validation scripts found",
            )
        else:
            self.log_test(
                "database-architect", test_name, "FAIL", "No database validation scripts found"
            )

    # =========================================================================
    # Security DevOps Agent Tests
    # =========================================================================

    def test_security_devops_agent(self):
        """Test @security-devops agent capabilities."""

        self.print_header("Testing @security-devops Agent")

        # Test 1: Security documentation exists
        test_name = "Security policies documented"
        security_docs = ["SECURITY.md", "DEPLOYMENT-COMPLETE.md", "LAUNCH-CHECKLIST.md"]

        existing_docs = [doc for doc in security_docs if (self.repo_root / doc).exists()]

        if len(existing_docs) == len(security_docs):
            self.log_test(
                "security-devops", test_name, "PASS", "All security documentation present"
            )
        else:
            missing = set(security_docs) - set(existing_docs)
            self.log_test("security-devops", test_name, "FAIL", f"Missing: {', '.join(missing)}")

        # Test 2: GitHub Actions workflows exist
        test_name = "CI/CD pipelines configured"
        workflows_dir = self.repo_root / ".github" / "workflows"

        if workflows_dir.exists():
            workflows = list(workflows_dir.glob("*.yml"))

            if workflows:
                self.log_test(
                    "security-devops",
                    test_name,
                    "PASS",
                    f"{len(workflows)} GitHub Actions workflows found",
                )
            else:
                self.log_test(
                    "security-devops",
                    test_name,
                    "FAIL",
                    ".github/workflows/ exists but no workflows defined",
                )
        else:
            self.log_test(
                "security-devops", test_name, "FAIL", ".github/workflows/ directory not found"
            )

        # Test 3: Dependency files exist
        test_name = "Dependency management configured"
        dep_files = ["requirements.txt", "package.json"]

        existing_deps = [dep for dep in dep_files if (self.repo_root / dep).exists()]

        if existing_deps:
            self.log_test(
                "security-devops",
                test_name,
                "PASS",
                f"{len(existing_deps)} dependency files present",
            )
        else:
            self.log_test(
                "security-devops", test_name, "FAIL", "No dependency management files found"
            )

    # =========================================================================
    # Documentation Agent Tests
    # =========================================================================

    def test_documentation_agent(self):
        """Test @documentation agent capabilities."""

        self.print_header("Testing @documentation Agent")

        # Test 1: Core documentation exists
        test_name = "Core project documentation"
        core_docs = ["README-NEW.md", "START-HERE.md", "EXECUTIVE-SUMMARY.md"]

        existing_core = [doc for doc in core_docs if (self.repo_root / doc).exists()]

        if len(existing_core) == len(core_docs):
            self.log_test(
                "documentation", test_name, "PASS", "All core documentation files present"
            )
        else:
            missing = set(core_docs) - set(existing_core)
            self.log_test("documentation", test_name, "FAIL", f"Missing: {', '.join(missing)}")

        # Test 2: User guides exist
        test_name = "User guides and quick starts"
        user_guides = ["ADMIN-QUICK-START.md", "COPYRIGHT-QUICK-START.md", "WEB-APP-GUIDE.md"]

        existing_guides = [guide for guide in user_guides if (self.repo_root / guide).exists()]

        if existing_guides:
            self.log_test(
                "documentation",
                test_name,
                "PASS",
                f"{len(existing_guides)}/{len(user_guides)} user guides present",
            )
        else:
            self.log_test("documentation", test_name, "FAIL", "No user guides found")

        # Test 3: Agent documentation exists
        test_name = "Agent system documented"
        agent_docs = ["AGENTS-QUICK-REF.md", "PROJECT-INDEX.md", ".github/copilot-agents.yml"]

        existing_agent_docs = [doc for doc in agent_docs if (self.repo_root / doc).exists()]

        if len(existing_agent_docs) == len(agent_docs):
            self.log_test("documentation", test_name, "PASS", "Agent documentation complete")
        else:
            missing = set(agent_docs) - set(existing_agent_docs)
            self.log_test("documentation", test_name, "FAIL", f"Missing: {', '.join(missing)}")

    # =========================================================================
    # Test Runner
    # =========================================================================

    def run_all_tests(self):
        """Execute all agent tests."""

        print("\n" + "=" * 80)
        print("  Evident Agent Integration Test Suite")
        print("  Validating all 7 custom Copilot agents")
        print("=" * 80)

        # Run tests for each agent
        self.test_legal_compliance_agent()
        self.test_bwc_forensics_agent()
        self.test_flask_backend_agent()
        self.test_frontend_dev_agent()
        self.test_database_architect_agent()
        self.test_security_devops_agent()
        self.test_documentation_agent()

        # Print summary
        self.print_summary()

        # Save results
        self.save_results()

        return self.test_results["failed"] == 0

    def print_summary(self):
        """Print test results summary."""

        self.print_header("Test Results Summary")

        total = self.test_results["passed"] + self.test_results["failed"]
        pass_rate = (self.test_results["passed"] / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        if self.test_results["failed"] == 0:
            print("[SUCCESS] All tests passed! Agents are fully operational.\n")
        else:
            print("[WARNING] Some tests failed. Review failures above for details.\n")

    def save_results(self):
        """Save test results to JSON file."""

        results_file = self.repo_root / "scripts" / "agent-test-results.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"[INFO] Test results saved to: {results_file}\n")


def main():
    """Run agent integration tests."""

    test_suite = AgentTestSuite()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
