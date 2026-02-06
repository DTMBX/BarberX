# ChatGPT 5.2 Integration Plan - Evident MAUI

**Integration Goal:** Enterprise-grade ChatGPT integration with custom project workspaces, user-provided API keys, and multi-platform support.

--

## 🎯 Feature Overview

### Core Features

1. **Custom Project Workspaces**
   - Users create isolated projects for different cases/clients
   - Each project has its own conversation history
   - Project-specific custom instructions
   - Memory boundaries prevent cross-contamination

2. **User API Key Integration**
   - Users bring their own OpenAI API key (GPT membership)
   - Secure storage using device SecureStorage
   - Key validation and quota tracking
   - Fallback to Evident AI credits for users without keys

3. **Advanced Prompt Engineering**
   - Custom instructions per project
   - System prompts for legal analysis
   - Context injection from case files
   - PDF document processing and analysis

4. **Multi-Platform Chat UI**
   - Native chat interface (Windows/iOS/Android)
   - Markdown rendering for responses
   - Code syntax highlighting
   - File attachment support
   - Voice input (platform-specific)

--

## 🏗️ Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MAUI App (Client)                     │
├─────────────────────────────────────────────────────────┤
│  ChatPage → ChatViewModel → ChatGptService              │
│  ProjectsPage → ProjectViewModel → ProjectService        │
│  PDF Upload → UploadService → Text Extraction           │
└────────────────┬────────────────────────────────────────┘
                 │ HTTPS + JWT
┌────────────────▼────────────────────────────────────────┐
│              Flask Backend (API Server)                  │
├─────────────────────────────────────────────────────────┤
│  /api/v1/chat/completions       - Send chat messages    │
│  /api/v1/projects/*             - Project management    │
│  /api/v1/conversations/*        - History management    │
│  /api/v1/openai/validate-key   - API key validation     │
│  /api/v1/extract/pdf-text      - PDF text extraction    │
└────────────────┬────────────────────────────────────────┘
                 │ API Key (user's)
┌────────────────▼────────────────────────────────────────┐
│                  OpenAI API (GPT-5.2)                   │
├─────────────────────────────────────────────────────────┤
│  gpt-5.2-codex / gpt-5.2 / gpt-5.2-turbo               │
│  128k context window                                     │
│  Function calling support                                │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → ChatViewModel → ChatGptService → Flask API
                                                    ↓
                               Add Custom Instructions + Context
                                                    ↓
                               Forward to OpenAI with User's API Key
                                                    ↓
                               Stream Response Back to Client
                                                    ↓
                Store in Conversation History (per Project)
```

--

## 📊 Database Schema Extensions

### New Tables

#### `projects` Table

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    custom_instructions TEXT,           - Project-specific system prompt
    model_preference VARCHAR(50) DEFAULT 'gpt-5.2',
    max_tokens INTEGER DEFAULT 4000,
    temperature FLOAT DEFAULT 0.7,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `conversations` Table

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),                 - Auto-generated from first message
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `messages` Table

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,          - 'system', 'user', 'assistant'
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

#### `user_api_keys` Table

```sql
CREATE TABLE user_api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,      - 'openai', 'anthropic', etc.
    encrypted_key TEXT NOT NULL,        - AES-256 encrypted
    is_active BOOLEAN DEFAULT TRUE,
    quota_used INTEGER DEFAULT 0,       - Track usage
    last_validated DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### `document_contexts` Table

```sql
CREATE TABLE document_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,           - Reference to uploaded file
    extracted_text TEXT,                - Text extracted from PDF
    chunk_index INTEGER,                - For large documents
    embedding_vector BLOB,              - Optional: for semantic search
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (file_id) REFERENCES pdf_uploads(id)
);
```

--

## 🔌 API Endpoints (Flask Backend)

### Chat Endpoints

#### POST `/api/v1/chat/completions`

Send a message and get GPT response.

**Request:**

```json
{
  "project_id": 123,
  "conversation_id": 456, // Optional, creates new if omitted
  "message": "Analyze this evidence for Brady violations",
  "include_context": true, // Include project documents in context
  "stream": false
}
```

**Response:**

```json
{
  "conversation_id": 456,
  "message_id": 789,
  "role": "assistant",
  "content": "Based on the evidence provided...",
  "tokens_used": 1250,
  "model": "gpt-5.2"
}
```

#### POST `/api/v1/chat/completions/stream`

Same as above but streams response in SSE format.

### Project Endpoints

#### GET `/api/v1/projects`

List user's projects.

**Response:**

```json
{
  "projects": [
    {
      "id": 123,
      "name": "State v. Johnson",
      "description": "Brady violation case",
      "custom_instructions": "You are a legal assistant...",
      "model_preference": "gpt-5.2",
      "conversation_count": 5,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

#### POST `/api/v1/projects`

Create new project.

**Request:**

```json
{
  "name": "State v. Johnson",
  "description": "Brady violation analysis",
  "custom_instructions": "You are a legal assistant specializing in criminal defense. Focus on finding Brady violations, discovery issues, and constitutional violations.",
  "model_preference": "gpt-5.2"
}
```

#### PUT `/api/v1/projects/{id}`

Update project settings.

#### DELETE `/api/v1/projects/{id}`

Delete project and all conversations.

### Conversation Endpoints

#### GET `/api/v1/conversations?project_id={id}`

List conversations in a project.

#### GET `/api/v1/conversations/{id}/messages`

Get all messages in a conversation.

**Response:**

```json
{
  "conversation": {
    "id": 456,
    "title": "Brady Violation Analysis",
    "project_id": 123
  },
  "messages": [
    {
      "id": 1,
      "role": "system",
      "content": "You are a legal assistant...",
      "created_at": "2026-01-20T10:00:00Z"
    },
    {
      "id": 2,
      "role": "user",
      "content": "Review this police report",
      "created_at": "2026-01-20T10:05:00Z"
    },
    {
      "id": 3,
      "role": "assistant",
      "content": "I've reviewed the report...",
      "tokens_used": 850,
      "created_at": "2026-01-20T10:05:15Z"
    }
  ]
}
```

#### DELETE `/api/v1/conversations/{id}`

Delete conversation.

### API Key Management

#### POST `/api/v1/openai/validate-key`

Validate user's OpenAI API key.

**Request:**

```json
{
  "api_key": "sk-..."
}
```

**Response:**

```json
{
  "valid": true,
  "organization": "user-org-123",
  "quota_remaining": 1000000, // tokens
  "models_available": ["gpt-5.2", "gpt-5.2-turbo"]
}
```

#### POST `/api/v1/user/api-keys`

Store encrypted API key.

**Request:**

```json
{
  "provider": "openai",
  "api_key": "sk-..."
}
```

#### GET `/api/v1/user/api-keys`

List user's stored API keys (masked).

**Response:**

```json
{
  "keys": [
    {
      "id": 1,
      "provider": "openai",
      "masked_key": "sk-...xyz",
      "is_active": true,
      "last_validated": "2026-01-20T10:00:00Z"
    }
  ]
}
```

### PDF Processing

#### POST `/api/v1/extract/pdf-text`

Extract text from uploaded PDF for chat context.

**Request:**

```json
{
  "file_id": 789,
  "project_id": 123
}
```

**Response:**

```json
{
  "file_id": 789,
  "text": "Full extracted text...",
  "page_count": 25,
  "word_count": 5000,
  "context_id": 999 // For referencing in chat
}
```

--

## 💾 MAUI Models (ApiModels.cs)

### Chat Models

```csharp
// Chat Request
public class ChatRequest
{
    [JsonPropertyName("project_id")]
    public int ProjectId { get; set; }

    [JsonPropertyName("conversation_id")]
    public int? ConversationId { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;

    [JsonPropertyName("include_context")]
    public bool IncludeContext { get; set; } = true;

    [JsonPropertyName("stream")]
    public bool Stream { get; set; } = false;
}

// Chat Response
public class ChatResponse
{
    [JsonPropertyName("conversation_id")]
    public int ConversationId { get; set; }

    [JsonPropertyName("message_id")]
    public int MessageId { get; set; }

    [JsonPropertyName("role")]
    public string Role { get; set; } = "assistant";

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("tokens_used")]
    public int TokensUsed { get; set; }

    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;
}

// Message Model
public class ChatMessage
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;  // "system", "user", "assistant"

    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;

    [JsonPropertyName("tokens_used")]
    public int? TokensUsed { get; set; }

    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }

    // UI helper property
    public bool IsUser => Role == "user";
    public bool IsAssistant => Role == "assistant";
}
```

### Project Models

```csharp
// Project Model
public class Project
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("custom_instructions")]
    public string? CustomInstructions { get; set; }

    [JsonPropertyName("model_preference")]
    public string ModelPreference { get; set; } = "gpt-5.2";

    [JsonPropertyName("max_tokens")]
    public int MaxTokens { get; set; } = 4000;

    [JsonPropertyName("temperature")]
    public double Temperature { get; set; } = 0.7;

    [JsonPropertyName("conversation_count")]
    public int ConversationCount { get; set; }

    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

// Create Project Request
public class CreateProjectRequest
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("custom_instructions")]
    public string? CustomInstructions { get; set; }

    [JsonPropertyName("model_preference")]
    public string ModelPreference { get; set; } = "gpt-5.2";
}

// Conversation Model
public class Conversation
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("project_id")]
    public int ProjectId { get; set; }

    [JsonPropertyName("title")]
    public string Title { get; set; } = "New Conversation";

    [JsonPropertyName("message_count")]
    public int MessageCount { get; set; }

    [JsonPropertyName("last_message_at")]
    public DateTime? LastMessageAt { get; set; }

    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

// API Key Model
public class ApiKeyInfo
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    [JsonPropertyName("provider")]
    public string Provider { get; set; } = "openai";

    [JsonPropertyName("masked_key")]
    public string MaskedKey { get; set; } = string.Empty;

    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; }

    [JsonPropertyName("last_validated")]
    public DateTime? LastValidated { get; set; }
}

// API Key Validation Response
public class ApiKeyValidation
{
    [JsonPropertyName("valid")]
    public bool Valid { get; set; }

    [JsonPropertyName("organization")]
    public string? Organization { get; set; }

    [JsonPropertyName("quota_remaining")]
    public long? QuotaRemaining { get; set; }

    [JsonPropertyName("models_available")]
    public List<string> ModelsAvailable { get; set; } = new();
}

// PDF Text Extraction
public class PdfTextExtractionResponse
{
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }

    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;

    [JsonPropertyName("page_count")]
    public int PageCount { get; set; }

    [JsonPropertyName("word_count")]
    public int WordCount { get; set; }

    [JsonPropertyName("context_id")]
    public int ContextId { get; set; }
}
```

--

## 🔧 Implementation Priority

### Phase 1: Backend Foundation (Week 1)

1. Create database migrations for new tables
2. Implement OpenAI service wrapper in Flask
3. Create chat API endpoints
4. Add API key encryption/storage
5. Test with Postman

### Phase 2: MAUI Services (Week 1-2)

1. Add models to ApiModels.cs
2. Create ChatGptService
3. Create ProjectService
4. Create ConversationService
5. Add API key storage in SecureStorage

### Phase 3: MAUI UI (Week 2)

1. Create ChatPage.xaml with message list
2. Create ProjectsPage.xaml for workspace management
3. Create ProjectSettingsPage.xaml for custom instructions
4. Implement ViewModels with MVVM
5. Add markdown rendering for chat responses

### Phase 4: Advanced Features (Week 3)

1. PDF text extraction integration
2. Context injection from case files
3. Streaming responses (SSE)
4. Voice input (platform-specific)
5. Export conversations

### Phase 5: Testing & Polish (Week 3-4)

1. Test on Windows
2. Test on Android
3. Test on iOS
4. Performance optimization
5. UI polish

--

## 🎨 UI Design Mockups

### ChatPage Layout

```
┌─────────────────────────────────────────┐
│  ≡  State v. Johnson    [Projects] [⚙]  │  ← Header
├─────────────────────────────────────────┤
│                                          │
│  [User Message]                          │  ← Messages
│  Analyze this police report              │     ScrollView
│                                          │
│           [Assistant Response]           │
│           Based on my analysis...        │
│                                          │
│  [User Message]                          │
│  What about Brady violations?            │
│                                          │
│           [Assistant typing...]          │  ← Typing indicator
│                                          │
├─────────────────────────────────────────┤
│  📎  Type a message...           [Send]  │  ← Input bar
└─────────────────────────────────────────┘
```

### ProjectsPage Layout

```
┌─────────────────────────────────────────┐
│  Projects                    [+ New]     │
├─────────────────────────────────────────┤
│                                          │
│  📁 State v. Johnson                     │
│     5 conversations • Modified 2h ago    │
│     [Open] [Settings] [Delete]           │
│                                          │
│  📁 City Council Investigation           │
│     2 conversations • Modified 1d ago    │
│     [Open] [Settings] [Delete]           │
│                                          │
│  📁 Template: Legal Analysis             │
│     0 conversations • Created 3d ago     │
│     [Open] [Settings] [Delete]           │
│                                          │
└─────────────────────────────────────────┘
```

### ProjectSettingsPage Layout

```
┌─────────────────────────────────────────┐
│  ← Project Settings                      │
├─────────────────────────────────────────┤
│  Project Name                            │
│  [State v. Johnson                    ]  │
│                                          │
│  Description                             │
│  [Brady violation case analysis       ]  │
│                                          │
│  Custom Instructions                     │
│  ┌────────────────────────────────────┐ │
│  │You are a legal assistant           │ │
│  │specializing in criminal defense... │ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Model: [gpt-5.2           ▼]           │
│  Temperature: [0.7         ▼]           │
│  Max Tokens: [4000         ▼]           │
│                                          │
│  OpenAI API Key                          │
│  [sk-...xyz                           ]  │
│  [Validate Key]                          │
│                                          │
│           [Save Changes]                 │
└─────────────────────────────────────────┘
```

--

## 🔐 Security Considerations

### API Key Storage

- **Client-side:** Use platform SecureStorage (Keychain/Keystore)
- **Server-side:** AES-256 encryption with user-specific salt
- **Transmission:** Always HTTPS, never log keys
- **Validation:** Test key before storing

### Context Injection

- Sanitize all user inputs
- Limit context size to prevent token exhaustion
- Filter PII before sending to OpenAI
- Option to disable context sharing per project

### Rate Limiting

- Enforce tier-based message limits (FREE: 10/day, PRO: 1000/day)
- Track token usage per user
- Implement exponential backoff for failures

--

## 📱 Multi-Platform Optimizations

### Windows

- Native file drag-and-drop for PDFs
- Keyboard shortcuts (Ctrl+Enter to send)
- System tray notification for long responses

### iOS

- SwiftKey integration for voice input
- Handoff support between devices
- Widget for quick access

### Android

- Material Design chat bubbles
- Notification channels for responses
- Share intent for sending files

--

**Next Step:** Start implementing backend API endpoints for chat functionality.

Ready to begin?
