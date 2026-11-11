import asyncio
from backend.app.ai.providers.mock_provider import MockAIProvider

def test_mock_ai_quick_add():
    provider = MockAIProvider()
    result = asyncio.run(provider.parse_quick_add("Study Python and network security tomorrow for 2 hours urgent"))
    assert result["priority"] == "urgent"
    assert result["estimated_minutes"] == 120
    assert result["category"] in ["Programming", "Cybersecurity", "Education"]

def test_mock_ai_productivity_tip():
    provider = MockAIProvider()
    tip = asyncio.run(provider.get_productivity_tip({"score": 85}))
    assert isinstance(tip, str)
    assert len(tip) > 10
