"""LLM provider abstraction — generate_answer with citations context."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Interface for LLM providers."""

    @abstractmethod
    def generate_answer(
        self,
        prompt: str,
        citations_context: str,
        system_prompt: str | None = None,
    ) -> dict:
        """Return {"text": str, "citations": list[dict]}."""
        ...


class DisabledProvider(LLMProvider):
    """No LLM configured — returns context and CourtListener results only."""

    def generate_answer(self, prompt: str, citations_context: str, system_prompt: str | None = None) -> dict:
        return {
            "text": (
                "LLM provider is disabled. Below is the relevant context found from "
                "internal documents and CourtListener search results. "
                "Configure LLM_PROVIDER in your environment to enable AI-generated answers.\n\n"
                f"--- Context ---\n{citations_context[:3000]}"
            ),
            "citations": [],
        }


class OpenAIProvider(LLMProvider):
    """OpenAI ChatCompletion provider."""

    def generate_answer(self, prompt: str, citations_context: str, system_prompt: str | None = None) -> dict:
        try:
            import openai

            client = openai.OpenAI(api_key=settings.openai_api_key)
            sys_msg = system_prompt or _default_system_prompt()
            messages = [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": f"Context:\n{citations_context}\n\nQuestion: {prompt}"},
            ]
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2048,
                temperature=0.2,
            )
            text = response.choices[0].message.content or ""
            return {"text": text, "citations": []}
        except Exception as exc:
            logger.error("OpenAI provider error: %s", exc)
            return {"text": f"Error calling OpenAI: {exc}", "citations": []}


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def generate_answer(self, prompt: str, citations_context: str, system_prompt: str | None = None) -> dict:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            sys_msg = system_prompt or _default_system_prompt()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=sys_msg,
                messages=[
                    {"role": "user", "content": f"Context:\n{citations_context}\n\nQuestion: {prompt}"},
                ],
            )
            text = response.content[0].text if response.content else ""
            return {"text": text, "citations": []}
        except Exception as exc:
            logger.error("Anthropic provider error: %s", exc)
            return {"text": f"Error calling Anthropic: {exc}", "citations": []}


def get_llm_provider() -> LLMProvider:
    """Factory — returns the configured LLM provider."""
    provider = settings.llm_provider.lower()
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    else:
        return DisabledProvider()


def _default_system_prompt() -> str:
    return (
        "You are a legal research assistant for the Evident BWC platform. "
        "You help attorneys, law firms, and pro se litigants analyze evidence and research case law.\n\n"
        "CRITICAL RULES:\n"
        "1. NEVER fabricate statutes, case citations, or legal authority.\n"
        "2. Only cite sources you find in the provided context or CourtListener results.\n"
        "3. If you cannot find a relevant authority, say 'Not found in sources searched' "
        "and suggest search refinements.\n"
        "4. Always include source references (document names, CourtListener URLs/IDs).\n"
        "5. Quote only small excerpts from sources.\n"
        "6. Do not provide legal advice — only research assistance.\n"
        "7. Mark any claim that needs verification with [NEEDS VERIFICATION].\n"
    )
