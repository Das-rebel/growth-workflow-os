"""Base inference engine for Growth Workflow OS.

Primary: MiniMax M2.7 via OpenAI-compatible API (fast, cheap)
Fallback: Mistral Small (working)
System context from prompts/system_context.txt prepended to every call.
"""

import os
import logging

# Silence LiteLLM debug noise at module load time
os.environ["LITELLM_LOG"] = "ERROR"
os.environ["LITELLM_SUPPRESS_MAX_RETRIES_WARNING"] = "true"
os.environ["LITELLM_FALLBACK_WARNINGS"] = "false"

# Suppress litellm logging handlers
for _name in ["litellm", "LiteLLM"]:
    _logger = logging.getLogger(_name)
    _logger.setLevel(logging.ERROR)
    for _h in _logger.handlers[:]:
        _logger.removeHandler(_h)
    _logger.addHandler(logging.NullHandler())
    _logger.propagate = False

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import litellm

from config import get_model_config, load_env

# Ensure env vars are loaded
load_env()

# System context loaded once at module init
_ROOT = Path(__file__).parent.parent
_SYSTEM_CONTEXT_PATH = _ROOT / "prompts" / "system_context.txt"

_OPERATOR_CONTEXT: str = ""
if _SYSTEM_CONTEXT_PATH.exists():
    _OPERATOR_CONTEXT = _SYSTEM_CONTEXT_PATH.read_text().strip()


def _load_env_key(key: str) -> str:
    """Load a key from environment or config/.env."""
    val = os.getenv(key, "")
    if val:
        return val
    env_path = _ROOT / "config" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return ""


class InferenceEngine(ABC):
    """Base class for all inference engines.

    Uses LiteLLM with Groq/Cerebras. Operator context prepended to every call.
    """

    def __init__(self, purpose: str):
        self.purpose = purpose
        self.config = get_model_config(purpose)

    def infer(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_output: bool = False,
        json_schema: Optional[dict] = None,
    ) -> str:
        """Run inference via LiteLLM (MiniMax/Mistral) with operator context.

        Args:
            prompt: The user prompt
            system_prompt: Additional context appended after operator context
            json_output: If True, request JSON response
            json_schema: JSON Schema for structured output

        Returns:
            The model's response text
        """
        model = self.config.get("model", "openai/MiniMax-M2.7")
        fallback = self.config.get("fallback", "mistral/mistral-small-latest")
        api_base = self.config.get("api_base")
        temperature = self.config.get("temperature", 0.5)
        max_tokens = self.config.get("max_tokens", 3000)

        # Build system message: operator context + any additional context
        system_parts = []
        if _OPERATOR_CONTEXT:
            system_parts.append(_OPERATOR_CONTEXT)
        if system_prompt:
            system_parts.append(system_prompt)

        system_message = "\n\n".join(system_parts) if system_parts else None

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": 60,
            "request_timeout": 60,
        }

        # Pass api_base + api_key for OpenAI-compatible providers (MiniMax via OpenCode)
        if api_base:
            kwargs["api_base"] = api_base
            kwargs["api_key"] = _load_env_key("OPENCODE_GO_API_KEY") or _load_env_key("MINIMAX_API_KEY")

        if json_output and json_schema:
            kwargs["response_format"] = {"type": "json_object", "json_schema": json_schema}

        try:
            response = litellm.completion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            if fallback:
                kwargs["model"] = fallback
                # Mistral uses its own key, remove MiniMax-specific params
                kwargs.pop("api_base", None)
                kwargs["api_key"] = _load_env_key("MISTRAL_API_KEY")
                try:
                    response = litellm.completion(**kwargs)
                    return response.choices[0].message.content
                except Exception:
                    pass
            raise RuntimeError(f"Inference failed: {e}")

    @abstractmethod
    def run(self, input_data) -> dict:
        """Run the inference engine on input data.

        Returns:
            Dict with inference results
        """
        pass