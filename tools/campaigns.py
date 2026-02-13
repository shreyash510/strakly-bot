from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_campaigns(status: str = None) -> dict:
    """Get email/SMS campaigns with optional status filter.

    Args:
        status: Filter by status - draft, scheduled, sending, sent, cancelled (optional)

    Use this tool when user asks about:
    - Campaigns list
    - Email campaigns
    - SMS campaigns
    - Marketing campaigns
    - Campaign status
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if status:
            params["status"] = status

        response = await client.get("/campaigns", params)
        campaigns = extract_list(response)

        if not campaigns:
            return {"count": 0, "campaigns": [], "message": "No campaigns found."}

        return {
            "count": len(campaigns),
            "campaigns": [
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "type": c.get("type"),
                    "status": c.get("status"),
                    "scheduledAt": c.get("scheduledAt"),
                    "sentAt": c.get("sentAt"),
                    "totalSent": c.get("totalSent"),
                    "totalOpened": c.get("totalOpened"),
                    "totalClicked": c.get("totalClicked"),
                }
                for c in campaigns
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_campaign_details(campaign_id: int) -> dict:
    """Get detailed information about a specific campaign including delivery stats.

    Args:
        campaign_id: The campaign ID (required)

    Use this tool when user asks about:
    - Campaign details
    - Campaign performance
    - Open rate or click rate for a campaign
    """
    client = get_api_client()
    try:
        response = await client.get(f"/campaigns/{campaign_id}")
        return response
    except Exception as e:
        return {"error": str(e)}
