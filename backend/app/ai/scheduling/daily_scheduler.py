"""
Deterministic daily schedule builder.

Architecture:
  User Request → Backend Validation → Deterministic Engine
  → Conflict Detection → Explanation → User Confirmation → DB Update

The scheduler does NOT call an LLM to decide times.  It uses a greedy
priority-based bin-packing algorithm that honours fixed commitments,
estimated durations, energy curves, and mandatory break insertion.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from copy import deepcopy


# ---------- energy curve (0-10) by hour of day ----------
# Peaks at 10 AM and 3 PM.  Low around 1-2 PM (post-lunch dip).
ENERGY_CURVE: Dict[int, int] = {
    6: 4, 7: 6, 8: 7, 9: 9, 10: 10, 11: 9,
    12: 7, 13: 5, 14: 5, 15: 8, 16: 8, 17: 7,
    18: 6, 19: 5, 20: 4, 21: 3, 22: 2, 23: 1,
}

PRIORITY_WEIGHT = {"urgent": 4, "high": 3, "medium": 2, "low": 1}

BREAK_AFTER_MINUTES = 90   # insert 10-min break after 90 min continuous work
BREAK_DURATION = 10        # minutes


def _slot_available(
    start: datetime, end: datetime, blocked: List[Dict[str, Any]]
) -> bool:
    """Return True if [start, end) does not overlap any blocked interval."""
    for b in blocked:
        b_start = b["start"]
        b_end = b["end"]
        if start < b_end and end > b_start:
            return False
    return True


def _find_next_slot(
    after: datetime,
    duration_min: int,
    blocked: List[Dict[str, Any]],
    day_end: datetime,
) -> Optional[datetime]:
    """Walk forward in 5-min steps to find the first open slot of given length."""
    cursor = after
    while cursor + timedelta(minutes=duration_min) <= day_end:
        proposed_end = cursor + timedelta(minutes=duration_min)
        if _slot_available(cursor, proposed_end, blocked):
            return cursor
        cursor += timedelta(minutes=5)
    return None


def build_daily_schedule(
    tasks: List[Dict[str, Any]],
    fixed_commitments: List[Dict[str, Any]],
    day_date: str = "",
    day_start_hour: int = 8,
    day_end_hour: int = 22,
    preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a non-overlapping schedule for *day_date*.

    Parameters
    ----------
    tasks : list of dicts with keys id, title, priority, estimated_minutes,
            category, due_date (iso str | None)
    fixed_commitments : list of dicts with keys title, start (iso), end (iso)
    day_date : "YYYY-MM-DD"  (defaults to today)
    day_start_hour / day_end_hour : workable hours
    preferences : optional overrides (break_duration, break_after, etc.)

    Returns
    -------
    dict with "scheduled", "unscheduled", "warnings", "total_minutes",
              "break_minutes"
    """
    if not day_date:
        day_date = datetime.utcnow().strftime("%Y-%m-%d")

    base = datetime.strptime(day_date, "%Y-%m-%d")
    day_start = base.replace(hour=day_start_hour, minute=0)
    day_end = base.replace(hour=day_end_hour, minute=0)

    break_after = (preferences or {}).get("break_after_minutes", BREAK_AFTER_MINUTES)
    break_dur = (preferences or {}).get("break_duration", BREAK_DURATION)

    # Build blocked list from fixed commitments
    blocked: List[Dict[str, Any]] = []
    for fc in fixed_commitments:
        s = datetime.fromisoformat(fc["start"]) if isinstance(fc["start"], str) else fc["start"]
        e = datetime.fromisoformat(fc["end"]) if isinstance(fc["end"], str) else fc["end"]
        blocked.append({"start": s, "end": e, "title": fc.get("title", "Fixed")})

    # Sort tasks: urgent/deadline first, then priority, then energy match
    def _sort_key(t: Dict[str, Any]):
        pw = PRIORITY_WEIGHT.get(t.get("priority", "medium"), 2)
        # Tasks with earlier due_date get priority
        due = t.get("due_date")
        if due and isinstance(due, str):
            try:
                due_dt = datetime.fromisoformat(due)
                due_days = max((due_dt - base).days, 0)
            except ValueError:
                due_days = 999
        else:
            due_days = 999
        return (-pw, due_days)

    sorted_tasks = sorted(deepcopy(tasks), key=_sort_key)

    scheduled: List[Dict[str, Any]] = []
    unscheduled: List[Dict[str, Any]] = []
    warnings: List[str] = []
    total_work_min = 0
    break_min = 0
    continuous_min = 0

    cursor = day_start

    for task in sorted_tasks:
        est = task.get("estimated_minutes", 30)

        # Insert break if continuous work exceeds threshold
        if continuous_min >= break_after:
            brk_slot = _find_next_slot(cursor, break_dur, blocked, day_end)
            if brk_slot:
                blocked.append({
                    "start": brk_slot,
                    "end": brk_slot + timedelta(minutes=break_dur),
                    "title": "Break",
                })
                cursor = brk_slot + timedelta(minutes=break_dur)
                break_min += break_dur
                continuous_min = 0

        slot = _find_next_slot(cursor, est, blocked, day_end)
        if slot is None:
            unscheduled.append(task)
            warnings.append(f"Cannot fit '{task.get('title', '')}' ({est} min) today.")
            continue

        end = slot + timedelta(minutes=est)
        entry = {
            "task_id": task.get("id"),
            "title": task.get("title", ""),
            "priority": task.get("priority", "medium"),
            "category": task.get("category", ""),
            "start": slot.isoformat(),
            "end": end.isoformat(),
            "duration_minutes": est,
            "energy_level": ENERGY_CURVE.get(slot.hour, 5),
        }
        scheduled.append(entry)
        blocked.append({"start": slot, "end": end, "title": task.get("title", "")})
        total_work_min += est
        continuous_min += est
        cursor = end

    return {
        "date": day_date,
        "scheduled": scheduled,
        "unscheduled": unscheduled,
        "warnings": warnings,
        "total_work_minutes": total_work_min,
        "break_minutes": break_min,
        "slots_used": len(scheduled),
        "available_hours": day_end_hour - day_start_hour,
    }
