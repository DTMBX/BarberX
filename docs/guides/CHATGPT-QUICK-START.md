# 🚀 ChatGPT Integration - Quick Start

**Goal:** Get ChatGPT integration running in 15 minutes

--

## Prerequisites

✅ Evident MAUI app built successfully (0 errors)  
✅ Flask backend running (`python app.py`)  
✅ OpenAI API key (from https://platform.openai.com/api-keys)

--

## Step 1: Install Dependencies (2 minutes)

```powershell
cd C:\web-dev\github-repos\Evident.info

# Install Python packages
pip install openai cryptography

# Verify installation
python -c "import openai; print('✅ OpenAI installed')"
python -c "from cryptography.fernet import Fernet; print('✅ Cryptography installed')"
```

--

## Step 2: Generate Encryption Key (1 minute)

```powershell
# Generate a secure encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copy the output (looks like: gAAAAABh...)
# Save it for next step
```

--

## Step 3: Set Environment Variable (1 minute)

**Windows (PowerShell):**

```powershell
# Create .env file if it doesn't exist
if (!(Test-Path .env)) { New-Item .env -ItemType File }

# Add encryption key (replace with your generated key)
Add-Content .env "API_KEY_ENCRYPTION_KEY=your-generated-key-here"
```

**Or manually create `.env` file:**

```
API_KEY_ENCRYPTION_KEY=gAAAAABh...your-key-here
OPENAI_API_KEY=sk-optional-default-key
```

--

## Step 4: Run Database Migration (2 minutes)

```powershell
python migrate_add_chatgpt.py
```

**Expected output:**

```
Creating ChatGPT integration tables...
✅ Tables created successfully:
  - projects
  - conversations
  - messages
  - user_api_keys
✅ Migration complete!
```

**Verify:**

```powershell
# Check tables were created
python -c "from models_auth import db; from api.chatgpt import Project, Conversation, Message, UserApiKey; print('✅ All models loaded')"
```

--

## Step 5: Register Blueprint (2 minutes)

Edit `app.py`:

```python
# Add at top with other imports
from api.chatgpt import chatgpt_bp

# Find where other blueprints are registered (around line 250-260)
# Add this line:
app.register_blueprint(chatgpt_bp)
```

**Full example:**

```python
# Register API blueprints
from api import register_api_blueprints
register_api_blueprints(app)

# Register ChatGPT blueprint
from api.chatgpt import chatgpt_bp
app.register_blueprint(chatgpt_bp)
```

--

## Step 6: Restart Flask App (1 minute)

```powershell
# Stop current Flask app (Ctrl+C)
# Start again
python app.py
```

**Verify:**

```
 * Running on http://127.0.0.1:5000
 * Running on http://localhost:5000
```

--

## Step 7: Test API with Postman (3 minutes)

### Test 1: Validate API Key

```
POST http://localhost:5000/api/v1/openai/validate-key
Content-Type: application/json

{
  "api_key": "sk-your-openai-api-key-here"
}
```

**Expected response:**

```json
{
  "valid": true,
  "models_available": ["gpt-4", "gpt-3.5-turbo"],
  "organization": "org-..."
}
```

### Test 2: Store API Key (requires login)

```
POST http://localhost:5000/api/v1/user/api-keys
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "provider": "openai",
  "api_key": "sk-your-key"
}
```

### Test 3: Create Project

```
POST http://localhost:5000/api/v1/projects
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "name": "Test Case Analysis",
  "description": "Testing ChatGPT integration",
  "custom_instructions": "You are a helpful legal assistant.",
  "model_preference": "gpt-4"
}
```

**Expected response:**

```json
{
  "id": 1,
  "name": "Test Case Analysis",
  "message": "Project created successfully"
}
```

### Test 4: Send Chat Message

```
POST http://localhost:5000/api/v1/chat/completions
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "project_id": 1,
  "message": "Hello! Can you analyze a Brady violation case?",
  "stream": false
}
```

**Expected response:**

```json
{
  "conversation_id": 1,
  "message_id": 2,
  "role": "assistant",
  "content": "Hello! I'd be happy to help analyze a Brady violation case...",
  "tokens_used": 450,
  "model": "gpt-4"
}
```

--

## Step 8: Register MAUI Services (2 minutes)

Edit `src/Evident.MatterDocket.MAUI/MauiProgram.cs`:

```csharp
// Add with other services (around line 25-36)
builder.Services.AddSingleton<IChatGptService, ChatGptService>();
builder.Services.AddSingleton<IProjectService, ProjectService>();
```

**Full example:**

```csharp
// Services
builder.Services.AddSingleton<ApiService>();
builder.Services.AddSingleton<AuthService>();
builder.Services.AddSingleton<UserService>();
builder.Services.AddSingleton<UploadService>();
builder.Services.AddSingleton<AnalysisService>();
builder.Services.AddSingleton<BillingService>();
builder.Services.AddSingleton<CaseService>();
builder.Services.AddSingleton<EvidenceService>();
builder.Services.AddSingleton<TierService>();
builder.Services.AddSingleton<IChatGptService, ChatGptService>();  // ← NEW
builder.Services.AddSingleton<IProjectService, ProjectService>();  // ← NEW
```

--

## Step 9: Build MAUI App (1 minute)

```powershell
cd src\Evident.MatterDocket.MAUI
dotnet build -f net10.0-windows10.0.19041.0
```

**Expected:**

```
Build succeeded.
    0 Error(s)
    49 Warning(s)
```

--

## ✅ Verification Checklist

Run through this checklist to confirm everything works:

```
✅ OpenAI package installed (pip install openai)
✅ Cryptography package installed (pip install cryptography)
✅ Encryption key generated and added to .env
✅ Database migration completed (4 new tables)
✅ ChatGPT blueprint registered in app.py
✅ Flask app restarted successfully
✅ API key validation endpoint works (Postman test)
✅ Project creation endpoint works (Postman test)
✅ Chat completion endpoint works (Postman test)
✅ MAUI services registered in MauiProgram.cs
✅ MAUI app builds successfully (0 errors)
```

--

## 🐛 Troubleshooting

### Error: "No module named 'openai'"

```powershell
pip install -upgrade openai
```

### Error: "No module named 'cryptography'"

```powershell
pip install -upgrade cryptography
```

### Error: "API_KEY_ENCRYPTION_KEY not set"

```powershell
# Verify .env file exists and has the key
cat .env
# Should show: API_KEY_ENCRYPTION_KEY=...
```

### Error: "Invalid API key"

- Verify you're using a real OpenAI API key from https://platform.openai.com/api-keys
- Make sure key starts with `sk-`
- Check key hasn't been revoked

### Error: "401 Unauthorized" on API calls

- Make sure you're logged in and have a valid JWT token
- Get token via POST /api/v1/auth/login
- Include in headers: `Authorization: Bearer your-token`

### Error: "Project not found"

- Create a project first using POST /api/v1/projects
- Use the returned `id` in chat requests

--

## 📋 What's Next?

Now that the backend is working, you can:

1. **Build Chat UI** - Create ChatPage.xaml in MAUI
2. **Build Projects UI** - Create ProjectsPage.xaml
3. **Add Markdown Rendering** - Display formatted GPT responses
4. **Test on Mobile** - Try Android/iOS builds
5. **Add Streaming** - Real-time response display
6. **Add PDF Context** - Inject case documents into prompts

--

## 🎯 Quick Test Flow

1. Start Flask: `python app.py`
2. Login: POST `/api/v1/auth/login`
3. Save token for next requests
4. Store API key: POST `/api/v1/user/api-keys`
5. Create project: POST `/api/v1/projects`
6. Send message: POST `/api/v1/chat/completions`
7. See GPT response! 🎉

--

## 📚 Documentation

- **Full Integration Plan:** `CHATGPT-INTEGRATION-PLAN.md`
- **Phase 1 Complete:** `CHATGPT-PHASE-1-COMPLETE.md`
- **API Reference:** `API-REFERENCE.md`

--

**Setup Time:** ~15 minutes  
**Status:** Backend Ready ✅  
**Next:** Build UI (ChatPage.xaml)

🚀 **You're all set! Start building the chat interface!**
