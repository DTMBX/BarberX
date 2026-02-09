# Evident Chat - Quick Start Guide

## Welcome! 👋

Evident Chat is your AI-powered legal assistant for e-discovery, case management, and legal research. This guide gets you started in 2 minutes.

## Step 1: Setup Your API Key (Required)

Evident Chat uses OpenAI's GPT-4 model. You'll need your own API key:

### Get an OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Configure in Evident

1. Open https://your-app/chat
2. Click **🔑 Configure API Key** button
3. Paste your API key
4. Click **Save Key**

✅ You're ready to chat!

## Step 2: Choose Your AI Persona

When creating a new conversation, select your role:

- **Legal Assistant** (Default) - General e-discovery, legal concepts, case research
- **Evidence Manager** - Chain of custody, privilege issues, evidence organization
- **Case Analyzer** - Deep precedent analysis, legal theory, constitutional law
- **Research Specialist** - Comprehensive legal research, synthesis, jurisdiction comparison

## Step 3: Start Asking Questions

### Example Prompts

**Legal Research:**

- "What's the significance of Marbury v. Madison?"
- "Explain the Fourth Amendment protections for digital privacy"
- "Compare Roe v. Wade and Dobbs v. Jackson"

**Case Management:**

- "Help me organize evidence from multiple sources"
- "Check if these emails are attorney-client privileged"
- "Create a collection for contract dispute evidence"

**Evidence Discovery:**

- "Search for all emails mentioning settlement from 2022"
- "What's the chain of custody for this video file?"
- "Analyze this PDF for key legal sections"

### Tips

- 💬 Type or paste questions in the input area
- ↵ Press Enter or click Send
- ⏱ AI responds in seconds (depending on query complexity)
- 📌 Shift+Enter for multi-line input
- 🔄 Create new chat for different topics

## Features

### Chat Interface

- **Sidebar** - View and manage conversations
- **Main Area** - Message history with timestamps
- **Input Box** - Type questions, auto-expands
- **Status** - Shows API key configuration status

### AI Tools

The chat agent can use these tools automatically:

- Search Supreme Court cases
- Get detailed case information
- Search evidence across cases
- Check privilege status
- Upload and process media
- Analyze documents
- Track chain of custody
- Create evidence collections

### Conversation Management

- **New Chat** - Start fresh conversation (orange button)
- **View History** - Click conversation in sidebar
- **Archive** - Delete button removes conversation
- **Export** - Export chat as JSON or Markdown

### API Key Management

- **Safe Storage** - Keys encrypted, never displayed
- **Multiple Keys** - Add keys for different services
- **Validation** - Automatic testing before storage
- **Usage Tracking** - Monitor token usage and costs

## Common Tasks

### Task 1: Research a Supreme Court Case

```
"Tell me about Marbury v. Madison"

The AI will:
1. Search legal library
2. Find case details
3. Explain holdings and impact
4. Link related cases
```

### Task 2: Organize Evidence

```
"Help me organize emails, documents, and videos from the 2022 deal"

The AI will:
1. Ask about case details
2. Suggest collection structure
3. Help categorize materials
4. Track chain of custody
```

### Task 3: Analyze Legal Precedent

```
"How has the Supreme Court's approach to free speech evolved?"

The AI will:
1. Search landmark cases
2. Trace legal evolution
3. Compare holdings
4. Identify emerging patterns
```

## Settings

### Change AI Persona

Click the persona badge to change roles mid-conversation (if supported).

### Update API Key

1. Click **🔑 Configure API Key** button
2. Enter new key
3. Click **Save Key**

### Export Conversation

1. Open conversation
2. Click ⋯ menu (future enhancement)
3. Select "Export as JSON" or "Export as PDF"

## Keyboard Shortcuts

| Shortcut    | Action            |
| ----------- | ----------------- |
| Enter       | Send message      |
| Shift+Enter | New line in input |
| Ctrl+K      | Focus input       |
| Esc         | Close settings    |

## Pricing & Costs

### How It Works

- You pay only for what you use
- Pay OpenAI directly (Evident passes through no markup)
- GPT-4: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- Typical conversation: $0.10-$0.50

### Monitor Costs

1. Click **Chat Settings** (future)
2. View "Usage Statistics"
3. See costs by service and month
4. Set monthly budget alerts

### Estimate Your Usage

- Short question: 50-200 tokens (~$0.01)
- Case analysis: 1,000-5,000 tokens (~$0.05-$0.30)
- Research synthesis: 5,000-10,000 tokens (~$0.30-$0.60)

## Troubleshooting

### "No API key configured"

**Fix:**

1. Click 🔑 Configure API Key
2. Paste your OpenAI API key
3. Click Save

### "API key validation failed"

**Causes:**

- Key is incorrect or revoked
- Key doesn't have GPT-4 access
- Copy/paste added extra spaces

**Fix:**

- Double-check key at https://platform.openai.com/api-keys
- Regenerate if needed
- Paste carefully without extra spaces

### "Context window exceeded"

**Cause:** Very long conversation exceeds token limit

**Fix:**

- Start new conversation for new topic
- Chat automatically manages by removing old messages

### "Tool execution failed"

**Cause:** Tool not implemented or backend service unavailable

**Fix:**

- Try simpler question
- Report to admin
- Try again after system restart

## Best Practices

### For Legal Research

1. ✅ Start with broad questions
2. ✅ Ask about related precedent
3. ✅ Verify citations independently for publication
4. ✅ Use for research efficiency, not legal advice

### For Evidence Management

1. ✅ Maintain clear chain of custody
2. ✅ Flag privilege issues immediately
3. ✅ Use collections to organize
4. ✅ Export for case files

### For Case Analysis

1. ✅ Provide context about your case
2. ✅ Ask about distinguishing factors
3. ✅ Request synthesis of multiple cases
4. ✅ Identify gaps or uncertainties

## Privacy & Security

### Your Data Is Protected

- ✅ All chat messages stored in your account
- ✅ API keys encrypted, never logged
- ✅ HTTPS encryption for all traffic
- ✅ No data sold to third parties

### OpenAI Data Usage

- ⚠️ Your conversations MAY be reviewed by OpenAI per their terms
- ⚠️ Don't include confidential client info in chats
- ⚠️ Review OpenAI's privacy policy at https://openai.com/policies/privacy-policy

### Best Practice

For confidential matters:

1. Use generic references (Case A, Party B, etc.)
2. Avoid specific client names
3. Don't paste full confidential documents
4. Export and store chat artifacts locally

## Getting Help

### Inside Evident

- Click help icon (?) in chat
- Read contextual tips
- Check this guide

### Online Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Supreme Court Cases](https://www.supremecourt.gov/opinions)
- [Evident Documentation](https://your-app/docs)

### Contact Support

- Email: support@evident-tech.com
- Chat: In-app support (future)
- Docs: https://your-app/docs

## Tips & Tricks 🎯

### Trick 1: Use Past Tense for Historical Analysis

❌ Bad: "What cases protect privacy?"
✅ Good: "What cases have addressed digital privacy historically?"

### Trick 2: Ask for Contrasts

❌ Bad: "Tell me about constitutional privacy"
✅ Good: "How does the Fourth Amendment differ from the Fifth Amendment?"

### Trick 3: Request Specific Formats

❌ Bad: "Research this topic"
✅ Good: "Give me a bulleted summary of privacy law evolution"

### Trick 4: Build Context

❌ Bad: First message: "Will this win?"
✅ Good:

1. First: "I have a case about..."
2. Then: "What precedent applies?"
3. Then: "Will this precedent help?"

### Trick 5: Leverage Tools

✅ Ask about tool capabilities
✅ Request tool usage explicitly
✅ Follow up on tool results

## Examples

### Example 1: Legal Research Session

```
You: "What are the main Supreme Court cases on free speech?"
AI: [Searches legal library, returns Brandenburg v. Ohio,
     Texas v. Johnson, Citizens United cases]

You: "How has it evolved?"
AI: [Traces evolution from Brandenburg test through modern cases]

You: "Apply that to social media regulation"
AI: [Analyzes how precedent applies to hypothetical policy]
```

### Example 2: Evidence Management Session

```
You: "I need to organize 500 documents from a contract dispute"
AI: [Suggests organization by date, party, issue]

You: "How do I handle attorney-client emails?"
AI: [Explains privilege, asks about client involvement]

You: "Create collection for privileged materials"
AI: [Processes request, shows organization structure]
```

### Example 3: Case Analysis Session

```
You: "I'm working on a Fourth Amendment case"
AI: [Loads related precedent]

You: "Distinguish my facts from Katz v. United States"
AI: [Analyzes distinctions, finds similar cases]

You: "What's the trend in modern courts?"
AI: [Identifies pattern in recent decisions]
```

## Next Steps

1. **Configure API Key** (if not done) - 2 minutes
2. **Create First Chat** - Click "New Chat"
3. **Ask a Question** - Type your question
4. **Explore Tools** - See what the AI can do
5. **Start Working** - Use Evident Chat daily for legal tasks!

---

**You're all set! Happy chatting! 🚀**

Got questions? Click **Support** or email support@evident-tech.com
