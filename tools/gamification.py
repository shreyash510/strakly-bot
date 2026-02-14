from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_challenges(status: str = None) -> dict:
    """Get gym challenges/competitions with optional status filter.

    Args:
        status: Filter by status - upcoming, active, completed (optional)

    Use this tool when user asks about:
    - Current challenges
    - Active competitions
    - Gym challenges
    - Upcoming challenges
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if status and status in ("upcoming", "active", "completed"):
            params["status"] = status

        response = await client.get("/gamification/challenges", params)
        challenges = extract_list(response)

        if not challenges:
            return {"count": 0, "challenges": [], "message": "No challenges found."}

        return {
            "count": len(challenges),
            "challenges": [
                {
                    "id": c.get("id"),
                    "title": c.get("title"),
                    "description": c.get("description"),
                    "type": c.get("type"),
                    "status": c.get("status"),
                    "startDate": c.get("startDate"),
                    "endDate": c.get("endDate"),
                    "participantCount": c.get("participantCount"),
                    "difficulty": c.get("difficulty"),
                }
                for c in challenges
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_challenge_leaderboard(challenge_id: int) -> dict:
    """Get the leaderboard for a specific challenge.

    Args:
        challenge_id: The challenge ID (required)

    Use this tool when user asks about:
    - Challenge leaderboard
    - Who is winning
    - Challenge rankings
    - Top performers in a challenge
    """
    client = get_api_client()
    try:
        response = await client.get(f"/gamification/challenges/{challenge_id}/leaderboard")
        entries = extract_list(response)

        if not entries:
            return {"count": 0, "leaderboard": [], "message": "No leaderboard entries yet."}

        return {
            "count": len(entries),
            "leaderboard": [
                {
                    "rank": i + 1,
                    "userId": e.get("userId"),
                    "userName": e.get("userName"),
                    "score": e.get("score") or e.get("currentValue"),
                    "progress": e.get("progress"),
                }
                for i, e in enumerate(entries)
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_user_achievements(user_id: int) -> dict:
    """Get achievements/badges earned by a specific user.

    Args:
        user_id: The user ID (required)

    Use this tool when user asks about:
    - Member's achievements
    - Badges earned by a member
    - What has a member accomplished
    """
    client = get_api_client()
    try:
        response = await client.get(f"/gamification/achievements/user/{user_id}")
        achievements = extract_list(response)

        if not achievements:
            return {"count": 0, "achievements": [], "message": "No achievements found for this user."}

        return {
            "count": len(achievements),
            "achievements": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "description": a.get("description"),
                    "badgeIcon": a.get("badgeIcon"),
                    "earnedAt": a.get("earnedAt"),
                }
                for a in achievements
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_gamification_stats() -> dict:
    """Get overall gamification statistics.

    Use this tool when user asks about:
    - Gamification stats
    - Challenge participation stats
    - How many people are participating
    - Badge statistics
    """
    client = get_api_client()
    try:
        response = await client.get("/gamification/stats")
        return response
    except Exception as e:
        return {"error": str(e)}
