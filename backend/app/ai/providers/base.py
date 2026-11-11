from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAIProvider(ABC):
    @abstractmethod
    async def parse_quick_add(self, prompt: str) -> Dict[str, Any]:
        """Parses natural language task into structured fields."""
        pass

    @abstractmethod
    async def suggest_schedule_optimizations(self, tasks: List[Dict[str, Any]], available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provides AI recommendations for daily schedule arrangement."""
        pass

    @abstractmethod
    async def get_productivity_tip(self, context: Dict[str, Any]) -> str:
        """Generates dynamic productivity recommendation based on history."""
        pass
