"""
Weekly planner — distributes tasks across 7 days, balancing workload.

Uses the daily_scheduler internally for each day, but first assigns
tasks to days based on:
  • Due-date urgency (must be on or before due date)
  • Priority weighting
  • Even workload distribution (minutes/day target)
  • Rest-day configuration
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from backend.app.ai.scheduling.daily_scheduler import build_daily_schedule

PRIORITY_WEIGHT = {"urgent": 4, "high": 3, "medium": 2, "low": 1}


def build_weekly_plan(
    tasks: List[Dict[str, Any]],
    fixed_commitments: List[Dict[str, Any]],
    week_start: str = "",
    day_start_hour: int = 8,
    day_end_hour: int = 22,
    rest_days: Optional[List[int]] = None,
    max_minutes_per_day: int = 480,
) -> Dict[str, Any]:
    """
    Distribute *tasks* across a 7-day week starting from *week_start*.

    Parameters
    ----------
    tasks : list of task dicts (id, title, priority, estimated_minutes,
            category, due_date)
    fixed_commitments : list of dicts (title, start ISO, end ISO)
    week_start : "YYYY-MM-DD" of Monday; defaults to current week's Monday
    rest_days : list of weekday indices (0=Mon) where no tasks are scheduled
    max_minutes_per_day : soft cap per day

    Returns
    -------
    dict with day_plans (list of daily schedules), unscheduled, warnings,
         total_minutes
    """
    if not week_start:
        today = datetime.utcnow()
        monday = today - timedelta(days=today.weekday())
        week_start = monday.strftime("%Y-%m-%d")

    if rest_days is None:
        rest_days = []  # No rest days by default

    base = datetime.strptime(week_start, "%Y-%m-%d")
    days = [(base + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    # Bucket fixed commitments by day
    fc_by_day: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for fc in fixed_commitments:
        fc_start = fc["start"] if isinstance(fc["start"], str) else fc["start"].isoformat()
        fc_day = fc_start[:10]
        fc_by_day[fc_day].append(fc)

    # Assign tasks to days
    day_buckets: Dict[str, List[Dict[str, Any]]] = {d: [] for d in days}
    day_load: Dict[str, int] = {d: 0 for d in days}  # total minutes assigned
    unscheduled: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # Sort tasks by urgency
    def _urgency(t: Dict[str, Any]):
        pw = PRIORITY_WEIGHT.get(t.get("priority", "medium"), 2)
        due = t.get("due_date")
        if due:
            try:
                dd = datetime.fromisoformat(due) if isinstance(due, str) else due
                diff = (dd - base).days
            except (ValueError, TypeError):
                diff = 999
        else:
            diff = 999
        return (-pw, diff)

    sorted_tasks = sorted(tasks, key=_urgency)

    for task in sorted_tasks:
        est = task.get("estimated_minutes", 30)
        due = task.get("due_date")
        assigned = False

        # Determine latest allowed day
        if due:
            try:
                due_dt = datetime.fromisoformat(due) if isinstance(due, str) else due
                latest_day = due_dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                latest_day = days[-1]
        else:
            latest_day = days[-1]

        # Find the lightest eligible day
        eligible = [
            d for d in days
            if d <= latest_day
            and days.index(d) not in rest_days
        ]

        if not eligible:
            # Past-due or no eligible days
            eligible = [d for d in days if days.index(d) not in rest_days]

        # Pick lightest day under capacity
        for d in sorted(eligible, key=lambda x: day_load[x]):
            if day_load[d] + est <= max_minutes_per_day:
                day_buckets[d].append(task)
                day_load[d] += est
                assigned = True
                break

        if not assigned:
            # Try any non-rest day (overflow)
            for d in sorted(eligible, key=lambda x: day_load[x]):
                day_buckets[d].append(task)
                day_load[d] += est
                assigned = True
                warnings.append(
                    f"Day {d} exceeds {max_minutes_per_day} min target with '{task.get('title', '')}'."
                )
                break

        if not assigned:
            unscheduled.append(task)
            warnings.append(f"Could not assign '{task.get('title', '')}' to any day this week.")

    # Build daily schedules
    day_plans: List[Dict[str, Any]] = []
    total_minutes = 0

    for d in days:
        weekday_idx = days.index(d)
        if weekday_idx in rest_days:
            day_plans.append({
                "date": d,
                "is_rest_day": True,
                "scheduled": [],
                "unscheduled": [],
                "warnings": [],
                "total_work_minutes": 0,
                "break_minutes": 0,
                "slots_used": 0,
                "available_hours": 0,
            })
            continue

        daily = build_daily_schedule(
            tasks=day_buckets[d],
            fixed_commitments=fc_by_day.get(d, []),
            day_date=d,
            day_start_hour=day_start_hour,
            day_end_hour=day_end_hour,
        )
        daily["is_rest_day"] = False
        day_plans.append(daily)
        total_minutes += daily.get("total_work_minutes", 0)

        # Collect any tasks the daily scheduler couldn't fit
        if daily.get("unscheduled"):
            for ut in daily["unscheduled"]:
                unscheduled.append(ut)
            warnings.extend(daily.get("warnings", []))

    return {
        "week_start": week_start,
        "day_plans": day_plans,
        "unscheduled": unscheduled,
        "warnings": warnings,
        "total_work_minutes": total_minutes,
    }
