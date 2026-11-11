import re
from typing import Dict, Any, List
from datetime import datetime, timedelta
from backend.app.ai.providers.base import BaseAIProvider

class MockAIProvider(BaseAIProvider):
    """
    Zero-dependency, offline mock AI provider for local testing and development.
    Uses pattern matching and heuristic logic to simulate natural language task extraction.
    """

    async def parse_quick_add(self, prompt: str) -> Dict[str, Any]:
        title = prompt.strip()
        priority = "medium"
        category = "Personal"
        duration = 30
        due_date = datetime.utcnow() + timedelta(days=1)

        low_prompt = prompt.lower()

        # Priority detection
        if any(w in low_prompt for w in ["urgent", "asap", "critical"]):
            priority = "urgent"
        elif any(w in low_prompt for w in ["important", "high priority"]):
            priority = "high"
        elif any(w in low_prompt for w in ["low priority", "someday", "when free"]):
            priority = "low"

        # Category detection
        if any(w in low_prompt for w in ["python", "code", "programming", "fastapi", "flutter", "dev"]):
            category = "Programming"
        elif any(w in low_prompt for w in ["security", "cyber", "network", "firewall", "audit"]):
            category = "Cybersecurity"
        elif any(w in low_prompt for w in ["study", "exam", "assignment", "lecture", "book", "learn"]):
            category = "Education"
        elif any(w in low_prompt for w in ["run", "gym", "workout", "water", "health", "sleep"]):
            category = "Health"
        elif any(w in low_prompt for w in ["work", "meeting", "client", "standup", "report"]):
            category = "Work"

        # Duration detection
        dur_match = re.search(r'(\d+)\s*(hour|hr|minute|min)', low_prompt)
        if dur_match:
            val = int(dur_match.group(1))
            unit = dur_match.group(2)
            duration = val * 60 if 'h' in unit else val

        return {
            "title": title,
            "category": category,
            "priority": priority,
            "estimated_minutes": duration,
            "suggested_due_date": due_date.isoformat(),
            "confidence": 0.95,
            "provider": "MockAIProvider"
        }

    async def suggest_schedule_optimizations(self, tasks: List[Dict[str, Any]], available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "status": "optimized",
            "message": "Tasks arranged according to priority and cognitive energy curve.",
            "recommended_order": [t.get("id") for t in tasks],
            "breaks_inserted": len(tasks) > 2,
            "provider": "MockAIProvider"
        }

    async def get_productivity_tip(self, context: Dict[str, Any]) -> str:
        score = context.get("score", 80)
        if score > 85:
            return "Outstanding velocity today. Maintain steady hydration and take a 5-minute breather."
        elif score > 70:
            return "Good progress! Focus on your highest priority task next to break through the day's plateau."
        else:
            return "Consider running a 25-minute Pomodoro session to kickstart momentum on a single pending item."
