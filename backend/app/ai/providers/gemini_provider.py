import os
import json
from typing import Dict, Any, List
from backend.app.ai.providers.base import BaseAIProvider
from backend.app.ai.providers.mock_provider import MockAIProvider
from backend.app.core.config import settings

class GeminiAIProvider(BaseAIProvider):
    """
    Google Gemini AI Provider with automatic fallback to MockAIProvider if credentials
    are unconfigured or network requests fail.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.fallback = MockAIProvider()
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel("gemini-1.5-flash")
            except Exception:
                self._client = None

    async def parse_quick_add(self, prompt: str) -> Dict[str, Any]:
        if not self._client:
            return await self.fallback.parse_quick_add(prompt)

        try:
            sys_prompt = (
                "Extract structured productivity task info from user text. Return ONLY a JSON object with keys: "
                "title (string), category (string: Work, Personal, Education, Programming, Cybersecurity, Health), "
                "priority (string: low, medium, high, urgent), estimated_minutes (integer), tags (list of strings)."
            )
            response = self._client.generate_content(f"{sys_prompt}\nUser input: {prompt}")
            text = response.text.strip()
            # Clean markdown formatting if present
            if text.startswith("```json"):
                text = text.split("```json")[1].split("```")[0].strip()
            elif text.startswith("```"):
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            data["provider"] = "GeminiAIProvider"
            return data
        except Exception:
            return await self.fallback.parse_quick_add(prompt)

    async def suggest_schedule_optimizations(self, tasks: List[Dict[str, Any]], available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self.fallback.suggest_schedule_optimizations(tasks, available_slots)

    async def get_productivity_tip(self, context: Dict[str, Any]) -> str:
        return await self.fallback.get_productivity_tip(context)
