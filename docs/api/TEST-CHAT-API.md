# Enhanced Chat API - Testing Guide

Complete test examples for all 7 API endpoints with authentication.

## Setup

First, log in to get an authentication session:

```bash
# Login (get session cookie)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=your-email@example.com&password=your-password" \
  -c cookies.txt
```

All subsequent requests must include the session cookie: `-b cookies.txt`

--

## Endpoint 1: POST /api/chat/ask

**Ask a question and get an AI response with citations**

### Basic Question

```bash
curl -X POST http://localhost:5000/api/chat/ask \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key legal principles in Miranda v. Arizona?",
    "conversation_id": null,
    "context_documents": []
  }'
```

### Continue Conversation

```bash
curl -X POST http://localhost:5000/api/chat/ask \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does that apply to custodial interrogations?",
    "conversation_id": "conv-abc123",
    "context_documents": []
  }'
```

### With Document Context

```bash
curl -X POST http://localhost:5000/api/chat/ask \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize the key findings in this case file",
    "conversation_id": null,
    "context_documents": ["doc-456", "doc-789"]
  }'
```

**Expected Response:**

```json
{
  "conversation_id": "conv-abc123",
  "message_id": "msg-xyz789",
  "response": "Miranda v. Arizona established the requirement...",
  "citations": [
    {
      "document_id": "doc-123",
      "page_number": 5,
      "snippet": "...the person must be warned...",
      "authority_citation": "384 U.S. 436"
    }
  ],
  "metadata": {
    "model": "gpt-4",
    "tokens_used": 450,
    "retrieval_time_ms": 125,
    "analysis_time_ms": 890,
    "passage_count": 8
  },
  "accessibility": {
    "aria_label": "AI response with 1 citation",
    "tts_text": "Miranda versus Arizona established...",
    "reading_time_seconds": 12
  }
}
```

--

## Endpoint 2: GET /api/chat/conversations

**List all conversations with search and filtering**

### List All Conversations

```bash
curl http://localhost:5000/api/chat/conversations \
  -b cookies.txt
```

### Search Conversations

```bash
curl "http://localhost:5000/api/chat/conversations?search=Miranda&limit=10" \
  -b cookies.txt
```

### Filter by Project

```bash
curl "http://localhost:5000/api/chat/conversations?project_id=proj-123" \
  -b cookies.txt
```

**Expected Response:**

```json
{
  "conversations": [
    {
      "id": "conv-abc123",
      "title": "Miranda Rights Analysis",
      "project_id": "proj-456",
      "message_count": 8,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:45:00Z",
      "preview": "What are the key legal principles...",
      "topics": ["Miranda rights", "Custodial interrogation"]
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

--

## Endpoint 3: GET /api/chat/conversation/:id

**Retrieve complete conversation history**

```bash
curl http://localhost:5000/api/chat/conversation/conv-abc123 \
  -b cookies.txt
```

**Expected Response:**

```json
{
  "id": "conv-abc123",
  "title": "Miranda Rights Analysis",
  "project_id": "proj-456",
  "messages": [
    {
      "id": "msg-001",
      "role": "user",
      "content": "What are the key legal principles in Miranda v. Arizona?",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "msg-002",
      "role": "assistant",
      "content": "Miranda v. Arizona established...",
      "citations": [
        {
          "document_id": "doc-123",
          "page_number": 5,
          "snippet": "...the person must be warned...",
          "authority_citation": "384 U.S. 436"
        }
      ],
      "created_at": "2024-01-15T10:30:15Z"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z",
  "summary": {
    "total_messages": 8,
    "user_messages": 4,
    "assistant_messages": 4,
    "total_citations": 12,
    "unique_documents": 5,
    "topics": ["Miranda rights", "Custodial interrogation"]
  }
}
```

--

## Endpoint 4: GET /api/chat/conversation/:id/export

**Export conversation in various formats**

### Export as Markdown

```bash
curl "http://localhost:5000/api/chat/conversation/conv-abc123/export?format=markdown" \
  -b cookies.txt \
  -o conversation.md
```

### Export as JSON

```bash
curl "http://localhost:5000/api/chat/conversation/conv-abc123/export?format=json" \
  -b cookies.txt \
  -o conversation.json
```

### Export as HTML

```bash
curl "http://localhost:5000/api/chat/conversation/conv-abc123/export?format=html" \
  -b cookies.txt \
  -o conversation.html
```

**Markdown Format Example:**

```markdown
# Miranda Rights Analysis

**Created:** 2024-01-15 10:30:00

--

## User (10:30:00)

What are the key legal principles in Miranda v. Arizona?

## Assistant (10:30:15)

Miranda v. Arizona established the requirement...

**Citations:**

- [384 U.S. 436] Document doc-123, Page 5: "...the person must be warned..."
```

--

## Endpoint 5: POST /api/chat/references/suggest

**Get intelligent reference suggestions based on context**

```bash
curl -X POST http://localhost:5000/api/chat/references/suggest \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "query": "exclusionary rule evidence",
    "conversation_id": "conv-abc123",
    "limit": 5
  }'
```

**Expected Response:**

```json
{
  "suggestions": [
    {
      "document_id": "doc-789",
      "title": "Mapp v. Ohio Brief",
      "relevance_score": 0.92,
      "snippet": "The exclusionary rule prohibits...",
      "page_number": 3,
      "authority_citation": "367 U.S. 643"
    },
    {
      "document_id": "doc-456",
      "title": "Fourth Amendment Analysis",
      "relevance_score": 0.87,
      "snippet": "Evidence obtained in violation...",
      "page_number": 12
    }
  ],
  "query_time_ms": 45
}
```

--

## Endpoint 6: GET /api/chat/analytics

**Retrieve conversation analytics and usage statistics**

### Overall Analytics

```bash
curl http://localhost:5000/api/chat/analytics \
  -b cookies.txt
```

### Filtered Analytics

```bash
curl "http://localhost:5000/api/chat/analytics?project_id=proj-123&days=30" \
  -b cookies.txt
```

**Expected Response:**

```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z",
    "days": 30
  },
  "conversations": {
    "total": 45,
    "active": 12,
    "archived": 33
  },
  "messages": {
    "total": 380,
    "user": 190,
    "assistant": 190,
    "avg_per_conversation": 8.4
  },
  "citations": {
    "total": 156,
    "unique_documents": 67,
    "avg_per_message": 0.82
  },
  "top_topics": [
    { "topic": "Miranda rights", "count": 23 },
    { "topic": "Search and seizure", "count": 18 },
    { "topic": "Exclusionary rule", "count": 15 }
  ],
  "most_cited_documents": [
    {
      "document_id": "doc-123",
      "title": "Miranda v. Arizona",
      "citation_count": 34,
      "authority": "384 U.S. 436"
    },
    {
      "document_id": "doc-456",
      "title": "Mapp v. Ohio",
      "citation_count": 28,
      "authority": "367 U.S. 643"
    }
  ],
  "usage": {
    "total_tokens": 125000,
    "avg_tokens_per_message": 658,
    "estimated_cost_usd": 2.5
  }
}
```

--

## Endpoint 7: GET /api/chat/reference/:id/context

**Get expanded context for a specific cited reference**

```bash
curl http://localhost:5000/api/chat/reference/ref-abc123/context \
  -b cookies.txt
```

### With Expanded Window

```bash
curl "http://localhost:5000/api/chat/reference/ref-abc123/context?window=1000" \
  -b cookies.txt
```

**Expected Response:**

```json
{
  "reference_id": "ref-abc123",
  "document_id": "doc-123",
  "page_number": 5,
  "original_snippet": "...the person must be warned...",
  "expanded_context": "In all cases where custodial interrogation occurs, the person must be warned that they have the right to remain silent, that anything they say can be used against them in court, that they have the right to consult with a lawyer...",
  "surrounding_text": {
    "before": "The Court held that the prosecution may not use...",
    "after": "...and to have that lawyer present during interrogation."
  },
  "authority": {
    "citation": "384 U.S. 436",
    "case_name": "Miranda v. Arizona",
    "year": 1966,
    "court": "Supreme Court of the United States"
  },
  "related_references": [
    {
      "reference_id": "ref-def456",
      "snippet": "...voluntariness of the confession...",
      "page_number": 7
    }
  ]
}
```

--

## Python Test Script

Complete test script using `requests` library:

```python
import requests
import json

BASE_URL = "http://localhost:5000"
session = requests.Session()

# 1. Login
login_response = session.post(
    f"{BASE_URL}/login",
    data={"email": "your-email@example.com", "password": "your-password"}
)
print(f"Login: {login_response.status_code}")

# 2. Ask a question
ask_response = session.post(
    f"{BASE_URL}/api/chat/ask",
    json={
        "question": "What are the key legal principles in Miranda v. Arizona?",
        "conversation_id": None,
        "context_documents": []
    }
)
result = ask_response.json()
conv_id = result["conversation_id"]
print(f"Ask: {ask_response.status_code} - Conv ID: {conv_id}")
print(f"Response: {result['response'][:100]}...")
print(f"Citations: {len(result['citations'])}")

# 3. List conversations
list_response = session.get(f"{BASE_URL}/api/chat/conversations")
conversations = list_response.json()
print(f"Conversations: {conversations['total']} found")

# 4. Get conversation history
history_response = session.get(f"{BASE_URL}/api/chat/conversation/{conv_id}")
history = history_response.json()
print(f"History: {len(history['messages'])} messages")

# 5. Export conversation
export_response = session.get(
    f"{BASE_URL}/api/chat/conversation/{conv_id}/export",
    params={"format": "markdown"}
)
print(f"Export: {export_response.status_code}")
with open("conversation.md", "w") as f:
    f.write(export_response.text)

# 6. Get reference suggestions
suggest_response = session.post(
    f"{BASE_URL}/api/chat/references/suggest",
    json={"query": "exclusionary rule", "conversation_id": conv_id, "limit": 5}
)
suggestions = suggest_response.json()
print(f"Suggestions: {len(suggestions['suggestions'])} documents")

# 7. Get analytics
analytics_response = session.get(f"{BASE_URL}/api/chat/analytics")
analytics = analytics_response.json()
print(f"Analytics: {analytics['conversations']['total']} conversations")
print(f"Total tokens: {analytics['usage']['total_tokens']}")

print("\n✓ All tests complete!")
```

--

## Common Issues

### 401 Unauthorized

- Ensure you're logged in and passing the session cookie
- Check that the user exists in the database

### 404 Not Found

- Verify conversation_id exists
- Check that the blueprint is registered in app.py

### 500 Internal Server Error

- Check that database tables exist (run migrations)
- Verify AI pipeline is initialized
- Check app logs for detailed error messages

### No Citations Returned

- Ensure documents are indexed in the pipeline
- Check that `enable_citation_tracking=True` in pipeline config
- Verify document IDs in context_documents array are valid

--

## Next Steps

1. **Run migrations**: `python migrations/create_chat_tables.py`
2. **Start Flask**: `python app.py`
3. **Test endpoints**: Use curl examples above
4. **Access UI**: Navigate to http://localhost:5000/chat
5. **Monitor logs**: Check console for pipeline initialization messages

--

## API Rate Limits

- **Free Tier**: 100 requests/hour
- **Professional**: 1,000 requests/hour
- **Enterprise**: 10,000 requests/hour

Rate limit headers included in all responses:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
