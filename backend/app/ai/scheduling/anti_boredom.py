"""
Anti-boredom scheduling engine / Cognitive task interleaving.

Prevents mental fatigue by alternating between different cognitive categories:
  - Technical / Logical (Programming, Cybersecurity, Math)
  - Learning / Theoretical (Education, Research, Reading)
  - Administrative / Operational (Work, Email, Chores)
  - Physical / Restorative (Health, Exercise)
  - Creative / Strategic (Entrepreneurship, Writing, Design)
"""

from typing import List, Dict, Any


CATEGORY_COGNITIVE_MAP = {
    "Programming": "logical",
    "Cybersecurity": "logical",
    "Education": "learning",
    "Research": "learning",
    "Work": "administrative",
    "Health": "physical",
    "Entrepreneurship": "creative",
    "Personal": "administrative",
}


def get_cognitive_type(category: str) -> str:
    return CATEGORY_COGNITIVE_MAP.get(category, "general")


def interleave_tasks_anti_boredom(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Reorders a list of tasks to minimize consecutive tasks with the same cognitive load.
    High/urgent priority tasks are prioritized, but within similar priorities,
    cognitive variety is maximized.
    """
    if len(tasks) <= 2:
        return tasks

    # Group by priority first
    urgent = [t for t in tasks if t.get("priority") == "urgent"]
    high = [t for t in tasks if t.get("priority") == "high"]
    medium = [t for t in tasks if t.get("priority") == "medium"]
    low = [t for t in tasks if t.get("priority") == "low"]

    def _interleave_tier(tier_tasks: List[Dict[str, Any]], last_type: str) -> (List[Dict[str, Any]], str):
        if not tier_tasks:
            return [], last_type

        result = []
        pool = list(tier_tasks)
        curr_last = last_type

        while pool:
            # Find task that doesn't match last cognitive type
            match_idx = -1
            for i, t in enumerate(pool):
                cog = get_cognitive_type(t.get("category", ""))
                if cog != curr_last:
                    match_idx = i
                    break
            
            if match_idx == -1:
                # If all remaining have same type, take the first one
                match_idx = 0

            chosen = pool.pop(match_idx)
            result.append(chosen)
            curr_last = get_cognitive_type(chosen.get("category", ""))

        return result, curr_last

    final_list: List[Dict[str, Any]] = []
    last_type = ""

    for tier in [urgent, high, medium, low]:
        interleaved, last_type = _interleave_tier(tier, last_type)
        final_list.extend(interleaved)

    return final_list
