# Orchestrator Agent Quick Reference

## 🎯 What is the Orchestrator?

The **@orchestrator** agent is your master coordinator that automatically runs all specialized agents in the optimal order for complex tasks. Instead of manually invoking each agent, ask the orchestrator and it handles the coordination.

## 🚀 Quick Start

### Simple Invocation

```
@orchestrator: Add batch PDF upload feature
```

The orchestrator will automatically:

1. ✅ Check legal compliance requirements (@legal-compliance)
2. ✅ Design database schema (@database-architect)
3. ✅ Build backend API (@flask-backend)
4. ✅ Create UI components (@frontend-dev)
5. ✅ Add security controls (@security-devops)
6. ✅ Generate documentation (@documentation)

## 📋 Common Use Cases

### Feature Development

```
@orchestrator: Create user authentication system with role-based access
@orchestrator: Add BWC video analysis with chain of custody
@orchestrator: Build case search API with copyright-safe exports
```

### Bug Fixes

```
@orchestrator: Fix upload validation error in batch processor
@orchestrator: Debug authentication issue affecting admin panel
```

### Performance Optimization

```
@orchestrator: Optimize database queries for 10,000+ cases
@orchestrator: Improve frontend loading time to under 2 seconds
```

### Deployment & Security

```
@orchestrator: Prepare platform for production deployment
@orchestrator: Perform comprehensive security audit
@orchestrator: Set up CI/CD pipeline with automated testing
```

## 🔄 Execution Phases

The orchestrator always follows this order:

### Phase 1: Foundation (Legal & Data)

- **@legal-compliance** - Copyright, compliance, legal requirements
- **@database-architect** - Schema design, migrations, indexes

### Phase 2: Core Implementation

- **@bwc-forensics** - Video analysis, forensics, evidence handling
- **@flask-backend** - API endpoints, business logic, authentication

### Phase 3: User Interface

- **@frontend-dev** - UI components, accessibility, performance

### Phase 4: Security & Operations

- **@security-devops** - Security, deployment, CI/CD

### Phase 5: Documentation

- **@documentation** - Guides, API docs, deployment instructions

## 🎓 Advanced Usage

### Multi-Step Complex Tasks

```
@orchestrator: Implement the following:
1. Secure batch PDF upload
2. Automatic copyright validation
3. Export for attorney review
4. Audit trail for all downloads
```

### With Specific Requirements

```
@orchestrator: Add case search API with these requirements:
- Must comply with 200-word fair use limits
- Support pagination for 50,000+ cases
- Include role-based access control
- Generate attribution manifests
- Deploy with rate limiting
```

### Cross-Domain Features

```
@orchestrator: Build BWC evidence timeline that:
-- Syncs multiple video sources
-- Validates SHA-256 checksums
-- Exports to PDF prepared for legal review
-- Includes full chain of custody
```

## 📊 Agent Specialties

| Agent                   | Expertise                                       |
| ----------------------- | ----------------------------------------------- |
| **@legal-compliance**   | Copyright, OPRA, export validation, attribution |
| **@database-architect** | Schema design, migrations, performance          |
| **@bwc-forensics**      | Video analysis, Whisper, chain of custody       |
| **@flask-backend**      | REST APIs, auth, rate limiting, business logic  |
| **@frontend-dev**       | UI/UX, accessibility, responsive design         |
| **@security-devops**    | SSL, CI/CD, secrets, deployment                 |
| **@documentation**      | User guides, API docs, tutorials                |

## ✅ Validation & Testing

After each phase, the orchestrator verifies:

- ✅ Code compiles without errors
- ✅ Tests pass (if applicable)
- ✅ No security vulnerabilities
- ✅ Compliance requirements met
- ✅ Documentation is accurate

## 🛑 When to Use Individual Agents

Use **individual agents** for:

- Simple, single-domain tasks
- Quick fixes in one area
- Specific expertise questions

Use **@orchestrator** for:

- Complex, multi-step features
- Cross-domain implementations
- Production deployments
- Full-stack development

## 📝 Examples from Your Platform

### Completed by Orchestrator

```
✅ Batch PDF Upload System
   - Legal compliance review
   - PDFUpload database model
   - /api/upload/pdf/batch endpoint
   - batch-pdf-upload.html interface
   - pdf-management.html admin panel
   - Migration script
   - Documentation
```

### Next Tasks for Orchestrator

```
@orchestrator: Implement BWC analysis dashboard with:
- Real-time transcription progress
- Speaker identification display
- Discrepancy highlighting
- Export to multiple formats
- Full audit trail
```

## 🔧 Troubleshooting

**Q: Agent skipped a phase?**
A: The orchestrator only invokes agents when their expertise is needed for the task.

**Q: Task failed mid-execution?**
A: The orchestrator stops at the failure point. Fix the issue and ask it to continue from that phase.

**Q: Want to skip a phase?**
A: Explicitly state it: "@orchestrator: Add feature X (skip documentation phase)"

## 🎯 Best Practices

1. **Be Specific**: Provide clear requirements upfront
2. **Include Context**: Mention compliance needs, performance targets
3. **Trust the Process**: Let the orchestrator handle sequencing
4. **Review Output**: Verify each phase before deploying
5. **Iterate**: Orchestrator can refine based on feedback

## 📚 Real-World Example

**Request:**

```
@orchestrator: Add export feature for case files with copyright compliance
```

**Orchestrator Executes:**

```
Phase 1: Foundation
→ @legal-compliance: Review Westlaw/Lexis export rules
   ✅ Confirmed: 200-word limit, citation required, attribution manifest

→ @database-architect: Design export_logs and export_manifests tables
   ✅ Created migration script, added indexes

Phase 2: Core Implementation
→ @flask-backend: Create /api/export/case endpoint
   ✅ Added copyright validation
   ✅ Implemented attorney certification
   ✅ Generate attribution manifests

Phase 3: User Interface
→ @frontend-dev: Build export-case.html interface
   ✅ Added format selection (PDF, DOCX, JSON)
   ✅ Attorney certification checkbox
   ✅ Download progress indicator

Phase 4: Security & Deployment
→ @security-devops: Add rate limiting to export endpoint
   ✅ Configured 10 exports per hour
   ✅ Added audit logging

Phase 5: Documentation
→ @documentation: Write export guide for attorneys
   ✅ Created EXPORT-GUIDE.md
   ✅ Documented API endpoint
   ✅ Added compliance checklist

✅ Feature Complete: Secure, compliant case export system ready
```

--

**Remember**: The orchestrator is your AI project manager. Describe what you want to achieve, and it coordinates the specialist agents to make it happen professionally and compliantly.
