"""
Chat API Routes for Evident
REST endpoints for chat functionality (conversations, messages, API keys)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc

from auth.chat_models import (
    Conversation, Message, UserAPIKey, ChatSession, db, ChatToolCall
)
from auth.api_key_manager import api_key_manager
from auth.prompt_templates import get_system_prompt, ChatRole
from services.chat_service import get_chat_service, ChatMessageRole
from services.chat_tools import EvidentChatTools, execute_tool

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


def rate_limit(calls_per_minute=30):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limit check (in production, use Redis)
            user_id = current_user.id
            key = f"rate_limit:{user_id}:{request.path}"
            
            # For now, just allow through - implement with Redis in production
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@chat_bp.route('/conversations', methods=['POST'])
@login_required
@rate_limit(calls_per_minute=20)
def create_conversation():
    """
    Create a new conversation
    
    POST /api/chat/conversations
    {
        "title": "Q4 Contract Review",
        "system_role": "legal_assistant",
        "model": "gpt-4",
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json() or {}
        
        chat_service = get_chat_service(current_user.id)
        conversation, message = chat_service.create_conversation(
            title=data.get('title', 'New Conversation'),
            system_role=data.get('system_role', 'legal_assistant'),
            model=data.get('model', 'gpt-4'),
            temperature=float(data.get('temperature', 0.7)),
            max_context_tokens=int(data.get('max_context_tokens', 8000)),
            context_strategy=data.get('context_strategy', 'rolling_window'),
        )
        
        if not conversation:
            return jsonify({'error': message}), 400
        
        # Create session token
        import secrets
        session_token = secrets.token_urlsafe(32)
        session = ChatSession(
            user_id=current_user.id,
            conversation_id=conversation.id,
            session_token=session_token,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'session_token': session_token
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        return jsonify({'error': 'Failed to create conversation'}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id: str):
    """
    Get conversation details
    
    GET /api/chat/conversations/{conversation_id}
    """
    try:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'message_count': conversation.messages.count()
        })
    
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return jsonify({'error': 'Failed to get conversation'}), 500


@chat_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    """
    List user's conversations
    
    GET /api/chat/conversations?archived=false&limit=50
    """
    try:
        include_archived = request.args.get('archived', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        chat_service = get_chat_service(current_user.id)
        conversations = chat_service.list_conversations(
            include_archived=include_archived,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'count': len(conversations)
        })
    
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        return jsonify({'error': 'Failed to list conversations'}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id: str):
    """
    Archive/delete a conversation
    
    DELETE /api/chat/conversations/{conversation_id}
    """
    try:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        conversation.is_archived = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Conversation archived'
        })
    
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({'error': 'Failed to delete conversation'}), 500


# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@chat_bp.route('/messages', methods=['POST'])
@login_required
@rate_limit(calls_per_minute=30)
def send_message():
    """
    Send a message and get AI response (with tool execution)
    
    POST /api/chat/messages
    {
        "conversation_id": "conv-123",
        "message": "Tell me about Marbury v. Madison",
        "use_tools": true
    }
    """
    try:
        data = request.get_json() or {}
        conversation_id = data.get('conversation_id')
        user_message = data.get('message', '').strip()
        use_tools = data.get('use_tools', True)
        
        if not conversation_id:
            return jsonify({'error': 'conversation_id required'}), 400
        
        if not user_message:
            return jsonify({'error': 'message required'}), 400
        
        if len(user_message) > 10000:
            return jsonify({'error': 'message too long (max 10000 chars)'}), 400
        
        # Get conversation and verify access
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Check if user has OpenAI key
        api_key = api_key_manager.get_api_key(current_user.id, 'openai')
        if not api_key:
            return jsonify({
                'error': 'No OpenAI API key configured',
                'action': 'configure_api_key'
            }), 400
        
        # Get chat service and generate response
        chat_service = get_chat_service(current_user.id)
        
        # Build system prompt
        system_prompt = get_system_prompt(conversation.system_role, include_tools=use_tools)
        
        # Prepare tools if enabled
        tools = EvidentChatTools.get_all_tools() if use_tools else None
        
        # Generate AI response
        response_content, tool_calls, usage = chat_service.generate_response(
            conversation_id=conversation_id,
            user_message=user_message,
            system_prompt=system_prompt,
            tools=tools,
            tool_choice="auto" if use_tools else "none"
        )
        
        if response_content is None:
            error_msg = usage.get('error', 'Failed to generate response')
            return jsonify({'error': error_msg}), 400
        
        # Process tool calls if any
        tool_results = []
        if tool_calls and use_tools:
            for tool_call in tool_calls:
                tool_name = tool_call.get('name')
                tool_args = tool_call.get('args', {})
                
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                
                # Execute tool
                success, result, metadata = chat_service.execute_tool(
                    conversation_id,
                    tool_name,
                    tool_args
                )
                
                tool_results.append({
                    'tool_name': tool_name,
                    'success': success,
                    'result': result,
                    'metadata': metadata
                })
        
        return jsonify({
            'success': True,
            'message': response_content,
            'tool_calls': tool_calls,
            'tool_results': tool_results,
            'usage': usage,
            'conversation_id': conversation_id,
        }), 201
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id: str):
    """
    Get conversation history
    
    GET /api/chat/conversations/{conversation_id}/messages?limit=50
    """
    try:
        limit = int(request.args.get('limit', 50))
        
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user.id
        ).first()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        chat_service = get_chat_service(current_user.id)
        messages = chat_service.get_conversation_history(conversation_id, limit=limit)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages),
            'conversation_id': conversation_id
        })
    
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({'error': 'Failed to get messages'}), 500


# ============================================================================
# TOOL ENDPOINTS
# ============================================================================

@chat_bp.route('/tools', methods=['GET'])
@login_required
def get_tools():
    """
    Get list of available tools and their descriptions
    
    GET /api/chat/tools
    """
    try:
        tools = EvidentChatTools.get_all_tools()
        descriptions = EvidentChatTools.get_tool_descriptions()
        
        return jsonify({
            'success': True,
            'tools': tools,
            'descriptions': descriptions,
            'tool_count': len(tools)
        })
    
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return jsonify({'error': 'Failed to get tools'}), 500


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

@chat_bp.route('/api-keys', methods=['GET'])
@login_required
def list_api_keys():
    """
    List user's API keys (keys hidden for security)
    
    GET /api/chat/api-keys
    """
    try:
        keys = api_key_manager.list_api_keys(current_user.id)
        
        return jsonify({
            'success': True,
            'api_keys': keys,
            'count': len(keys)
        })
    
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        return jsonify({'error': 'Failed to list API keys'}), 500


@chat_bp.route('/api-keys', methods=['POST'])
@login_required
@rate_limit(calls_per_minute=10)
def add_api_key():
    """
    Add/update an API key
    
    POST /api/chat/api-keys
    {
        "service_name": "openai",
        "api_key": "sk-...",
        "validate": true
    }
    """
    try:
        data = request.get_json() or {}
        service_name = data.get('service_name', '').strip()
        api_key = data.get('api_key', '').strip()
        should_validate = data.get('validate', True)
        
        if not service_name or not api_key:
            return jsonify({'error': 'service_name and api_key required'}), 400
        
        # Optional: validate before storing
        if should_validate:
            is_valid, validation_msg = api_key_manager.validate_api_key(
                service_name,
                api_key,
                data.get('endpoint_url')
            )
            
            if not is_valid:
                return jsonify({
                    'error': f'API key validation failed: {validation_msg}'
                }), 400
        
        # Store key
        user_key, message = api_key_manager.store_api_key(
            current_user.id,
            service_name,
            api_key,
            metadata=data.get('metadata')
        )
        
        if not user_key:
            return jsonify({'error': message}), 400
        
        return jsonify({
            'success': True,
            'api_key': user_key.to_dict(),
            'message': message
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding API key: {e}")
        return jsonify({'error': 'Failed to store API key'}), 500


@chat_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id: str):
    """
    Delete an API key
    
    DELETE /api/chat/api-keys/{key_id}
    """
    try:
        success = api_key_manager.delete_api_key(key_id, current_user.id)
        
        if not success:
            return jsonify({'error': 'API key not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'API key deleted'
        })
    
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        return jsonify({'error': 'Failed to delete API key'}), 500


@chat_bp.route('/api-keys/<key_id>/validate', methods=['POST'])
@login_required
def validate_api_key(key_id: str):
    """
    Validate an API key
    
    POST /api/chat/api-keys/{key_id}/validate
    """
    try:
        user_key = UserAPIKey.query.filter_by(
            id=key_id,
            user_id=current_user.id
        ).first()
        
        if not user_key:
            return jsonify({'error': 'API key not found'}), 404
        
        is_valid, message = api_key_manager.validate_user_key(
            current_user.id,
            user_key.service_name
        )
        
        return jsonify({
            'success': is_valid,
            'message': message,
            'is_valid': is_valid,
            'service_name': user_key.service_name
        })
    
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return jsonify({'error': 'Failed to validate API key'}), 500


# ============================================================================
# USAGE AND STATISTICS ENDPOINTS
# ============================================================================

@chat_bp.route('/usage', methods=['GET'])
@login_required
def get_usage():
    """
    Get user's API usage and cost statistics
    
    GET /api/chat/usage
    """
    try:
        usage = api_key_manager.get_total_usage(current_user.id)
        
        # Get conversation statistics
        conversations = Conversation.query.filter_by(user_id=current_user.id).all()
        total_tokens = sum(c.total_input_tokens + c.total_output_tokens for c in conversations)
        
        return jsonify({
            'success': True,
            'api_usage': usage,
            'conversation_stats': {
                'total_conversations': len(conversations),
                'total_tokens_used': total_tokens,
                'total_cost': usage.get('total_cost', 0)
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return jsonify({'error': 'Failed to get usage stats'}), 500


@chat_bp.route('/export/<conversation_id>', methods=['GET'])
@login_required
def export_conversation(conversation_id: str):
    """
    Export conversation (JSON or Markdown)
    
    GET /api/chat/export/{conversation_id}?format=json
    """
    try:
        format_type = request.args.get('format', 'json')
        
        if format_type not in ['json', 'markdown']:
            return jsonify({'error': 'format must be json or markdown'}), 400
        
        chat_service = get_chat_service(current_user.id)
        export_data = chat_service.export_conversation(conversation_id, format_type)
        
        if not export_data:
            return jsonify({'error': 'Conversation not found'}), 404
        
        response_type = 'application/json' if format_type == 'json' else 'text/markdown'
        
        return export_data, 200, {
            'Content-Type': response_type,
            'Content-Disposition': f'attachment; filename="conversation.{format_type}"'
        }
    
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        return jsonify({'error': 'Failed to export conversation'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@chat_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized - please log in'}), 401


@chat_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden - insufficient permissions'}), 403


@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
