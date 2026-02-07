# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

#!/usr/bin/env python
"""
Orchestrator Agent Usage Examples
Demonstrates how to use the @orchestrator agent for complex multi-agent tasks
"""

# Example 1: Complete Feature Development
"""
@orchestrator: Add secure batch PDF upload with copyright compliance

Expected Flow:
1. @legal-compliance - Review PDF copyright requirements
2. @database-architect - Design pdf_uploads table
3. @flask-backend - Create upload API with validation
4. @frontend-dev - Build upload interface
5. @security-devops - Add rate limiting and file validation
6. @documentation - Write user guide and API docs
"""

# Example 2: BWC Analysis Pipeline
"""
@orchestrator: Implement end-to-end BWC video analysis with chain of custody

Expected Flow:
1. @legal-compliance - Verify evidence handling requirements
2. @database-architect - Design analysis and audit_log tables
3. @bwc-forensics - Build Whisper transcription pipeline
4. @bwc-forensics - Add SHA-256 integrity verification
5. @flask-backend - Create /api/analyze endpoint
6. @frontend-dev - Build analysis dashboard
7. @security-devops - Secure file storage and access
8. @documentation - Write forensics guide
"""

# Example 3: Production Deployment
"""
@orchestrator: Prepare platform for production deployment

Expected Flow:
1. @legal-compliance - Review export compliance checklist
2. @database-architect - Plan SQLite to PostgreSQL migration
3. @security-devops - Configure SSL certificates
4. @security-devops - Set up CI/CD pipeline
5. @security-devops - Implement secrets management
6. @flask-backend - Add production error handling
7. @documentation - Update deployment checklist
"""

# Example 4: API Development with Compliance
"""
@orchestrator: Create case search API with copyright-safe exports

Expected Flow:
1. @legal-compliance - Define export attribution requirements
2. @database-architect - Add indexes for search performance
3. @flask-backend - Build /api/cases/search endpoint
4. @flask-backend - Integrate export validation
5. @frontend-dev - Create search interface
6. @security-devops - Add rate limiting
7. @documentation - Document API with examples
"""

# Example 5: Performance Optimization
"""
@orchestrator: Optimize platform performance for 10,000+ cases

Expected Flow:
1. @database-architect - Analyze query performance
2. @database-architect - Add database indexes
3. @flask-backend - Implement caching layer
4. @frontend-dev - Add pagination and lazy loading
5. @security-devops - Configure CDN for static assets
6. @documentation - Update performance guidelines
"""

# Example 6: Security Audit
"""
@orchestrator: Perform comprehensive security audit and remediation

Expected Flow:
1. @security-devops - Run security vulnerability scan
2. @legal-compliance - Review data privacy compliance
3. @flask-backend - Fix authentication vulnerabilities
4. @database-architect - Implement row-level security
5. @frontend-dev - Add CSRF protection
6. @security-devops - Configure security headers
7. @documentation - Update security documentation
"""

# Quick Reference Commands

ORCHESTRATOR_PATTERNS = {
    "full_feature": "@orchestrator: [Feature description with compliance requirements]",
    "bug_fix": "@orchestrator: Debug and fix [issue] across all affected layers",
    "optimization": "@orchestrator: Optimize [component] for production scale",
    "deployment": "@orchestrator: Deploy [feature] with full security review",
    "migration": "@orchestrator: Migrate [data/system] with zero downtime",
}

# Agent Capabilities Quick Reference

AGENT_SPECIALTIES = {
    "@legal-compliance": [
        "Copyright compliance review",
        "Export validation",
        "Attribution requirements",
        "Fair use doctrine (200-word limits)",
        "Attorney certification",
    ],
    "@database-architect": [
        "Schema design",
        "Migration scripts",
        "Index optimization",
        "Query performance",
        "SQLite/PostgreSQL planning",
    ],
    "@bwc-forensics": [
        "Video analysis (Whisper, pyannote)",
        "SHA-256 integrity checks",
        "Chain of custody logging",
        "Evidence timeline reconstruction",
        "Forensic report generation",
    ],
    "@flask-backend": [
        "REST API development",
        "Authentication & authorization",
        "Rate limiting",
        "Business logic",
        "Database integration",
    ],
    "@frontend-dev": [
        "Responsive UI components",
        "Accessibility (WCAG 2.1)",
        "Performance optimization",
        "Animation (60fps)",
        "Mobile-first design",
    ],
    "@security-devops": [
        "SSL/TLS configuration",
        "CI/CD pipelines",
        "Secrets management",
        "DDoS protection",
        "Security auditing",
    ],
    "@documentation": [
        "User guides",
        "API documentation",
        "Deployment guides",
        "Attorney-friendly tutorials",
        "Technical specifications",
    ],
}

if __name__ == "__main__":
    print("Evident Orchestrator Agent - Usage Examples")
    print("=" * 60)
    print("\nAvailable Agents:")
    for agent, capabilities in AGENT_SPECIALTIES.items():
        print(f"\n{agent}:")
        for capability in capabilities:
            print(f"  • {capability}")

    print("\n" + "=" * 60)
    print("\nExample Invocation:")
    print(
        """
@orchestrator: Add secure document export with copyright compliance

This will automatically:
1. Review legal requirements
2. Design database schema  
3. Implement backend API
4. Build frontend interface
5. Add security controls
6. Generate documentation
"""
    )
