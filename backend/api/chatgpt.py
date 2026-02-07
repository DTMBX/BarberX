# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
ChatGPT API endpoints for Evident
Handles chat completions, project management, and conversation history
"""

import json
from datetime import datetime

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_login import login_required
from sqlalchemy import desc

from chatgpt_service import ChatGPTService
from models_auth import db
from tier_gating import check_tier_access

# Create blueprint
chatgpt_bp = Blueprint("chatgpt", __name__, url_prefix="/api/v1")


# Database Models
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


class Project(db.Model):
    """Project/Workspace for organizing conversations"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    custom_instructions = Column(Text)
    model_preference = Column(String(50), default="gpt-4")
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="projects")
    conversations = relationship(
        "Conversation", back_populates="project", cascade="all, delete-orphan"
    )


class Conversation(db.Model):
    """Conversation thread within a project"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="conversations")
    user = relationship("User")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(db.Model):
    """Individual message in a conversation"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'system', 'user', 'assistant'
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    model = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class UserApiKey(db.Model):
    """Store encrypted user API keys"""

    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'openai', 'anthropic'
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    quota_used = Column(Integer, default=0)
    last_validated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")


# Helper functions
def get_user_api_key(user_id, provider="openai"):
    """Get user's API key for a provider"""
    import os

    from cryptography.fernet import Fernet

    key_record = UserApiKey.query.filter_by(
        user_id=user_id, provider=provider, is_active=True
    ).first()

    if not key_record:
        return None

    # Decrypt the key
    encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY", "default-key-change-this")
    fernet = Fernet(encryption_key.encode())

    try:
        decrypted_key = fernet.decrypt(key_record.encrypted_key.encode()).decode()
        return decrypted_key
    except:
        return None


def encrypt_api_key(api_key):
    """Encrypt an API key for storage"""
    import os

    from cryptography.fernet import Fernet

    encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY", "default-key-change-this")
    fernet = Fernet(encryption_key.encode())

    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


# Routes
@chatgpt_bp.route("/chat/completions", methods=["POST"])
@check_tier_access("ai_analysis")
def chat_completion():
    """
    Send a message and get GPT response

    Request JSON:
        {
            "project_id": 123,
            "conversation_id": 456,  // Optional
            "message": "Analyze this evidence",
            "include_context": true,
            "stream": false
        }
    """
    try:
        from flask_login import current_user

        data = request.get_json()
        project_id = data.get("project_id")
        conversation_id = data.get("conversation_id")
        message_content = data.get("message")
        _include_context = data.get("include_context", True)  # Reserved for future use
        stream = data.get("stream", False)

        if not project_id or not message_content:
            return jsonify({"error": "project_id and message are required"}), 400

        # Get project
        project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Get or create conversation
        if conversation_id:
            conversation = Conversation.query.filter_by(
                id=conversation_id, project_id=project_id, user_id=current_user.id
            ).first()

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404
        else:
            # Create new conversation
            conversation = Conversation(
                project_id=project_id,
                user_id=current_user.id,
                title=message_content[:50],  # Use first 50 chars as title
            )
            db.session.add(conversation)
            db.session.commit()

        # Get user's API key
        user_api_key = get_user_api_key(current_user.id)

        if not user_api_key:
            return (
                jsonify(
                    {"error": "No OpenAI API key configured. Please add your API key in settings."}
                ),
                400,
            )

        # Initialize ChatGPT service with user's key
        chatgpt = ChatGPTService(api_key=user_api_key)

        # Build messages array
        messages = []

        # Add system prompt
        system_prompt = chatgpt.build_legal_system_prompt(project.custom_instructions)
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        history_messages = (
            Message.query.filter_by(conversation_id=conversation.id)
            .order_by(Message.created_at)
            .limit(20)
            .all()
        )  # Last 20 messages

        for msg in history_messages:
            if msg.role != "system":  # Skip system messages in history
                messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": message_content})

        # Save user message
        user_message = Message(
            conversation_id=conversation.id, role="user", content=message_content
        )
        db.session.add(user_message)
        db.session.commit()

        # Get completion from OpenAI
        if stream:
            # Streaming response
            def generate():
                full_content = ""
                for chunk in chatgpt.create_chat_completion_stream(
                    messages=messages,
                    model=project.model_preference,
                    max_tokens=project.max_tokens,
                    temperature=project.temperature,
                ):
                    if chunk.get("success"):
                        content = chunk.get("content", "")
                        full_content += content
                        yield f"data: {json.dumps(chunk)}\n\n"

                    if chunk.get("finish_reason") == "stop":
                        # Save assistant message
                        assistant_message = Message(
                            conversation_id=conversation.id,
                            role="assistant",
                            content=full_content,
                            model=project.model_preference,
                        )
                        db.session.add(assistant_message)
                        db.session.commit()

                        yield f"data: {json.dumps({'done': True, 'message_id': assistant_message.id})}\n\n"

            return Response(stream_with_context(generate()), mimetype="text/event-stream")
        else:
            # Regular response
            response = chatgpt.create_chat_completion(
                messages=messages,
                model=project.model_preference,
                max_tokens=project.max_tokens,
                temperature=project.temperature,
            )

            if not response.get("success"):
                return jsonify({"error": response.get("error")}), 500

            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=response["content"],
                tokens_used=response.get("tokens_used"),
                model=response.get("model"),
            )
            db.session.add(assistant_message)
            db.session.commit()

            return jsonify(
                {
                    "conversation_id": conversation.id,
                    "message_id": assistant_message.id,
                    "role": "assistant",
                    "content": response["content"],
                    "tokens_used": response.get("tokens_used"),
                    "model": response.get("model"),
                }
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chatgpt_bp.route("/projects", methods=["GET"])
def get_projects():
    """Get user's projects"""
    from flask_login import current_user

    projects = (
        Project.query.filter_by(user_id=current_user.id).order_by(desc(Project.updated_at)).all()
    )

    return jsonify(
        {
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "custom_instructions": p.custom_instructions,
                    "model_preference": p.model_preference,
                    "conversation_count": len(p.conversations),
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in projects
            ]
        }
    )


@chatgpt_bp.route("/projects", methods=["POST"])
def create_project():
    """Create new project"""
    from flask_login import current_user

    data = request.get_json()

    project = Project(
        user_id=current_user.id,
        name=data.get("name"),
        description=data.get("description"),
        custom_instructions=data.get("custom_instructions"),
        model_preference=data.get("model_preference", "gpt-4"),
    )

    db.session.add(project)
    db.session.commit()

    return (
        jsonify(
            {"id": project.id, "name": project.name, "message": "Project created successfully"}
        ),
        201,
    )


@chatgpt_bp.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    """Update project settings"""
    from flask_login import current_user

    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()

    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]
    if "custom_instructions" in data:
        project.custom_instructions = data["custom_instructions"]
    if "model_preference" in data:
        project.model_preference = data["model_preference"]

    db.session.commit()

    return jsonify({"message": "Project updated successfully"})


@chatgpt_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete project and all conversations"""
    from flask_login import current_user

    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()

    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({"message": "Project deleted successfully"})


@chatgpt_bp.route("/conversations", methods=["GET"])
def get_conversations():
    """Get conversations for a project"""
    from flask_login import current_user

    project_id = request.args.get("project_id", type=int)

    if not project_id:
        return jsonify({"error": "project_id required"}), 400

    conversations = (
        Conversation.query.filter_by(project_id=project_id, user_id=current_user.id)
        .order_by(desc(Conversation.updated_at))
        .all()
    )

    return jsonify(
        {
            "conversations": [
                {
                    "id": c.id,
                    "project_id": c.project_id,
                    "title": c.title,
                    "message_count": len(c.messages),
                    "last_message_at": (
                        c.messages[-1].created_at.isoformat() if c.messages else None
                    ),
                    "created_at": c.created_at.isoformat(),
                }
                for c in conversations
            ]
        }
    )


@chatgpt_bp.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
def get_messages(conversation_id):
    """Get all messages in a conversation"""
    from flask_login import current_user

    conversation = Conversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()

    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404

    messages = (
        Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    )

    return jsonify(
        {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "project_id": conversation.project_id,
            },
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "tokens_used": m.tokens_used,
                    "model": m.model,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
        }
    )


@chatgpt_bp.route("/openai/validate-key", methods=["POST"])
@login_required
def validate_api_key():
    """Validate OpenAI API key"""
    data = request.get_json()
    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    chatgpt = ChatGPTService()
    result = chatgpt.validate_api_key(api_key)

    return jsonify(result)


@chatgpt_bp.route("/user/api-keys", methods=["POST"])
@login_required
def store_api_key():
    """Store encrypted API key"""
    from flask_login import current_user

    data = request.get_json()
    provider = data.get("provider", "openai")
    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "api_key required"}), 400

    # Ensure encryption key is configured safely
    import os

    encryption_key = os.getenv("API_KEY_ENCRYPTION_KEY", "default-key-change-this")
    if encryption_key == "default-key-change-this":
        return (
            jsonify(
                {
                    "error": "API key encryption is not configured. Please set API_KEY_ENCRYPTION_KEY.",
                }
            ),
            500,
        )

    # Validate key first
    chatgpt = ChatGPTService()
    validation = chatgpt.validate_api_key(api_key)

    if not validation.get("valid"):
        return jsonify({"error": "Invalid API key"}), 400

    # Deactivate old keys
    UserApiKey.query.filter_by(user_id=current_user.id, provider=provider).update(
        {"is_active": False}
    )

    # Encrypt and store new key
    encrypted_key = encrypt_api_key(api_key)

    key_record = UserApiKey(
        user_id=current_user.id,
        provider=provider,
        encrypted_key=encrypted_key,
        is_active=True,
        last_validated=datetime.utcnow(),
    )

    db.session.add(key_record)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "API key stored successfully",
                "masked_key": f"{api_key[:7]}...{api_key[-4:]}",
            }
        ),
        201,
    )


@chatgpt_bp.route("/user/api-keys", methods=["GET"])
@login_required
def get_api_keys():
    """Get user's stored API keys (masked)"""
    from flask_login import current_user

    keys = UserApiKey.query.filter_by(user_id=current_user.id).all()

    return jsonify(
        {
            "keys": [
                {
                    "id": k.id,
                    "provider": k.provider,
                    "masked_key": "sk-...***",  # Don't expose even masked key
                    "is_active": k.is_active,
                    "last_validated": k.last_validated.isoformat() if k.last_validated else None,
                    "created_at": k.created_at.isoformat(),
                }
                for k in keys
            ]
        }
    )
