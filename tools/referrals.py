from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_referrals_list() -> dict:
    """Get list of all referrals.

    Use this tool when user asks about:
    - List of referrals
    - Show me all referrals
    - Referral tracking
    """
    client = get_api_client()
    try:
        response = await client.get("/referrals", {"limit": 100})
        referrals = extract_list(response)

        if not referrals:
            return {"count": 0, "referrals": [], "message": "No referrals found."}

        return {
            "count": len(referrals),
            "referrals": [
                {
                    "id": r.get("id"),
                    "referrerName": r.get("referrerName"),
                    "referredName": r.get("referredName"),
                    "code": r.get("referralCode"),
                    "status": r.get("status"),
                    "rewardType": r.get("rewardType"),
                    "rewardAmount": r.get("rewardAmount"),
                }
                for r in referrals
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_referral_stats() -> dict:
    """Get referral program statistics.

    Use this tool when user asks about:
    - Referral stats/statistics
    - How many referrals
    - Referral performance
    """
    client = get_api_client()
    try:
        response = await client.get("/referrals/stats")
        return {
            "total": response.get("total", 0),
            "pending": response.get("pending", 0),
            "converted": response.get("converted", 0),
            "rewarded": response.get("rewarded", 0),
            "totalRewardAmount": response.get("totalRewardAmount", 0),
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_user_referrals(user_id: int) -> dict:
    """Get referrals made by or for a specific user.

    Args:
        user_id: The user ID to look up referrals for

    Use this tool when user asks about a specific member's referrals.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/referrals/user/{user_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def create_referral(
    referrer_id: int,
    referral_code: str,
    referred_id: int = None,
    notes: str = None,
) -> dict:
    """Create a new referral record.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        referrer_id: User ID of the person who made the referral (required)
        referral_code: Unique referral code (required)
        referred_id: User ID of the referred person (optional)
        notes: Additional notes (optional)
    """
    client = get_api_client()
    try:
        data = {
            "referrerId": referrer_id,
            "referralCode": referral_code,
        }
        if referred_id:
            data["referredId"] = referred_id
        if notes:
            data["notes"] = notes

        response = await client.post("/referrals", data)
        return {
            "success": True,
            "message": "Referral created successfully",
            "referral": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def mark_referral_rewarded(
    referral_id: int,
    reward_type: str,
    reward_amount: float,
) -> dict:
    """Mark a referral as rewarded.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        referral_id: The ID of the referral (required)
        reward_type: Type of reward - discount, free_days, cash, or credit (required)
        reward_amount: Reward amount (required)
    """
    valid_types = ["discount", "free_days", "cash", "credit"]
    if reward_type not in valid_types:
        return {"error": f"Invalid reward type. Must be one of: {', '.join(valid_types)}", "success": False}

    client = get_api_client()
    try:
        response = await client.patch(
            f"/referrals/{referral_id}/reward",
            {"rewardType": reward_type, "rewardAmount": reward_amount},
        )
        return {
            "success": True,
            "message": "Referral marked as rewarded",
            "referral": response,
        }
    except Exception as e:
        return {"error": str(e), "success": False}
