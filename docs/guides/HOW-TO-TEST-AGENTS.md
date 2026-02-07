# How to Test & Use Evident Custom Copilot Agents v2.0

**Quick Start Guide for Testing Enhanced Agents**

--

## ✅ Validation Checklist

### 1. Verify Agent Configuration

```powershell
# Validate all 7 agents are properly configured
python scripts/validate-agents.py
```

**Expected Output:**

- ✅ All 7 agents properly configured
- ✅ Instruction sets ~3,000 chars each
- ✅ All key files referenced correctly
- ✅ All models using claude-sonnet-4.5

### 2. Run Integration Tests

```powershell
# Run 21 integration tests
python scripts/test-agents.py
```

**Expected Output:**

- Total Tests: 21
- Passed: 21
- Failed: 0
- Pass Rate: 100.0%

### 3. Run Agent Simulation

```powershell
# Test agents with real-world scenarios
python scripts/simulate-agents.py
```

**Expected Output:**

- Simulations Run: 7
- Improvements Identified: 2 (down from 5 in v1.0)

--

## 🤖 Using Agents in GitHub Copilot Chat

### Prerequisites

1. **VS Code** with GitHub Copilot extension installed
2. **Active GitHub Copilot subscription**
3. **Evident workspace** open in VS Code

### How to Invoke Agents

1. Open **GitHub Copilot Chat** (Ctrl+Shift+I or Cmd+Shift+I)
2. Type `@` to see available agents
3. Select an agent from the dropdown
4. Type your question or request

--

## 📚 Practical Examples

### Example 1: Copyright Compliance Review

**Scenario:** You've written an export function and need to ensure it doesn't
violate Westlaw copyright.

**How to use:**

1. Open Copilot Chat
2. Type:

   ```
   @legal-compliance Review this export function for copyright violations

   [Paste your export code]
   ```

**What the agent will provide:**

1. ✅ Compliance status (PASS/FAIL)
2. 📋 List of violations found
3. 💻 Corrected code example
4. 📖 Reference to compliance pattern violated
5. 🧪 Suggested tests to prevent regression
6. 🤝 Suggestion to collaborate with @flask-backend for API implementation

**Sample Response:**

```
1. Compliance Status: FAIL

2. Violations Found:
   - Full Westlaw opinion exported (Pattern 1: Pointer, Don't Republish)
   - Missing attribution manifest (Pattern 3: Rights-Aware Exports)

3. Corrected Code:
   [Shows Material() pattern with citation + link instead of full text]

4. Pattern Violated: Pattern 1 - Never republish proprietary content

5. Suggested Tests:
   - Test export blocks full text >200 words
   - Test attribution manifest generation

For API implementation, collaborate with @flask-backend
```

--

### Example 2: BWC Forensics - Chain of Custody

**Scenario:** You need to add file integrity checking to video uploads.

**How to use:**

1. Open Copilot Chat
2. Type:

   ```
   @bwc-forensics Add SHA-256 hash verification to video upload function

   [Paste your upload_video() function]
   ```

**What the agent will provide:**

1. 🔬 Forensic methodology explanation
2. 💻 Complete code implementation with hashing
3. ⚖️ Explanation of evidentiary value
4. 📋 Court admissibility requirements (Daubert standard)
5. 🧪 Validation tests (hash generation, mismatch detection)
6. 🤝 Suggestion to collaborate with @database-architect for schema

**Sample Response:**

```python
def upload_video(file, user_id):
    # GOOD: Hash file for integrity
    file_hash = hashlib.sha256(file.read()).hexdigest()
    file.seek(0)  # Reset for storage

    evidence = Evidence(
        filename=file.filename,
        sha256_hash=file_hash,
        uploaded_by=user_id,
        chain_of_custody=[{
            'action': 'upload',
            'user': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'hash': file_hash
        }]
    )
```

--

### Example 3: Flask Backend - Secure API

**Scenario:** You need to create a secure endpoint for case retrieval.

**How to use:**

1. Open Copilot Chat
2. Type:
   ```
   @flask-backend Create secure API endpoint to retrieve case by ID with ownership validation
   ```

**What the agent will provide:**

1. 🔒 Endpoint signature (method, path, auth requirements)
2. 💻 Complete code with @login_required and ownership checks
3. 🛡️ List of security measures applied
4. 📄 Request/response format documentation
5. 🧪 Unit and integration test suggestions
6. 🤝 Suggestion to collaborate with @security-devops for rate limiting

**Sample Response:**

```python
@app.route('/api/cases/<int:case_id>', methods=['GET'])
@login_required
def get_case(case_id):
    # GOOD: Validate ownership
    case = Case.query.get_or_404(case_id)
    if case.attorney_id != current_user.id and not current_user.is_admin:
        raise Forbidden("You don't have access to this case")

    # GOOD: Don't expose proprietary data
    return jsonify(case.to_dict(exclude_proprietary=True))

# Suggested Tests:
# - Test authentication (@login_required)
# - Test ownership validation
# - Test SQL injection prevention
```

--

### Example 4: Frontend - Accessible Form

**Scenario:** You need to create an accessible file upload form.

**How to use:**

1. Open Copilot Chat
2. Type:
   ```
   @frontend-dev Create WCAG AA accessible case upload form with drag-drop
   ```

**What the agent will provide:**

1. 🎨 Complete HTML/CSS/JS component code
2. 📖 Explanation of design decisions
3. ♿ List of accessibility features (ARIA, keyboard nav)
4. 📱 Description of responsive behavior
5. 🧪 Accessibility and visual regression test suggestions
6. 🤝 Suggestion to collaborate with @flask-backend for API integration

**Sample Response:**

```html
<form class="case-upload-form" role="form" aria-label="Upload BWC Evidence">
  <label for="caseNumber">
    Case Number
    <span class="required" aria-label="required">*</span>
  </label>
  <input
    id="caseNumber"
    type="text"
    required
    aria-required="true"
    aria-describedby="caseNumberHelp"
  />
  <span id="caseNumberHelp" class="help-text">
    Enter the official case docket number
  </span>
</form>

<!-- Accessibility Features:
- ARIA labels for screen readers
- Keyboard navigation (Tab, Enter, Escape)
- Color contrast 4.5:1 (WCAG AA)
- Help text with aria-describedby
->

<!-- Suggested Tests:
- Test keyboard navigation
- Test screen reader compatibility
- Test color contrast ratios
->
```

--

### Example 5: Database - Schema Design

**Scenario:** You need to optimize case search queries.

**How to use:**

1. Open Copilot Chat
2. Type:
   ```
   @database-architect Add indexes to optimize case search by attorney and date
   ```

**What the agent will provide:**

1. 📊 SQLAlchemy model definition with indexes
2. 📖 Explanation of normalization and relationships
3. 🔍 List of indexes and constraints added
4. 📝 Migration script to apply changes
5. 🧪 Schema validation and query performance tests
6. 🤝 Suggestion to collaborate with @flask-backend for query integration

**Sample Response:**

```python
class Case(db.Model):
    -tablename- = 'cases'

    id = Column(Integer, primary_key=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    attorney_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, index=True)

    # GOOD: Composite index for common queries
    -table_args- = (
        Index('ix_case_attorney_date', 'attorney_id', 'created_at'),
    )

# Suggested Tests:
# - Test query performance with EXPLAIN
# - Test unique constraints
# - Test foreign key relationships
```

--

### Example 6: Security - Environment Secrets

**Scenario:** You need to secure API keys and database credentials.

**How to use:**

1. Open Copilot Chat
2. Type:
   ```
   @security-devops Implement environment variable secrets management for production
   ```

**What the agent will provide:**

1. 🔒 Identification of security vulnerabilities
2. ⚠️ Risk level assessment (Critical/High/Medium/Low)
3. 💻 Secure code example with environment variables
4. 🛡️ Explanation of attack vector prevented
5. 🧪 Security test suggestions
6. 🤝 Suggestion to collaborate with @flask-backend for config integration

**Sample Response:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # GOOD: Validate secrets exist
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable not set")

# BAD: ❌ NEVER DO THIS
# SECRET_KEY = "hardcoded-secret-key-123"  # Security vulnerability

# Suggested Tests:
# - Test secrets loading from .env
# - Test application fails if secrets missing
# - Test dependency vulnerability scanning
```

--

### Example 7: Documentation - API Docs

**Scenario:** You need to document a new REST API endpoint.

**How to use:**

1. Open Copilot Chat
2. Type:
   ```
   @documentation Document the POST /api/cases endpoint with curl examples
   ```

**What the agent will provide:**

1. 📝 Step-by-step API documentation
2. 💻 Curl command examples
3. 📄 Expected output/response samples
4. 🔧 Troubleshooting section for common errors
5. 🔗 Cross-references to related documentation
6. 🤝 Suggestion to collaborate with @flask-backend for technical accuracy

**Sample Response:**

````markdown
## Create New Case

**Endpoint:** `POST /api/cases`

**Authentication:** Required (Bearer token)

**Request:**

```bash
curl -X POST \
  https://Evident.info/api/cases \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "A-000313-25",
    "description": "BWC footage analysis"
  }'
```

**Response (Success):**

```json
{
  "id": 12345,
  "case_number": "A-000313-25",
  "created_at": "2026-01-23T10:30:00Z",
  "status": "open"
}
```

**Error Codes:**

- `400` - Invalid request data
- `401` - Missing or invalid authentication token
- `409` - Case number already exists
````

--

## 🔄 Multi-Agent Workflows

The enhanced agents now suggest collaboration with other agents for complex
tasks.

### Workflow Example: Copyright-Compliant Export Feature

**Step 1:** Start with @legal-compliance

```
@legal-compliance What are the requirements for a compliant PDF export?
```

→ Agent provides 3 compliance patterns and suggests collaborating with
@flask-backend

**Step 2:** Switch to @flask-backend

```
@flask-backend Implement export endpoint following the compliance patterns from @legal-compliance
```

→ Agent creates secure API endpoint and suggests collaborating with
@database-architect for schema

**Step 3:** Switch to @database-architect

```
@database-architect Create ExportManifest table for attorney certification tracking
```

→ Agent creates schema with indexes and suggests collaborating with
@documentation

**Step 4:** Switch to @documentation

```
@documentation Document the export workflow for attorneys
```

→ Agent creates step-by-step user guide

**Result:** Complete feature with compliance, API, database, and documentation
all working together!

--

## 🧪 Testing Your Changes

After using agents to modify code, always run the test suite:

```powershell
# Run all tests
python scripts/test-agents.py

# Run specific agent tests
python scripts/validate-agents.py

# Run simulation for improvements
python scripts/simulate-agents.py
```

--

## 📊 Metrics to Track

Monitor agent effectiveness:

1. **Response Quality** - Are code examples copy-paste ready?
2. **Collaboration** - Are agents suggesting other agents appropriately?
3. **Testing** - Are test suggestions comprehensive?
4. **Error Handling** - Are edge cases covered?

--

## 🐛 Troubleshooting

### Agent not appearing in Copilot Chat

**Solution:**

1. Ensure `.github/copilot-agents.yml` exists in workspace root
2. Reload VS Code window (Ctrl+Shift+P → "Reload Window")
3. Check GitHub Copilot subscription is active

### Agent provides generic responses

**Solution:**

1. Be specific in your prompt (include file names, line numbers)
2. Paste relevant code context
3. Specify desired output format

### Agent doesn't suggest collaboration

**Solution:**

1. Ask for complete implementation (not just code snippet)
2. Mention you're working on a complex feature
3. Use v2.0 enhanced agents (check `copilot-agents.yml` has ~3,000 char
   instruction sets)

--

## 📚 Additional Resources

- **Interactive Demo:** [agents-demo-v2.html](agents-demo-v2.html)
- **Cheat Sheet:** [agents-cheat-sheet.html](agents-cheat-sheet.html)
- **Example Library:**
  [scripts/agent-examples.json](scripts/agent-examples.json)
- **Enhancement Summary:**
  [AGENTS-V2-ENHANCEMENTS.md](AGENTS-V2-ENHANCEMENTS.md)

--

## 🎯 Next Steps

1. ✅ **Test agents** with scripts/validate-agents.py
2. ✅ **Try examples** from this guide in Copilot Chat
3. ✅ **Monitor usage** and collect feedback
4. 🔄 **Iterate** based on real-world attorney usage

--

**Version:** 2.0  
**Last Updated:** January 23, 2026  
**Status:** ✅ Production Ready (100% test coverage)
