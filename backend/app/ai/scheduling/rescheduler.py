"""
Rescheduler — detects missed/incomplete tasks and suggests alternative
time slots.  Never auto-modifies the database.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.app.ai.scheduling.daily_scheduler import _find_next_slot, _slot_available


def find_missed_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return tasks that are overdue and not completed."""
    now = datetime.utcnow()
    missed: List[Dict[str, Any]] = []
    for t in tasks:
        if t.get("is_completed"):
            continue
        due = t.get("due_date")
        if due:
            try:
                due_dt = datetime.fromisoformat(due) if isinstance(due, str) else due
                if due_dt < now:
                    missed.append(t)
            except (ValueError, TypeError):
                pass
    return missed


def suggest_reschedule(
    missed_tasks: List[Dict[str, Any]],
    fixed_commitments: List[Dict[str, Any]],
    existing_scheduled: List[Dict[str, Any]],
    reschedule_start: str = "",
    day_start_hour: int = 8,
    day_end_hour: int = 22,
    days_ahead: int = 3,
) -> Dict[str, Any]:
    """
    For each missed task, find the earliest available slot within the next
    *days_ahead* days.

    Returns
    -------
    dict with "suggestions" list and "could_not_reschedule" list.
    Each suggestion: {task_id, title, original_due, suggested_start, suggested_end, day}
    """
    if not reschedule_start:
        reschedule_start = datetime.utcnow().strftime("%Y-%m-%d")

    base = datetime.strptime(reschedule_start, "%Y-%m-%d")

    # Build master blocked list
    blocked: List[Dict[str, Any]] = []
    for fc in fixed_commitments:
        s = datetime.fromisoformat(fc["start"]) if isinstance(fc["start"], str) else fc["start"]
        e = datetime.fromisoformat(fc["end"]) if isinstance(fc["end"], str) else fc["end"]
        blocked.append({"start": s, "end": e, "title": fc.get("title", "")})

    for es in existing_scheduled:
        s = datetime.fromisoformat(es["start"]) if isinstance(es["start"], str) else es["start"]
        e = datetime.fromisoformat(es["end"]) if isinstance(es["end"], str) else es["end"]
        blocked.append({"start": s, "end": e, "title": es.get("title", "")})

    suggestions: List[Dict[str, Any]] = []
    could_not: List[Dict[str, Any]] = []

    for task in missed_tasks:
        est = task.get("estimated_minutes", 30)
        placed = False

        for d in range(days_ahead):
            day_dt = base + timedelta(days=d)
            day_start = day_dt.replace(hour=day_start_hour, minute=0, second=0)
            day_end = day_dt.replace(hour=day_end_hour, minute=0, second=0)

            slot = _find_next_slot(day_start, est, blocked, day_end)
            if slot:
                end = slot + timedelta(minutes=est)
                suggestions.append({
                    "task_id": task.get("id"),
                    "title": task.get("title", ""),
                    "priority": task.get("priority", "medium"),
                    "original_due": task.get("due_date"),
                    "suggested_start": slot.isoformat(),
                    "suggested_end": end.isoformat(),
                    "day": day_dt.strftime("%Y-%m-%d"),
                    "duration_minutes": est,
                })
                # Block the slot so subsequent tasks don't overlap
                blocked.append({"start": slot, "end": end, "title": task.get("title", "")})
                placed = True
                break

        if not placed:
            could_not.append(task)

    return {
        "suggestions": suggestions,
        "could_not_reschedule": could_not,
        "days_searched": days_ahead,
    }
