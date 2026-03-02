"""
Chat Service for Evident
Core service handling conversations, messages, AI integration, and tool execution
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple, Callable
from enum import Enum
import openai
import tiktoken

from auth.chat_models import (
    Conversation, Message, UserAPIKey, ChatSession, ChatToolCall, db
)
from auth.api_key_manager import api_key_manager
from auth.models import User
from services.tool_implementations import TOOL_EXECUTORS, execute_tool as execute_tool_impl

logger = logging.getLogger(__name__)


class ChatMessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ContextStrategy(str, Enum):
    """Context window management strategies"""
    ROLLING_WINDOW = "rolling_window"  # Keep most recent N messages
    SUMMARIZE = "summarize"  # Summarize older messages
    KEEP_FIRST_LAST = "keep_first_last"  # Keep first and last N messages


class ChatService:
    """Core chat service handling conversations and AI interaction"""
    
    # Token limits per model
    MODEL_CONTEXT_LIMITS = {
        'gpt-4': 8000,
        'gpt-4-turbo': 128000,
        'gpt-4-32k': 32000,
        'gpt-3.5-turbo': 4000,
        'gpt-3.5-turbo-16k': 16000,
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
    }
    
    # Approximate tokens per message overhead
    TOKENS_PER_MESSAGE = 4
    
    def __init__(self, user_id: int):
        """Initialize chat service for a user"""
        self.user_id = user_id
        self.user = User.query.get(user_id)
        if not self.user:
            raise ValueError(f"User {user_id} not found")
        
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def create_conversation(
        self,
        title: str = "New Conversation",
        system_role: str = "legal_assistant",
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_context_tokens: int = 8000,
        context_strategy: str = "rolling_window",
    ) -> Tuple[Conversation, str]:
        """
        Create a new conversation
        
        Args:
            title: Conversation title
            system_role: AI system role (legal_assistant, evidence_manager, etc.)
            model: Model to use
            temperature: Temperature for generation (0-1)
            max_context_tokens: Max tokens to use for context
            context_strategy: How to manage context window
            
        Returns:
            Tuple of (Conversation, status_message)
        """
        try:
            conversation = Conversation(
                user_id=self.user_id,
                title=title,
                system_role=system_role,
                model=model,
                temperature=temperature,
                max_context_tokens=max_context_tokens,
                context_strategy=context_strategy,
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            logger.info(f"Created conversation {conversation.id} for user {self.user_id}")
            return conversation, f"Conversation '{title}' created"
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating conversation: {e}")
            return None, f"Failed to create conversation: {str(e)}"
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation (with access check)"""
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=self.user_id
        ).first()
        
        if not conversation:
            logger.warning(f"Attempted access to non-existent conversation {conversation_id}")
        
        return conversation
    
    def list_conversations(self, include_archived: bool = False, limit: int = 50) -> List[Dict]:
        """List user's conversations"""
        try:
            query = Conversation.query.filter_by(user_id=self.user_id)
            
            if not include_archived:
                query = query.filter_by(is_archived=False)
            
            conversations = query.order_by(Conversation.updated_at.desc()).limit(limit).all()
            
            return [conv.to_dict() for conv in conversations]
        
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return []
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> Tuple[Message, str]:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_calls: Optional list of tool calls made
            tool_results: Optional list of tool results
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            
        Returns:
            Tuple of (Message, status_message)
        """
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return None, "Conversation not found"
            
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                tool_results=tool_results,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            
            # Update conversation stats
            conversation.total_input_tokens += input_tokens
            conversation.total_output_tokens += output_tokens
            conversation.updated_at = datetime.utcnow()
            
            db.session.add(message)
            db.session.add(conversation)
            db.session.commit()
            
            logger.info(f"Added {role} message to conversation {conversation_id}")
            return message, "Message added"
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding message: {e}")
            return None, f"Failed to add message: {str(e)}"
    
    def get_conversation_history(
        self,
        conversation_id: str,
        include_tool_results: bool = True,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get conversation history for API calls
        
        Args:
            conversation_id: Conversation ID
            include_tool_results: Whether to include tool results
            limit: Max messages to return (most recent)
            
        Returns:
            List of message dicts formatted for OpenAI API
        """
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return []
            
            query = Message.query.filter_by(
                conversation_id=conversation_id,
                is_deleted=False
            ).order_by(Message.created_at.asc())
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    'role': msg.role,
                    'content': msg.content,
                }
                
                # Include tool calls if present
                if msg.tool_calls and msg.role == ChatMessageRole.ASSISTANT:
                    formatted_msg['tool_calls'] = msg.get_tool_calls()
                
                # Include tool results if present
                if msg.tool_results and include_tool_results:
                    formatted_msg['tool_results'] = msg.tool_results
                
                formatted_messages.append(formatted_msg)
            
            return formatted_messages
        
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return len(text.split())  # Fallback to word count
    
    def manage_context_window(
        self,
        conversation_id: str,
        system_prompt_tokens: int,
        reserved_tokens: int = 500,  # Reserved for response
    ) -> List[Dict]:
        """
        Manage context window and apply context strategy
        
        Args:
            conversation_id: Conversation ID
            system_prompt_tokens: Tokens used by system prompt
            reserved_tokens: Tokens to reserve for response
            
        Returns:
            List of messages that fit in context window
        """
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return []
            
            max_tokens = conversation.max_context_tokens
            available_tokens = max_tokens - system_prompt_tokens - reserved_tokens
            
            if available_tokens < 500:
                logger.warning(f"Very limited context for conversation {conversation_id}")
            
            all_messages = self.get_conversation_history(conversation_id)
            
            if not all_messages:
                return all_messages
            
            # Apply context strategy
            if conversation.context_strategy == ContextStrategy.ROLLING_WINDOW:
                return self._apply_rolling_window(all_messages, available_tokens)
            
            elif conversation.context_strategy == ContextStrategy.KEEP_FIRST_LAST:
                return self._apply_keep_first_last(all_messages, available_tokens)
            
            else:  # summarize (not implemented yet)
                return self._apply_rolling_window(all_messages, available_tokens)
        
        except Exception as e:
            logger.error(f"Error managing context: {e}")
            return all_messages if 'all_messages' in locals() else []
    
    def _apply_rolling_window(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Keep most recent messages that fit in token limit"""
        current_tokens = 0
        result_messages = []
        
        # Work backwards from most recent
        for msg in reversed(messages):
            msg_tokens = self.count_tokens(msg.get('content', '')) + self.TOKENS_PER_MESSAGE
            
            if current_tokens + msg_tokens <= max_tokens:
                result_messages.append(msg)
                current_tokens += msg_tokens
            else:
                break
        
        return list(reversed(result_messages))
    
    def _apply_keep_first_last(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
        """Keep first message (context) plus most recent messages"""
        if not messages:
            return []
        
        result = [messages[0]]  # Keep first
        current_tokens = self.count_tokens(messages[0].get('content', ''))
        
        # Append most recent messages
        for msg in reversed(messages[1:]):
            msg_tokens = self.count_tokens(msg.get('content', '')) + self.TOKENS_PER_MESSAGE
            
            if current_tokens + msg_tokens <= max_tokens:
                result.append(msg)
                current_tokens += msg_tokens
            else:
                break
        
        return result
    
    def generate_response(
        self,
        conversation_id: str,
        user_message: str,
        system_prompt: str,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
    ) -> Tuple[str, Optional[List[Dict]], Dict]:
        """
        Generate AI response using OpenAI API
        
        Args:
            conversation_id: Conversation ID
            user_message: User's message
            system_prompt: System prompt for AI
            tools: Optional list of tools/functions
            tool_choice: Tool choice strategy
            
        Returns:
            Tuple of (response_content, tool_calls, usage_stats)
        """
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return None, None, {'error': 'Conversation not found'}
            
            # Get user's API key
            api_key = api_key_manager.get_api_key(self.user_id, 'openai')
            if not api_key:
                return None, None, {'error': 'No OpenAI API key configured'}
            
            # Set up OpenAI client
            client = openai.OpenAI(api_key=api_key)
            
            # Add user message to conversation
            user_msg, _ = self.add_message(conversation_id, ChatMessageRole.USER, user_message)
            
            # Get conversation history with context management
            system_prompt_tokens = self.count_tokens(system_prompt)
            context_messages = self.manage_context_window(
                conversation_id,
                system_prompt_tokens
            )
            
            # Build request payload
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context_messages)
            messages.append({"role": "user", "content": user_message})
            
            # Prepare API call
            api_kwargs = {
                'model': conversation.model,
                'messages': messages,
                'temperature': conversation.temperature,
                'max_tokens': 2000,
            }
            
            if tools:
                api_kwargs['tools'] = tools
                api_kwargs['tool_choice'] = tool_choice
            
            # Call OpenAI API
            response = client.chat.completions.create(**api_kwargs)
            
            # Extract response
            choice = response.choices[0]
            response_content = choice.message.content or ""
            tool_calls = None
            
            # Handle tool calls
            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                tool_calls = [
                    {
                        'name': tc.function.name,
                        'args': json.loads(tc.function.arguments),
                        'id': tc.id
                    }
                    for tc in choice.message.tool_calls
                ]
            
            # Record usage
            usage_stats = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
            }
            
            # Store assistant message
            self.add_message(
                conversation_id,
                ChatMessageRole.ASSISTANT,
                response_content,
                tool_calls=tool_calls,
                input_tokens=usage_stats['input_tokens'],
                output_tokens=usage_stats['output_tokens'],
            )
            
            # Update user's API key usage
            user_key = UserAPIKey.query.filter_by(
                user_id=self.user_id,
                service_name='openai',
                is_active=True
            ).first()
            
            if user_key:
                # Rough cost calculation (GPT-4 pricing)
                input_cost = (usage_stats['input_tokens'] / 1000) * 0.03
                output_cost = (usage_stats['output_tokens'] / 1000) * 0.06
                total_cost = input_cost + output_cost
                
                user_key.mark_used(
                    tokens_used=usage_stats['total_tokens'],
                    cost=total_cost
                )
                db.session.commit()
            
            logger.info(f"Generated response for conversation {conversation_id}")
            return response_content, tool_calls, usage_stats
        
        except openai.AuthenticationError:
            return None, None, {'error': 'Invalid OpenAI API key'}
        except openai.RateLimitError:
            return None, None, {'error': 'OpenAI rate limit exceeded'}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None, None, {'error': str(e)}
    
    def execute_tool(
        self,
        conversation_id: str,
        tool_name: str,
        tool_args: Dict,
    ) -> Tuple[bool, Any, Dict]:
        """
        Execute a tool and store results
        Routes to real tool implementations in tool_implementations.py
        
        Args:
            conversation_id: Conversation ID
            tool_name: Name of tool to execute
            tool_args: Arguments to pass to tool
            
        Returns:
            Tuple of (success, result, metadata)
        """
        try:
            start_time = datetime.utcnow()
            
            # Use real tool implementation
            result = execute_tool_impl(tool_name, tool_args)
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            success = result.get('status') == 'success'
            
            # Get latest message (should be from assistant)
            latest_msg = Message.query.filter_by(
                conversation_id=conversation_id,
                role=ChatMessageRole.ASSISTANT
            ).order_by(Message.created_at.desc()).first()
            
            if latest_msg:
                tool_call = ChatToolCall(
                    message_id=latest_msg.id,
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_result=result,
                    execution_time_ms=int(execution_time),
                    success=success,
                )
                db.session.add(tool_call)
                db.session.commit()
            
            logger.info(f"Executed tool {tool_name} in {execution_time:.0f}ms - {'success' if success else 'failed'}")
            return success, result, {'execution_time_ms': int(execution_time), 'tool': tool_name}
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return False, None, {'error': str(e), 'tool': tool_name}
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete/archive a conversation"""
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            conversation.is_archived = True
            db.session.commit()
            
            logger.info(f"Archived conversation {conversation_id}")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    def export_conversation(self, conversation_id: str, format: str = 'json') -> Optional[str]:
        """Export conversation to JSON or Markdown"""
        try:
            conversation = self.get_conversation(conversation_id)
            if not conversation:
                return None
            
            history = self.get_conversation_history(conversation_id)
            
            if format == 'json':
                export_data = {
                    'conversation_id': conversation_id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'messages': history,
                }
                return json.dumps(export_data, indent=2)
            
            elif format == 'markdown':
                lines = [f"# {conversation.title}\n"]
                for msg in history:
                    role = msg['role'].capitalize()
                    content = msg['content']
                    lines.append(f"\n**{role}:**\n{content}")
                
                return '\n'.join(lines)
            
            return None
        
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return None


# Helper to create chat service instance
def get_chat_service(user_id: int) -> ChatService:
    """Factory function to create chat service"""
    return ChatService(user_id)
