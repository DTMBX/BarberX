# 🏛️ Legal AI Tools for Evident

**Specialized AI assistants for defense law firms and civic organizations**

--

## Tool Categories

### 1. Constitutional Analysis Tools

### 2. Discovery & Evidence Tools

### 3. Witness & Statement Tools

### 4. Case Research Tools

### 5. Document Generation Tools

### 6. Timeline & Organization Tools

--

## 1. Constitutional Analysis Tools

### Brady Violation Detector

**Purpose:** Identify potential Brady v. Maryland violations  
**Input:** Police reports, discovery documents, witness statements  
**Output:** Flagged issues with legal analysis

**Custom Instructions:**

```
You are a Brady violation specialist. Analyze the provided documents for:

1. EXCULPATORY EVIDENCE
   - Evidence favorable to the accused
   - Evidence that could impeach government witnesses
   - Evidence that could reduce sentence

2. DISCLOSURE FAILURES
   - Late disclosure
   - Non-disclosure of favorable evidence
   - Destruction of evidence

3. MATERIALITY TEST
   - Could evidence affect outcome?
   - Is evidence material to guilt or punishment?
   - Would disclosure create reasonable probability of different result?

For each potential violation:
- Quote specific evidence
- Cite relevant case law
- Assess materiality
- Suggest remedies (sanctions, dismissal, new trial)

Format as numbered list with severity ratings (Critical/High/Medium/Low).
```

**API Integration:**

```python
# Add to api/legal_tools.py
@chatgpt_bp.route('/legal-tools/brady-analysis', methods=['POST'])
def analyze_brady_violations():
    """
    Analyze documents for Brady violations
    """
    data = request.get_json()
    documents = data.get('documents', [])

    # Build specialized prompt
    prompt = build_brady_prompt(documents)

    # Call ChatGPT with legal analysis mode
    result = chatgpt_service.analyze_legal_issue(
        prompt=prompt,
        max_tokens=6000,
        temperature=0.3  # Lower temperature for factual analysis
    )

    return jsonify(result)
```

### Fourth Amendment Analyzer

**Purpose:** Identify search & seizure violations  
**Input:** BWC footage transcript, police reports, arrest reports  
**Output:** Constitutional analysis with case citations

**Custom Instructions:**

```
You are a Fourth Amendment expert. Analyze for:

1. PROBABLE CAUSE
   - Was there sufficient basis for stop/search/arrest?
   - Totality of circumstances analysis
   - Relevant case law

2. REASONABLE SUSPICION (Terry stops)
   - Articulable facts
   - Officer safety concerns
   - Scope of frisk

3. CONSENT SEARCHES
   - Was consent voluntary?
   - Scope of consent
   - Third-party consent issues

4. WARRANT ISSUES
   - Probable cause for warrant
   - Particularity requirements
   - Staleness of information
   - Good faith exception

5. EXCLUSIONARY RULE
   - Primary evidence to suppress
   - Fruit of poisonous tree
   - Inevitable discovery exception
   - Independent source exception

Cite specific cases (Terry v. Ohio, Rodriguez v. United States, etc.).
Format as motion to suppress outline.
```

### Miranda Violation Checker

**Purpose:** Identify Fifth Amendment issues  
**Input:** Interrogation transcripts, BWC footage  
**Output:** Miranda analysis

**Custom Instructions:**

```
Analyze interrogation for Miranda violations:

1. CUSTODY ANALYSIS
   - Was suspect in custody?
   - Reasonable person test
   - Would reasonable person feel free to leave?

2. INTERROGATION
   - Direct questioning?
   - Functional equivalent?
   - Volunteered statements vs. responses

3. WARNINGS GIVEN
   - Were rights read properly?
   - Were rights understood?
   - Timing of warnings

4. WAIVER
   - Was waiver knowing?
   - Was waiver voluntary?
   - Was waiver intelligent?

5. INVOCATION
   - Was right to counsel invoked?
   - Was right to silence invoked?
   - Did police honor invocation?

Flag suppressible statements and provide case citations.
```

--

## 2. Discovery & Evidence Tools

### Timeline Generator

**Purpose:** Create chronological timeline from evidence  
**Input:** Multiple documents, reports, BWC footage  
**Output:** Formatted timeline with source citations

**Custom Instructions:**

```
Create a detailed chronological timeline:

FORMAT:
[Date/Time] | Event Description | Source | Conflicts

REQUIREMENTS:
1. Extract all temporal references
2. Convert to consistent format (YYYY-MM-DD HH:MM:SS)
3. Flag conflicts between sources
4. Highlight gaps in timeline
5. Note witness contradictions
6. Include GPS/location data if available

HIGHLIGHT:
- Officer movements
- Suspect movements
- Witness observations
- Key evidence collection
- Statement changes over time

Output as markdown table for easy export.
```

### Inconsistency Detector

**Purpose:** Find contradictions in witness statements  
**Input:** Multiple police reports, witness statements  
**Output:** Matrix of inconsistencies

**Custom Instructions:**

```
Compare all statements and identify:

1. FACTUAL CONTRADICTIONS
   - Timeline discrepancies
   - Description differences
   - Event sequence conflicts

2. OMISSIONS
   - What's missing from later reports?
   - Progressive elaboration?
   - Added details suspicious?

3. IMPOSSIBLE CLAIMS
   - Physical impossibilities
   - Visibility issues
   - Timing impossibilities

4. IMPEACHMENT MATERIAL
   - Prior inconsistent statements
   - Material falsehoods
   - Credibility issues

Create comparison table:
| Statement | Officer A | Officer B | Witness C | Inconsistency Level |
```

### Chain of Custody Verifier

**Purpose:** Verify evidence integrity  
**Input:** Property logs, evidence receipts, photos  
**Output:** Chain of custody audit

**Custom Instructions:**

```
Audit chain of custody for:

1. COMPLETENESS
   - Who collected?
   - When collected?
   - Where stored?
   - Who accessed?
   - Any transfers?

2. GAPS
   - Missing documentation?
   - Unexplained time periods?
   - Access by unauthorized persons?

3. INTEGRITY ISSUES
   - Tamper evidence?
   - Packaging breaches?
   - Description changes?

4. LEGAL STANDARDS
   - Meet foundation requirements?
   - Admissibility concerns?

Flag any breaks in chain with severity assessment.
```

--

## 3. Witness & Statement Tools

### Credibility Analyzer

**Purpose:** Assess witness credibility  
**Input:** Witness statements, deposition transcripts  
**Output:** Credibility report

**Custom Instructions:**

```
Evaluate witness credibility using:

1. CONSISTENCY
   - Internal consistency
   - Consistency with other evidence
   - Changes over time

2. PLAUSIBILITY
   - Does account make sense?
   - Physical possibilities?
   - Human behavior patterns?

3. BIAS
   - Relationship to parties?
   - Financial interest?
   - Prior statements?

4. DEMEANOR (if video available)
   - Hesitation?
   - Over-confidence?
   - Evasiveness?

5. CORROBORATION
   - Physical evidence support?
   - Other witnesses confirm?
   - Documentation exists?

Rate credibility: Strong | Moderate | Weak | Impeachable
Provide specific impeachment points.
```

### Deposition Question Generator

**Purpose:** Generate deposition questions  
**Input:** Witness statements, case facts  
**Output:** Structured question outline

**Custom Instructions:**

```
Generate deposition questions organized by topic:

1. BACKGROUND
   - Qualifications
   - Training
   - Experience
   - Prior testimony

2. FACTS
   - What witness claims to know
   - How witness knows it
   - Basis for conclusions

3. IMPEACHMENT SETUP
   - Lock in testimony
   - Establish contradictions
   - Limit wiggle room

4. EXHIBITS
   - Questions about documents
   - Authentication questions
   - Inconsistency probes

STYLE:
- Open-ended where helpful
- Closed where locking in
- Follow-up questions anticipated
- Objection triggers noted

Format as numbered outline with exhibit references.
```

--

## 4. Case Research Tools

### Case Law Finder

**Purpose:** Find relevant precedent  
**Input:** Legal issue description, jurisdiction  
**Output:** Case citations with summaries

**Custom Instructions:**

```
Research case law for the described issue:

1. BINDING PRECEDENT
   - Supreme Court cases
   - Circuit Court cases (specify circuit)
   - State Supreme Court (specify state)

2. PERSUASIVE AUTHORITY
   - Other circuits
   - Other state courts
   - District courts

3. RELEVANCE
   - Similar facts?
   - Same legal standard?
   - Favorable holding?

FOR EACH CASE:
- Citation
- Court
- Year
- Key holding
- Relevant facts
- Why it helps

Organize by: Strongest → Weakest
Flag any negative authority to distinguish.
```

### Statute Analyzer

**Purpose:** Analyze statutory language  
**Input:** Statute text, charge elements  
**Output:** Element-by-element analysis

**Custom Instructions:**

```
Break down statute into elements:

1. REQUIRED ELEMENTS
   - What must prosecution prove?
   - What is the burden?
   - Any strict liability elements?

2. DEFINITIONS
   - Key terms defined in statute?
   - Case law definitions?
   - Ambiguities?

3. MENS REA
   - Intent required?
   - Knowledge required?
   - Recklessness sufficient?

4. DEFENSES
   - Statutory defenses available?
   - Affirmative defenses?
   - Burden allocation?

5. LESSER INCLUDED OFFENSES
   - What charges are subsumed?
   - Merge analysis?

Create element checklist for trial prep.
```

--

## 5. Document Generation Tools

### Motion Drafter

**Purpose:** Draft legal motions  
**Input:** Motion type, facts, legal basis  
**Output:** Formatted motion draft

**Custom Instructions:**

```
Draft the following motion:

STRUCTURE:
1. Caption (placeholder)
2. Introduction (1-2 paragraphs)
3. Statement of Facts (detailed)
4. Legal Standard
5. Argument (organized by point)
6. Conclusion
7. Certificate of Service (placeholder)

STYLE:
- Professional legal writing
- Active voice where possible
- Clear topic sentences
- Numbered paragraphs
- Case citations in Bluebook format

TYPES SUPPORTED:
- Motion to Suppress Evidence
- Motion to Dismiss
- Motion in Limine
- Motion for Discovery
- Motion for Sanctions

Include placeholder for case-specific details in [BRACKETS].
```

### Discovery Request Generator

**Purpose:** Generate discovery requests  
**Input:** Case type, known evidence  
**Output:** Comprehensive discovery list

**Custom Instructions:**

```
Generate discovery requests for:

1. MANDATORY DISCLOSURES
   - Brady material
   - Giglio material
   - Expert reports
   - Witness lists

2. SPECIFIC REQUESTS
   - BWC footage (all officers, all dates)
   - Dispatch recordings
   - GPS/AVL data
   - Personnel files
   - Training records
   - Use of force policies
   - Similar incident reports

3. FORENSIC EVIDENCE
   - Lab reports
   - Chain of custody
   - Testing protocols
   - Examiner qualifications

4. ELECTRONIC EVIDENCE
   - Cell phone records
   - Social media posts
   - Emails/texts
   - Computer forensics

Format as numbered requests with definitions and time periods.
```

--

## 6. Timeline & Organization Tools

### Case Organizer

**Purpose:** Structure complex cases  
**Input:** All case materials  
**Output:** Organized case outline

**Custom Instructions:**

```
Organize case into structured outline:

I. CHARGES
   A. Count 1: [Offense]
      1. Elements
      2. Evidence (Prosecution)
      3. Evidence (Defense)
      4. Witnesses (Pro/Con)
      5. Legal Issues

II. TIMELINE
   A. Critical Dates
   B. Statute of Limitations
   C. Speedy Trial Issues

III. WITNESSES
   A. Government Witnesses
      1. Officer A
         - Expected Testimony
         - Credibility Issues
         - Cross-Exam Outline
   B. Defense Witnesses

IV. EVIDENCE
   A. Physical Evidence
   B. Documentary Evidence
   C. Digital Evidence
   D. Demonstrative Evidence

V. LEGAL ISSUES
   A. Pretrial Motions
   B. Evidentiary Issues
   C. Jury Instructions

VI. TRIAL STRATEGY
   A. Theory of Defense
   B. Theme
   C. Opening Statement Outline
   D. Closing Argument Outline
```

--

## Implementation in Evident

### Add to Project Settings UI

```xml
<!-- ProjectSettingsPage.xaml ->
<Picker x:Name="LegalToolPicker"
        Title="Legal Analysis Tool"
        ItemsSource="{Binding AvailableTools}">
    <Picker.ItemTemplate>
        <DataTemplate>
            <Label Text="{Binding Name}" />
        </DataTemplate>
    </Picker.ItemTemplate>
</Picker>

<Button Text="Run Analysis"
        Command="{Binding RunLegalToolCommand}"
        CommandParameter="{Binding SelectedItem, Source={x:Reference LegalToolPicker}}" />
```

### Add to ChatViewModel

```csharp
public ObservableCollection<LegalTool> AvailableTools { get; set; } = new()
{
    new LegalTool {
        Name = "Brady Violation Detector",
        CustomInstructions = bradyInstructions,
        Icon = "🔍"
    },
    new LegalTool {
        Name = "Fourth Amendment Analyzer",
        CustomInstructions = fourthAmendmentInstructions,
        Icon = "⚖️"
    },
    // ... more tools
};

[RelayCommand]
async Task RunLegalTool(LegalTool tool)
{
    // Apply tool's custom instructions to current project
    // Run analysis on selected documents
}
```

--

## Usage Examples

### Example 1: Brady Analysis

```
User uploads:
- Police incident report
- Officer statements
- Discovery log

Runs "Brady Violation Detector"

Output:
🔍 BRADY VIOLATION ANALYSIS

CRITICAL ISSUES FOUND: 2
HIGH PRIORITY ISSUES: 1

1. [CRITICAL] Undisclosed Exculpatory Evidence
   Source: Officer Smith's statement, page 3
   Quote: "Subject appeared confused and disoriented, possibly medical condition"
   Issue: This favorable evidence not disclosed in discovery
   Materiality: HIGH - Could negate mens rea element
   Remedy: Motion to compel + sanctions

2. [CRITICAL] Late Disclosure
   Source: Lab report dated 2024-01-15, disclosed 2024-03-20
   Issue: Report shows negative drug test, disclosed 2 months late
   Materiality: HIGH - Contradicts prosecution theory
   Remedy: Motion to exclude or dismiss

3. [HIGH] Impeachment Evidence Not Disclosed
   Source: Officer Jones personnel file
   Issue: Prior sustained complaint for false statements
   Materiality: MEDIUM - Giglio material
   Remedy: Motion to compel + potential Brady violation
```

### Example 2: Timeline Generation

```
User uploads:
- BWC footage (4 officers)
- Dispatch audio
- GPS logs

Runs "Timeline Generator"

Output:
📅 CHRONOLOGICAL TIMELINE

| Time | Event | Source | Conflicts |
|------|-------|--------|-----------|
| 14:23:15 | Initial dispatch | Radio Log | ✓ |
| 14:28:42 | Officer A arrives | GPS, BWC-A | ✓ |
| 14:29:10 | Officer B arrives | BWC-A, BWC-B | ✓ |
| 14:30:05 | First contact with suspect | BWC-A | ⚠️ Report says 14:32 |
| 14:31:22 | Suspect placed in cuffs | BWC-A, BWC-B | ✓ |
| 14:32:00 | Search begins | BWC-A | ⚠️ No warrant timestamp |
| 14:35:18 | Evidence recovered | BWC-A, BWC-B | ⚠️ Photo timestamp 14:40 |

🚨 CONFLICTS DETECTED:
- First contact timing discrepancy (Report vs. BWC)
- Evidence photo timestamp after recovery claim
- No warrant shown on BWC
```

--

**Next:** Implement these tools in ChatPage UI with quick access buttons!
