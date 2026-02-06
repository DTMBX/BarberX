"""
Integration Guide - Add Enhanced Chat to app.py

Add this to your app.py to enable the enhanced chat system.
"""

# ============================================================================

# STEP 1: Add import at top of app.py (around line 50)

# ============================================================================

# Add after existing imports:

try:
from api.enhanced_chat import chat_bp
ENHANCED_CHAT_AVAILABLE = True
except ImportError as e:
ENHANCED_CHAT_AVAILABLE = False
print(f"[!] Enhanced chat not available: {e}")

# ============================================================================

# STEP 2: Register blueprint (around line 300 where other blueprints are registered)

# ============================================================================

# Add after existing blueprint registrations:

if ENHANCED_CHAT_AVAILABLE:
app.register_blueprint(chat_bp)
print("[✓] Enhanced chat API registered at /api/chat/\*")

# ============================================================================

# STEP 3: Initialize unified pipeline (in create_app() or after app creation)

# ============================================================================

# Add configuration:

from src.ai.pipeline import get_orchestrator

# Configure pipeline

pipeline_config = {
"db_path": "instance/Evident_legal.db",
"storage_root": "./uploads",
"manifest_root": "./manifest",
"enable_vector_index": False, # Enable when ChromaDB is set up
"ocr_threshold": 50, # Min chars/page before OCR
}

# Initialize orchestrator (singleton)

orchestrator = get_orchestrator(config=pipeline_config)

print("[✓] AI Pipeline orchestrator initialized")

# ============================================================================

# STEP 4: Add route for chat UI (optional - if you want a web interface)

# ============================================================================

@app.route("/chat")
@login_required
def chat_interface():
"""Enhanced chat interface with memory and references"""
return render_template(
"chat/interface.html",
user=current_user,
conversations=[] # TODO: Load from database
)

# ============================================================================

# STEP 5: Example usage in existing routes

# ============================================================================

# You can now use the enhanced chat in your existing routes:

@app.route("/api/case/<int:case_id>/analyze", methods=["POST"])
@login_required
def analyze_case_with_chat(case_id):
"""Analyze case using enhanced chat assistant"""
from src.ai.chat import EnhancedChatAssistant

    # Get case data
    case = Case.query.get_or_404(case_id)

    # Initialize assistant
    assistant = EnhancedChatAssistant(user_id=current_user.id)

    # Start conversation about case
    conv = assistant.start_conversation(
        title=f"Analysis of Case {case_id}",
        context_documents=[case.evidence_doc_id]  # Pre-load case documents
    )

    # Ask analysis question
    response = assistant.ask(
        query=request.json.get("query", "Summarize the key legal issues"),
        retrieve_references=True,
        accessibility_mode=request.json.get("accessibility", False)
    )

    return jsonify({
        "conversation_id": conv["conversation_id"],
        "analysis": response["answer"],
        "citations": response["citations"],
        "case_id": case_id
    })

# ============================================================================

# COMPLETE INTEGRATION EXAMPLE

# ============================================================================

"""
Full example showing how to integrate enhanced chat into an existing Flask app:

```python
# app.py

from flask import Flask
from api.enhanced_chat import chat_bp
from src.ai.pipeline import get_orchestrator
from src.ai.chat import EnhancedChatAssistant

app = Flask(__name__)

# Register enhanced chat API
app.register_blueprint(chat_bp)

# Initialize AI pipeline
orchestrator = get_orchestrator({
    "storage_root": "./uploads",
    "manifest_root": "./manifest"
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

if -name- == "-main-":
    app.run(debug=True)
```

Then in your frontend (JavaScript):

```javascript
// Ask a question
async function askQuestion(query) {
  const response = await fetch("/api/chat/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: query,
      retrieve_references: true,
      max_passages: 5,
      accessibility_mode: false,
    }),
  });

  const data = await response.json();

  console.log("Answer:", data.answer);
  console.log("Citations:", data.citations);

  return data;
}

// List conversations
async function listConversations() {
  const response = await fetch("/api/chat/conversations?limit=20");
  const data = await response.json();

  console.log("Conversations:", data.conversations);

  return data;
}

// Export conversation
function exportConversation(conversationId) {
  window.location.href = `/api/chat/conversation/${conversationId}/export?format=markdown`;
}
```

Frontend HTML template example:

```html
<!-- templates/chat.html ->
<!DOCTYPE html>
<html>
  <head>
    <title>Evident Chat Assistant</title>
  </head>
  <body>
    <div class="chat-container">
      <div class="chat-header">
        <h1>Legal Research Assistant</h1>
      </div>

      <div id="messages" class="chat-messages" role="log" aria-live="polite">
        <!-- Messages appear here ->
      </div>

      <form id="chat-form" class="chat-input">
        <input
          type="text"
          id="query-input"
          placeholder="Ask about evidence, formats, or system usage — not legal advice"
          aria-label="Enter your question"
          required
        />
        <button type="submit">Ask</button>
      </form>
    </div>

    <script>
      document
        .getElementById("chat-form")
        .addEventListener("submit", async (e) => {
          e.preventDefault();

          const query = document.getElementById("query-input").value;
          const messagesDiv = document.getElementById("messages");

          // Add user message
          messagesDiv.innerHTML += `
                <div class="message user-message">
                    <strong>You:</strong> ${query}
                </div>
            `;

          // Call API
          const response = await fetch("/api/chat/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query }),
          });

          const data = await response.json();

          // Add assistant response
          let citationsHtml = "";
          if (data.citations && data.citations.length > 0) {
            citationsHtml = '<div class="citations">';
            data.citations.forEach((cit) => {
              citationsHtml += `
                        <a href="/doc/${cit.document_id}#page-${cit.page_number}">
                            Doc ${cit.document_id}, Page ${cit.page_number}
                        </a>
                    `;
            });
            citationsHtml += "</div>";
          }

          messagesDiv.innerHTML += `
                <div class="message assistant-message">
                    <strong>Evident:</strong> ${data.answer}
                    ${citationsHtml}
                </div>
            `;

          // Clear input
          document.getElementById("query-input").value = "";

          // Scroll to bottom
          messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });
    </script>
  </body>
</html>
```

"""
