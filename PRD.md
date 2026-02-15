# Planning Guide

A court-defensible, citation-first "Hierarchy of Law" reference platform that delivers simple clarity for ordinary residents while maintaining precision sufficient for legal professionals—every claim traceable to official primary sources with full versioning, provenance tracking, and immutable audit trails.

**Experience Qualities**:
1. **Trustworthy**: Every legal claim is backed by verifiable citations to primary sources with clear separation between authoritative text, neutral explanation, and commentary
2. **Empowering**: Plain-language education demystifies complex legal hierarchies, enabling users to act through lawful civic channels with confidence
3. **Accessible**: Offline-first architecture, keyboard navigation, screen-reader optimization, and mobile-responsive design ensure universal access to constitutional knowledge

**Complexity Level**: Complex Application (advanced functionality, likely with multiple views)
This is a sophisticated educational platform requiring multi-jurisdictional document management, hierarchical browsing, full-text search, guided analysis tools, role-based access control, audit logging, offline synchronization, and careful truthfulness safeguards—far beyond a simple reference viewer.

## Essential Features

### Jurisdiction Selector & Personalized Stack
- **Functionality**: User selects federal + state/territory + optionally county/municipality to build a customized legal hierarchy view
- **Purpose**: Every user needs to see laws that actually govern them, not generic information
- **Trigger**: Onboarding flow and persistent settings with visible jurisdiction badge
- **Progression**: Choose state/territory dropdown → optional local government picker → system assembles "My Stack" showing U.S. Constitution + selected state constitution + local authority derivation → save and persist
- **Success criteria**: User can switch jurisdictions and immediately see applicable constitutional documents; "My Stack" displays hierarchy with citations to home rule provisions

### Constitutional Library (U.S. + 50 States + Territories)
- **Functionality**: Browse and read full text of U.S. Constitution (Articles + 27 Amendments), all 50 state constitutions, and territorial organic acts/constitutions
- **Purpose**: Foundation of legal literacy—primary source access without paywalls or vendor mediation
- **Trigger**: Library tab → Authority Level filter (Federal/State/Territory) → document selection
- **Progression**: Navigate hierarchy tree → select document → view structured outline (articles/amendments) → tap section to read full text with canonical citation → bookmark/highlight → export citation card
- **Success criteria**: Every constitution displays official text with article/section structure; citations are canonical (e.g., "U.S. Const. art. I, § 8, cl. 3"); offline download available

### Full-Text Search Across Sources
- **Functionality**: Search all included documents with filters by authority level, jurisdiction, document type, topic tags, effective date
- **Purpose**: Rapidly locate controlling provisions without manual browsing
- **Trigger**: Search tab or persistent search bar
- **Progression**: Enter query → apply filters (authority level, jurisdiction, date range) → see results with authoritative snippets + citations → "view in context" → jump to full document with highlighted term
- **Success criteria**: Search returns relevant sections within 2 seconds; results show authority level badges; offline search works on downloaded packs

### Hierarchy Map & Supremacy Learning Module
- **Functionality**: Interactive educational content explaining Supremacy Clause, preemption types (express/implied/field/conflict), incorporation, separation of powers, and limits of local authority
- **Purpose**: Users must understand constitutional framework to evaluate conflicts accurately
- **Trigger**: Learn tab → Hierarchy & Preemption topic
- **Progression**: Read plain-language explainer with linked primary text → view visual hierarchy diagram (U.S. Constitution → Federal Statutes/Treaties → Federal Regulations → State Constitutions → State Statutes → Local Ordinances) → explore hypothetical examples clearly labeled "Example" → quiz optional → bookmark key concepts
- **Success criteria**: Every concept links to primary constitutional text (e.g., Supremacy Clause links to U.S. Const. art. VI, cl. 2); examples are labeled and do not constitute advice

### Conflict/Preemption Analyzer (Guided Issue-Spotting)
- **Functionality**: Educational questionnaire that helps users identify potential conflicts between authority levels and generates an issue-spotting report with citations
- **Purpose**: Teach legal reasoning and next steps without providing legal advice or verdicts
- **Trigger**: Analyzer tab → "Start New Analysis"
- **Progression**: Answer guided questions (What authority levels are involved? What is the subject matter? What provisions are you comparing?) → system searches relevant higher-law provisions → generates report showing (a) relevant constitutional/statutory text with citations, (b) potential preemption categories, (c) key factual questions, (d) lawful next steps (contact clerk, attend public meeting, consult attorney, file records request) → prominently display "This is not legal advice" → save/export report
- **Success criteria**: Report includes only verifiable citations; suggests lawful civic pathways; explicitly disclaims legal advice; no fabricated statutes

### Local Law Workspace
- **Functionality**: Three modes—link to official municipal codes, user-submitted PDFs with source proof, curated bulk imports (where licensed)
- **Purpose**: Extend hierarchy to local ordinances while maintaining verification standards
- **Trigger**: Library → Local Law section or user submission flow
- **Progression**: Browse verified local sources → or submit new ordinance (upload PDF + provide official source URL + metadata) → system marks "Unverified/Verified/Official Source" and last-checked date → curators review submissions → approved items appear in search and hierarchy
- **Success criteria**: Every local law item displays verification status badge; unverified items require explicit warning; audit log tracks all additions

### Citation & Export Tools
- **Functionality**: Generate court-defensible citations in multiple formats (Bluebook, ALWD, APA, MLA, Chicago, BibTeX, Plain Text, Court Filing) with complete verification metadata, audit trails, and export to multiple file formats (TXT, MD, HTML, JSON, CSV, BibTeX); organize saved citations with tags and collections powered by AI-driven smart tag suggestions
- **Purpose**: Enable reliable, court-defensible sourcing for journalists, educators, advocates, researchers, and legal professionals with full traceability and verification standards; provide powerful organization tools with intelligent automation to reduce manual effort
- **Trigger**: From any document section → "Export Citation" button or quick export dropdown; from Citation Library → tag management, smart suggestions, and filtering
- **Progression**: Select citation style (Bluebook/ALWD/APA/MLA/Chicago/Court Filing/BibTeX/Plain/JSON) → choose export format (TXT/MD/HTML/JSON/CSV/BibTeX) → configure options (include full text, metadata, verification chain, audit trail, disclaimers) → view AI-powered smart tag suggestions based on content analysis (document type, authority level, constitutional keywords, legal topic detection, practice area identification) → apply suggested tags individually or in batch with confidence indicators (high/medium/low) → optionally browse and select from predefined tag categories (constitutional provisions, legal topics, case types, authority levels, jurisdictions, practice areas, or custom) → assign to collections → preview citation → export to file or copy to clipboard → system generates immutable audit log entry → recipient receives properly formatted citation with verification metadata
- **Success criteria**: Citations match canonical legal citation formats; smart tag suggestions appear within 300ms of opening dialog; suggestion accuracy >70% user acceptance; high-confidence tags prioritized; already-applied tags excluded from suggestions; all exports include verification status, source URLs, last-verified dates, and audit trail IDs; disclaimers clearly state educational purpose and requirement to cite official sources for court filings; batch export supports multiple citations in single file; quick export enables clipboard copy in common formats; all exports are traceable through audit logs; tags enable efficient filtering and organization by topic, case type, or project; tag statistics show usage patterns and trending topics

### Batch Citation Export
- **Functionality**: Export multiple citations simultaneously in a combined file with consistent formatting and complete verification metadata for all items
- **Purpose**: Enable efficient citation management for research projects, briefs, articles, and educational materials requiring multiple legal references
- **Trigger**: From bookmark lists, search results, or library views → "Batch Export" action
- **Progression**: Select multiple sections/provisions → choose citation style and export format → configure options for all items → preview selection count → export combined file with table of contents → system logs batch export action
- **Success criteria**: Batch exports maintain formatting consistency across all citations; combined files include master disclaimer and verification standards note; supports all major formats; preserves individual audit trail IDs for each citation; enables select/deselect all functionality

### Smart Tag Suggestions
- **Functionality**: AI-powered tag recommendation system with dual-mode analysis (Deep LLM vs Quick Keyword) that analyzes citation content, document type, authority level, and text to automatically suggest relevant organizational tags with confidence scoring
- **Purpose**: Reduce manual tagging effort; improve tagging consistency; help users discover relevant tags they might not think of; accelerate citation library organization
- **Trigger**: When adding citations to library; when editing existing citations
- **Progression**: User opens citation dialog → system analyzes section text, document metadata, citation title, and user notes → identifies constitutional keywords (Commerce Clause, Due Process, etc.), legal topics (Preemption, Federalism), practice areas (Immigration, Environmental), case types (Constitutional Challenge), and authority levels → generates 3-8 prioritized suggestions with confidence scores (high/medium/low) and explanatory reasons → user can apply individual tags, apply all, or dismiss → dismissed suggestions won't reappear → applied suggestions increment tag usage statistics
- **Success criteria**: Suggestions appear within 300ms (keyword mode) or 3s (LLM mode); high-confidence tags have >80% acceptance rate; keyword matching identifies 90%+ of common constitutional provisions; document type and authority level tags suggested automatically; users can dismiss unwanted suggestions permanently; bulk apply/dismiss actions work correctly; tag usage statistics reflect applied suggestions; system excludes already-applied tags from suggestions; LLM mode provides semantic understanding beyond keywords; users can toggle between Deep and Quick analysis modes

### Batch Deep Analysis
- **Functionality**: AI-powered batch processing tool that runs deep LLM analysis on multiple citations simultaneously, automatically suggesting tags for entire citation libraries with progress tracking, pause/resume, and comprehensive results review
- **Purpose**: Accelerate initial library setup and periodic maintenance by analyzing dozens or hundreds of citations in minutes rather than hours; provide comprehensive tagging across large citation collections with optional auto-application
- **Trigger**: Citation Library → "Batch Analysis" button when citations are selected
- **Progression**: Select citations for analysis (or select all) → configure options (auto-apply high confidence, skip already tagged) → start batch analysis → system processes citations sequentially with real-time progress updates → pause/resume as needed → review aggregate statistics (completed, failed, skipped, high confidence) → examine per-citation results showing suggested tags, confidence, reasoning, legal concepts, practice areas, constitutional issues → selectively apply tags to individual citations → export complete analysis report with timestamps for audit trail
- **Success criteria**: Processes 50+ citations with >95% success rate; provides pause/resume without data loss; clearly indicates analyzing/completed/failed/skipped status per citation; displays aggregate statistics accurately; enables selective tag application from results; exports court-defensible analysis documentation; auto-apply only affects high-confidence results when enabled; respects skip threshold (3+ existing tags); includes rate limiting to prevent API overload; shows estimated time remaining; processing time ~3 seconds per citation

### Offline Reading Packs
- **Functionality**: Download jurisdictional packs (e.g., "Federal + California + SF County") for offline reading and search
- **Purpose**: Ensure access without connectivity; support privacy-conscious users
- **Trigger**: Settings → Downloads → Select packs
- **Progression**: Choose jurisdiction bundles → download → access Library and Search offline → sync notes/bookmarks on reconnect
- **Success criteria**: Offline search works; downloaded packs under 50MB per state; sync handles conflicts gracefully

### Role-Based Access & Audit Logging
- **Functionality**: Readers (default), Verified Contributors (submit local laws), Curators (approve sources, edit explanations), Admins (manage roles/features)
- **Purpose**: Maintain accuracy and accountability for all editorial actions; provide court-defensible audit trail
- **Trigger**: User role assignment; all curator/admin actions
- **Progression**: Curator edits explanation → system logs who, what, when with immutable timestamp → changes are versioned → admins can review audit trail and rollback → all logs retained for 7+ years
- **Success criteria**: Every source edit is logged immutably; change history is viewable; rollback restores previous version; audit logs exportable for legal proceedings

### Admin Observability Console
- **Functionality**: Enterprise-grade monitoring dashboard that visualizes ingestion throughput, OCR success rates, parsing errors, queue depth, similarity job runtimes, search latency, and historical trends with anomaly detection; exposes structured logs with correlation IDs for end-to-end tracing; monitors background job lifecycles (queued, running, retrying, failed, completed); runs health checks across parsers, search indexes, citation graphs, and databases; verifies tamper-evident ledger integrity using hash-chain validation; provides system bill of materials (SBOM) with dependency versions and vulnerability scanning
- **Purpose**: Demonstrate operational maturity, reliability engineering discipline, and enterprise readiness; enable rapid incident response; provide audit-grade transparency; meet investor/client due diligence expectations
- **Trigger**: Admin user clicks shield icon in header → Admin Console
- **Progression**: View real-time metrics dashboard → inspect historical charts for throughput/latency/errors with anomaly highlights → drill into structured logs filtered by level/component/correlation ID → trace user action end-to-end via correlation chain → monitor background jobs with retry counts and error stacks → run health check suite showing green/yellow/red status badges → verify ledger integrity with hash-chain validation → export SBOM with parser versions, embedding models, runtime versions, and security vulnerability status
- **Success criteria**: Metrics refresh every 10 seconds when auto-refresh enabled; anomaly detection flags spikes in parsing errors or latency; correlation IDs link user actions across components; ledger verification detects tampered events via broken hash links; health checks complete in <2 seconds; SBOM includes all critical dependencies with CVE status; all admin actions are audit-logged with immutable timestamps

### Legal Disclaimer & Compliance System
- **Functionality**: Multi-layered disclaimer system with required user acknowledgment, persistent banners, and court-defensible documentation
- **Purpose**: Protect against unauthorized practice of law claims; establish educational purpose; create legal defensibility
- **Trigger**: Application launch (first-time users); entering Analyzer tool; viewing legal content; exporting citations
- **Progression**: User views comprehensive legal disclaimers → checks acknowledgment boxes for each required disclaimer (not legal advice, educational only, no attorney-client relationship, verify sources, accuracy limitations) → system logs acknowledgment with timestamp → disclaimers persist throughout application → sticky disclaimer appears during sensitive actions
- **Success criteria**: All users acknowledge required disclaimers before access; acknowledgments logged in audit trail; disclaimers visible at all critical interaction points; court-defensible documentation generated

### Source Verification & Provenance Display
- **Functionality**: Three-tier verification status (Official/Verified/Unverified) with full provenance information and court-defensible citations
- **Purpose**: Establish trustworthiness of sources; provide transparency; enable court-defensible usage
- **Trigger**: Viewing any legal document or section; generating citations; curator review workflow
- **Progression**: User views content → verification badge displayed prominently → can expand to see full provenance (official source URL, last checked date, verification method, curator notes) → can generate court-defensible citation with all metadata → warnings displayed for unverified content
- **Success criteria**: Every document displays verification status; unverified content includes prominent warnings; citations include source URL and verification date; audit trail documents all verification actions

## Edge Case Handling

- **Empty Search Results**: Suggest refining filters, link to glossary, offer to report missing content
- **Conflicting Local Submissions**: Curators review; users notified of verification status; duplicates merged with provenance tracking
- **Outdated Constitutional Amendments**: Version/revision tracking with effective dates; historical amendments accessible with "superseded" labels
- **User Tries to Treat Analyzer as Legal Advice**: Prominent disclaimers at start, during questionnaire, and on report; suggest consulting attorney for binding guidance
- **Misinformation or Safety Concerns**: "Report" flow captures issue type, sends to moderation queue, curator reviews and can hide/annotate/remove content with audit trail
- **Offline Sync Conflicts**: Show user conflicting edits to notes/bookmarks; allow merge or keep local/remote version
- **Inaccessible PDFs**: Warn uploaders about accessibility; provide OCR/text extraction tools; require alt-text for images
- **Court Defensibility Challenges**: Comprehensive audit trail, source verification documentation, and disclaimer acknowledgments provide evidence of responsible operation
- **Unauthorized Practice of Law Claims**: Multi-layered disclaimers, educational framing, and explicit no-attorney-client-relationship statements protect against such claims
- **Data Breach or Security Incident**: Immediate containment, user notification within 72 hours, full incident documentation in audit log, and remediation with enhanced controls
- **Tag Management**: Users can create custom tags or select from predefined categories; duplicate tag names prevented; unused tags can be deleted; tag renaming updates all citations
- **Tag Filtering**: Support multiple tag filters with AND logic (citations must have all selected tags); clear visual indication of active filters; one-click filter clearing
- **Collection vs Tag Confusion**: Collections are user-defined groupings (like folders), tags are flexible labels (like sticky notes); citations can belong to multiple collections and have multiple tags

## Design Direction

The design should evoke **institutional trust, clarity, and civic dignity**—the aesthetic of a well-maintained public library or courthouse reading room translated to digital form. The interface must feel authoritative without intimidation, rigorous without sterility, and accessible to users ranging from high school students to municipal staff. Visual language should communicate transparency, non-partisanship, and the gravitas of constitutional law while remaining warm and inviting.

## Color Selection

A palette rooted in **civic blue and warm neutrals** with high-contrast accents for accessibility and clear semantic meaning.

- **Primary Color**: **Deep Civic Blue** `oklch(0.42 0.10 250)` – conveys authority, trust, and the heritage of constitutional governance (blue of government seals)
- **Secondary Colors**: 
  - **Warm Parchment** `oklch(0.94 0.015 85)` – evokes historical documents and creates warmth without distraction
  - **Slate Gray** `oklch(0.55 0.01 260)` – neutral, professional, used for body text and less prominent UI elements
- **Accent Color**: **Amber Alert** `oklch(0.72 0.15 65)` – warm, attention-grabbing for CTAs, warnings ("not legal advice"), and verification status badges
- **Foreground/Background Pairings**:
  - Primary (Deep Civic Blue `oklch(0.42 0.10 250)`): White text `oklch(0.99 0 0)` – Ratio 9.2:1 ✓
  - Background (Warm Parchment `oklch(0.94 0.015 85)`): Slate text `oklch(0.28 0.01 260)` – Ratio 10.1:1 ✓
  - Accent (Amber Alert `oklch(0.72 0.15 65)`): Deep slate text `oklch(0.20 0.01 260)` – Ratio 8.4:1 ✓
  - Muted (Light gray `oklch(0.88 0.005 260)`): Slate text `oklch(0.40 0.01 260)` – Ratio 5.8:1 ✓

## Font Selection

Typography should balance **formal legibility for dense legal text** with **approachable hierarchy** for learning modules—evoking editorial quality and institutional clarity.

- **Primary Typeface**: **Newsreader** (serif) – editorial credibility and excellent readability for long-form constitutional text; brings gravitas without stuffiness
- **Secondary Typeface**: **Space Grotesk** (sans-serif) – clean, modern, excellent for UI labels, navigation, and data-heavy tables; geometric precision suggests accuracy

**Typographic Hierarchy**:
- **H1 (Screen Title)**: Space Grotesk Bold / 32px / -0.02em letter spacing / line-height 1.2
- **H2 (Section Header)**: Space Grotesk Semibold / 24px / -0.01em / line-height 1.3
- **H3 (Subsection)**: Space Grotesk Medium / 18px / normal / line-height 1.4
- **Body (Constitutional Text)**: Newsreader Regular / 17px / normal / line-height 1.65 / generous paragraph spacing
- **Body (UI/Explanations)**: Space Grotesk Regular / 15px / normal / line-height 1.6
- **Caption (Citations, Metadata)**: Space Grotesk Regular / 13px / normal / line-height 1.5 / muted color
- **Button Labels**: Space Grotesk Medium / 15px / uppercase / 0.05em letter spacing

## Animations

Animations should be **deliberate and institutional**, reinforcing hierarchy transitions and document navigation without frivolity. Every motion serves wayfinding or feedback.

- **Hierarchy Navigation**: Gentle slide-in from right when drilling down (Federal → State → Local), slide-out left when returning—reinforces spatial mental model
- **Search Results**: Staggered fade-in (50ms delay per item) to communicate progressive relevance ranking
- **Analyzer Progress**: Smooth progress bar fills with slight elastic easing, celebrates completion with a single subtle pulse
- **Citation Copy**: Button transforms to checkmark with 150ms scale animation, provides satisfying feedback
- **Disclaimer Modals**: Backdrop fades in 200ms, modal scales from 95% to 100% with slight ease-out—commands attention without alarm
- **Offline Sync**: Subtle rotating icon during sync, green checkmark pulse on success
- **Avoid**: Decorative flourishes, bouncing, or distracting looping animations that undermine seriousness

## Component Selection

- **Components**: 
  - **Tabs** (main navigation for mobile; Library/Analyzer/Learn sections)
  - **Accordion** (collapsible constitutional articles and learning modules)
  - **Card** (document preview tiles, citation cards, issue-spotting report sections)
  - **Dialog** (disclaimer modals, confirmation prompts, submission forms)
  - **Select** (jurisdiction picker, filters, citation format chooser)
  - **Input** + **Label** (search bar, analyzer questionnaire forms)
  - **Button** (primary for CTAs, secondary for navigation, ghost for inline actions)
  - **Badge** (authority level indicators: Federal/State/Local, verification status: Verified/Unverified/Official)
  - **Breadcrumb** (showing authority hierarchy for current document: Local Ordinance → County → State Statute → U.S. Constitution)
  - **Scroll-area** (long constitutional text, search results)
  - **Separator** (visual breaks between hierarchy levels, sections)
  - **Alert** (disclaimers, warnings, info messages)
  - **Tooltip** (contextual help for legal terms, icons)
  - **Popover** (quick citation preview, glossary term definitions)
  - **Checkbox** + **Radio-group** (filters, analyzer question selections)
  - **Textarea** (user notes, submission forms)
  - **Switch** (settings toggles: offline mode, analytics opt-in)
  - **Sheet** (mobile drawer for filters, settings)
  - **Command** (power-user search palette with keyboard shortcuts)
  
- **Customizations**: 
  - **Authority Badge**: Custom component using Badge base, color-coded by level (Federal: deep blue, State: medium blue, Local: light blue, Unverified: amber with alert icon)
  - **Citation Card**: Custom Card layout with document title, canonical citation, snippet preview, and share buttons
  - **Hierarchy Tree**: Custom nested Accordion with visual connectors showing parent-child authority relationships
  - **Issue-Spotting Report**: Custom structured output using Cards with section headers, bulleted lists of citations, and footer with disclaimer Alert
  
- **States**: 
  - Buttons: default (solid primary), hover (darker with subtle lift shadow), active (pressed inset), disabled (muted with 50% opacity), focus (2px accent ring)
  - Inputs: default (border), focus (accent border + ring), error (destructive border + helper text), success (green border post-validation)
  - Authority Badges: static (no hover), semantic colors by level
  - Cards: default (subtle border), hover (slight shadow lift for interactive tiles), selected (accent border)
  
- **Icon Selection**: 
  - **MagnifyingGlass** (search)
  - **Books** (library)
  - **ChartBar** (hierarchy/analyzer)
  - **GraduationCap** (learn)
  - **Gear** (settings)
  - **MapPin** (jurisdiction selector)
  - **SealCheck** (verified status)
  - **Warning** (disclaimers, unverified)
  - **ArrowRight** / **ArrowLeft** (navigation, breadcrumb)
  - **DownloadSimple** (offline packs)
  - **BookmarkSimple** (save)
  - **ShareNetwork** (share citation)
  - **Flag** (report misinformation)
  - **User** (profile/roles)
  - **ClockCounterClockwise** (history/audit log)
  
- **Spacing**: 
  - Page padding: `px-4 py-6` mobile, `px-8 py-10` desktop
  - Card internal padding: `p-6`
  - Section gaps: `gap-8` for major sections, `gap-4` for related elements, `gap-2` for tight groups
  - Button padding: `px-6 py-3` primary, `px-4 py-2` secondary
  - Consistent `space-y-4` for vertical stacks in forms and content
  
- **Mobile**: 
  - Bottom tab navigation (Home, Library, Search, Analyzer, Learn) with icons + labels
  - Persistent jurisdiction badge in header (tappable to change)
  - Collapsible filters in Sheet drawer
  - Readable text minimum 16px on mobile (scales up)
  - Touch targets minimum 44x44px
  - Single-column card layouts
  - Sticky search bar
  - Condensed breadcrumbs (show only current + one parent with ellipsis)
