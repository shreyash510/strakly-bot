from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_member_goals(user_id: int, status: str = None) -> dict:
    """Get goals for a specific member.

    Args:
        user_id: The user ID of the member (required)
        status: Filter by status - active, achieved, or abandoned (optional)

    Use this tool when user asks about:
    - Member's goals
    - What goals does a member have
    - Goal progress for a member
    """
    client = get_api_client()
    try:
        params = {}
        if status and status in ("active", "achieved", "abandoned"):
            params["status"] = status

        response = await client.get(f"/member-goals/user/{user_id}", params)
        goals = extract_list(response)

        if not goals:
            return {"count": 0, "goals": [], "message": "No goals found for this member."}

        return {
            "count": len(goals),
            "goals": [
                {
                    "id": g.get("id"),
                    "title": g.get("title"),
                    "goalType": g.get("goalType"),
                    "status": g.get("status"),
                    "targetValue": g.get("targetValue"),
                    "currentValue": g.get("currentValue"),
                    "unit": g.get("unit"),
                    "targetDate": g.get("targetDate"),
                    "assignedByName": g.get("assignedByName"),
                }
                for g in goals
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_member_goal(
    user_id: int,
    title: str,
    goal_type: str = "general_fitness",
    description: str = None,
    target_value: float = None,
    unit: str = None,
    target_date: str = None,
) -> dict:
    """Create a new goal for a member.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        user_id: The user ID of the member (required)
        title: Goal title (required)
        goal_type: Type - weight_loss, muscle_gain, general_fitness, sports_prep, rehab, flexibility, endurance, other (optional)
        description: Goal description (optional)
        target_value: Numeric target value (optional)
        unit: Unit of measurement e.g. kg, reps (optional)
        target_date: Target date in YYYY-MM-DD format (optional)
    """
    valid_types = ["weight_loss", "muscle_gain", "general_fitness", "sports_prep", "rehab", "flexibility", "endurance", "other"]
    if goal_type not in valid_types:
        return {"error": f"Invalid goal type. Must be one of: {', '.join(valid_types)}", "success": False}

    client = get_api_client()
    try:
        data = {
            "userId": user_id,
            "goalType": goal_type,
            "title": title,
        }
        if description:
            data["description"] = description
        if target_value is not None:
            data["targetValue"] = target_value
        if unit:
            data["unit"] = unit
        if target_date:
            data["targetDate"] = target_date

        response = await client.post("/member-goals", data)
        return {
            "success": True,
            "message": f"Goal '{title}' created for member",
            "goal": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def update_goal_progress(goal_id: int, current_value: float) -> dict:
    """Update the current progress value for a member's goal.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        goal_id: The ID of the goal (required)
        current_value: The new current value (required)
    """
    client = get_api_client()
    try:
        response = await client.patch(f"/member-goals/{goal_id}/progress", {"currentValue": current_value})
        return {
            "success": True,
            "message": f"Goal progress updated to {current_value}",
            "goal": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def update_goal_status(goal_id: int, status: str) -> dict:
    """Update a goal's status (mark as achieved or abandoned).

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        goal_id: The ID of the goal (required)
        status: New status - active, achieved, or abandoned (required)
    """
    valid_statuses = ["active", "achieved", "abandoned"]
    if status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}", "success": False}

    client = get_api_client()
    try:
        response = await client.patch(f"/member-goals/{goal_id}/status", {"status": status})
        return {
            "success": True,
            "message": f"Goal marked as {status}",
            "goal": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def get_goal_milestones(goal_id: int) -> dict:
    """Get milestones/sub-goals for a specific goal.

    Args:
        goal_id: The ID of the goal

    Use this tool when user asks about milestones, sub-goals, or checklist items for a goal.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/member-goals/{goal_id}/milestones")
        milestones = extract_list(response)

        if not milestones:
            return {"count": 0, "milestones": [], "message": "No milestones found for this goal."}

        return {
            "count": len(milestones),
            "completed": sum(1 for m in milestones if m.get("isCompleted")),
            "milestones": [
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "isCompleted": m.get("isCompleted"),
                    "completedAt": m.get("completedAt"),
                    "targetValue": m.get("targetValue"),
                    "currentValue": m.get("currentValue"),
                    "unit": m.get("unit"),
                }
                for m in milestones
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_goal_milestone(goal_id: int, title: str, target_value: float = None, unit: str = None) -> dict:
    """Create a new milestone/sub-goal for a goal.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        goal_id: The ID of the goal (required)
        title: Milestone title (required)
        target_value: Numeric target value (optional)
        unit: Unit of measurement (optional)
    """
    client = get_api_client()
    try:
        data = {"title": title}
        if target_value is not None:
            data["targetValue"] = target_value
        if unit:
            data["unit"] = unit

        response = await client.post(f"/member-goals/{goal_id}/milestones", data)
        return {
            "success": True,
            "message": f"Milestone '{title}' added to goal",
            "milestone": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def toggle_milestone_complete(milestone_id: int, is_completed: bool) -> dict:
    """Toggle a milestone as completed or incomplete.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        milestone_id: The ID of the milestone (required)
        is_completed: True to mark as completed, False to mark as incomplete (required)
    """
    client = get_api_client()
    try:
        response = await client.patch(f"/member-goals/milestones/{milestone_id}", {"isCompleted": is_completed})
        status_text = "completed" if is_completed else "incomplete"
        return {
            "success": True,
            "message": f"Milestone marked as {status_text}",
            "milestone": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}
