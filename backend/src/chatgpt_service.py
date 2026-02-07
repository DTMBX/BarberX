from typing import Optional
# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
ChatGPT Integration Service for Evident
Handles OpenAI API interactions with user-provided API keys
"""

import os
from typing import Any

import openai


class ChatGPTService:
    """Service for interacting with OpenAI's ChatGPT API"""

Optional[def __init__(self, api_key: str] = None):
        """
        Initialize ChatGPT service

        Args:
            api_key: User's OpenAI API key. If None, uses environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def validate_api_key(self, api_key: str) -> dict[str, Any]:
        """
        Validate an OpenAI API key

        Args:
            api_key: The API key to validate

        Returns:
            dict: Validation result with organization, quota info
        """
        try:
            # Set the API key temporarily
            openai.api_key = api_key

            # Make a minimal API call to validate
            response = openai.models.list()

            # Get models available
            models_available = [model.id for model in response.data if "gpt" in model.id.lower()]

            return {
                "valid": True,
                "models_available": models_available,
                "organization": getattr(response, "organization", None),
            }

        except openai.AuthenticationError:
            return {"valid": False, "error": "Invalid API key"}
        except Exception as e:
            return {"valid": False, "error": str(e)}
        finally:
            # Restore original API key
            openai.api_key = self.api_key

    def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Create a chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
            max_tokens: Maximum tokens in response
            temperature: Creativity (0-2)
            stream: Whether to stream the response

        Returns:
            dict: Response with content and metadata
        """
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
            )

            if stream:
                return response  # Return generator for streaming

            # Extract response data
            message = response.choices[0].message

            return {
                "success": True,
                "content": message.content,
                "role": message.role,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except openai.RateLimitError:
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "error_type": "rate_limit",
            }
        except openai.APIError as e:
            return {
                "success": False,
                "error": f"OpenAI API error: {str(e)}",
                "error_type": "api_error",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "error_type": "unknown"}

    def create_chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ):
        """
        Create a streaming chat completion

        Yields chunks of the response as they arrive
        """
        try:
            stream = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "success": True,
                        "content": chunk.choices[0].delta.content,
                        "finish_reason": chunk.choices[0].finish_reason,
                    }

        except Exception as e:
            yield {"success": False, "error": str(e)}

Optional[def build_legal_system_prompt(self, custom_instructions: str] = None) -> str:
        """
        Build system prompt for legal analysis

        Args:
            custom_instructions: User's custom instructions to append

        Returns:
            str: Complete system prompt
        """
        base_prompt = """You are an expert legal assistant specializing in criminal defense and civil rights litigation. Your expertise includes:

1. Constitutional Law & Civil Rights
   - Brady violations and discovery issues
   - Fourth Amendment (search and seizure)
   - Fifth Amendment (self-incrimination)
   - Sixth Amendment (right to counsel)
   - Fourteenth Amendment (due process, equal protection)

2. Criminal Procedure
   - Evidence admissibility
   - Chain of custody
   - Police misconduct
   - Prosecutorial misconduct
   - Witness credibility

3. BWC & Evidence Analysis
   - Body-worn camera footage review
   - Timeline reconstruction
   - Inconsistency detection
   - Officer statement analysis

When analyzing evidence:
- Be thorough and cite specific legal standards
- Identify potential constitutional violations
- Highlight inconsistencies in officer testimony
- Suggest relevant case law when applicable
- Use clear, professional language suitable for court filings

IMPORTANT: You are an AI assistant, not a licensed attorney. Always remind users to consult with a licensed attorney for legal advice."""

        if custom_instructions:
            base_prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

        return base_prompt

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Uses rough approximation: 1 token ≈ 4 characters

        Args:
            text: Text to estimate

        Returns:
            int: Estimated token count
        """
        return len(text) // 4

    def truncate_context(self, context: str, max_tokens: int = 8000) -> str:
        """
        Truncate context to fit within token limit

        Args:
            context: Full context text
            max_tokens: Maximum tokens allowed

        Returns:
            str: Truncated context
        """
        estimated_tokens = self.estimate_tokens(context)

        if estimated_tokens <= max_tokens:
            return context

        # Truncate to approximate character count
        max_chars = max_tokens * 4
        return context[:max_chars] + "\n\n[Context truncated due to length...]"