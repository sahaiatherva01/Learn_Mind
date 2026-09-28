# LLM client interface and stub implementation per ARCH.md §3 and Rules.md D.5, G.3
import hashlib
from typing import Optional, Dict, Any


class LLMClient:
    """
    Unified LLM Client interface with caching, retries, and provider fallback.
    Rules.md D.5: All LLM calls go through LLMClient.
    """

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    @staticmethod
    def compute_prompt_hash(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_tier: str = "fast",  # "fast" or "strong"
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """
        Base generation method.
        """
        # In mock mode / unit test mode, return deterministic structured output
        prompt_hash = self.compute_prompt_hash(prompt)
        return {
            "text": f"Mock response for hash {prompt_hash[:8]}",
            "model": f"mock-{model_tier}",
            "tokens_used": 50,
            "cached": False,
        }


llm_client = LLMClient()
