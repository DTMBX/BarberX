# Civics Stack

A court-defensible, educational platform for understanding the hierarchy of U.S. law through accurate, cited primary sources and neutral frameworks.

## 🏛️ Mission

Civics Stack empowers everyday citizens, advocates, journalists, and civic workers to understand constitutional law and legal hierarchies through verified primary sources—promoting informed, lawful civic engagement and due process.

## ⚖️ Court Defensibility & Legal Compliance

**This application is designed with strict court-defensible standards:**

### Legal Safeguards

- **Not Legal Advice**: Comprehensive disclaimer system with required user acknowledgment
- **Educational Purpose**: Clear framing as educational tool, not legal consultation
- **No Attorney-Client Relationship**: Explicit statements preventing any legal relationship
- **Source Verification**: Three-tier verification system (Official/Verified/Unverified)
- **Immutable Audit Trail**: All actions logged with 7-year retention for legal compliance
- **Court-Defensible Citations**: Generated citations include full provenance and verification dates

### Compliance Features

✓ Multi-layered disclaimers at all critical interaction points  
✓ User acknowledgment required before access  
✓ Prominent verification status badges on all content  
✓ Source URLs and last-checked dates for all documents  
✓ Audit logging of all user actions and content changes  
✓ Role-based access control with least privilege  
✓ Content integrity checks and verification workflows  
✓ Privacy-by-design architecture  

See [COMPLIANCE.md](./COMPLIANCE.md) for complete documentation.

## 🔒 Security & Privacy

- **Local-First**: User data stored locally using secure KV storage
- **No Third-Party Services**: All persistence uses built-in Spark runtime APIs
- **Minimal Data Collection**: Only essential data collected
- **No PII Sale**: Explicit policy against selling personal information
- **Private Notes**: User bookmarks and notes remain on device
- **Opt-In Analytics**: Analytics disabled by default

## 🎯 Key Features

### Verified Legal Content

- **U.S. Constitution**: Complete text with all 27 amendments
- **State Constitutions**: All 50 states plus territories
- **Federal Statutes**: Key U.S. Code references
- **Treaties**: Index of international agreements
- **Local Ordinances**: User-submitted with verification workflow

### Educational Tools

- **Hierarchy Map**: Visual explanation of legal authority levels
- **Conflict Analyzer**: Guided issue-spotting tool (educational only)
- **Learning Modules**: Plain-language civics education
- **Citation Generator**: Court-defensible citation formats

### Accountability Features

- **Audit Log Viewer**: Complete action history for administrators
- **Source Verification Display**: Transparent provenance information
- **Version Control**: Track changes to all legal content
- **Curator Workflow**: Review and approval process for submissions

## 🚀 Getting Started

1. **Accept Disclaimers**: First-time users must acknowledge required legal disclaimers
2. **Select Jurisdiction**: Choose your state/territory to personalize content
3. **Explore Library**: Browse constitutional texts and statutes
4. **Use Analyzer**: Educational tool for understanding potential conflicts
5. **Bookmark Content**: Save important sections for future reference

## 📋 User Roles

### Reader (Default)
- View all public content
- Create bookmarks and notes
- Use analyzer tool
- Export citations

### Verified Contributor
- All Reader permissions
- Submit local ordinances
- Provide source documentation

### Curator
- All Contributor permissions
- Approve/reject submissions
- Edit neutral explanations
- Set verification status
- Manage citations

### Administrator
- All Curator permissions
- View audit logs
- Manage user roles
- Configure system settings
- **Access Admin Observability Console** (owner-only)

## 🛡️ Admin Observability Console (Owner-Only)

**For platform owners**, Civics Stack includes an enterprise-grade admin console demonstrating operational maturity and governance awareness:

### Access
- Shield icon appears in header for owner users
- Click to open `/admin-observability` dashboard

### Features

#### Real-Time Metrics
- Ingestion throughput monitoring
- OCR success rate tracking
- Parsing error detection
- Queue depth visibility
- Search latency (p95)
- Job runtime analytics

#### Structured Logging
- Correlation ID tracing
- Component-level filtering
- Error stack traces
- End-to-end request tracking

#### Health Monitoring
- Parser validation checks
- Search index consistency
- Citation graph integrity
- Database connection health
- Network latency monitoring

#### Tamper-Evident Ledger
- Hash-chain verification
- Cryptographic integrity checks
- Audit event validation
- Broken link detection

#### System Transparency
- Bill of Materials (SBOM)
- Dependency tracking
- Version monitoring
- Security vulnerability scanning

### Why This Matters
The Admin Console demonstrates:
- **Governance Awareness**: Policy enforcement, compliance tracking
- **Operational Discipline**: Real metrics, not mock dashboards
- **Reliability Engineering**: Comprehensive health checks
- **Cryptographic Integrity**: Tamper-evident audit trails
- **Enterprise Readiness**: SBOM, dependency transparency

See [ADMIN_OBSERVABILITY.md](./ADMIN_OBSERVABILITY.md) for complete technical documentation.

## ⚠️ Important Disclaimers

### Not Legal Advice

**THIS APPLICATION PROVIDES EDUCATIONAL INFORMATION ONLY AND DOES NOT CONSTITUTE LEGAL ADVICE.** The information provided is for general educational and informational purposes only. It is not intended to be, and should not be relied upon as, legal advice. No attorney-client relationship is created by using this application.

### For Court Use

**Always cite directly to official government publications when preparing court documents.** This educational platform is not admissible as legal authority. Consult the Bluebook or your jurisdiction's citation rules for proper legal citation formats.

### Verify All Sources

While we maintain strict verification standards, users are responsible for confirming all information through official government sources before relying on it. Laws, regulations, and constitutional provisions may change.

### Consult an Attorney

For legal advice specific to your situation, you must consult with a licensed attorney in your jurisdiction. This tool helps you understand legal concepts but cannot replace professional legal counsel.

## 🏗️ Architecture

### Technology Stack

- **Frontend**: React 19 with TypeScript
- **Styling**: Tailwind CSS v4 with custom civic theme
- **Components**: shadcn/ui v4 component library
- **State Management**: React hooks with useKV for persistence
- **Icons**: Phosphor Icons
- **Typography**: Space Grotesk (sans) + Newsreader (serif)

### Data Persistence

All data is stored using the Spark runtime KV storage API:
- User settings and preferences
- Bookmarks and personal notes
- Disclaimer acknowledgments
- Audit logs (immutable)
- Verification records

### Audit Trail

Every significant action is logged:
- User views, exports, or bookmarks content
- Curators approve or reject submissions
- Administrators change roles or settings
- Content is created, updated, or verified

Logs include:
- User ID and role
- Action type and timestamp
- Entity affected
- Before/after snapshots
- IP address and user agent (when available)

## 📚 Key Documents

- **[COMPLIANCE.md](./COMPLIANCE.md)**: Court defensibility and security measures
- **[PRD.md](./PRD.md)**: Product requirements and design decisions
- **[SECURITY.md](./SECURITY.md)**: Security vulnerability reporting

## 🎨 Design Philosophy

### Institutional Trust

The interface evokes the gravitas of constitutional law while remaining accessible:
- Civic blue primary color conveying governmental authority
- Serif typography (Newsreader) for legal text readability
- Clean sans-serif (Space Grotesk) for navigation and UI
- Generous whitespace and clear hierarchy
- High-contrast color pairings (WCAG AA compliant)

### Educational Clarity

Every interaction reinforces the educational purpose:
- Prominent disclaimers at critical points
- Clear verification status badges
- Direct links to official sources
- Plain-language explanations alongside legal text
- Guided workflows with contextual help

## 🔄 Content Update Workflow

1. **Submission**: User provides document and official source
2. **Automated Check**: System verifies required fields
3. **Curator Review**: Human verification against primary sources
4. **Status Assignment**: Official/Verified/Unverified based on evidence
5. **Audit Logging**: All actions recorded immutably
6. **Re-verification**: Periodic checks (90-day recommended interval)

## 🛡️ Truthfulness Safeguards

- **No Fabrication**: Strict prohibition on invented citations
- **Citations Required**: All claims backed by verifiable sources
- **Clear Labeling**: Separation of primary text, explanation, and user content
- **Confidence Indicators**: Prominent verification status display
- **Source Registry**: Public documentation of data origins
- **Report Flow**: Users can flag misinformation for curator review

## 📊 Compliance Standards

### Required Fields for All Documents

- Canonical citation (Bluebook-style)
- Official source URL
- Verification status
- Last checked date
- Document title and type
- Authority level
- Jurisdiction

### Verification Intervals

- **U.S. Constitution**: Continuous monitoring
- **State Constitutions**: Quarterly review
- **Federal Statutes**: Annual review
- **Treaties**: Semi-annual review
- **Local Ordinances**: 90-day re-verification

## 🤝 Contributing

### Content Contributions

Users can submit local ordinances and corrections:
1. Provide official source URL
2. Upload document or text
3. Include verification evidence
4. Curator reviews submission
5. Approved content marked as Verified

### Code Contributions

This is an educational platform. All contributions should:
- Maintain court-defensible standards
- Preserve audit trail integrity
- Include appropriate disclaimers
- Follow accessibility guidelines
- Not compromise source verification

## 📞 Contact & Support

For questions about:
- **Security Issues**: See SECURITY.md
- **Content Verification**: [To be configured]
- **Legal Compliance**: See COMPLIANCE.md
- **General Inquiries**: [To be configured]

## 📜 License

MIT License - See LICENSE file for details

Copyright GitHub, Inc.

---

**Built with Spark** | **Designed for Civic Engagement** | **Court-Defensible by Design**

Remember: This is an educational tool. Always verify information through official sources and consult qualified legal professionals for advice about your specific situation.
