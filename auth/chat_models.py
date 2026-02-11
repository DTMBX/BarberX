"""
Chat Models for Evident Chat Service
Stores conversations, messages, and user API keys
"""

import uuid
import json
from datetime import datetime
from sqlalchemy import Index
from auth.models import db


class Conversation(db.Model):
    """Stores chat conversations"""
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, default='New Conversation')
    system_role = db.Column(
        db.String(50), 
        nullable=False, 
        default='legal_assistant',
        comment='Role: legal_assistant, evidence_manager, case_analyzer, research_specialist'
    )
    model = db.Column(db.String(50), default='gpt-4', nullable=False)
    temperature = db.Column(db.Float, default=0.7, nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    
    # Token tracking
    total_input_tokens = db.Column(db.Integer, default=0, nullable=False)
    total_output_tokens = db.Column(db.Integer, default=0, nullable=False)
    estimated_cost = db.Column(db.Float, default=0.0, nullable=False)
    
    # Context management
    max_context_tokens = db.Column(db.Integer, default=8000, nullable=False)
    context_strategy = db.Column(
        db.String(50),
        default='rolling_window',
        nullable=False,
        comment='rolling_window, summarize, or keep_first_last'
    )
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='conversations')
    
    # Indexes for fast queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_user_archived', 'user_id', 'is_archived'),
    )
    
    def __repr__(self):
        return f'<Conversation {self.id[:8]}... ({self.title})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'system_role': self.system_role,
            'model': self.model,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_archived': self.is_archived,
            'is_public': self.is_public,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'estimated_cost': self.estimated_cost,
            'message_count': self.messages.count()
        }


class Message(db.Model):
    """Stores individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('chat_conversations.id'), nullable=False, index=True)
    
    role = db.Column(
        db.String(20),
        nullable=False,
        index=True,
        comment='user, assistant, or system'
    )
    content = db.Column(db.Text, nullable=False)
    
    # For assistant messages with tool usage
    tool_calls = db.Column(db.JSON, nullable=True, default=None)  # Array of tool call objects
    tool_results = db.Column(db.JSON, nullable=True, default=None)  # Results from tool execution
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Token tracking
    input_tokens = db.Column(db.Integer, default=0, nullable=False)
    output_tokens = db.Column(db.Integer, default=0, nullable=False)
    
    # Optional metadata
    message_metadata = db.Column(db.JSON, nullable=True)  # Custom metadata dict
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # 'conversation' backref is created by Conversation.messages relationship
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_role', 'role'),
    )
    
    def __repr__(self):
        preview = self.content[:50] if self.content else '(empty)'
        return f'<Message {self.role}: {preview}...>'
    
    def to_dict(self, include_content=True):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content if include_content else None,
            'tool_calls': self.tool_calls,
            'tool_results': self.tool_results,
            'created_at': self.created_at.isoformat(),
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'metadata': self.message_metadata,
        }
    
    def get_tool_calls(self):
        """Get parsed tool calls"""
        if not self.tool_calls:
            return []
        if isinstance(self.tool_calls, str):
            return json.loads(self.tool_calls)
        return self.tool_calls


class UserAPIKey(db.Model):
    """Stores user's encrypted API keys for various services"""
    __tablename__ = 'user_api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    service_name = db.Column(
        db.String(100),
        nullable=False,
        comment='openai, anthropic, cohere, huggingface, custom_url, etc.'
    )
    
    # Encrypted key storage
    encrypted_key = db.Column(db.Text, nullable=False)
    
    # Key metadata
    key_version = db.Column(db.Integer, default=1, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Validation info
    is_validated = db.Column(db.Boolean, default=False, nullable=False)
    validation_error = db.Column(db.String(500), nullable=True)
    
    # Usage tracking
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    last_validated_at = db.Column(db.DateTime, nullable=True)
    
    # Billing/usage tracking
    total_requests = db.Column(db.Integer, default=0, nullable=False)
    total_cost = db.Column(db.Float, default=0.0, nullable=False)
    monthly_cost = db.Column(db.Float, default=0.0, nullable=False)
    
    # Optional metadata (e.g., endpoint URL for custom providers)
    provider_metadata = db.Column(db.JSON, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='api_keys')
    
    # Indexes
    __table_args__ = (
        Index('idx_user_service', 'user_id', 'service_name'),
        Index('idx_active_validated', 'is_active', 'is_validated'),
    )
    
    def __repr__(self):
        return f'<APIKey {self.service_name} (user={self.user_id}, active={self.is_active})>'
    
    def to_dict(self, include_key=False):
        """Return dict representation (key hidden by default for security)"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'key': f'{self.encrypted_key[:10]}...' if include_key else None,
            'is_active': self.is_active,
            'is_validated': self.is_validated,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'total_requests': self.total_requests,
            'total_cost': self.total_cost,
            'monthly_cost': self.monthly_cost,
        }
    
    def mark_used(self, tokens_used=0, cost=0.0):
        """Record that this key was used"""
        self.last_used_at = datetime.utcnow()
        self.total_requests += 1
        self.total_cost += cost
        self.monthly_cost += cost
    
    def mark_validated(self, success=True, error=None):
        """Record validation result"""
        self.is_validated = success
        self.validation_error = error
        self.last_validated_at = datetime.utcnow()


class ChatSession(db.Model):
    """Tracks active chat sessions for real-time updates"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('chat_conversations.id'), nullable=False, index=True)
    
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    
    # Session metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', backref='chat_sessions')
    conversation = db.relationship('Conversation')
    
    def __repr__(self):
        return f'<ChatSession {self.id[:8]}... (user={self.user_id})>'
    
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        db.session.commit()


class ChatToolCall(db.Model):
    """Tracks individual tool calls for audit and debugging"""
    __tablename__ = 'chat_tool_calls'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = db.Column(db.String(36), db.ForeignKey('chat_messages.id'), nullable=False, index=True)
    
    tool_name = db.Column(db.String(100), nullable=False, index=True)
    tool_args = db.Column(db.JSON, nullable=False)
    tool_result = db.Column(db.JSON, nullable=True)
    
    # Execution info
    execution_time_ms = db.Column(db.Integer, nullable=True)
    success = db.Column(db.Boolean, nullable=True)
    error = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    message = db.relationship('Message')
    
    __table_args__ = (
        Index('idx_message_tool', 'message_id', 'tool_name'),
    )
    
    def __repr__(self):
        return f'<ToolCall {self.tool_name} (success={self.success})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tool_name': self.tool_name,
            'tool_args': self.tool_args,
            'tool_result': self.tool_result,
            'execution_time_ms': self.execution_time_ms,
            'success': self.success,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
        }
