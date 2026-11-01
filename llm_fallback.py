"""Frugal OpenAI-compatible LLM with retry/backoff + fallback across models.

LLM_MODEL may be a comma-separated list, e.g.
  nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-31b-it:free
Each model is tried in order; transient errors (429/503/timeouts) get
exponential backoff before moving on. REQUEST_COUNT tracks real HTTP calls.
"""
import asyncio
import logging
import os

from forecasting_tools import GeneralLlm

logger = logging.getLogger(__name__)
REQUEST_COUNT = {"total": 0, "ok": 0, "by_model": {}}


class FallbackLlm(GeneralLlm):
    def __init__(self, models: list[str], base_url: str, api_key: str,
                 temperature: float = 0.3, tries_per_model: int = 2,
                 backoff_s: float = 8.0):
        super().__init__(model="openai/" + models[0], api_base=base_url,
                         api_key=api_key, temperature=temperature,
                         timeout=180, allowed_tries=1)
        self._fb_llms = [
            (m, GeneralLlm(model="openai/" + m, api_base=base_url, api_key=api_key,
                           temperature=temperature, timeout=180, allowed_tries=1))
            for m in models]
        self._tries = tries_per_model
        self._fb_base_url, self._fb_api_key, self._fb_temperature = base_url, api_key, temperature
        self._backoff = backoff_s

    async def invoke(self, prompt, system_prompt=None) -> str:
        last = None
        for name, llm in self._fb_llms:
            for attempt in range(self._tries):
                REQUEST_COUNT["total"] += 1
                REQUEST_COUNT["by_model"][name] = REQUEST_COUNT["by_model"].get(name, 0) + 1
                try:
                    out = await llm.invoke(prompt, system_prompt)
                    if out and out.strip():
                        REQUEST_COUNT["ok"] += 1
                        logger.info(f"LLM ok via {name}")
                        return out
                    raise RuntimeError("empty response")
                except Exception as e:  # noqa: BLE001
                    last = e
                    msg = str(e)[:200]
                    logger.warning(f"LLM {name} attempt {attempt+1} failed: {msg}")
                    if any(c in msg for c in ("429", "503", "502", "timeout", "Timeout", "empty")):
                        await asyncio.sleep(self._backoff * (2 ** attempt))
                    else:
                        break  # non-transient: next model
        raise RuntimeError(f"All fallback models failed; last error: {last}")


def from_env(temperature: float) -> FallbackLlm:
    models = [m.strip() for m in os.environ["LLM_MODEL"].split(",") if m.strip()]
    return FallbackLlm(models, os.environ["LLM_BASE_URL"], os.environ["LLM_API_KEY"],
                       temperature=temperature,
                       tries_per_model=int(os.getenv("LLM_TRIES_PER_MODEL", "2")))
