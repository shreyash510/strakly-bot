from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_loyalty_dashboard() -> dict:
    """Get loyalty program dashboard analytics.

    Use this tool when user asks about:
    - Loyalty program overview
    - Loyalty stats
    - Rewards program performance
    - Points distribution
    """
    client = get_api_client()
    try:
        response = await client.get("/loyalty/dashboard")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_loyalty_tiers() -> dict:
    """Get loyalty program tiers (bronze, silver, gold, platinum, etc.).

    Use this tool when user asks about:
    - Loyalty tiers
    - Reward levels
    - Tier benefits
    - How do tiers work
    """
    client = get_api_client()
    try:
        response = await client.get("/loyalty/tiers")
        tiers = extract_list(response)

        if not tiers:
            return {"count": 0, "tiers": [], "message": "No loyalty tiers configured."}

        return {
            "count": len(tiers),
            "tiers": [
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "minPoints": t.get("minPoints"),
                    "multiplier": t.get("multiplier"),
                    "benefits": t.get("benefits"),
                }
                for t in tiers
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_user_loyalty_points(user_id: int) -> dict:
    """Get loyalty points balance and tier for a specific user.

    Args:
        user_id: The user ID (required)

    Use this tool when user asks about:
    - Member's loyalty points
    - How many points does a member have
    - Member's tier level
    - Reward points for a user
    """
    client = get_api_client()
    try:
        response = await client.get(f"/loyalty/points/user/{user_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_available_rewards() -> dict:
    """Get available rewards that can be redeemed with loyalty points.

    Use this tool when user asks about:
    - Available rewards
    - What can be redeemed
    - Reward options
    - Points redemption options
    """
    client = get_api_client()
    try:
        response = await client.get("/loyalty/rewards")
        rewards = extract_list(response)

        if not rewards:
            return {"count": 0, "rewards": [], "message": "No rewards available."}

        return {
            "count": len(rewards),
            "rewards": [
                {
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "description": r.get("description"),
                    "pointsCost": r.get("pointsCost"),
                    "type": r.get("type"),
                    "isActive": r.get("isActive"),
                }
                for r in rewards
            ],
        }
    except Exception as e:
        return {"error": str(e)}
