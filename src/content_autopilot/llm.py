from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from .config import Settings


class LLMClient:
    def __init__(self, settings: Settings):
        if not settings.llm_api_key:
            raise RuntimeError("CONTENTAUTOPILOT_LLM_API_KEY is not configured")
        self.model = settings.llm_model
        self.client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)

    def text(self, system: str, user: str, temperature: float = 0.4) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned an empty response")
        return content.strip()

    def json(self, system: str, user: str, temperature: float = 0.2) -> dict[str, Any]:
        raw = self.text(system + "\nReturn valid JSON only.", user, temperature=temperature)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                raise RuntimeError(f"Could not parse JSON from LLM response: {raw[:300]}")
            return json.loads(match.group(0))
